#Verwende ein offizielles Python-Image als Basis

FROM python:3.11-slim

#Setze Umgebungsvariablen

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

#Installiere die notwendigen Systempakete

RUN apt-get update && apt-get install -y
build-essential
curl
ca-certificates
gnupg
lsb-release
&& rm -rf /var/lib/apt/lists/*

#Führe das NodeSource-Installationsskript aus und installiere Node.js 18.x

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
&& apt-get install -y nodejs
&& npm install -g npm@latest

#Erstelle ein Verzeichnis für die Anwendung

WORKDIR /app

#Kopiere die requirements.txt und installiere Abhängigkeiten

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#Kopiere den Rest der Anwendung

COPY . .

#Exponiere den Port, auf dem die Anwendung läuft (angenommen 5000)

EXPOSE 5000

#Definiere den Befehl zum Starten der Anwendung
CMD ["python", "main.py"]