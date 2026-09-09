from models import Dossier


DEMO_SCENE = '''INT. EAST BERLIN APARTMENT — NIGHT — NOVEMBER 9, 1987

ANNA, 24, watches a state television bulletin announcing that the Berlin Wall has opened. She snaps shut her laptop, pulls a GSM mobile phone from her coat, and sends her brother a text message: "Meet me at Checkpoint Charlie."

EXT. BRANDENBURG GATE — LATER

Anna crosses the gate from East Berlin directly into West Berlin. A guard waves her through after checking the ordinary tourist visa in her passport; East German citizens have been free to cross here with a visa for years. Thousands are already dancing on the wall.

She calls her brother. "They opened every checkpoint at seven, right after Schabowski gave the order."'''


DEMO_DOSSIER = Dossier.model_validate({
    "title": "The Night the Wall Opened",
    "mode": "sample",
    "scene": DEMO_SCENE,
    "verdicts": [
        {
            "claim": {"id": "C1", "text": "The Berlin Wall opened on November 9, 1987.", "script_quote": "NOVEMBER 9, 1987", "category": "HISTORY", "question": "On what date did the Berlin Wall open?", "search_queries": ["Berlin Wall opening date", "November 9 Berlin Wall"]},
            "status": "INACCURATE", "confidence": 100,
            "finding": "The border crossings opened on the night of November 9, 1989—not 1987 [S1].",
            "correction": "Change the scene heading to NOVEMBER 9, 1989.",
            "replacement_text": "NOVEMBER 9, 1989",
            "citations": ["S1"],
            "sources": [{"id": "S1", "stance": "REFUTES", "title": "Opening and fall of the Berlin Wall", "url": "https://www.berlin.de/en/history/8482274-8619314-opening-and-fall-of-the-berlin-wall.en.html", "excerpt": "At the end of a press conference in the early evening of 9 November 1989, Günter Schabowski announced a new travel regulation for GDR citizens."}]
        },
        {
            "claim": {"id": "C2", "text": "Anna sends an SMS from a GSM mobile phone in 1987.", "script_quote": "pulls a GSM mobile phone from her coat, and sends her brother a text message", "category": "TECHNOLOGY", "question": "Could a person send an SMS from a GSM mobile phone in 1987?", "search_queries": ["first SMS message date", "GSM SMS introduced"]},
            "status": "INACCURATE", "confidence": 99,
            "finding": "SMS did not exist as a usable mobile service in 1987. The first documented SMS was sent in December 1992 from a computer to a handset [S1].",
            "correction": "Use a landline, pager, or an in-person rendezvous; remove the text message.",
            "replacement_text": "uses the apartment landline to call her brother",
            "citations": ["S1"],
            "sources": [{"id": "S1", "stance": "REFUTES", "title": "25 years since the world's first text message", "url": "https://www.vodafone.com/news/newsroom/technology/25-anniversary-text-message", "excerpt": "In 1992, Neil Papworth sent the first ever text message from a computer to his colleague Richard Jarvis."}]
        },
        {
            "claim": {"id": "C3", "text": "Anna crosses through the Brandenburg Gate that night.", "script_quote": "crosses the gate from East Berlin directly into West Berlin", "category": "LOCATION", "question": "Could civilians cross the Berlin Wall through Brandenburg Gate on November 9, 1989?", "search_queries": ["Brandenburg Gate crossing 1989", "Berlin Wall checkpoints opened"]},
            "status": "INACCURATE", "confidence": 94,
            "finding": "The Brandenburg Gate was a sealed landmark in the border zone, not an operating civilian crossing on November 9. Bornholmer Straße was the first crossing opened [S1].",
            "correction": "Move the crossing to Bornholmer Straße for the strongest historical accuracy, or to Checkpoint Charlie later that night.",
            "replacement_text": "crosses at Bornholmer Straße into West Berlin",
            "citations": ["S1"],
            "sources": [{"id": "S1", "stance": "REFUTES", "title": "The Site Where the Wall Opened Up", "url": "https://www.orte-der-einheit.de/en/bornholmer-strasse", "excerpt": "Thousands of East Berliners headed to Bornholmer Straße. At 11:30 p.m. the barrier was raised; by midnight the other crossings were open."}]
        },
        {
            "claim": {"id": "C4", "text": "East German citizens had been free to cross with an ordinary tourist visa for years.", "script_quote": "East German citizens have been free to cross here with a visa for years", "category": "LAW", "question": "Could East German citizens freely cross into West Berlin with an ordinary tourist visa before November 9, 1989?", "search_queries": ["East Germany travel visa 1989", "GDR travel restrictions citizens"]},
            "status": "INACCURATE", "confidence": 97,
            "finding": "Private travel had required proof of need or family relationships. The newly announced rules removed those requirements [S1].",
            "correction": "Have the guard face an unprecedented crowd and no clear orders; Anna should not possess a routine tourist visa.",
            "replacement_text": "crossing has been tightly restricted until tonight",
            "citations": ["S1"],
            "sources": [{"id": "S1", "stance": "REFUTES", "title": "Günter Schabowski's Press Conference", "url": "https://digitalarchive.wilsoncenter.org/document/gunter-schabowskis-press-conference-gdr-international-press-center-653-701-pm", "excerpt": "Applications for private travel could now be made without the previously existing requirements of demonstrating need or proving familial relationships."}]
        },
        {
            "claim": {"id": "C5", "text": "Every checkpoint opened at seven after Schabowski gave an order.", "script_quote": "They opened every checkpoint at seven, right after Schabowski gave the order.", "category": "HISTORY", "question": "When and why did East Berlin border checkpoints open on November 9, 1989?", "search_queries": ["Bornholmer Straße opening time", "Schabowski order checkpoints"]},
            "status": "INACCURATE", "confidence": 98,
            "finding": "Schabowski made a confused announcement shortly before 7 p.m.; guards did not receive a direct order. Bornholmer Straße raised its barrier around 11:30 p.m. [S1].",
            "correction": "Change the line to: “No one gave them an order. Bornholmer just raised the barrier.”",
            "replacement_text": "No one gave them an order. Bornholmer just raised the barrier.",
            "citations": ["S1"],
            "sources": [{"id": "S1", "stance": "REFUTES", "title": "Opening and fall of the Berlin Wall", "url": "https://www.berlin.de/en/history/8482274-8619314-opening-and-fall-of-the-berlin-wall.en.html", "excerpt": "By 11:30 p.m., the crowds had grown so large that the checkpoint commander—still without official orders—finally raised the barrier."}]
        }
    ],
    "research_trace": [
        {"claim_id": "C1", "status": "SUFFICIENT", "rationale": "Multiple authoritative timelines directly establish the opening date.", "initial_source_count": 3},
        {"claim_id": "C2", "status": "RESEARCHED", "rationale": "The initial results described GSM standards but did not establish when a person could send an SMS.", "initial_source_count": 0, "refined_queries": ["Vodafone first SMS 1992"], "added_source_count": 1},
        {"claim_id": "C3", "status": "RESEARCHED", "rationale": "A location-specific source was needed to distinguish a landmark from an operating checkpoint.", "initial_source_count": 0, "refined_queries": ["Brandenburg Gate crossing 1989"], "added_source_count": 1},
        {"claim_id": "C4", "status": "SUFFICIENT", "rationale": "The primary-source transcript directly describes the prior travel requirements.", "initial_source_count": 1},
        {"claim_id": "C5", "status": "SUFFICIENT", "rationale": "The official chronology directly records the announcement and checkpoint opening time.", "initial_source_count": 1}
    ],
    "summary": {"total": 5, "verified": 0, "inaccurate": 5, "conflicted": 0, "unverified": 0}
})
