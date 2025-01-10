import io
import re
from flask import Flask, render_template, request, send_file
from api_chat_completion import generate_reply, log_to_json
from prompt import prompt
from aio_straico import straico_client
import os


app = Flask(__name__)
straico_api_key = os.getenv('STRAICO_API_KEY')

def sanitize_filename(name):
    # Erlaubte Zeichen: Buchstaben, Zahlen, Bindestrich und Unterstrich
    return re.sub(r'[^A-Za-z0-9\-_.]', '_', name)

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
    dateiname = sanitize_filename(frage[:20])
    return render_template('index.html', output_log=output_log, antwort=antwort, frage=frage, dateiname=dateiname)


@app.route('/download')
def download():
    frage = request.args.get('frage')
    antwort = request.args.get('antwort')
    dateiname = request.args.get('dateiname')

    if frage and antwort and dateiname:
        # Inhalt der Textdatei erstellen
        content = f"Frage:\n{frage}\n\nAntwort:\n{antwort}"
        # Datei im Speicher erstellen
        file_stream = io.BytesIO()
        file_stream.write(content.encode('utf-8'))
        file_stream.seek(0)
        # Datei an den Benutzer senden
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=f"{dateiname}.txt",
            mimetype='text/plain'
        )
    else:
        return "Fehler: Ungültige Daten."
    app.run(host="0.0.0.0", port=5000)
