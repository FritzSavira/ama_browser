/**
 * Wartet, bis das DOM vollständig geladen ist, bevor das Skript ausgeführt wird.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Auswahl der benötigten DOM-Elemente
    const frageForm = document.getElementById('frageForm');
    const chatMessages = document.getElementById('chatMessages');
    const downloadButton = document.getElementById('download_md');

    // Variablen zum Speichern der aktuellen Frage und Antwort in Markdown
    let aktuelleFrage = '';
    let aktuelleAntwortMarkdown = '';

    /**
     * Event Listener für das Absenden der Frage.
     * Sendet die Frage an den Server und verarbeitet die Antwort.
     */
    frageForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const frageInput = document.getElementById('frage').value;

        // Überprüfen, ob die Frage nicht leer ist
        if (frageInput.trim() === '') {
            alert('Bitte gib eine Frage ein.');
            return;
        }

        // Lösche den bisherigen Chat-Verlauf
        chatMessages.innerHTML = '';

        // Zeige die Benutzernachricht an
        displayMessage(frageInput, 'user-message');
        document.getElementById('frage').value = ''; // Eingabefeld leeren

        // Ladeindikator erstellen
        const loadingMessage = displayMessage('Antwort wird generiert...', 'bot-message');

        // Array mit verschiedenen Ladetexten
        const loadingTexts = [
            'Antwort wird generiert...',
            'Ich schlage etwas nach ...',
            'Formulierung vorbereiten ...',
            'Antwort zusammenfassen ...',
            'Nochmal prüfen ...'
        ];

        let currentIndex = 0;
        // Intervall für den Wechsel der Ladetexte
        const loadingInterval = setInterval(() => {
            currentIndex = (currentIndex + 1) % loadingTexts.length;
            loadingMessage.innerHTML = loadingTexts[currentIndex];
        }, 4000);

        // Download-Button während der Anfrage verstecken
        downloadButton.style.display = 'none';

        try {
            // Senden der Frage an den Server
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ frage: frageInput })
            });

            // Ladeintervall stoppen
            clearInterval(loadingInterval);

            if (response.ok) {
                const data = await response.json();

                // Zeige die Antwort an
                loadingMessage.innerHTML = data.antwort;
                aktuelleFrage = data.frage;
                aktuelleAntwortMarkdown = data.antwort_markdown;
                downloadButton.style.display = 'inline-block';

                // Feedback-Aufforderung als separate Bot-Nachricht
                const feedbackPrompt = displayMessage('Bitte bewerte die Antwort, vielen Dank!:', 'bot-message');

                // Feedback-Formular als Benutzernachricht
                const feedbackContainer = displayMessage('', 'user-message');
                const feedbackForm = createFeedbackForm();
                // Entferne die Überschrift aus dem Formular, da sie bereits angezeigt wurde
                feedbackForm.querySelector('h5').remove();
                feedbackContainer.appendChild(feedbackForm);

                // Scrolle zur Antwort
                loadingMessage.scrollIntoView({ behavior: 'smooth' });

                // Event Listener für das Absenden des Feedback-Formulars
                feedbackForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const formData = new FormData(feedbackForm);
                    const feedbackData = {};
                    formData.forEach((value, key) => {
                        feedbackData[key] = value;
                    });
                    feedbackData['frage'] = data.frage; // Frage hinzufügen

                    // Sende das Feedback an das Backend
                    const feedbackResponse = await fetch('/feedback', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(feedbackData)
                    });
                    if (feedbackResponse.ok) {
                        alert('Danke für dein Feedback!');
                        feedbackContainer.remove(); // Formular entfernen
                        feedbackPrompt.remove(); // Aufforderung entfernen
                    } else {
                        alert('Fehler beim Senden des Feedbacks.');
                    }
                });

            } else {
                loadingMessage.textContent = 'Fehler bei der Verarbeitung der Anfrage.';
            }
        } catch (error) {
            // Ladeintervall auch bei Fehler stoppen
            clearInterval(loadingInterval);
            console.error('Error:', error);
            loadingMessage.textContent = 'Ein Fehler ist aufgetreten.';
        }
    });

    /**
     * Zeigt eine Nachricht im Chat-Verlauf an.
     * @param {string} messageContent - Der Inhalt der Nachricht.
     * @param {string} messageClass - Die CSS-Klasse für die Nachricht (z.B. 'user-message' oder 'bot-message').
     * @returns {HTMLElement} Das erstellte Nachrichten-Element.
     */
    function displayMessage(messageContent, messageClass) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-bubble', messageClass);
        messageElement.innerHTML = messageContent;
        chatMessages.appendChild(messageElement);
        // Zum Ende scrollen
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return messageElement;
    }

    /**
     * Erstellt das Feedback-Formular.
     * @returns {HTMLFormElement} Das erstellte Feedback-Formular.
     */
    function createFeedbackForm() {
        const form = document.createElement('form');
        form.id = 'feedbackForm';
        form.classList.add('mt-3');

        // Definieren der Merkmale für das Feedback
        const merkmale = [
            {
                name: 'Inhalt',
                beschreibungen: [
                    '0 - Der Inhalt fehlt oder ist verwirrend.',
                    '1 - Schlecht entworfener Inhalt, relevante Details fehlen.',
                    '2 - Akzeptabler Inhalt, vermittelt die Hauptbotschaft.',
                    '3 - Informative und gut durchdachte Inhalte, gibt Einblicke tieferes Verständnis.',
                    '4 - Sehr ausführlicher und gut recherchierter Inhalt, bietet eine umfassende Analyse.',
                    '5 - Transformative Inhalte, die neue Perspektiven bieten.'
                ]
            },
            {
                name: 'Theologie',
                beschreibungen: [
                    '0 - Kein theologischer Bezug oder falsche theologische Aussagen.',
                    '1 - Schwache theologische Grundlagen, die theologische Tiefe fehlt.',
                    '2 - Basisanwendung theologischer Konzepte.',
                    '3 - Solide theologische Ansätze, berücksichtigt wichtige theologische Lehrmeinungen.',
                    '4 - Gut informierte und präzise Verwendung theologischer Lehre.',
                    '5 - Innovative theologische Gedanken, die das theologische Verständnis erweitern.'
                ]
            },
            {
                name: 'Seelsorge',
                beschreibungen: [
                    '0 - Keine seelsorglichen Aspekte oder unangemessene Empfehlungen.',
                    '1 - Ungefährliche, aber wenig nützliche seelsorgliche Inputs.',
                    '2 - Grundlegende seelsorgerische Begleitung, bietet Gewohnheitslösungen.',
                    '3 - Hilfreiche und ermutigende Seelsorge, bietet praktische Schritte.',
                    '4 - Tiefgreifende und empathische Seelsorge, versteht die individuellen Herausforderungen.',
                    '5 - Transformative Seelsorge, die Heilung und Wachstum fördert.'
                ]
            },
        ];

        // Überschrift des Formulars
        const heading = document.createElement('h5');
        heading.textContent = 'Bitte bewerte die Antwort, vielen Dank!:';
        form.appendChild(heading);

        // Generierung der Bewertungsfelder für jedes Merkmal
        merkmale.forEach((merkmalObj) => {
            const merkmal = merkmalObj.name;
            const beschreibungen = merkmalObj.beschreibungen;

            const fieldset = document.createElement('fieldset');
            fieldset.style.marginTop = '20px';
            const legend = document.createElement('legend');
            legend.style.fontWeight = 'bold';
            legend.textContent = merkmal;
            fieldset.appendChild(legend);

            beschreibungen.forEach((beschreibung, index) => {
                const label = document.createElement('label');
                label.style.display = 'block';
                label.style.marginBottom = '5px';

                const input = document.createElement('input');
                input.type = 'radio';
                input.name = merkmal;
                input.value = index;
                input.required = true;
                label.appendChild(input);

                // Füge die Beschreibung hinzu
                const beschreibungText = document.createTextNode(' ' + beschreibung);
                label.appendChild(beschreibungText);

                fieldset.appendChild(label);
            });

            form.appendChild(fieldset);
        });

        // Freitext-Eingabefeld hinzufügen
        const freitextLabel = document.createElement('label');
        freitextLabel.style.display = 'block';
        freitextLabel.style.marginTop = '20px';
        freitextLabel.style.fontWeight = 'bold';
        freitextLabel.textContent = 'Weitere Anmerkungen:';

        const freitextTextarea = document.createElement('textarea');
        freitextTextarea.name = 'freitext';
        freitextTextarea.rows = 4;
        freitextTextarea.style.width = '100%';
        freitextTextarea.placeholder = 'Optional: Deine Anmerkungen oder Verbesserungsvorschläge';

        freitextLabel.appendChild(freitextTextarea);
        form.appendChild(freitextLabel);

        // Senden-Button für das Feedback-Formular
        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.textContent = 'Feedback senden';
        submitButton.classList.add('btn', 'btn-success', 'mt-3');
        form.appendChild(submitButton);

        return form;
    }

    /**
     * Event Listener für den Download-Button.
     * Ermöglicht das Herunterladen der aktuellen Frage und Antwort als Markdown-Datei.
     */
    downloadButton.addEventListener('click', () => {
        if (!aktuelleFrage || !aktuelleAntwortMarkdown) {
            alert('Keine Daten zum Herunterladen verfügbar.');
            return;
        }

        // Inhalt für die .md-Datei formatieren
        const mdContent = `# Frage\n\n${aktuelleFrage}\n\n# Antwort\n\n${aktuelleAntwortMarkdown}`;

        // Blob-Objekt mit dem Markdown-Inhalt erstellen
        const blob = new Blob([mdContent], { type: 'text/markdown' });

        // Temporären Link zum Herunterladen erstellen
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        // Dateinamen bereinigen und auf 30 Zeichen begrenzen
        const safeFrage = aktuelleFrage.replace(/[^a-z0-9]/gi, '_').toLowerCase().substring(0, 30);
        a.download = `frage_antwort_${safeFrage}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    /**
     * Fügt eine Erfolgsanimation zu einem Element hinzu.
     * @param {HTMLElement} element - Das Element, dem die Animation hinzugefügt wird.
     */
    function addSuccessAnimation(element) {
        element.classList.add('success-animation');
        element.addEventListener('animationend', () => {
            element.classList.remove('success-animation');
        });
    }

    /**
     * Zeigt eine Erfolgsnachricht an.
     * @param {string} message - Die anzuzeigende Nachricht.
     */
    function showSuccessFeedback(message) {
        const feedback = document.createElement('div');
        feedback.classList.add('alert', 'alert-success', 'fade');
        feedback.style.position = 'fixed';
        feedback.style.top = '20px';
        feedback.style.right = '20px';
        feedback.style.zIndex = '1000';
        feedback.textContent = message;
        document.body.appendChild(feedback);

        setTimeout(() => {
            feedback.classList.add('show');
        }, 100);

        setTimeout(() => {
            feedback.classList.remove('show');
            setTimeout(() => {
                feedback.remove();
            }, 300);
        }, 3000);
    }

    // Event-Listener für Feedback-Animation bei allen Buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', () => {
            addSuccessAnimation(btn);
        });
    });
});