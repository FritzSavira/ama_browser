from flask import Flask, render_template, request, jsonify
from prompt import prompt
from aio_straico import straico_client
import os
import json
import markdown
import bleach



app = Flask(__name__, static_folder='static', template_folder='templates')
straico_api_key = os.getenv('STRAICO_API_KEY')

# Definiere erlaubte HTML-Tags und Attribute für die Sanitierung
ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS.union({
    'p', 'pre', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br'
})
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id', 'style'],
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title'],
}

ANTWORT_FOOTER = ("\n\n *Dies ist eine mögliche Antwort."
                  " Die Verantwortung, wie du diese Antwort nutzt, liegt bei dir.*")

def generate_reply(frage):
    """
    Generiert eine Antwort auf die gegebene Frage unter Verwendung des Sprachmodells.

    :param frage: Die gestellte Frage
    :return: Die generierte Antwort als JSON-Objekt
    """
    # llm = 'openai/gpt-4o-2024-08-06' Ohne Fehler, manchmal ein wenig geschwätzig, am Thema vorbei. 3 Coins
    # llm = 'openai/gpt-4o-2024-11-20' Robust, sehr gut geeignet. 3,3 Coins
    # llm = 'openai/o3-mini' Ausreichende Präzision für einfache bis mittlere Komplexität. 1,5 Coins
    # llm = 'openai/o1-preview'
    # llm = 'amazon/nova-pro-v1' #Einfaches, preiswertes Model mit einfacher Ausdrucksweise für einfache Fragen. 1 Coin
    # llm = 'anthropic/claude-3-opus' Exzellente Antworten, extrem teuer. 24 Coins
    # llm = 'anthropic/claude-3.5-sonnet' Gut, klare Antworten. Störend: Regieanweisungen wie 'Pastor lächelt'. 4,8 Coins
    llm = 'cohere/command-r-08-2024'
    with straico_client(API_KEY=straico_api_key) as client:
        reply = client.prompt_completion(llm, prompt + frage)
        return reply

def convert_markdown_to_html(markdown_text):
    """
    Konvertiert Markdown in HTML und sanitisiert das Ergebnis.

    :param markdown_text: Markdown-Text
    :return: Sicheres HTML
    """
    # Konvertiere Markdown zu HTML
    html = markdown.markdown(markdown_text, extensions=['fenced_code', 'codehilite'])
    # Sanitisiere das HTML
    clean_html = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    return clean_html

def log_to_json(file_path, frage, prompt_text, reply):
    """
    Speichert die Frage, den Prompt und die Antwort in einer JSON-Datei.

    :param file_path: Pfad zur JSON-Datei
    :param frage: Die gestellte Frage
    :param prompt_text: Der verwendete Prompt
    :param reply: Die generierte Antwort
    """
    log_entry = {
        "frage": frage,
        "prompt": prompt_text,
        "reply": reply
    }
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    data.append(log_entry)

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

@app.route('/', methods=['GET'])
def index():
    """
    Render die Hauptseite der Anwendung.
    """
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    """
    Verarbeitung der AJAX-Anfrage zur Beantwortung einer Frage.
    """
    data = request.get_json()
    frage = data.get('frage', '')
    if frage:
        reply = generate_reply(frage)
        # Extrahiere die Markdown-Antwort
        antwort_markdown = reply['completion']['choices'][0]['message']['content'] + ANTWORT_FOOTER
        # Konvertiere zu HTML
        antwort_html = convert_markdown_to_html(antwort_markdown)
        # Logge die Daten
        log_to_json('/data/ama_log.json', frage, prompt, reply)
        return jsonify({'antwort': antwort_html, 'antwort_markdown': antwort_markdown, 'frage': frage})
    return jsonify({'antwort': 'Keine Frage gestellt.'}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)