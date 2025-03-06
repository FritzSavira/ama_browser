from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request, jsonify
from prompt import prompt_pastor, prompt_theologe, prompt_prediger, prompt_tags, prompt_abstraction
from aio_straico import straico_client
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError, OperationFailure
from typing import Dict, List
import uuid  # Import uuid to generate unique IDs
import os
import re
import json
import markdown
import bleach
import logging
import certifi
import ssl

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Konstanten
DATA_DIR = '/data'
LOG_FILE = os.path.join(DATA_DIR, 'ama_log.json')
ANTWORT_FOOTER = ("\n\n *Diese Antwort wurde mit KI erstellt und kann fehlerhaft sein."
                  " Die Verantwortung, wie du diese Antwort nutzt, liegt bei dir.*")

# MongoDB Konfiguration
MONGODB_URI = os.environ.get('MONGODB_URI')
DB_NAME = 'ama_browser'
COLLECTION_AMA_LOG = 'ama_log'
COLLECTION_AMA_PROMPT = 'ama_prompts'

# MongoDB Client Initialisierung
def get_mongodb_client():
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


# HTML-Sanitizer-Konfiguration
ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS.union({
    'p', 'pre', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br'
})
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id', 'style'],
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title'],
}

# LLM-Konfiguration
ANTWORT_LLM = 'openai/gpt-4o-2024-11-20'
TAGS_LLM = 'anthropic/claude-3.5-sonnet'

app = Flask(__name__, static_folder='../static', template_folder='../templates')
straico_api_key = os.getenv('STRAICO_API_KEY')

# Globaler Thread-Pool für asynchrone Operationen
executor = ThreadPoolExecutor(max_workers=3)


def process_tags_and_logging(antwort_markdown: str, frage: str, reply: Dict,
                           prompt_text: str, unique_id: str, abstraction):
    """Verarbeitet Tags, Abstraktion und Logging asynchron nach der Hauptantwort."""
    try:
        # Generate tags
        reply_tags = ChatService.generate_tags(antwort_markdown)
        tags = reply_tags['completion']['choices'][0]['message']['content']
        tags = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', tags).group()

        # Generate abstraction
        # with straico_client(API_KEY=straico_api_key) as client:
        #    abstraction = AbstractionService.abstract_question(frage, client)

        # Save log with abstraction
        LoggingService.save_log(prompt_text, reply, tags,
                              abstraction, unique_id)

        logger.info(f"Tags, abstraction and logging processed for question: {frage[:50]}...")
    except Exception as e:
        logger.error(f"Error in processing: {str(e)}")


class AbstractionService:
    @staticmethod
    def abstract_question(question: str, llm_client, prompt_abstraction: str) -> Dict:
        """Erstellt eine datenschutzkonforme Abstraktion der Benutzeranfrage."""
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
            logger.error(f"Fehler bei der Abstraktion: {str(e)}")
            return {}



class ChatService:
    @staticmethod
    def generate_reply(abstraction, frage: str, prompt_text: str) -> Dict:
        """Generates an AI answer to the given question using the specified prompt."""
        try:
            with straico_client(API_KEY=straico_api_key) as client:
                abstraction_str = str(abstraction)
                reply = client.prompt_completion(ANTWORT_LLM, prompt_text + abstraction_str + frage)
                return reply
        except Exception as e:
            logger.error(f"Error generating reply: {str(e)}")
            raise

    @staticmethod
    def generate_tags(antwort_markdown: str) -> Dict:
        """Generiert Tags zur gegebenen KI-Antwort """
        try:
            with straico_client(API_KEY=straico_api_key) as client:
                reply = client.prompt_completion(TAGS_LLM, prompt_tags + antwort_markdown)
                return reply
        except Exception as e:
            logger.error(f"Fehler beim Tagging: {str(e)}")
            raise

    @staticmethod
    def convert_markdown_to_html(markdown_text: str) -> str:
        """Konvertiert Markdown zu sicherem HTML."""
        try:
            html = markdown.markdown(markdown_text, extensions=['fenced_code', 'codehilite'])
            return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        except Exception as e:
            logger.error(f"Fehler bei der Markdown-Konvertierung: {str(e)}")
            raise


# Modifizierte LoggingService Klasse
class LoggingService:
    @staticmethod
    def save_log(prompt_text: str, reply: Dict, tags: str,
                 abstraction: Dict, entry_id: str) -> None:
        """Speichert Chat-Interaktionen in MongoDB."""
        tags = json.loads(tags)
        try:
            client = get_mongodb_client()
            db = client[DB_NAME]
            collection = db[COLLECTION_AMA_LOG]

            log_entry = {
                "id": entry_id,
                "frage_abstraktion": abstraction,
                "prompt": prompt_text,
                "reply": reply,
                "tags": tags
            }

            collection.insert_one(log_entry)
            client.close()

        except Exception as e:
            logger.error(f"Fehler beim Speichern in MongoDB: {str(e)}")
            raise

    @staticmethod
    def save_feedback(entry_id: str, feedback_data: Dict) -> None:
        """Speichert Benutzer-Feedback in MongoDB."""
        try:
            client = get_mongodb_client()
            db = client[DB_NAME]
            collection = db[COLLECTION_AMA_LOG]

            # Bereite die Felder vor, die aktualisiert werden sollen
            update_fields = {}
            for key, value in feedback_data.items():
                if key in ['bewertung', 'freitext']:
                    update_fields[f"feedback.{key}"] = value

            if not update_fields:
                logger.error(f"Keine gültigen Feedback-Daten für ID: {entry_id} bereitgestellt.")
                return

            # Aktualisiere das bestehende Dokument mit den Feedback-Feldern
            result = collection.update_one(
                {"id": entry_id},
                {"$set": update_fields}
            )

            if result.modified_count == 0:
                logger.error(f"Kein passender Eintrag für ID: {entry_id} gefunden.")

            client.close()

        except Exception as e:
            logger.error(f"Fehler beim Speichern des Feedbacks: {str(e)}")
            raise

    def save_prompt(self):


@app.route('/')
def index():
    """Rendert die Landing Page."""
    return render_template('landing.html')

@app.route('/chat')
def chat():
    """Rendert die Hauptseite."""
    return render_template('chat.html')

@app.route('/theolog')
def theolog():
    return render_template('theolog.html')


@app.route('/legal')
def legal():
    return render_template('legal.html')


@app.route('/ask', methods=['POST'])
def ask():
    """Processes questions and generates answers."""
    try:
        data = request.get_json()
        frage = data.get('frage', '')
        agent = data.get('agent', '')

        if not frage:
            return jsonify({'antwort': 'Keine Frage gestellt.'}), 400
        if not agent:
            return jsonify({'antwort': 'Kein Agent ausgewählt.'}), 400

        # Map the agent to the appropriate prompt
        if agent == 'pastoral-seelsorgerlich':
            prompt_text = prompt_pastor
        elif agent == 'theologisch-wissenschaftlich':
            prompt_text = prompt_theologe
        elif agent == 'predigend-erzählend':
            prompt_text = prompt_prediger
        else:
            return jsonify({'antwort': 'Ungültiger Agent ausgewählt.'}), 400

        # Generate abstraction
        with straico_client(API_KEY=straico_api_key) as client:
            abstraction = AbstractionService.abstract_question(frage, client, prompt_abstraction)

        # Generate reply using the appropriate prompt
        reply = ChatService.generate_reply(abstraction, frage, prompt_text)
        antwort_markdown = (reply['completion']['choices'][0]['message']['content']
                            + ANTWORT_FOOTER)
        antwort_html = ChatService.convert_markdown_to_html(antwort_markdown)

        # Generate unique ID for logging and feedback
        unique_id = str(uuid.uuid4())

        # Asynchronous processing of tags and logging
        executor.submit(process_tags_and_logging, antwort_markdown, frage, reply, prompt_text, unique_id, abstraction)

        return jsonify({
            'antwort': antwort_html,
            'antwort_markdown': antwort_markdown,
            'frage': frage,
            'id': unique_id  # Include the unique id in response
        })
    except Exception as e:
        logger.error(f"Error in /ask: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/feedback', methods=['POST'])
def feedback():
    """Verarbeitet Benutzer-Feedback."""
    try:
        feedback_data = request.get_json()
        entry_id = feedback_data.pop('id', None)

        if not entry_id:
            return jsonify({
                'status': 'error',
                'message': 'Keine gültige ID gefunden.'
            }), 400

        LoggingService.save_feedback(entry_id, feedback_data)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Fehler in /feedback: {str(e)}")
        return jsonify({'error': 'Interner Server-Fehler'}), 500

# Beim App-Start ausführen
def setup_mongodb_indexes():
    try:
        client = get_mongodb_client()
        db = client[DB_NAME]
        collection = db[COLLECTION_AMA_LOG]
        collection.create_index("id")
        client.close()
    except Exception as e:
        logger.error(f"Error creating MongoDB indexes: {str(e)}")

if __name__ == '__main__':
    setup_mongodb_indexes()
    app.run(host="0.0.0.0", port=5000)

