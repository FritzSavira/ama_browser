from flask import Flask, render_template, request
from prompt import prompt
from aio_straico import straico_client
import os
import json


app = Flask(__name__)
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



@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Verarbeitet die Hauptseite der Anwendung.
    Bei POST-Anfragen wird die eingehende Frage verarbeitet und eine Antwort generiert.
    """
    antwort = ""
    output_log = ""
    if request.method == 'POST':
        frage = request.form.get('frage')
        if frage:
            output_log = f"Die zu beantwortende Frage lautet: {frage}"
            reply = generate_reply(frage)
            antwort = reply['completion']['choices'][0]['message']['content']
            log_to_json('/data/ama_log.json', frage, prompt, reply)
    return render_template('index.html', output_log=output_log, antwort=antwort)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
