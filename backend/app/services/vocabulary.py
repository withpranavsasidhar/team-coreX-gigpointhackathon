"""Configurable business vocabulary for the language layer.

Data, not logic — new languages and shop dialects are added by editing these
maps, never by touching the extraction code or the UI.

Each language contributes terms in two forms:
  * native script  — what browser speech recognition returns for te-IN / hi-IN
  * romanised      — what people actually type, and what mixed speech looks like
                     ("Rendu cartons Coke vachayi")

Both forms map onto the same canonical English concept, because the goal is
business meaning, not translation.
"""

TELUGU = "te"
HINDI = "hi"
ENGLISH = "en"

# --- Intent markers -------------------------------------------------------
# event_type -> language -> phrases
INTENT_VOCABULARY: dict[str, dict[str, list[str]]] = {
    "CREDIT_SALE": {
        ENGLISH: ["on credit", "will pay", "pay later", "pay tomorrow", "pay next", "owes", "owe", "credit", "udhar"],
        TELUGU: ["అప్పు", "తరువాత ఇస్తాను", "రేపు ఇస్తాను", "బాకీ", "appu", "baki", "repu istanu", "tarvata istanu"],
        HINDI: ["उधार", "बाद में दूंगा", "कल दूंगा", "बाकी", "udhaar", "baad mein", "kal denge", "kal dunga"],
    },
    "DAMAGE": {
        ENGLISH: ["damaged", "damage", "broken", "break", "spoiled", "spoilt", "expired", "leaked"],
        TELUGU: ["పాడైంది", "పాడైపోయింది", "పగిలింది", "చెడిపోయింది", "padaindi", "padipoyindi", "pagilindi", "chedipoyindi"],
        HINDI: ["खराब", "टूट गया", "टूटा", "खराब हो गया", "kharab", "toot gaya", "tuta"],
    },
    "LOSS": {
        ENGLISH: ["lost", "missing", "stolen", "theft"],
        TELUGU: ["పోయింది", "తప్పిపోయింది", "poyindi", "tappipoyindi"],
        HINDI: ["खो गया", "गायब", "kho gaya", "gayab"],
    },
    "RETURN": {
        ENGLISH: ["returned", "return", "sent back", "came back"],
        TELUGU: ["వాపసు", "తిరిగి వచ్చింది", "vapasu", "tirigi vachindi"],
        HINDI: ["वापस", "लौटा", "wapas", "lauta"],
    },
    "PURCHASE": {
        ENGLISH: ["bought", "purchased", "purchase"],
        TELUGU: ["కొన్నాను", "కొన్నాము", "konnanu", "konnamu"],
        HINDI: ["खरीदा", "खरीद लिया", "kharida", "khareeda"],
    },
    "STOCK_IN": {
        ENGLISH: [
            "received", "receive", "came in", "came", "arrived", "arrive",
            "delivered", "delivery", "add", "added", "stock in", "got",
        ],
        TELUGU: [
            "వచ్చాయి", "వచ్చింది", "వచ్చాడు", "చేర్చు", "చేర్చండి", "కలుపు", "తెచ్చారు",
            "vachayi", "vachaayi", "vachindi", "vachchayi", "cherchu", "cheyyi", "kalupu", "techaru",
        ],
        HINDI: ["आया", "आ गया", "आई", "मिला", "जोड़ो", "डालो", "aaya", "aa gaya", "aayi", "mila", "jodo", "dalo"],
    },
    "SALE": {
        ENGLISH: ["sold", "sell", "sale"],
        TELUGU: ["అమ్మాను", "అమ్మేశాను", "అమ్మాము", "అయ్యాయి", "ammanu", "ammesanu", "ammamu", "ayyayi", "ammaru"],
        HINDI: ["बेचा", "बेच दिया", "बिक गया", "becha", "bech diya", "bik gaya"],
    },
    "STOCK_OUT": {
        ENGLISH: ["take out", "took out", "remove", "removed", "issued", "gave", "give", "took"],
        TELUGU: ["తీసుకున్నాడు", "తీసుకెళ్లాడు", "తీసుకున్నారు", "తీసేయ్", "teesukunnadu", "teesukellaadu", "teesukunnaru", "teesey"],
        HINDI: ["ले गया", "लिया", "निकालो", "हटाओ", "le gaya", "liya", "nikalo", "hatao"],
    },
    "ADJUSTMENT": {
        ENGLISH: ["adjust", "adjusted", "correction", "correct to", "set to"],
        TELUGU: ["సరిచేయి", "sarichey"],
        HINDI: ["सुधारो", "ठीक करो", "sudharo", "theek karo"],
    },
}

# --- Units ----------------------------------------------------------------
UNIT_VOCABULARY: dict[str, list[str]] = {
    # "packet" now resolves to its own unit rather than collapsing into pieces,
    # so a bakery's packets and a kirana's loose pieces stay distinguishable.
    "pieces": [
        "piece", "pieces", "pcs", "pc", "pack", "packs",
        "unit", "units", "nos", "ముక్కలు", "नग", "pudi",
    ],
    "kg": ["kg", "kgs", "kilo", "kilos", "kilogram", "kilograms", "కిలో", "కిలోలు", "kilolu", "किलो"],
    "litres": ["litre", "litres", "liter", "liters", "ltr", "లీటర్", "లీటర్లు", "literlu", "लीटर"],
    "bags": ["bag", "bags", "బస్తా", "బస్తాలు", "basta", "bastalu", "बोरी", "बोरा", "bori", "sanchi"],
    "cartons": ["carton", "cartons", "కార్టన్", "కార్టన్లు", "cartonlu", "कार्टन"],
    "boxes": ["box", "boxes", "బాక్స్", "బాక్సులు", "boxulu", "डिब्बा", "डिब्बे", "dabba", "dibba"],
    "dozens": ["dozen", "dozens", "డజను", "డజన్లు", "dajanu", "दर्जन", "darjan"],
    "quintals": ["quintal", "quintals", "క్వింటాల్", "क्विंटल"],
    "grams": ["gram", "grams", "gm", "gms", "గ్రాము", "గ్రాములు", "ग्राम"],
    "ml": ["ml", "millilitre", "millilitres", "milliliter", "milliliters", "మిల్లీ"],
    "packets": [
        "packet", "packets", "pkt", "pkts", "sachet", "sachets",
        "ప్యాకెట్", "ప్యాకెట్లు", "packetlu", "पैकेट",
    ],
    "crates": ["crate", "crates", "క్రేట్", "क्रेट", "kreta"],
    "trays": ["tray", "trays", "ట్రే", "ट्रे"],
    "meters": ["meter", "meters", "metre", "metres", "mtr", "mtrs", "మీటర్", "मीटर"],
    "rolls": ["roll", "rolls", "bundle", "bundles", "రోల్", "रोल"],
    "pairs": ["pair", "pairs", "జత", "जोड़ी", "jodi"],
    "sets": ["set", "sets", "సెట్", "सेट"],
    "bunches": ["bunch", "bunches", "కట్ట", "కట్టలు", "katta", "गुच्छा", "guccha"],
    "reams": ["ream", "reams", "రీమ్", "रीम"],
}

# --- Numbers --------------------------------------------------------------
NUMBER_WORDS: dict[str, float] = {
    # English
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "hundred": 100, "half": 0.5,
    # Telugu — romanised
    "okati": 1, "okka": 1, "rendu": 2, "mudu": 3, "moodu": 3, "nalugu": 4,
    "aidu": 5, "ayidu": 5, "aaru": 6, "edu": 7, "enimidi": 8, "tommidi": 9,
    "padi": 10, "padihenu": 15, "iravai": 20, "muppai": 30, "vanda": 100,
    # Telugu — script
    "ఒకటి": 1, "ఒక": 1, "రెండు": 2, "మూడు": 3, "నాలుగు": 4, "అయిదు": 5,
    "ఐదు": 5, "ఆరు": 6, "ఏడు": 7, "ఎనిమిది": 8, "తొమ్మిది": 9, "పది": 10,
    "పదిహేను": 15, "ఇరవై": 20, "ముప్పై": 30, "వంద": 100,
    # Hindi — romanised
    "ek": 1, "do": 2, "teen": 3, "char": 4, "chaar": 4, "paanch": 5, "panch": 5,
    "cheh": 6, "chhe": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10,
    "pandrah": 15, "bees": 20, "tees": 30, "sau": 100,
    # Hindi — script
    "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5, "पाँच": 5, "छह": 6,
    "सात": 7, "आठ": 8, "नौ": 9, "दस": 10, "पंद्रह": 15, "बीस": 20, "सौ": 100,
}

# --- Temporal -------------------------------------------------------------
# phrase -> day offset from today
TEMPORAL_HINTS: dict[str, int] = {
    "today": 0, "tonight": 0, "this morning": 0, "this evening": 0,
    "yesterday": -1, "tomorrow": 1, "next week": 7,
    # Telugu
    "ఈరోజు": 0, "ఈ రోజు": 0, "ivala": 0, "ee roju": 0,
    "నిన్న": -1, "ninna": -1,
    "రేపు": 1, "repu": 1, "reepu": 1,
    # Hindi — "kal" is both yesterday and tomorrow; in a payment promise it
    # always means tomorrow, which is the only context we use it in.
    "आज": 0, "aaj": 0,
    "कल": 1, "kal": 1,
    "परसों": 2, "parson": 2,
}

# Words that never form part of a product name.
STOPWORDS: set[str] = {
    # English
    "i", "we", "he", "she", "they", "the", "a", "an", "of", "to", "and", "is",
    "was", "were", "has", "have", "had", "this", "that", "these", "those",
    "today", "yesterday", "tomorrow", "morning", "evening", "afternoon",
    "night", "now", "just", "please", "some", "my", "our", "his", "her",
    "will", "shall", "for", "from", "in", "on", "at", "by", "with", "it",
    "rupees", "rs", "price", "each", "total", "worth", "there", "here",
    # Telugu function words
    "ఈ", "ఆ", "నేను", "మేము", "అతను", "కి", "కు", "లో", "ని", "నా",
    "naku", "nenu", "memu", "atanu", "ki", "ku", "lo",
    # Hindi function words
    "मैं", "हम", "वह", "को", "में", "से", "का", "की", "के", "ने", "है", "हैं",
    "main", "hum", "woh", "ko", "mein", "se", "ka", "ki", "ke", "ne", "hai",
}

# --- Product word mapping -------------------------------------------------
# Everyday goods named in a regional language, mapped to the English word the
# catalogue is likely to use. Brand names ("Coke", "Maggi") stay in Latin even
# in regional speech, so they need no entry here.
PRODUCT_ALIASES: dict[str, str] = {
    # Telugu — script then romanised
    "బియ్యం": "rice", "biyyam": "rice", "బియ్యo": "rice",
    "గోధుమ": "wheat", "godhuma": "wheat", "godhumalu": "wheat",
    "నూనె": "oil", "nune": "oil", "noone": "oil",
    "పాలు": "milk", "palu": "milk", "paalu": "milk",
    "గుడ్లు": "eggs", "gudlu": "eggs", "kodi gudlu": "eggs",
    "బిస్కెట్": "biscuits", "బిస్కెట్లు": "biscuits", "biskettu": "biscuits",
    "చక్కెర": "sugar", "పంచదార": "sugar", "chakkera": "sugar",
    # Hindi — script then romanised
    "चावल": "rice", "chawal": "rice", "chaval": "rice",
    "गेहूं": "wheat", "gehun": "wheat", "gehu": "wheat",
    "तेल": "oil", "tel": "oil", "tail": "oil",
    "दूध": "milk", "doodh": "milk", "dudh": "milk",
    "अंडे": "eggs", "ande": "eggs", "anda": "eggs",
    "बिस्कुट": "biscuits", "biskut": "biscuits",
    "चीनी": "sugar", "cheeni": "sugar", "chini": "sugar",
}


# --- Responses ------------------------------------------------------------
# Simple, plain confirmations in the owner's chosen language. Units stay as
# spoken (shopkeepers say "cartons" in every language).
RESPONSE_TEMPLATES: dict[str, dict[str, str]] = {
    ENGLISH: {
        "STOCK_IN": "{qty} {unit} of {product} added",
        "PURCHASE": "{qty} {unit} of {product} purchased",
        "RETURN": "{qty} {unit} of {product} returned",
        "SALE": "{qty} {unit} of {product} sold",
        "STOCK_OUT": "{qty} {unit} of {product} taken out",
        "CREDIT_SALE": "{qty} {unit} of {product} given to {customer} on credit",
        "DAMAGE": "{qty} {unit} of {product} marked damaged",
        "LOSS": "{qty} {unit} of {product} marked lost",
        "ADJUSTMENT": "{product} adjusted by {qty} {unit}",
    },
    TELUGU: {
        "STOCK_IN": "{qty} {unit} {product} చేర్చాము",
        "PURCHASE": "{qty} {unit} {product} కొన్నాము",
        "RETURN": "{qty} {unit} {product} వాపసు వచ్చింది",
        "SALE": "{qty} {unit} {product} అమ్మాము",
        "STOCK_OUT": "{qty} {unit} {product} తీసేశాము",
        "CREDIT_SALE": "{qty} {unit} {product} {customer} గారికి అప్పుగా ఇచ్చాము",
        "DAMAGE": "{qty} {unit} {product} పాడైనట్టు నమోదు చేశాము",
        "LOSS": "{qty} {unit} {product} పోయినట్టు నమోదు చేశాము",
        "ADJUSTMENT": "{product} {qty} {unit} సరిచేశాము",
    },
    HINDI: {
        "STOCK_IN": "{qty} {unit} {product} जोड़ दिया",
        "PURCHASE": "{qty} {unit} {product} खरीदा",
        "RETURN": "{qty} {unit} {product} वापस आया",
        "SALE": "{qty} {unit} {product} बेचा",
        "STOCK_OUT": "{qty} {unit} {product} निकाला",
        "CREDIT_SALE": "{qty} {unit} {product} {customer} को उधार दिया",
        "DAMAGE": "{qty} {unit} {product} खराब दर्ज किया",
        "LOSS": "{qty} {unit} {product} खोया दर्ज किया",
        "ADJUSTMENT": "{product} {qty} {unit} सुधारा",
    },
}

# Prompts the clarification/confirmation flow shows, per language.
UI_PHRASES: dict[str, dict[str, str]] = {
    ENGLISH: {
        "which_product": "More than one product matches. Which did you mean?",
        "which_product_missing": "Which product was that?",
        "how_many": "How many? I couldn't hear a quantity.",
        "who_credit": "Who took it on credit?",
        "confirm": "Please confirm this is right.",
        "unsure": "I'm not sure I understood. Please check the details.",
        "no_match": 'No product matching "{guess}" is in your catalogue.',
        "no_speech": "I didn't catch anything. Try speaking again.",
        "no_products": "No products yet. Add a product before recording movements.",
    },
    TELUGU: {
        "which_product": "ఒకటి కంటే ఎక్కువ సరుకులు సరిపోయాయి. ఏది?",
        "which_product_missing": "ఏ సరుకు?",
        "how_many": "ఎన్ని? పరిమాణం వినిపించలేదు.",
        "who_credit": "ఎవరు అప్పుగా తీసుకున్నారు?",
        "confirm": "ఇది సరైనదో నిర్ధారించండి.",
        "unsure": "నాకు సరిగ్గా అర్థం కాలేదు. వివరాలు చూడండి.",
        "no_match": '"{guess}" అనే సరుకు మీ జాబితాలో లేదు.',
        "no_speech": "ఏమీ వినిపించలేదు. మళ్లీ చెప్పండి.",
        "no_products": "ఇంకా సరుకులు లేవు. ముందు ఒక సరుకు చేర్చండి.",
    },
    HINDI: {
        "which_product": "एक से ज़्यादा सामान मिले। आपका मतलब कौन सा था?",
        "which_product_missing": "कौन सा सामान?",
        "how_many": "कितने? मात्रा सुनाई नहीं दी।",
        "who_credit": "किसने उधार लिया?",
        "confirm": "कृपया पुष्टि करें कि यह सही है।",
        "unsure": "मुझे ठीक से समझ नहीं आया। विवरण देखें।",
        "no_match": '"{guess}" नाम का सामान आपकी सूची में नहीं है।',
        "no_speech": "कुछ सुनाई नहीं दिया। दोबारा बोलें।",
        "no_products": "अभी कोई सामान नहीं है। पहले एक सामान जोड़ें।",
    },
}

SUPPORTED_LANGUAGES = [ENGLISH, TELUGU, HINDI]


def canonical_unit(word: str) -> str | None:
    lowered = word.lower().strip(".,")
    for unit, synonyms in UNIT_VOCABULARY.items():
        if lowered in synonyms:
            return unit
    return None


def flat_intent_phrases() -> list[tuple[str, str, str]]:
    """Every (event_type, language, phrase) triple, longest phrases first."""
    triples = [
        (event_type, language, phrase)
        for event_type, by_language in INTENT_VOCABULARY.items()
        for language, phrases in by_language.items()
        for phrase in phrases
    ]
    return sorted(triples, key=lambda t: len(t[2]), reverse=True)


def phrase_for(language: str, key: str, **kwargs) -> str:
    table = UI_PHRASES.get(language) or UI_PHRASES[ENGLISH]
    template = table.get(key) or UI_PHRASES[ENGLISH][key]
    return template.format(**kwargs) if kwargs else template


def describe(language: str, event_type: str, qty, unit: str, product: str, customer: str | None) -> str:
    table = RESPONSE_TEMPLATES.get(language) or RESPONSE_TEMPLATES[ENGLISH]
    template = table.get(event_type) or RESPONSE_TEMPLATES[ENGLISH].get(event_type, "{product}")
    quantity = f"{qty:g}" if isinstance(qty, (int, float)) else str(qty or "")
    return " ".join(
        template.format(
            qty=quantity, unit=unit or "", product=product, customer=customer or ""
        ).split()
    )
