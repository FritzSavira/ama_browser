# Verwende ein offizielles Python-Image als Basis
FROM python:3.11-slim

# Setze Umgebungsvariablen
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installiere Abhängigkeiten für Python-Pakete (falls benötigt)
RUN apt-get update && apt-get install -y build-essential

# Erstelle ein Verzeichnis für die Anwendung
WORKDIR /app

# Kopiere die requirements.txt und installiere Abhängigkeiten
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Kopiere den Rest der Anwendung
COPY . .

# Exponiere den Port, auf dem die Anwendung läuft (angenommen 5000)
EXPOSE 5000

# Definiere den Befehl zum Starten der Anwendung
CMD ["python", "main.py"]