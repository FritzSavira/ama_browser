import json
from prompt import prompt
from aio_straico import straico_client
import os

straico_api_key = os.getenv('STRAICO_API_KEY')

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

def main():
    """
    Hauptfunktion, die die Frage aus einer Datei liest, die Antwort generiert und die Ergebnisse protokolliert.
    """
#    frage = read_frage_from_file('frage.txt')
#    reply = generate_reply(frage)
#    log_to_json('ama_log.json', frage, prompt, reply)
#    antwort = reply['completion']['choices'][0]['message']['content']
#    print(antwort)

if __name__ == "__main__":
    main()
