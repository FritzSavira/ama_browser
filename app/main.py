import uuid  # Import uuid to generate unique IDs
from concurrent.futures import ThreadPoolExecutor
import asyncio
from flask import Flask, render_template, request, jsonify
from prompt import prompt_pastor, prompt_theologe, prompt_prediger, prompt_tags
from aio_straico import straico_client
import os
import json
import markdown
import bleach
from typing import Dict, List
import logging
import re

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
                           prompt_text: str, unique_id: str):
    """Verarbeitet Tags, Abstraktion und Logging asynchron nach der Hauptantwort."""
    try:
        # Generate tags
        reply_tags = ChatService.generate_tags(antwort_markdown)
        tags = reply_tags['completion']['choices'][0]['message']['content']
        tags = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', tags).group()

        # Generate abstraction
        with straico_client(API_KEY=straico_api_key) as client:
            abstraction = AbstractionService.abstract_question(frage, client)

        # Save log with abstraction
        LoggingService.save_log(frage, prompt_text, reply, tags,
                              abstraction, unique_id)

        logger.info(f"Tags, abstraction and logging processed for question: {frage[:50]}...")
    except Exception as e:
        logger.error(f"Error in processing: {str(e)}")


class AbstractionService:
    @staticmethod
    def abstract_question(question: str, llm_client) -> Dict:
        """Erstellt eine datenschutzkonforme Abstraktion der Benutzeranfrage."""
        abstraction_prompt = """
        Analysiere die folgende Frage und erstelle eine strukturierte Abstraktion in folgendem JSON-Format:
        {
            "categorization": {
                "category": "",
                "subcategory": "",
                "type": "",
                "complexity": 0
            },
            "tagging": {
                "tags": [],
                "relation": "",
                "abstraction_level": ""
            },
            "intent": {
                "main_goal": "",
                "context": "",
                "expected_output": ""
            },
            "semantic": {
                "generic_query": "",
                "domain": "",
                "information_goal": ""
            }
        }

        Frage: """

        try:
            reply = llm_client.prompt_completion(
                TAGS_LLM,
                abstraction_prompt + question
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
    def generate_reply(frage: str, prompt_text: str) -> Dict:
        """Generates an AI answer to the given question using the specified prompt."""
        try:
            with straico_client(API_KEY=straico_api_key) as client:
                reply = client.prompt_completion(ANTWORT_LLM, prompt_text + frage)
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


class LoggingService:
    @staticmethod
    def save_log(frage: str, prompt_text: str, reply: Dict, tags: str,
                 abstraction: Dict, entry_id: str) -> None:
        """Speichert Chat-Interaktionen mit Abstraktion in der Log-Datei."""
        tags = json.loads(tags)
        try:
            log_entry = {
                "id": entry_id,
                "frage_abstraktion": abstraction,  # Neue abstrahierte Version
                "prompt": prompt_text,
                "reply": reply,
                "tags": tags
            }

            data = LoggingService.read_log_file()
            data.append(log_entry)

            with open(LOG_FILE, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Logs: {str(e)}")
            raise

    @staticmethod
    def read_log_file() -> List:
        """Liest die Log-Datei oder erstellt eine neue."""
        try:
            if not os.path.exists(LOG_FILE):
                return []
            with open(LOG_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Fehler beim Lesen des Logs: {str(e)}")
            return []

    @staticmethod
    def save_feedback(entry_id: str, feedback: Dict) -> None:
        """Speichert Benutzer-Feedback zu einer Antwort."""
        try:
            log_data = LoggingService.read_log_file()

            for entry in reversed(log_data):
                if entry.get('id') == entry_id and 'feedback' not in entry:
                    entry['feedback'] = feedback
                    break
            else:
                logger.error(f"No matching entry found for ID: {entry_id}")

            with open(LOG_FILE, 'w', encoding='utf-8') as file:
                json.dump(log_data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Feedbacks: {str(e)}")
            raise


@app.route('/')
def index():
    """Rendert die Landing Page."""
    return render_template('landing.html')

@app.route('/chat')
def chat():
    """Rendert die Hauptseite."""
    return render_template('chat.html')

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

        # Generate reply using the appropriate prompt
        reply = ChatService.generate_reply(frage, prompt_text)
        antwort_markdown = (reply['completion']['choices'][0]['message']['content']
                            + ANTWORT_FOOTER)
        antwort_html = ChatService.convert_markdown_to_html(antwort_markdown)

        # Generate unique ID for logging and feedback
        unique_id = str(uuid.uuid4())

        # Asynchronous processing of tags and logging
        executor.submit(process_tags_and_logging, antwort_markdown, frage, reply, prompt_text, unique_id)

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
        data = request.get_json()
        entry_id = data.pop('id', None)

        if not entry_id:
            return jsonify({
                'status': 'error',
                'message': 'Keine gültige ID gefunden.'
            }), 400

        LoggingService.save_feedback(entry_id, data)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Fehler in /feedback: {str(e)}")
        return jsonify({'error': 'Interner Server-Fehler'}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

