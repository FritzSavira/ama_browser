from flask import Flask, render_template, request
from api_chat_completion import generate_reply, log_to_json
from prompt import prompt
from aio_straico import straico_client
import os


app = Flask(__name__)
STRAICO_API_KEY = os.environ['STRAICO_API_KEY']

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
            log_to_json('ama_log.json', frage, prompt, reply)
    return render_template('index.html', output_log=output_log, antwort=antwort)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
