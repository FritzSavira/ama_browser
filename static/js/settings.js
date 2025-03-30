// settings.js - Add at the top or in a separate JS file
const facetsData = [
  {
    id: 'facet_role1',
    dimension: 'Rolle',
    sub_dimension: 'Identität',
    dim_description: 'Beschreibt deine Rolle, in der du die Frage beantwortest.',
    promptCharacteristic: 'Du bist ein wissenschaftlich arbeitender, evangelikaler Theologe und Professor für Theologie.'
  },
  {
    id: 'facet_role2',
    dimension: 'Rolle',
    sub_dimension: 'Identität',
    dim_description: 'Beschreibt deine Rolle, in der du die Frage beantwortest.',
    promptCharacteristic: 'Du bist ein mitfühlender Gemeindepastor mit langjähriger Erfahrung in der Seelsorge.'
  },
  {
    id: 'facet_role3',
    dimension: 'Rolle',
    sub_dimension: 'Ziel',
    dim_description: 'Beschreibt die Ziele, die du primär mit der Beantwortung der Frage erzielen willst.',
    promptCharacteristic: 'Beantworte Fragen gründlich und persönlich, mit dem Ziel einer vertieften Erkenntnis'
  },
  {
    id: 'facet_role4',
    dimension: 'Rolle',
    sub_dimension: 'Ziel',
    dim_description: 'Beschreibt die Ziele, die du primär mit der Beantwortung der Frage erzielen willst.',
    promptCharacteristic: 'Ziele auf geistliche Erbauung und praktische Lebenshilfe ab'
  },
  {
    id: 'facet_persoality1',
    dimension: 'Persönlichkeit',
    sub_dimension: 'Glaubensbasis',
    dim_description: 'Beschreibt deine Glaubensbasis.',
    promptCharacteristic: 'Du bist ein evangelikaler, bibeltreuer Wissenschaftler mit tiefer persönlicher Glaubensüberzeugung'
  },
  {
    id: 'facet_persoality2',
    dimension: 'Persönlichkeit',
    sub_dimension: 'Glaubensbasis',
    dim_description: 'Beschreibt deine Glaubensbasis.',
    promptCharacteristic: 'Du bist ein offener, ökumenisch orientierter Christ, der verschiedene Glaubenstraditionen wertschätzt.'
  },
  {
    id: 'facet_persoality3',
    dimension: 'Persönlichkeit',
    sub_dimension: 'Haltung',
    dim_description: 'Beschreibt deine Haltung.',
    promptCharacteristic: 'Deine Arbeit ist durch Gebet und Glauben getragen; du bist zugleich wissenschaftlich rigoros und demütig'
  },
  {
    id: 'facet_persoality4',
    dimension: 'Persönlichkeit',
    sub_dimension: 'Haltung',
    dim_description: 'Beschreibt deine Haltung.',
    promptCharacteristic: 'Du bist geduldig und besonnen, auch bei kontroversen theologischen Fragen.'
  }
];

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

    const facetsContainer = document.getElementById('facets-container');

    // Gruppiere Facetten nach Dimension und dann nach Sub-Dimension
    const groupedFacets = {};
    facetsData.forEach(facet => {
        if (!groupedFacets[facet.dimension]) {
            groupedFacets[facet.dimension] = {};
        }
        if (!groupedFacets[facet.dimension][facet.sub_dimension]) {
            groupedFacets[facet.dimension][facet.sub_dimension] = [];
        }
        groupedFacets[facet.dimension][facet.sub_dimension].push(facet);
    });

    // Erstelle Facetten gruppiert nach Dimensionen und Sub-Dimensionen
    for (const dimension in groupedFacets) {
        // Erstelle einen Container für jede Dimension (als Akkordeon-Element)
        const dimensionDiv = document.createElement('div');
        dimensionDiv.classList.add('dimension-group', 'accordion-item');

        // Füge die Dimension als Akkordeon-Header hinzu
        const dimensionHeader = document.createElement('div');
        dimensionHeader.classList.add('accordion-header');
        dimensionHeader.innerHTML = `<h2>${dimension}</h2><span class="accordion-icon">+</span>`;
        dimensionDiv.appendChild(dimensionHeader);

        // Erstelle einen Container für den Inhalt der Dimension
        const dimensionContent = document.createElement('div');
        dimensionContent.classList.add('accordion-content');
        dimensionContent.style.display = 'none';  // Initial versteckt

        // Füge Event-Listener für das Aufklappen/Zuklappen hinzu
        dimensionHeader.addEventListener('click', function() {
            const isOpen = dimensionContent.style.display !== 'none';
            dimensionContent.style.display = isOpen ? 'none' : 'block';
            dimensionHeader.querySelector('.accordion-icon').textContent = isOpen ? '+' : '-';
        });

        // Für jede Sub-Dimension in dieser Dimension
        for (const subDimension in groupedFacets[dimension]) {
            // Erstelle einen Container für jede Sub-Dimension (als Akkordeon-Element)
            const subDimensionDiv = document.createElement('div');
            subDimensionDiv.classList.add('sub-dimension-group', 'accordion-item');
            subDimensionDiv.dataset.dimension = dimension;
            subDimensionDiv.dataset.subDimension = subDimension;

            // Füge die Sub-Dimension als Akkordeon-Header hinzu
            const subDimensionHeader = document.createElement('div');
            subDimensionHeader.classList.add('accordion-header', 'sub-header');
            subDimensionHeader.innerHTML = `<h3>${subDimension}</h3><span class="accordion-icon">+</span>`;
            subDimensionDiv.appendChild(subDimensionHeader);

            // Container für die Beschreibung und ausgewählte Facetten
            const subDimensionInfo = document.createElement('div');
            subDimensionInfo.classList.add('sub-dimension-info');
            subDimensionDiv.appendChild(subDimensionInfo);

            // Füge die Dimensionsbeschreibung hinzu
            if (groupedFacets[dimension][subDimension].length > 0) {
                const descriptionElement = document.createElement('p');
                descriptionElement.classList.add('dimension-description');
                descriptionElement.textContent = groupedFacets[dimension][subDimension][0].dim_description;
                subDimensionInfo.appendChild(descriptionElement);
            }

            // Container für ausgewählte Einträge erstellen
            const selectedFacetsContainer = document.createElement('div');
            selectedFacetsContainer.classList.add('selected-facets');
            subDimensionInfo.appendChild(selectedFacetsContainer);

            // Erstelle einen Container für den Inhalt der Sub-Dimension
            const subDimensionContent = document.createElement('div');
            subDimensionContent.classList.add('accordion-content');
            subDimensionContent.style.display = 'none';  // Initial versteckt

            // Füge Event-Listener für das Aufklappen/Zuklappen hinzu
            subDimensionHeader.addEventListener('click', function(event) {
                event.stopPropagation();  // Verhindert, dass das Klicken auf die Sub-Dimension auch die Dimension toggled
                const isOpen = subDimensionContent.style.display !== 'none';
                const willBeClosed = isOpen; // Wenn es offen ist, wird es geschlossen und umgekehrt

                subDimensionContent.style.display = isOpen ? 'none' : 'block';
                subDimensionHeader.querySelector('.accordion-icon').textContent = isOpen ? '+' : '-';

                // Aktualisiere die angezeigten ausgewählten Facetten
                // Wenn die Sub-Dimension geschlossen wird, zeige ausgewählte Facetten
                updateSelectedFacets(subDimensionDiv, willBeClosed);
            });

            // Füge alle Facetten dieser Sub-Dimension hinzu
            groupedFacets[dimension][subDimension].forEach(facet => {
                const facetDiv = document.createElement('div');
                facetDiv.classList.add('facet');

                // Erstelle Checkbox für diese Facette (standardmäßig deaktiviert)
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `${facet.id}-checkbox`;
                checkbox.classList.add('facet-checkbox');
                checkbox.dataset.facetId = facet.id;
                checkbox.checked = false;  // Standardmäßig deaktiviert

                // Event-Listener für Checkbox-Änderungen
                checkbox.addEventListener('change', function() {
                    // Aktualisiere die angezeigten ausgewählten Facetten
                    const isSubDimensionClosed = subDimensionContent.style.display === 'none';
                    updateSelectedFacets(subDimensionDiv, isSubDimensionClosed);
                });

                const facetLabel = document.createElement('label');
                facetLabel.htmlFor = `${facet.id}-checkbox`;
                facetLabel.classList.add('facet-label');
                facetLabel.textContent = facet.promptCharacteristic;

                // Füge die Elemente hinzu
                facetDiv.appendChild(checkbox);
                facetDiv.appendChild(facetLabel);

                subDimensionContent.appendChild(facetDiv);
            });

            // Füge die Sub-Dimension zum Inhalt der Dimension hinzu
            subDimensionDiv.appendChild(subDimensionContent);
            dimensionContent.appendChild(subDimensionDiv);

            // Initial die ausgewählten Facetten aktualisieren (bei geschlossener Sub-Dimension)
            updateSelectedFacets(subDimensionDiv, true);
        }

        // Füge den Inhalt der Dimension zum Container hinzu
        dimensionDiv.appendChild(dimensionContent);
        facetsContainer.appendChild(dimensionDiv);
    }

    // Funktion zum Aktualisieren der angezeigten ausgewählten Facetten
    function updateSelectedFacets(subDimensionDiv, shouldShowSelectedFacets) {
        const dimension = subDimensionDiv.dataset.dimension;
        const subDimension = subDimensionDiv.dataset.subDimension;
        const selectedFacetsContainer = subDimensionDiv.querySelector('.selected-facets');

        if (!selectedFacetsContainer) return;

        // Leere den Container
        selectedFacetsContainer.innerHTML = '';

        // Finde alle ausgewählten Facetten in dieser Sub-Dimension
        const subDimensionFacets = groupedFacets[dimension][subDimension];
        const selectedFacets = subDimensionFacets.filter(facet => {
            const checkbox = document.getElementById(`${facet.id}-checkbox`);
            return checkbox && checkbox.checked;
        });

        // Wenn keine Facetten ausgewählt sind, verstecke den Container
        if (selectedFacets.length === 0) {
            selectedFacetsContainer.style.display = 'none';
            return;
        }

        // Erstelle einen Eintrag für jede ausgewählte Facette
        selectedFacets.forEach(facet => {
            const facetElement = document.createElement('div');
            facetElement.classList.add('selected-facet');
            facetElement.textContent = facet.promptCharacteristic;
            selectedFacetsContainer.appendChild(facetElement);
        });

        // Zeige den Container nur an, wenn die Sub-Dimension geschlossen ist (shouldShowSelectedFacets=true)
        // und wenn tatsächlich Facetten ausgewählt sind
        selectedFacetsContainer.style.display = shouldShowSelectedFacets && selectedFacets.length > 0 ? 'block' : 'none';
    }

    generatePromptButton.addEventListener('click', function() {
        // Sammlung der Facettenwerte nur für aktivierte Checkboxen
        let facetsValues = {};

        facetsData.forEach(facet => {
            const checkbox = document.getElementById(`${facet.id}-checkbox`);
            // Nur aktivierte Facetten einbeziehen
            if (checkbox.checked) {
                facetsValues[facet.id] = getFacetValue(facet.id);
            }
        });

        // Generate the system prompt
        let systemPrompt = generateSystemPrompt(facetsValues);

        // Prepare JSON data
        let systemPromptJson = JSON.stringify(facetsValues, null, 2);

        // Display the results
        systemPromptTextarea.value = systemPrompt;
        systemPromptJsonTextarea.value = systemPromptJson;
        resultsDiv.style.display = 'block';

        // Daten an den Server senden
        fetch('/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                system_prompt: systemPrompt,
                system_prompt_json: facetsValues
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
        });
    });

    function getFacetValue(facetId) {
        const facet = facetsData.find(f => f.id === facetId);
        if (facet) {
            return facet.promptCharacteristic;
        }
        return '';
    }

    function generateSystemPrompt(facetsValues) {
        let prompt = "prompt_system = '''\n";

        // Group facets by dimension and sub-dimension
        const groupedFacets = {};
        facetsData.forEach(facet => {
            const checkbox = document.getElementById(`${facet.id}-checkbox`);
            // Nur aktivierte Facetten gruppieren
            if (checkbox.checked) {
                if (!groupedFacets[facet.dimension]) {
                    groupedFacets[facet.dimension] = {};
                }
                if (!groupedFacets[facet.dimension][facet.sub_dimension]) {
                    groupedFacets[facet.dimension][facet.sub_dimension] = [];
                }
                groupedFacets[facet.dimension][facet.sub_dimension].push(facet);
            }
        });

        // Build prompt for each dimension and sub-dimension
        for (const dimension in groupedFacets) {
            if (Object.keys(groupedFacets[dimension]).length > 0) {
                prompt += `\n${dimension}:\n`;

                for (const subDimension in groupedFacets[dimension]) {
                    if (groupedFacets[dimension][subDimension].length > 0) {
                        prompt += `  ${subDimension}:\n`;
                        prompt += `  ${groupedFacets[dimension][subDimension][0].dim_description}\n`;

                        groupedFacets[dimension][subDimension].forEach(facet => {
                            prompt += `  ${facet.promptCharacteristic}\n`;
                        });
                    }
                }
            }
        }

        return prompt += "'''";
    }
});