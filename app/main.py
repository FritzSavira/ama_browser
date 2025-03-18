# Standard library imports
import json
import logging
import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

# Third-party imports
import bleach
import certifi
import markdown
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

# Local imports
from aio_straico import straico_client
from .prompt import (
    prompt_pastor, prompt_theologian, prompt_preacher,
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
ANSWER_FOOTER = ("\n\n *Diese Antwort wurde mit KI erstellt und kann fehlerhaft sein." 
                 " Die Verantwortung, wie du diese Antwort nutzt, liegt bei dir.*")

# MongoDB configuration
MONGODB_URI = os.environ.get('MONGODB_URI')
DB_NAME = 'ama_browser'
COLLECTION_AMA_LOG = 'ama_log'
COLLECTION_AMA_PROMPTS = 'ama_prompts'

# HTML sanitizer configuration
ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS).union({
    'p', 'pre', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br'
})
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id', 'style'],
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title'],
}

# LLM configuration
ANSWER_LLM = 'openai/gpt-4o-2024-11-20'
# ANSWER_LLM = 'anthropic/claude-3.7-sonnet:thinking'
TAGS_LLM = 'anthropic/claude-3.5-sonnet'


# Global thread pool for asynchronous operations
executor = ThreadPoolExecutor(max_workers=3)


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

    @staticmethod
    def convert_markdown_to_html(markdown_text: str) -> str:
        """
        Convert Markdown text to safe HTML.

        Args:
            markdown_text: The Markdown text to convert

        Returns:
            str: The sanitized HTML

        Raises:
            Exception: If an error occurs during conversion
        """
        try:
            html = markdown.markdown(
                markdown_text,
                extensions=['fenced_code', 'codehilite']
            )
            return bleach.clean(
                html,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRIBUTES
            )
        except Exception as e:
            logger.error(f"Error during markdown conversion: {str(e)}")
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
        if agent == 'pastoral-seelsorgerlich':
            prompt_version = f"prompt_pastor_{created}"
        elif agent == 'theologisch-wissenschaftlich':
            prompt_version = f"prompt_theologian_{created}"
        elif agent == 'predigend-erzählend':
            prompt_version = f"prompt_preacher_{created}"
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
straico_api_key = os.getenv('STRAICO_API_KEY')


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
    faqs = [
        {
            'question': 'Welche theologische Ausrichtung hat ShepWise?',
            'answer': 'ShepWise basiert auf einer biblisch fundierten Theologie.'
                      ' Die Antworten orientieren sich an der Autorität der Heiligen Schrift (sola scriptura)'
                      ' und stehen in der Tradition reformatorischer Theologie.'
                      ' Die denominative Tendenz der Antworten kann durch die Justierung der Persona'
                      ' des Systemprompts eingestellt werden (Pro-Version).'
                      ' In der voreingestellten Version antwortet Shepwise mit evangelikalen Tendenzen.'
        },
        {
            'question': 'Wie stellt ShepWise sicher, dass die Antworten theologisch fundiert sind?',
            'answer': 'Die App greift auf ein breites Spektrum theologischer Ressourcen zurück, darunter systematische Theologie, Hermeneutik, Bibelauslegung, Kirchengeschichte, Apologetik und klassische christliche Schriften. Jede Antwort wird auf Grundlage dieser Quellen generiert.'
        },
        {
            'question': 'Ersetzt ShepWise das eigene Bibelstudium?',
            'answer': 'Nein. Wie in den Nutzungshinweisen betont, ersetzt ShepWise nicht das persönliche Gebet, Bibelstudium und geistliche Wachstum. Die App dient als Formulierungshilfe und theologische Unterstützung, nicht als Ersatz für die eigene theologische Reflexion.'
        },
        {
            'question': 'Für welche pastoralen Situationen ist ShepWise besonders hilfreich?',
            'answer': 'ShepWise unterstützt Sie besonders bei: - Vorbereitung von Predigten und Bibelarbeiten - Formulierung seelsorgerlicher Antworten in komplexen Situationen - Theologischer Reflexion aktueller gesellschaftlicher Fragen - Schneller Orientierung bei unerwarteten seelsorgerlichen Anfragen - Unterstützung für junge Pastoren oder ehrenamtliche Mitarbeiter'
        },
        {
            'question': 'Wie formuliere ich meine Fragen, um optimale Antworten zu bekommen?',
            'answer': 'Formulieren Sie Ihre Fragen so konkret wie möglich. Nennen Sie den Kontext, in dem Sie die Antwort verwenden möchten, und geben Sie relevante Details an, ohne persönliche Informationen Dritter preiszugeben.'
        },
        {
            'question': 'Wie unterscheiden sich die drei Antwortformate?',
            'answer': '- Pastoral-seelsorgerlich**: Empathisch, begleitend, auf zwischenmenschliche Beziehungen ausgerichtet - **Theologisch-wissenschaftlich**: Exegetisch fundiert, mit Bibelstellen, kirchengeschichtlichen Bezügen und lehrmäßiger Tiefe - **Predigend-erzählend**: Anschaulich, mit Metaphern, Beispielen und einer klaren Botschaft für die Verkündigung '
        },
        {
            'question': 'Werden meine Fragen gespeichert?',
            'answer': 'Nein, ShepWise speichert keine personenbezogenen Daten. Die App arbeitet ohne Konto, ohne Cookies und ohne dauerhafte Speicherung der von Ihnen formulierten Fragen.'
        },
        {
            'question': 'Kann ich ShepWise für vertrauliche seelsorgerliche Anliegen nutzen?',
            'answer': 'Ja, allerdings sollten Sie keine identifizierenden Details zu Ihren Gemeindemitgliedern eingeben. Formulieren Sie Anfragen zu seelsorgerlichen Situationen immer anonymisiert.'
        },
        {
            'question': 'Welche Arten von Fragen sollte ich nicht stellen?',
            'answer': 'Vermeiden Sie: - Fragen mit personenbezogenen Daten Dritter - Fragen zu medizinischen, rechtlichen oder finanziellen Fachthemen - Anfragen für fertige Predigten, die Sie unverändert übernehmen wollen'
        },
        {
            'question': 'Kann ShepWise bei akuten Krisen oder psychischen Notfällen helfen?',
            'answer': 'ShepWise ersetzt keine professionelle Krisenintervention oder psychologische Beratung. Bei akuten Krisen sollten immer entsprechende Fachstellen hinzugezogen werden.'
        },
        {
            'question': 'Wie aktuell sind die Antworten zu gesellschaftlichen Themen?',
            'answer': 'ShepWise kann zu grundlegenden theologischen Aspekten aktueller Themen Position beziehen, ist jedoch nicht für tagesaktuelle Ereignisse oder spezifische politische Situationen optimiert.'
        },
        {
            'question': 'Was kostet die Nutzung von ShepWise?',
            'answer': 'Sie können ShepWise zunächst kostenfrei testen. Für detaillierte Preisinformationen nach der Testphase kontaktieren Sie uns bitte direkt. E-Mail: info@shepwise.com'
        },
        {
            'question': 'Gibt es Einschränkungen während der kostenlosen Testphase?',
            'answer': 'In der Testphase können Sie alle Funktionen ohne Einschränkung nutzen, um die Eignung für Ihren Dienst zu prüfen.'
        },
        {
            'question': 'Kann ich ShepWise auch auf mobilen Geräten nutzen?',
            'answer': 'Ja, ShepWise ist für alle Geräte mit Internetzugang geeignet – vom Desktop-Computer bis zum Smartphone.'
        },
        {
            'question': 'Wie kann ich Feedback geben?',
            'answer': 'Wir freuen uns über Ihr Feedback zur Verbesserung von ShepWise. Nutzen Sie dafür unsere E-Mail: info@shepwise.com.'
        },
    ]
    return render_template('faq.html', faqs=faqs)


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
        if agent == 'pastoral-seelsorgerlich':
            prompt_text = prompt_pastor
        elif agent == 'theologisch-wissenschaftlich':
            prompt_text = prompt_theologian
        elif agent == 'predigend-erzählend':
            prompt_text = prompt_preacher
        else:
            return jsonify({'answer': 'Invalid agent selected.'}), 400

        # Generate abstraction
        with straico_client(API_KEY=straico_api_key) as client:
            abstraction = AbstractionService.abstract_question(question, client, prompt_abstraction)

        # Generate reply using the appropriate prompt
        reply = ChatService.generate_reply(abstraction, question, prompt_text)
        answer_markdown = (reply['completion']['choices'][0]['message']['content']
                           + ANSWER_FOOTER)
        answer_html = ChatService.convert_markdown_to_html(answer_markdown)

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
            'antwort': answer_html,  # Keep original key for backward compatibility
            'antwort_markdown': answer_markdown,  # Keep original key for backward compatibility
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
# if __name__ == '__main__':
#    setup_mongodb_indexes()
#    app.run(host="0.0.0.0", port=5000)
