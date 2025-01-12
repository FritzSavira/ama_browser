from flask import Flask, render_template, request, jsonify
from prompt import prompt
from aio_straico import straico_client
import os
import json

app = Flask(__name__, static_folder='static', template_folder='templates')
straico_api_key = os.getenv('STRAICO_API_KEY')

def generate_reply(frage):
    """
    Generiert eine Antwort auf die gegebene Frage unter Verwendung des Sprachmodells.

    :param frage: Die gestellte Frage
    :return: Die generierte Antwort als JSON-Objekt
    """
    llm = 'openai/gpt-4o-2024-08-06'
    with straico_client(API_KEY=straico_api_key) as client:
        reply = client.prompt_completion(llm, prompt + frage)
        return reply

def log_to_json(file_path, frage, prompt, reply):
    """
    Speichert die Frage, den Prompt und die Antwort in einer JSON-Datei.

    :param file_path: Pfad zur JSON-Datei
    :param frage: Die gestellte Frage
    :param prompt: Der verwendete Prompt
    :param reply: Die generierte Antwort
    """
    log_entry = {
        "frage": frage,
        "prompt": prompt,
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
        antwort = reply['completion']['choices'][0]['message']['content']
        log_to_json('/data/ama_log.json', frage, prompt, reply)
        return jsonify({'antwort': antwort})
    return jsonify({'antwort': 'Keine Frage gestellt.'}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
