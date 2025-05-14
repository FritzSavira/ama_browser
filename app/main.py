# Standard library imports
import json
import logging
import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

# Third-party imports
import certifi
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient

# Local imports
from aio_straico import straico_client
# .prompt muss für gunicorn auf Fly.io sein
from prompt import (
    prompt_pastor_personal, prompt_theologian_personal, prompt_preacher_personal,
    prompt_pastor_factual, prompt_theologian_factual, prompt_preacher_factual,
    prompt_tags, prompt_abstraction
)


# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants and configuration
DATA_DIR = '/data'
LOG_FILE = os.path.join(DATA_DIR, 'ama_log.json')
ANSWER_FOOTER = ("<br /><br /> *Diese Antwort wurde mit KI erstellt und kann fehlerhaft sein."
                 " Die Verantwortung, wie Sie diese Antwort nutzen, liegt bei Ihnen.*")

# MongoDB configuration
MONGODB_URI = os.environ.get('MONGODB_URI')
DB_NAME = 'ama_browser'
COLLECTION_AMA_LOG = 'ama_log'
COLLECTION_AMA_PROMPTS = 'ama_prompts'

# LLM configuration
ANSWER_LLM = 'openai/gpt-4o-2024-11-20'
# ANSWER_LLM = 'anthropic/claude-3.7-sonnet:thinking'
TAGS_LLM = 'anthropic/claude-3.5-sonnet'

# Global thread pool for asynchronous operations
executor = ThreadPoolExecutor(max_workers=3)


# Hilfsfunktion: Ist der Benutzer ein Pro-Nutzer?
def is_pro_user():
    return session.get('is_pro', False)


def get_mongodb_client() -> MongoClient:
    """
    Initialize and return a MongoDB client with proper configuration.

    Returns:
        MongoClient: A configured MongoDB client instance

    Raises:
        Exception: If unable to connect to MongoDB
    """
    try:
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            tls=True,
            tlsCAFile=certifi.where()
        )
        return client
    except Exception as e:
        logger.error(f"MongoDB connection error: {str(e)}")
        raise


def process_tags_and_logging(answer_markdown: str, question: str, reply: Dict,
                             prompt_text: str, unique_id: str, abstraction: Dict, agent: str) -> None:
    """
    Process tags, abstraction, and logging asynchronously after the main response.

    Args:
        answer_markdown: The Markdown text of the AI answer
        question: The user's question
        reply: The LLM response
        prompt_text: The prompt used for generation
        unique_id: Unique ID for the interaction
        abstraction: The question abstraction
        agent: The agent type used
    """
    try:
        # Generate tags
        reply_tags = ChatService.generate_tags(answer_markdown)
        tags = reply_tags['completion']['choices'][0]['message']['content']
        tags = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', tags).group()

        # Save prompt and log
        prompt_version = LoggingService.save_prompt(reply, prompt_text, agent)
        LoggingService.save_log(reply, tags, abstraction, unique_id, prompt_version)

        logger.info(f"Tags, abstraction and logging processed for question: {question[:50]}...")
    except Exception as e:
        logger.error(f"Error in processing: {str(e)}")


def get_prompt_setting():
    """
    Dynamically reads the current value of prompt_setting from the file.
    """
    try:
        with open('app/prompt_setting.py', 'r', encoding='utf-8') as f:
            content = f.read()
            return content
    except Exception as e:
        logger.error(f"Error reading prompt_setting.py: {str(e)}")
        # Fallback zu einem Standardwert
        return "Die prompt_setting.py Datei konnte nicht gelesen werden."


def get_faq():
    """
    Reads the FAQ data from the JSON file.
    Returns:
    list: List of dictionaries with questions and answers
    """
    try:
        # Path to JSON file relative to script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, 'faq.json')

        # Opening and reading the JSON file
        with open(json_path, 'r', encoding='utf-8') as file:
            faq_data = json.load(file)
        return faq_data

    except FileNotFoundError:
        print("Fehler: Die Datei faq.json wurde nicht gefunden.")
        return []
    except json.JSONDecodeError:
        print("Fehler: Die JSON-Datei konnte nicht dekodiert werden.")
        return []
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {str(e)}")
        return []


class AbstractionService:
    """
    Service for creating privacy-compliant abstractions of user queries.
    """

    @staticmethod
    def abstract_question(question: str, llm_client, prompt_abstraction: str) -> Dict:
        """
        Create a privacy-compliant abstraction of the user query.

        Args:
            question: The user's question
            llm_client: The LLM client to use for abstraction
            prompt_abstraction: The abstraction prompt

        Returns:
            Dict: The abstraction result
        """
        try:
            reply = llm_client.prompt_completion(
                TAGS_LLM,
                prompt_abstraction + question
            )
            abstraction = json.loads(
                reply['completion']['choices'][0]['message']['content']
            )
            return abstraction
        except Exception as e:
            logger.error(f"Error during abstraction: {str(e)}")
            return {}


class ChatService:
    """
    Service for generating AI responses and processing text.
    """

    @staticmethod
    def generate_reply(abstraction: Dict, question: str, prompt_text: str) -> Dict:
        """
        Generate an AI answer to the given question using the specified prompt.

        Args:
            abstraction: The abstracted question information
            question: The original user question
            prompt_text: The prompt to use for generation

        Returns:
            Dict: The LLM response

        Raises:
            Exception: If an error occurs during generation
        """
        try:
            with straico_client(API_KEY=straico_api_key) as client:
                abstraction_str = str(abstraction)
                reply = client.prompt_completion(
                    ANSWER_LLM,
                    prompt_text + abstraction_str + question
                )
                return reply
        except Exception as e:
            logger.error(f"Error generating reply: {str(e)}")
            raise

    @staticmethod
    def generate_tags(answer_markdown: str) -> Dict:
        """
        Generate tags for the given AI response.

        Args:
            answer_markdown: The Markdown text of the AI response

        Returns:
            Dict: The LLM response containing tags

        Raises:
            Exception: If an error occurs during tag generation
        """
        try:
            with straico_client(API_KEY=straico_api_key) as client:
                reply = client.prompt_completion(
                    TAGS_LLM,
                    prompt_tags + answer_markdown
                )
                return reply
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            raise


class LoggingService:
    """
    Service for logging chat interactions and feedback.
    """

    @staticmethod
    def save_log(reply: Dict, tags: str, abstraction: Dict,
                 entry_id: str, prompt_version: str) -> None:
        """
        Save chat interactions to MongoDB.

        Args:
            reply: The LLM response
            tags: The generated tags
            abstraction: The question abstraction
            entry_id: Unique ID for the interaction
            prompt_version: The prompt version used

        Raises:
            Exception: If an error occurs during saving
        """
        tags = json.loads(tags)
        try:
            client = get_mongodb_client()
            db = client[DB_NAME]
            collection = db[COLLECTION_AMA_LOG]

            log_entry = {
                "id": entry_id,
                "question_abstraction": abstraction,
                "prompt": prompt_version,
                "reply": reply,
                "tags": tags
            }

            collection.insert_one(log_entry)
            client.close()

        except Exception as e:
            logger.error(f"Error saving log data to MongoDB: {str(e)}")
            raise

    @staticmethod
    def save_feedback(entry_id: str, feedback_data: Dict) -> None:
        """
        Save user feedback to MongoDB.

        Args:
            entry_id: The unique ID of the chat interaction
            feedback_data: The feedback data to save

        Raises:
            Exception: If an error occurs during saving
        """
        try:
            client = get_mongodb_client()
            db = client[DB_NAME]
            collection = db[COLLECTION_AMA_LOG]

            # Prepare fields to update
            update_fields = {}
            for key, value in feedback_data.items():
                if key in ['rating', 'free_text']:
                    update_fields[f"feedback.{key}"] = value

            if not update_fields:
                logger.error(f"No valid feedback data provided for ID: {entry_id}")
                return

            # Update the existing document with feedback fields
            result = collection.update_one(
                {"id": entry_id},
                {"$set": update_fields}
            )

            if result.modified_count == 0:
                logger.error(f"No matching entry found for ID: {entry_id}")

            client.close()

        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
            raise

    @staticmethod
    def save_prompt(reply: Dict, prompt_text: str, agent: str) -> str:
        """
        Save the prompt to a dedicated MongoDB collection.

        Args:
            reply: The LLM response
            prompt_text: The prompt text used
            agent: The agent type

        Returns:
            str: The prompt version identifier

        Raises:
            Exception: If an error occurs during saving
        """
        try:
            # Get timestamp from reply
            created = reply['completion']['created']
        except (KeyError, TypeError):
            created = 'NA'

        # Map the agent to the appropriate prompt_version
        if agent == 'pastoral-seelsorgerlich-sachlich':
            prompt_version = f"prompt_pastor_factual_{created}"
        elif agent == 'pastoral-seelsorgerlich-persönlich':
            prompt_version = f"prompt_pastor_personal_{created}"
        elif agent == 'theologisch-wissenschaftlich-sachlich':
            prompt_version = f"prompt_theologian_factual_{created}"
        elif agent == 'theologisch-wissenschaftlich-persönlich':
            prompt_version = f"prompt_theologian_personal_{created}"
        elif agent == 'predigend-erzählend-sachlich':
            prompt_version = f"prompt_preacher_factual_{created}"
        elif agent == 'predigend-erzählend-persönlich':
            prompt_version = f"prompt_preacher_personal_{created}"
        elif agent == 'individuell-setting':
            prompt_version = f"prompt_setting_{created}"
        else:
            prompt_version = f"prompt_{created}"

        try:
            client = get_mongodb_client()
            db = client[DB_NAME]
            collection = db[COLLECTION_AMA_PROMPTS]

            # Check if prompt already exists
            result = collection.find_one({'prompt_entry': prompt_text})

            if not result:
                # If prompt not in collection, add it
                prompt_entry = {
                    "prompt_version": prompt_version,
                    "prompt_entry": prompt_text
                }
                collection.insert_one(prompt_entry)
            else:
                # If prompt already exists, return the existing version
                prompt_version = result.get('prompt_version')

            client.close()
            return prompt_version

        except Exception as e:
            logger.error(f"Error saving prompt to MongoDB: {str(e)}")
            raise


# Flask application initialization
app = Flask(__name__, static_folder='../static', template_folder='../templates')
app.secret_key = 'dein_geheimer_schluessel'  # In Produktion aus Umgebungsvariablen laden
straico_api_key = os.getenv('STRAICO_API_KEY')


# Middleware zur Initialisierung von session['is_pro']

@app.before_request
def initialize_session():
    if 'is_pro' not in session:
        session['is_pro'] = False  # Standardmäßig sind neue Benutzer Free-Nutzer


# Alle Templates erhalten die Pro-Status-Information
@app.context_processor
def inject_pro_status():
    return {'is_pro': is_pro_user()}


@app.route('/')
def index():
    """
    Render the landing page.

    Returns:
        Rendered landing page template
    """
    return render_template('landing.html')


@app.route('/chat')
def chat():
    """
    Render the main chat page.

    Returns:
        Rendered chat page template
    """
    return render_template('chat.html')


@app.route('/howto')
def howto():
    """
    Render the howto page.

    Returns:
        Rendered howto page template
    """
    return render_template('howto.html')


@app.route('/theolog')
def theolog():
    """
    Render the theologian page.

    Returns:
        Rendered theologian page template
    """
    return render_template('theolog.html')


@app.route('/legal')
def legal():
    """
    Render the legal information page.

    Returns:
        Rendered legal page template
    """
    return render_template('legal.html')


@app.route('/faq')
def faq():
    """
    Render the faq page.

    Returns:
        Rendered faq page template with questions and answers as content
    """
    faqs = get_faq()

    return render_template('faq.html', faqs=faqs)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    # Pro-Schutz: Nur Pro-Nutzer können auf die Einstellungen zugreifen
    if not is_pro_user():
        return redirect(url_for('upgrade'))

    if request.method == 'POST':
        # Daten vom Frontend empfangen
        data = request.get_json()
        prompt_setting = data.get('prompt_setting')
        prompt_setting_json = data.get('prompt_setting_json')

        # Beispiel: Speichern der Daten in einer Datei
        with open('app/prompt_setting.py', 'w', encoding='utf-8') as f:
            f.write(prompt_setting)

        with open('app/prompt_setting.jsonl', 'w', encoding='utf-8') as f:
            json.dump(prompt_setting_json, f, ensure_ascii=False)

        message = jsonify({
            'message': 'Daten erfolgreich gespeichert.',
            'prompt_setting': prompt_setting
        })
        return message
    else:
        # Rendern der HTML-Vorlage
        return render_template('settings.html')


@app.route('/upgrade')
def upgrade():
    """
    Render the upgrade page.

    Returns:
        Rendered upgrade page template
    """
    return render_template('upgrade.html')


@app.route('/toggle_version', methods=['POST'])
def toggle_version():
    # Aktuellen Status bekommen oder False, wenn nicht vorhanden
    current_status = session.get('is_pro', False)
    # Umschalten und speichern
    session['is_pro'] = not current_status
    return redirect(url_for('index'))


@app.route('/ask', methods=['POST'])
def ask():
    """
    Process questions and generate answers.

    Returns:
        JSON response with answer and metadata
    """
    try:
        data = request.get_json()
        question = data.get('frage', '')  # Keep original key for backward compatibility
        agent = data.get('agent', '')

        if not question:
            return jsonify({'answer': 'No question provided.'}), 400
        if not agent:
            return jsonify({'answer': 'No agent selected.'}), 400

        # Map the agent to the appropriate prompt
        if agent == 'seelsorgerlich-sachlich':
            prompt_text = prompt_pastor_factual
        elif agent == 'seelsorgerlich-persönlich':
            prompt_text = prompt_pastor_personal
        elif agent == 'theologisch-sachlich':
            prompt_text = prompt_theologian_factual
        elif agent == 'theologisch-persönlich':
            prompt_text = prompt_theologian_personal
        elif agent == 'predigend-sachlich':
            prompt_text = prompt_preacher_factual
        elif agent == 'predigend-persönlich':
            prompt_text = prompt_preacher_personal
        elif agent == 'individuell-setting':
            # Dynamically load the current value
            prompt_text = get_prompt_setting()
        else:
            return jsonify({'answer': 'Invalid agent selected.'}), 400

        # Generate abstraction
        with straico_client(API_KEY=straico_api_key) as client:
            abstraction = AbstractionService.abstract_question(question, client, prompt_abstraction)

        # Generate reply using the appropriate prompt
        reply = ChatService.generate_reply(abstraction, question, prompt_text)
        answer_markdown = (reply['completion']['choices'][0]['message']['content']
                           + ANSWER_FOOTER)

        # Generate unique ID for logging and feedback
        unique_id = str(uuid.uuid4())

        # Asynchronous processing of tags and logging
        executor.submit(
            process_tags_and_logging,
            answer_markdown,
            question,
            reply,
            prompt_text,
            unique_id,
            abstraction,
            agent
        )

        return jsonify({
            'antwort': answer_markdown,  # Jetzt direkt Markdown zurückgeben
            'antwort_markdown': answer_markdown,  # Für die Abwärtskompatibilität behalten
            'frage': question,  # Keep original key for backward compatibility
            'id': unique_id
        })
    except Exception as e:
        logger.error(f"Error in /ask: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/feedback', methods=['POST'])
def feedback():
    """
    Process user feedback.

    Returns:
        JSON response indicating success or failure
    """
    try:
        feedback_data = request.get_json()
        entry_id = feedback_data.pop('id', None)

        if not entry_id:
            return jsonify({
                'status': 'error',
                'message': 'No valid ID found.'
            }), 400

        # Map German keys to English for backward compatibility
        if 'bewertung' in feedback_data:
            feedback_data['rating'] = feedback_data.pop('bewertung')
        if 'freitext' in feedback_data:
            feedback_data['free_text'] = feedback_data.pop('freitext')

        LoggingService.save_feedback(entry_id, feedback_data)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Error in /feedback: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500


def setup_mongodb_indexes():
    """
    Set up MongoDB indexes at application startup.
    """
    try:
        client = get_mongodb_client()
        db = client[DB_NAME]
        collection = db[COLLECTION_AMA_LOG]
        collection.create_index("id")
        client.close()
    except Exception as e:
        logger.error(f"Error creating MongoDB indexes: {str(e)}")


# Call setup_mongodb_indexes()
setup_mongodb_indexes()

# Wird nicht für Gunicorn-Server benötigt
if __name__ == '__main__':
    setup_mongodb_indexes()
    app.run(host="0.0.0.0", port=5000)