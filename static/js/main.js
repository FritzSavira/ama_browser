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
    let aktuelleID = ''; // Variable zum Speichern der ID

    /**
     * Event Listener für das Absenden der Frage.
     * Sendet die Frage an den Server und verarbeitet die Antwort.
     */
    frageForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Erfassen der Frage
        const frageInput = document.getElementById('frage').value;

        // Erfassen des ausgewählten Agenten
        const agentInput = document.querySelector('input[name="agent"]:checked');

        // Überprüfen, ob eine Frage eingegeben wurde
        if (frageInput.trim() === '') {
            alert('Bitte gib eine Frage ein.');
            return;
        }

        // Überprüfen, ob ein Agent ausgewählt wurde
        if (!agentInput) {
            alert('Bitte wählen Sie einen Agenten aus.');
            return;
        }

        const agentValue = agentInput.value;

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
                body: JSON.stringify({ frage: frageInput, agent: agentValue })
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
                aktuelleID = data.id; // Zeile zum Speichern der ID

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
                    feedbackData['id'] = aktuelleID; // ID dem Feedback hinzufügen

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

        // Heading of the form
        const heading = document.createElement('h5');
        heading.textContent = 'Wie fandest du die Antwort?';
        form.appendChild(heading);

        // Container for feedback options
        const feedbackOptions = document.createElement('div');
        feedbackOptions.classList.add('feedback-options');

        // Positive feedback option (thumbs up)
        const positiveLabel = document.createElement('label');
        positiveLabel.classList.add('feedback-positive');
        positiveLabel.style.cursor = 'pointer';

        const positiveInput = document.createElement('input');
        positiveInput.type = 'radio';
        positiveInput.name = 'bewertung';
        positiveInput.value = 'positiv';
        positiveInput.style.display = 'none';
        positiveInput.required = true;
        positiveLabel.appendChild(positiveInput);

        const positiveIcon = document.createElement('i');
        positiveIcon.classList.add('fas', 'fa-thumbs-up');
        positiveLabel.appendChild(positiveIcon);

        feedbackOptions.appendChild(positiveLabel);

        // Negative feedback option (thumbs down)
        const negativeLabel = document.createElement('label');
        negativeLabel.classList.add('feedback-negative');
        negativeLabel.style.cursor = 'pointer';

        const negativeInput = document.createElement('input');
        negativeInput.type = 'radio';
        negativeInput.name = 'bewertung';
        negativeInput.value = 'negativ';
        negativeInput.style.display = 'none';
        negativeInput.required = true;
        negativeLabel.appendChild(negativeInput);

        const negativeIcon = document.createElement('i');
        negativeIcon.classList.add('fas', 'fa-thumbs-down');
        negativeLabel.appendChild(negativeIcon);

        feedbackOptions.appendChild(negativeLabel);

        form.appendChild(feedbackOptions);

        // Label for the free-text field
        const freitextLabel = document.createElement('label');
        freitextLabel.style.display = 'block';
        freitextLabel.style.marginTop = '20px';
        freitextLabel.style.fontWeight = 'bold';
        freitextLabel.textContent = 'Weitere Anmerkungen:';
        form.appendChild(freitextLabel);

        // Create an input group for the textarea and button
        const inputGroup = document.createElement('div');
        inputGroup.classList.add('input-group');

        // Create the textarea
        const freitextTextarea = document.createElement('textarea');
        freitextTextarea.name = 'freitext';
        freitextTextarea.rows = 4;
        freitextTextarea.classList.add('form-control');
        freitextTextarea.style.resize = 'vertical';
        freitextTextarea.placeholder = 'Optional: Deine Anmerkungen oder Verbesserungsvorschläge';

        // Append the textarea to the input group
        inputGroup.appendChild(freitextTextarea);

        // Create the input group append for the button
        const inputGroupAppend = document.createElement('div');
        inputGroupAppend.classList.add('input-group-append');

        // Create the submit button with the paper plane icon
        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.classList.add('btn', 'btn-success');
        const sendIcon = document.createElement('i');
        sendIcon.classList.add('fas', 'fa-paper-plane');
        submitButton.appendChild(sendIcon);

        // Append the button to the input group append
        inputGroupAppend.appendChild(submitButton);

        // Append the input group append to the input group
        inputGroup.appendChild(inputGroupAppend);

        // Append the input group to the form
        form.appendChild(inputGroup);

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