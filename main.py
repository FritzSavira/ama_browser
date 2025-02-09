"""
Flask-Anwendung für einen Frage-Antwort-Chat mit KI-Unterstützung.
Gehostet auf Fly.io in einem Docker-Container.
"""

from flask import Flask, render_template, request, jsonify
from prompt import prompt_antwort, prompt_tags
from aio_straico import straico_client
import os
import json
import markdown
import bleach
from typing import Dict, List, Union
import logging


# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Konstanten
DATA_DIR = '/data'
LOG_FILE = os.path.join(DATA_DIR, 'ama_log.json')
ANTWORT_FOOTER = ("\n\n *Dies ist eine mögliche Antwort."
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
TAGS_LLM = 'openai/gpt-4o-min'

app = Flask(__name__, static_folder='static', template_folder='templates')
straico_api_key = os.getenv('STRAICO_API_KEY')


class ChatService:
    @staticmethod
    def generate_reply(frage: str) -> Dict:
        """Generiert eine KI-Antwort auf die gegebene Frage."""
        try:
            with straico_client(API_KEY=straico_api_key) as client:
                reply = client.prompt_completion(ANTWORT_LLM, prompt_antwort + frage)
                return reply
        except Exception as e:
            logger.error(f"Fehler bei der Antwortgenerierung: {str(e)}")
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
    def save_log(frage: str, prompt_text: str, reply: Dict, tags: Dict) -> None:
        """Speichert Chat-Interaktionen in der Log-Datei."""
        try:
            log_entry = {
                "frage": frage,
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
    def save_feedback(frage: str, feedback: Dict) -> None:
        """Speichert Benutzer-Feedback zu einer Antwort."""
        try:
            log_data = LoggingService.read_log_file()

            for entry in reversed(log_data):
                if entry['frage'] == frage and 'feedback' not in entry:
                    entry['feedback'] = feedback
                    break

            with open(LOG_FILE, 'w', encoding='utf-8') as file:
                json.dump(log_data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Feedbacks: {str(e)}")
            raise


@app.route('/')
def index():
    """Rendert die Hauptseite."""
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    """Verarbeitet Fragen und generiert Antworten."""
    try:
        data = request.get_json()
        frage = data.get('frage', '')

        if not frage:
            return jsonify({'antwort': 'Keine Frage gestellt.'}), 400

        reply = ChatService.generate_reply(frage)
        antwort_markdown = (reply['completion']['choices'][0]['message']['content']
                            + ANTWORT_FOOTER)
        antwort_html = ChatService.convert_markdown_to_html(antwort_markdown)

        reply_tags = ChatService.generate_tags(antwort_markdown)
        tags = (reply_tags['completion']['choices'][0]['message']['content'])

        LoggingService.save_log(frage, prompt_antwort, reply, tags)

        return jsonify({
            'antwort': antwort_html,
            'antwort_markdown': antwort_markdown,
            'frage': frage




        })
    except Exception as e:
        logger.error(f"Fehler in /ask: {str(e)}")
        return jsonify({'error': 'Interner Server-Fehler'}), 500


@app.route('/feedback', methods=['POST'])
def feedback():
    """Verarbeitet Benutzer-Feedback."""
    try:
        data = request.get_json()
        frage = data.pop('frage', None)

        if not frage:
            return jsonify({
                'status': 'error',
                'message': 'Keine gültige Frage gefunden.'
            }), 400

        LoggingService.save_feedback(frage, data)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Fehler in /feedback: {str(e)}")
        return jsonify({'error': 'Interner Server-Fehler'}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)