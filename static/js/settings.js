document.addEventListener('DOMContentLoaded', function() {
    const startButton = document.getElementById('start-button');
    const mainContent = document.getElementById('main-content');
    const generatePromptButton = document.getElementById('generate-prompt-button');
    const resultsDiv = document.getElementById('results');
    const systemPromptTextarea = document.getElementById('system-prompt');
    const systemPromptJsonTextarea = document.getElementById('system-prompt-json');

    startButton.addEventListener('click', function() {
        startButton.style.display = 'none';
        mainContent.style.display = 'block';
    });

    generatePromptButton.addEventListener('click', function() {
        // Sammlung der Facettenwerte
        let facets = {};

        // Beispiel: Offenheit für Erfahrungen
        facets['Ist originell, entwickelt neue Ideen'] = getFacetValue('facet1');
        facets['Ist vielseitig interessiert'] = getFacetValue('facet2');
        // Wiederholen für alle Facetten...

        // Gewissenhaftigkeit
        facets['Erledigt Aufgaben gründlich'] = getFacetValue('facet11');
        // Wiederholen für alle Facetten...

        // Weitere Dimensionen hier hinzufügen...

        // Generierung des System Prompts
        let systemPrompt = generateSystemPrompt(facets);

        // Vorbereitung der JSON-Daten
        let systemPromptJson = JSON.stringify(facets, null, 2);

        // Anzeige der Ergebnisse
        systemPromptTextarea.value = systemPrompt;
        systemPromptJsonTextarea.value = systemPromptJson;
        resultsDiv.style.display = 'block';

        // Optional: Daten an den Server senden
        /*
        fetch('/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                system_prompt: systemPrompt,
                system_prompt_json: facets
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
        });
        */
    });

    function getFacetValue(facetId, reverseScored = false) {
        let value = parseInt(document.getElementById(facetId).value);
        if (reverseScored) {
            // Umkehrung des Wertes für umgekehrt bewertete Items (Skala von 1 bis 7)
            value = 8 - value;
        }
        return value;
    }

    function generateSystemPrompt(facets) {
        // Hier können Sie komplexere Logik einfügen, um einen zusammenhängenden Prompt zu erstellen

        let prompt = "Du bist ein KI-Assistent mit folgenden Persönlichkeitsmerkmalen:\n\n";

        // Gruppierung der Facetten nach Dimensionen (als Beispiel)
        prompt += "Offenheit für Erfahrungen:\n";
        prompt += "- Ist originell, entwickelt neue Ideen: " + facets['Ist originell, entwickelt neue Ideen'] + "\n";
        prompt += "- Ist vielseitig interessiert: " + facets['Ist vielseitig interessiert'] + "\n";
        // Weitere Facetten hinzufügen...

        prompt += "\nGewissenhaftigkeit:\n";
        prompt += "- Erledigt Aufgaben gründlich: " + facets['Erledigt Aufgaben gründlich'] + "\n";
        // Weitere Facetten hinzufügen...

        // Weitere Dimensionen hinzufügen...

        return prompt;
    }
});