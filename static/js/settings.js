// document.addEventListener('DOMContentLoaded', function() {

// settings.js - Add at the top or in a separate JS file
const facetsData = [
  {
    id: 'facet1',
    dimension: 'Offenheit für Erfahrungen',
    dim_description: 'Beschreibt deine intellektuelle Neugier, Kreativität und Präferenz für Abwechslung.',
    facetLabel: 'Ist originell, entwickelt neue Ideen',
    promptCharacteristic: 'Neue Ideen betreffend bist du',
    reverseScored: false,
    valueLabels: [
      'völlig unoriginell',
      'sehr wenig originell',
      'eher unoriginell',
      'mäßig originell',
      'eher originell',
      'sehr originell',
      'äußerst originell'
    ]
  },
  {
    id: 'facet2',
    dimension: 'Offenheit für Erfahrungen',
    dim_description: 'Beschreibt deine intellektuelle Neugier, Kreativität und Präferenz für Abwechslung.',
    facetLabel: 'Ist vielseitig interessiert',
    promptCharacteristic: 'Interessen betreffend bist du',
    reverseScored: false,
    valueLabels: [
      'extrem spezialisiert',
      'sehr spezialisiert',
      'eher spezialisiert',
      'mäßig vielseitig',
      'eher vielseitig',
      'sehr vielseitig',
      'äußerst vielseitig'
    ]
  },
  {
    id: 'facet3',
    dimension: 'Offenheit für Erfahrungen',
    dim_description: 'Beschreibt deine intellektuelle Neugier, Kreativität und Präferenz für Abwechslung.',
    facetLabel: 'Ist einfallsreich und tiefsinnig',
    promptCharacteristic: 'Einfälle betreffend bist du',
    reverseScored: false,
    valueLabels: [
      'völlig oberflächlich',
      'sehr oberflächlich',
      'eher oberflächlich',
      'mäßig tiefsinnig',
      'eher tiefsinnig',
      'sehr tiefsinnig',
      'äußerst tiefsinnig'
    ]
  },
  {
    id: 'facet4',
    dimension: 'Offenheit für Erfahrungen',
    dim_description: 'Beschreibt deine intellektuelle Neugier, Kreativität und Präferenz für Abwechslung.',
    facetLabel: 'Hat eine lebhafte Fantasie',
    promptCharacteristic: 'Lebhafte Fantasie betreffend bist du',
    reverseScored: false,
    valueLabels: [
      'völlig fantasielos',
      'sehr fantasiearm',
      'eher fantasiearm',
      'mäßig fantasievoll',
      'eher fantasievoll',
      'sehr fantasievoll',
      'äußerst fantasievoll'
    ]
  },
  {
    id: 'facet5',
    dimension: 'Offenheit für Erfahrungen',
    dim_description: 'Beschreibt deine intellektuelle Neugier, Kreativität und Präferenz für Abwechslung.',
    facetLabel: 'Ist erfinderisch',
    promptCharacteristic: 'Erfindungen betreffend bist du',
    reverseScored: false,
    valueLabels: [
      'völlig unerfinderisch',
      'sehr unerfinderisch',
      'eher unerfinderisch',
      'mäßig erfinderisch',
      'eher erfinderisch',
      'sehr erfinderisch',
      'äußerst erfinderisch'
    ]
  },
  {
    id: 'facet6',
    dimension: 'Offenheit für Erfahrungen',
    dim_description: 'Beschreibt deine intellektuelle Neugier, Kreativität und Präferenz für Abwechslung.',
    facetLabel: 'Reflektiert gerne, spielt mit Ideen',
    promptCharacteristic: 'Du bist',
    reverseScored: false,
    valueLabels: [
      'völlig unreflektiert',
      'sehr wenig reflektiert',
      'eher unreflektiert',
      'mäßig reflektiert',
      'eher reflektiert',
      'sehr reflektiert',
      'äußerst reflektiert'
    ]
  },
  {
    id: 'facet7',
    dimension: 'Offenheit für Erfahrungen',
    dim_description: 'Beschreibt deine intellektuelle Neugier, Kreativität und Präferenz für Abwechslung.',
    facetLabel: 'Hat wenig künstlerische Interessen (umgekehrt bewertet)',
    promptCharacteristic: 'Du hast',
    reverseScored: true,
    valueLabels: [
      'keine künstlerischen Interessen',
      'sehr wenige künstlerische Interessen',
      'wenige künstlerische Interessen',
      'einige künstlerische Interessen',
      'mehrere künstlerische Interessen',
      'viele künstlerische Interessen',
      'sehr viele künstlerische Interessen'
    ]
  },
  {
    id: 'facet8',
    dimension: 'Gewissenhaftigkeit',
    dim_description: 'Beschreibt dich hinsichtlich Selbstdisziplin, Pflichtbewusstsein und Streben nach Leistung.',
    facetLabel: 'Erledigt Aufgaben gründlich',
    promptCharacteristic: 'Aufgaben erledigst du',
    reverseScored: false,
    valueLabels: [
      'äußerst oberflächlich',
      'sehr oberflächlich',
      'eher oberflächlich',
      'mittelmäßig gründlich',
      'eher gründlich',
      'sehr gründlich',
      'äußerst gründlich'
    ]
  },
  {
    id: 'facet9',
    dimension: 'Gewissenhaftigkeit',
    dim_description: 'Beschreibt dich hinsichtlich Selbstdisziplin, Pflichtbewusstsein und Streben nach Leistung.',
    facetLabel: 'Kann manchmal nachlässig sein (umgekehrt bewertet)',
    promptCharacteristic: 'Du bist',
    reverseScored: true,
    valueLabels: [
      'ständig nachlässig',
      'sehr häufig nachlässig',
      'oft nachlässig',
      'gelegentlich nachlässig',
      'selten nachlässig',
      'sehr selten nachlässig',
      'nie nachlässig'
    ]
  },
  {
    id: 'facet10',
    dimension: 'Gewissenhaftigkeit',
    dim_description: 'Beschreibt dich hinsichtlich Selbstdisziplin, Pflichtbewusstsein und Streben nach Leistung.',
    facetLabel: 'Ist ein zuverlässiger Arbeiter',
    promptCharacteristic: 'Du bist',
    reverseScored: false,
    valueLabels: [
      'völlig unzuverlässig',
      'sehr unzuverlässig',
      'eher unzuverlässig',
      'mäßig zuverlässig',
      'eher zuverlässig',
      'sehr zuverlässig',
      'äußerst zuverlässig'
    ]
  },
  {
    id: 'facet11',
    dimension: 'Gewissenhaftigkeit',
    dim_description: 'Beschreibt dich hinsichtlich Selbstdisziplin, Pflichtbewusstsein und Streben nach Leistung.',
    facetLabel: 'Neigt zur Unordentlichkeit (umgekehrt bewertet)',
    promptCharacteristic: 'Du bist',
    reverseScored: true,
    valueLabels: [
      'extrem unordentlich',
      'sehr unordentlich',
      'eher unordentlich',
      'mittelmäßig ordentlich',
      'eher ordentlich',
      'sehr ordentlich',
      'extrem ordentlich'
    ]
  },
  {
    id: 'facet12',
    dimension: 'Gewissenhaftigkeit',
    dim_description: 'Beschreibt dich hinsichtlich Selbstdisziplin, Pflichtbewusstsein und Streben nach Leistung.',
    facetLabel: 'Neigt zur Faulheit (umgekehrt bewertet)',
    promptCharacteristic: 'Du bist',
    reverseScored: true,
    valueLabels: [
      'extrem faul',
      'sehr faul',
      'eher faul',
      'mittelmäßig fleißig',
      'eher fleißig',
      'sehr fleißig',
      'extrem fleißig'
    ]
  },
  {
    id: 'facet13',
    dimension: 'Gewissenhaftigkeit',
    dim_description: 'Beschreibt dich hinsichtlich Selbstdisziplin, Pflichtbewusstsein und Streben nach Leistung.',
    facetLabel: 'Führt Aufgaben bis zum Ende durch',
    promptCharacteristic: 'Duchhaltevermögen:',
    reverseScored: false,
    valueLabels: [
      'gibt sofort auf',
      'gibt sehr schnell auf',
      'gibt eher schnell auf',
      'mittelmäßig beharrlich',
      'eher beharrlich',
      'sehr beharrlich',
      'extrem beharrlich'
    ]
  },
  {
    id: 'facet14',
    dimension: 'Gewissenhaftigkeit',
    dim_description: 'Beschreibt dich hinsichtlich Selbstdisziplin, Pflichtbewusstsein und Streben nach Leistung.',
    facetLabel: 'Erledigt Dinge effizient',
    promptCharacteristic: 'Du erledigst Dinge ',
    reverseScored: false,
    valueLabels: [
      'extrem ineffizient',
      'sehr ineffizient',
      'eher ineffizient',
      'mittelmäßig effizient',
      'eher effizient',
      'sehr effizient',
      'extrem effizient'
    ]
  },
  {
    id: 'facet15',
    dimension: 'Gewissenhaftigkeit',
    dim_description: 'Beschreibt dich hinsichtlich Selbstdisziplin, Pflichtbewusstsein und Streben nach Leistung.',
    facetLabel: 'Plant und hält sich an diese Pläne',
    promptCharacteristic: 'Du ',
    reverseScored: false,
    valueLabels: [
      'planst nie',
      'planst selten',
      'planst gelegentlich',
      'planst regelmäßig',
      'planst häufig und hältst meist ein',
      'planst sehr oft und hältst fast immer ein',
      'planst immer und hältst sich strikt daran'
    ]
  },
  {
    id: 'facet16',
    dimension: 'Gewissenhaftigkeit',
    dim_description: 'Beschreibt dich hinsichtlich Selbstdisziplin, Pflichtbewusstsein und Streben nach Leistung.',
    facetLabel: 'Lässt sich leicht ablenken (umgekehrt bewertet)',
    promptCharacteristic: 'Hinsichtlich Ablenkung bist du',
    reverseScored: true,
    valueLabels: [
      'extrem ablenkbar',
      'sehr leicht ablenkbar',
      'eher leicht ablenkbar',
      'mäßig fokussiert',
      'eher fokussiert',
      'sehr fokussiert',
      'extrem fokussiert'
    ]
  },
  {
    id: 'facet17',
    dimension: 'Extraversion',
    dim_description: 'Beschreibt dich hinsichtlich Geselligkeit, Durchsetzungsvermögen und Energieniveau.',
    facetLabel: 'Ist gesprächig',
    promptCharacteristic: 'Hinsichtlich Gesprächigkeit bist du',
    reverseScored: false,
    valueLabels: [
      'extrem wortkarg',
      'sehr schweigsam',
      'eher still',
      'mäßig gesprächig',
      'eher gesprächig',
      'sehr redselig',
      'äußerst gesprächig'
    ]
  },
  {
    id: 'facet18',
    dimension: 'Extraversion',
    dim_description: 'Beschreibt dich hinsichtlich Geselligkeit, Durchsetzungsvermögen und Energieniveau.',
    facetLabel: 'Ist zurückhaltend (umgekehrt bewertet)',
    promptCharacteristic: 'Du bist',
    reverseScored: true,
    valueLabels: [
      'äußerst zurückhaltend',
      'sehr zurückhaltend',
      'eher zurückhaltend',
      'mittelmäßig zurückhaltend',
      'eher offen',
      'sehr offen',
      'äußerst offenherzig'
    ]
  },
  {
    id: 'facet19',
    dimension: 'Extraversion',
    dim_description: 'Beschreibt dich hinsichtlich Geselligkeit, Durchsetzungsvermögen und Energieniveau.',
    facetLabel: 'Ist voller Energie',
    promptCharacteristic: 'Du bist',
    reverseScored: false,
    valueLabels: [
      'völlig energielos',
      'sehr energiearm',
      'eher antriebslos',
      'mäßig energisch',
      'eher energiegeladen',
      'sehr energiegeladen',
      'äußerst energiegeladen'
    ]
  },
  {
    id: 'facet20',
    dimension: 'Extraversion',
    dim_description: 'Beschreibt dich hinsichtlich Geselligkeit, Durchsetzungsvermögen und Energieniveau.',
    facetLabel: 'Ist begeisterungsfähig und motivierend',
    promptCharacteristic: 'Du bist',
    reverseScored: false,
    valueLabels: [
      'völlig unbegeistert',
      'sehr schwer zu begeistern',
      'eher schwer zu begeistern',
      'mäßig begeisterungsfähig',
      'eher enthusiastisch',
      'sehr motivierend',
      'äußerst mitreißend'
    ]
  },
  {
    id: 'facet21',
    dimension: 'Extraversion',
    dim_description: 'Beschreibt dich hinsichtlich Geselligkeit, Durchsetzungsvermögen und Energieniveau.',
    facetLabel: 'Ist eher still (umgekehrt bewertet)',
    promptCharacteristic: 'Du bist',
    reverseScored: true,
    valueLabels: [
      'völlig verstummt',
      'sehr still',
      'eher still',
      'mittelmäßig kommunikativ',
      'eher gesprächig',
      'sehr ausdrucksstark',
      'äußerst lebhaft im Ausdruck'
    ]
  },
  {
    id: 'facet22',
    dimension: 'Extraversion',
    dim_description: 'Beschreibt dich hinsichtlich Geselligkeit, Durchsetzungsvermögen und Energieniveau.',
    facetLabel: 'Hat eine durchsetzungsfähige Persönlichkeit',
    promptCharacteristic: 'Hinsichtlich Durchsetzungsfähigkeit bist du',
    reverseScored: false,
    valueLabels: [
      'völlig nachgiebig',
      'sehr wenig durchsetzungsfähig',
      'eher zurückhaltend',
      'mäßig durchsetzungsfähig',
      'eher bestimmt',
      'sehr durchsetzungsstark',
      'äußerst dominant'
    ]
  },
  {
    id: 'facet23',
    dimension: 'Extraversion',
    dim_description: 'Beschreibt dich hinsichtlich Geselligkeit, Durchsetzungsvermögen und Energieniveau.',
    facetLabel: 'Ist manchmal schüchtern und gehemmt (umgekehrt bewertet)',
    promptCharacteristic: 'Du bist',
    reverseScored: true,
    valueLabels: [
      'extrem schüchtern',
      'sehr gehemmt',
      'eher zurückhaltend',
      'teils gehemmt, teils ungezwungen',
      'eher selbstsicher',
      'sehr selbstbewusst',
      'äußerst selbstsicher'
    ]
  },
  {
    id: 'facet24',
    dimension: 'Extraversion',
    dim_description: 'Beschreibt dich hinsichtlich Geselligkeit, Durchsetzungsvermögen und Energieniveau.',
    facetLabel: 'Ist kontaktfreudig und gesellig',
    promptCharacteristic: 'Hinsichtlich Kontaktfreudigkeit bist du',
    reverseScored: false,
    valueLabels: [
      'extrem zurückgezogen',
      'sehr kontaktscheu',
      'eher einzelgängerisch',
      'mäßig gesellig',
      'eher kontaktfreudig',
      'sehr gesellig',
      'äußerst gesellschaftsorientiert'
    ]
  },
  {
    id: 'facet25',
    dimension: 'Verträglichkeit',
    dim_description: 'Beschreibt dein zwischenmenschliches Verhalten wie Mitgefühl, Kooperationsbereitschaft und Vertrauen.',
    facetLabel: 'Neigt dazu, andere zu kritisieren (umgekehrt bewertet)',
    promptCharacteristic: 'Gegenüber anderen Personen bist du',
    reverseScored: true,
    valueLabels: [
      'äußerst unkritisch',
      'sehr zurückhaltend mit Kritik',
      'eher zurückhaltend mit Kritik',
      'gelegentlich kritisch',
      'häufig kritisch',
      'sehr kritisch veranlagt',
      'extrem kritisch'
    ]
  },
  {
    id: 'facet26',
    dimension: 'Verträglichkeit',
    dim_description: 'Beschreibt dein zwischenmenschliches Verhalten wie Mitgefühl, Kooperationsbereitschaft und Vertrauen.',
    facetLabel: 'Ist hilfsbereit und selbstlos gegenüber anderen',
    promptCharacteristic: 'Gegenüber anderen Personen bist du',
    reverseScored: false,
    valueLabels: [
      'überhaupt nicht hilfsbereit',
      'selten hilfsbereit',
      'gelegentlich hilfsbereit',
      'mäßig hilfsbereit',
      'oft hilfsbereit',
      'sehr hilfsbereit',
      'außerordentlich selbstlos'
    ]
  },
  {
    id: 'facet27',
    dimension: 'Verträglichkeit',
    dim_description: 'Beschreibt dein zwischenmenschliches Verhalten wie Mitgefühl, Kooperationsbereitschaft und Vertrauen.',
    facetLabel: 'Beginnt Streit mit anderen (umgekehrt bewertet)',
    promptCharacteristic: 'Du bist',
    reverseScored: true,
    valueLabels: [
      'völlig konfliktscheu',
      'sehr friedfertig',
      'eher harmonieorientiert',
      'gelegentlich streitbar',
      'häufig streitlustig',
      'sehr konfliktfreudig',
      'extrem konfrontativ'
    ]
  },
  {
    id: 'facet28',
    dimension: 'Verträglichkeit',
    dim_description: 'Beschreibt dein zwischenmenschliches Verhalten wie Mitgefühl, Kooperationsbereitschaft und Vertrauen.',
    facetLabel: 'Hat ein verzeihendes Wesen',
    promptCharacteristic: 'Du bist',
    reverseScored: false,
    valueLabels: [
      'unversöhnlich',
      'trägt lange nach',
      'verzeiht schwer',
      'manchmal verzeihend',
      'überwiegend verzeihend',
      'sehr verzeihend',
      'außerordentlich vergebungsbereit'
    ]
  },
  {
    id: 'facet29',
    dimension: 'Verträglichkeit',
    dim_description: 'Beschreibt dein zwischenmenschliches Verhalten wie Mitgefühl, Kooperationsbereitschaft und Vertrauen.',
    facetLabel: 'Ist grundsätzlich vertrauensvoll',
    promptCharacteristic: 'Du bist',
    reverseScored: false,
    valueLabels: [
      'völlig misstrauisch',
      'sehr misstrauisch',
      'eher misstrauisch',
      'vorsichtig abwägend',
      'eher vertrauensvoll',
      'sehr vertrauensvoll',
      'blind vertrauend'
    ]
  },
  {
    id: 'facet30',
    dimension: 'Verträglichkeit',
    dim_description: 'Beschreibt dein zwischenmenschliches Verhalten wie Mitgefühl, Kooperationsbereitschaft und Vertrauen.',
    facetLabel: 'Kann kühl und distanziert sein (umgekehrt bewertet)',
    promptCharacteristic: 'Du verhältst dich anderen Personen gegenüber',
    reverseScored: true,
    valueLabels: [
      'äußerst herzlich',
      'sehr warm und nahbar',
      'überwiegend warm im Umgang',
      'teils warm, teils distanziert',
      'eher reserviert',
      'deutlich distanziert',
      'extrem kühl und unnahbar'
    ]
  },
  {
    id: 'facet31',
    dimension: 'Verträglichkeit',
    dim_description: 'Beschreibt dein zwischenmenschliches Verhalten wie Mitgefühl, Kooperationsbereitschaft und Vertrauen.',
    facetLabel: 'Ist rücksichtsvoll und freundlich zu fast allen Menschen',
    promptCharacteristic: 'Du bist',
    reverseScored: false,
    valueLabels: [
      'grob und rücksichtslos',
      'meist unfreundlich',
      'eher unfreundlich',
      'neutral im Umgang',
      'überwiegend freundlich',
      'sehr rücksichtsvoll',
      'außergewöhnlich zuvorkommend'
    ]
  },
  {
    id: 'facet32',
    dimension: 'Verträglichkeit',
    dim_description: 'Beschreibt dein zwischenmenschliches Verhalten wie Mitgefühl, Kooperationsbereitschaft und Vertrauen.',
    facetLabel: 'Ist manchmal unhöflich zu anderen (umgekehrt bewertet)',
    promptCharacteristic: 'Du verhältst dich anderen Personen gegenüber',
    reverseScored: true,
    valueLabels: [
      'stets tadellos höflich',
      'fast immer höflich',
      'überwiegend höflich',
      'meist höflich, gelegentlich nicht',
      'gelegentlich unhöflich',
      'häufig unhöflich',
      'durchweg unhöflich'
    ]
  },
  {
    id: 'facet33',
    dimension: 'Verträglichkeit',
    dim_description: 'Beschreibt dein zwischenmenschliches Verhalten wie Mitgefühl, Kooperationsbereitschaft und Vertrauen.',
    facetLabel: 'Arbeitet gerne mit anderen zusammen',
    promptCharacteristic: 'Du arbeitest',
    reverseScored: false,
    valueLabels: [
      'strikt einzelgängerisch',
      'stark einzelgängerisch',
      'eher einzelgängerisch',
      'neutral zur Zusammenarbeit',
      'arbeitet gerne im Team',
      'bevorzugt stark die Teamarbeit',
      'ausschließlich teamorientiert'
    ]
  },
  {
    id: 'facet34',
    dimension: 'Neurotizismus',
    dim_description: 'Beschreibt deine emotionale Stabilität bzw. Instabilität.',
    facetLabel: 'Ist niedergeschlagen, deprimiert',
    promptCharacteristic: 'Du bist',
    reverseScored: false,
    valueLabels: [
      'nie niedergeschlagen',
      'selten niedergeschlagen',
      'gelegentlich niedergeschlagen',
      'manchmal niedergeschlagen',
      'häufig niedergeschlagen',
      'meist niedergeschlagen',
      'ständig deprimiert'
    ]
  },
  {
    id: 'facet35',
    dimension: 'Neurotizismus',
    dim_description: 'Beschreibt deine emotionale Stabilität bzw. Instabilität.',
    facetLabel: 'Ist entspannt, geht gut mit Stress um (umgekehrt bewertet)',
    promptCharacteristic: 'In Stresssituationen bist du',
    reverseScored: true,
    valueLabels: [
      'außergewöhnlich stressresistent',
      'sehr entspannt',
      'überwiegend gelassen',
      'mäßig stressresistent',
      'eher stressanfällig',
      'sehr stressanfällig',
      'extrem angespannt'
    ]
  },
  {
    id: 'facet36',
    dimension: 'Neurotizismus',
    dim_description: 'Beschreibt deine emotionale Stabilität bzw. Instabilität.',
    facetLabel: 'Kann angespannt sein',
    promptCharacteristic: 'Generell bist du',
    reverseScored: false,
    valueLabels: [
      'nie angespannt',
      'sehr selten angespannt',
      'selten angespannt',
      'gelegentlich angespannt',
      'häufig angespannt',
      'meist angespannt',
      'ständig angespannt'
    ]
  },
  {
    id: 'facet37',
    dimension: 'Neurotizismus',
    dim_description: 'Beschreibt deine emotionale Stabilität bzw. Instabilität.',
    facetLabel: 'Macht sich viele Sorgen',
    promptCharacteristic: 'Sorgen betreffend handelst du',
    reverseScored: false,
    valueLabels: [
      'praktisch sorgenfrei',
      'sehr sorglos',
      'eher unbesorgt',
      'gelegentlich besorgt',
      'regelmäßige besorgt',
      'sehr besorgt',
      'ständig besorgt'
    ]
  },
  {
    id: 'facet38',
    dimension: 'Neurotizismus',
    dim_description: 'Beschreibt deine emotionale Stabilität bzw. Instabilität.',
    facetLabel: 'Ist emotional stabil, nicht leicht aus der Fassung zu bringen (umgekehrt bewertet)',
    promptCharacteristic: 'Emotionen betreffend bist du',
    reverseScored: true,
    valueLabels: [
      'außerordentlich gefasst',
      'sehr emotional stabil',
      'überwiegend stabil',
      'mäßig stabil',
      'leicht aus der Fassung zu bringen',
      'sehr leicht erschütterbar',
      'extrem emotional instabil'
    ]
  },
    {
    id: 'facet39',
    dimension: 'Neurotizismus',
    dim_description: 'Beschreibt deine emotionale Stabilität bzw. Instabilität.',
    facetLabel: 'Kann launisch sein',
    promptCharacteristic: 'Du bist',
    reverseScored: false,
    valueLabels: [
      'nie launisch',
      'äußerst selten launisch',
      'selten launisch',
      'gelegentlich launisch',
		'häufig launisch',
      'sehr launisch',
      'extrem stimmungsschwankend'
    ]
  },
    {
    id: 'facet40',
    dimension: 'Neurotizismus',
    dim_description: 'Beschreibt deine emotionale Stabilität bzw. Instabilität.',
    facetLabel: 'Wird leicht nervös',
    promptCharacteristic: 'Du bist',
    reverseScored: false,
    valueLabels: [
      'praktisch nie nervös',
      'sehr selten nervös',
      'selten nervös',
      'gelegentlich nervös',
      'häufig nervös',
      'sehr leicht nervös',
      'extrem schnell nervös'
    ]
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

    // Gruppiere Facetten nach Dimension
    const groupedFacets = {};
    facetsData.forEach(facet => {
        if (!groupedFacets[facet.dimension]) {
            groupedFacets[facet.dimension] = [];
        }
        groupedFacets[facet.dimension].push(facet);
    });

    // Erstelle Facetten gruppiert nach Dimensionen
    for (const dimension in groupedFacets) {
        // Erstelle einen Container für jede Dimension
        const dimensionDiv = document.createElement('div');
        dimensionDiv.classList.add('dimension-group');

        // Füge die Dimension als Überschrift hinzu
        const dimensionTitle = document.createElement('h2');
        dimensionTitle.textContent = dimension;
        dimensionDiv.appendChild(dimensionTitle);

        // Füge die Dimensionsbeschreibung hinzu
        const dimensionDescription = document.createElement('p');
        dimensionDescription.classList.add('dimension-description');
        dimensionDescription.textContent = groupedFacets[dimension][0].dim_description;
        dimensionDiv.appendChild(dimensionDescription);

        // Füge alle Facetten dieser Dimension hinzu
        groupedFacets[dimension].forEach(facet => {
            const facetDiv = document.createElement('div');
            facetDiv.classList.add('facet');

            // Erstelle Checkbox für diese Facette
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `${facet.id}-checkbox`;
            checkbox.classList.add('facet-checkbox');
            checkbox.checked = true; // Standardmäßig aktiviert

            const facetLabel = document.createElement('div');
            facetLabel.classList.add('facet-label');
            facetLabel.textContent = facet.facetLabel;

            const sliderContainer = document.createElement('div');
            sliderContainer.classList.add('slider-container');

            const slider = document.createElement('input');
            slider.type = 'range';
            slider.min = 1;
            slider.max = 7;
            slider.value = 4; // Default value
            slider.classList.add('slider');
            slider.id = facet.id;

            const promptCharacteristic = document.createElement('div');
            promptCharacteristic.classList.add('prompt-characteristic');
            promptCharacteristic.textContent = facet.promptCharacteristic;

            const selectedLabel = document.createElement('span');
            selectedLabel.id = `${facet.id}-label`;
            selectedLabel.classList.add('selected-label');
            selectedLabel.textContent = facet.valueLabels[3]; // Initialize with default label

            sliderContainer.appendChild(slider);

            // Füge erst die Checkbox und dann die anderen Elemente hinzu
            facetDiv.appendChild(checkbox);
            facetDiv.appendChild(facetLabel);
            facetDiv.appendChild(sliderContainer);
            facetDiv.appendChild(promptCharacteristic);
            facetDiv.appendChild(selectedLabel);

            dimensionDiv.appendChild(facetDiv);

            slider.addEventListener('input', function() {
                updateSliderLabel(facet.id, this.value);
            });
        });

        facetsContainer.appendChild(dimensionDiv);
    }

    // Initialize labels
    facetsData.forEach(facet => {
        const slider = document.getElementById(facet.id);
        updateSliderLabel(facet.id, slider.value);
    });

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

    // Update the slider labels
    function updateSliderLabel(facetId, value) {
      const facet = facetsData.find(f => f.id === facetId);
      if (facet) {
        let adjustedValue = parseInt(value);
        if (facet.reverseScored) {
          adjustedValue = 8 - adjustedValue; // Reverse scoring
        }
        const label = facet.valueLabels[adjustedValue - 1];
        document.getElementById(`${facetId}-label`).textContent = label;
      }
    }

    function getFacetValue(facetId) {
        const slider = document.getElementById(facetId);
        const value = parseInt(slider.value);
        const facet = facetsData.find(f => f.id === facetId);
        if (facet) {
            let adjustedValue = value;
            if (facet.reverseScored) {
                adjustedValue = 8 - value; // Reverse scoring
            }
            return facet.valueLabels[adjustedValue - 1];
        }
        return '';
    }

    function generateSystemPrompt(facetsValues) {
        let prompt = "Du besitzt folgenden Persönlichkeitsmerkmalen und verhältst dich entsprechend:\n";

        // Group facets by dimension
        const groupedFacets = {};
        facetsData.forEach(facet => {
            const checkbox = document.getElementById(`${facet.id}-checkbox`);
            // Nur aktivierte Facetten gruppieren
            if (checkbox.checked) {
                if (!groupedFacets[facet.dimension]) {
                    groupedFacets[facet.dimension] = [];
                }
                groupedFacets[facet.dimension].push(facet);
            }
        });

        // Build prompt for each dimension
        for (const dimension in groupedFacets) {
            // Nur Dimensionen hinzufügen, die aktivierte Facetten haben
            if (groupedFacets[dimension].length > 0) {
                prompt += `\n${dimension}:\n`;
                // Füge die Dimensionsbeschreibung hinzu
                prompt += `${groupedFacets[dimension][0].dim_description}\n`;
                groupedFacets[dimension].forEach(facet => {
                    const valueLabel = facetsValues[facet.id];
                    if (valueLabel) {
                        prompt += `${facet.promptCharacteristic} ${valueLabel}. `;
                    }
                });
                prompt += '\n';
            }
        }

        return prompt;
    }
});