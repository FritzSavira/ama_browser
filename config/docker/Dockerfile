# Verwende ein offizielles Python-Image als Basis
FROM python:3.11-slim

# Setze Umgebungsvariablen
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installiere Abhängigkeiten für Python-Pakete und Systempakete
RUN apt-get update && apt-get install -y build-essential curl

# Installiere Node.js (Version 20.x LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Erstelle ein Verzeichnis für die Anwendung
WORKDIR /app

# Kopiere die requirements.txt und installiere Python-Abhängigkeiten
COPY ../config/requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Kopiere die package.json und package-lock.json (falls vorhanden) und installiere JavaScript-Abhängigkeiten
COPY ../../package.json package-lock.json* ./
RUN npm install

# Kopiere den Rest der Anwendung
COPY ../.. .

# Optional: Build-Schritte für das Frontend (falls verwendet)
# RUN npm run build

# Exponiere den Port, auf dem die Anwendung läuft (angenommen 5000)
EXPOSE 5000

# Definiere den Befehl zum Starten der Anwendung
CMD ["python", "app/main.py"]