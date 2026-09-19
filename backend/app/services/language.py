"""Reusable language-processing layer.

Handles detection, mixed-language normalisation and entity spotting for every
supported language, so extraction providers and prompts share one
implementation rather than each re-deriving it.

The aim is business meaning, not translation: "Rendu cartons Coke vachayi" and
"I received two cartons of Coke" must produce the same structured event.
"""
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, timedelta

from app.services.vocabulary import (
    ENGLISH, HINDI, NUMBER_WORDS, PRODUCT_ALIASES, STOPWORDS,
    SUPPORTED_LANGUAGES, TELUGU, TEMPORAL_HINTS, canonical_unit,
    flat_intent_phrases,
)

TELUGU_RANGE = (0x0C00, 0x0C7F)
DEVANAGARI_RANGE = (0x0900, 0x097F)

# Indic vowel signs are combining marks, which Python's \w excludes. Matching
# on letters alone shatters "నాలుగు" into "న ల గ", so the Telugu and Devanagari
# blocks are admitted explicitly to keep each word intact.
_INDIC = r"ऀ-ॿఀ-౿"
TOKEN_RE = re.compile(rf"\d+\.?\d*|(?:[^\W\d_]|[{_INDIC}])+", re.UNICODE)

# Words from any language that are never part of a product name.
_INTENT_WORDS: set[str] = {
    word.lower()
    for _, _, phrase in flat_intent_phrases()
    for word in phrase.split()
}
_TEMPORAL_WORDS: set[str] = {w for phrase in TEMPORAL_HINTS for w in phrase.split()}


def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def _script_counts(text: str) -> tuple[int, int, int]:
    telugu = devanagari = latin = 0
    for ch in text:
        code = ord(ch)
        if TELUGU_RANGE[0] <= code <= TELUGU_RANGE[1]:
            telugu += 1
        elif DEVANAGARI_RANGE[0] <= code <= DEVANAGARI_RANGE[1]:
            devanagari += 1
        elif ch.isalpha() and "LATIN" in unicodedata.name(ch, ""):
            latin += 1
    return telugu, devanagari, latin


def _romanised_hits(text: str) -> dict[str, int]:
    """Count romanised regional terms, for speech typed in Latin script."""
    found = {TELUGU: 0, HINDI: 0}
    word_set = set(tokens(text))

    for _, language, phrase in flat_intent_phrases():
        if language in found and phrase.isascii() and phrase in text.lower():
            found[language] += 1

    for word in word_set:
        if not word.isascii():
            continue
        # Regional number words are a strong signal ("rendu", "do", "nalugu").
        if word in NUMBER_WORDS and word not in {
            "a", "an", "one", "two", "three", "four", "five", "six", "seven",
            "eight", "nine", "ten", "eleven", "twelve", "fifteen", "twenty",
            "thirty", "forty", "fifty", "hundred", "half",
        }:
            if word in {"okati", "okka", "rendu", "mudu", "moodu", "nalugu", "aidu",
                        "ayidu", "aaru", "edu", "enimidi", "tommidi", "padi",
                        "padihenu", "iravai", "muppai", "vanda"}:
                found[TELUGU] += 1
            else:
                found[HINDI] += 1
    return found


def detect_language(text: str) -> str:
    """Returns en | te | hi | te-en | hi-en."""
    telugu, devanagari, latin = _script_counts(text)

    if telugu and latin:
        return "te-en"
    if telugu:
        return TELUGU
    if devanagari and latin:
        return "hi-en"
    if devanagari:
        return HINDI

    hits = _romanised_hits(text)
    if hits[TELUGU] and hits[TELUGU] >= hits[HINDI]:
        return "te-en"
    if hits[HINDI]:
        return "hi-en"
    return ENGLISH


def primary_language(detected: str) -> str:
    """The language to reply in, given a possibly-mixed detection."""
    base = detected.split("-")[0]
    return base if base in SUPPORTED_LANGUAGES else ENGLISH


def detect_intent(text: str) -> tuple[str | None, str | None]:
    """Longest matching phrase across all languages wins."""
    lowered = text.lower()
    for event_type, _, phrase in flat_intent_phrases():
        if phrase.isascii():
            # Word boundaries matter: "oil" must not match inside "spoiled".
            if re.search(rf"(?<![a-z]){re.escape(phrase)}(?![a-z])", lowered):
                return event_type, phrase
        elif phrase in lowered:
            return event_type, phrase
    return None, None


def extract_quantity(text: str) -> float | None:
    digits = re.search(r"(\d+\.?\d*)", text)
    if digits:
        return float(digits.group(1))

    total: float | None = None
    for token in tokens(text):
        if token in NUMBER_WORDS:
            value = NUMBER_WORDS[token]
            total = value if total is None else (total + value if value < 10 else total * value)
    return total


def extract_unit(text: str) -> str | None:
    for token in tokens(text):
        unit = canonical_unit(token)
        if unit:
            return unit
    return None


def extract_price(text: str) -> float | None:
    for pattern in (
        r"(?:rs\.?|rupees?|₹|రూ|रु)\s*(\d+\.?\d*)",
        r"(\d+\.?\d*)\s*(?:rs\.?|rupees?|రూపాయలు|रुपये)",
    ):
        match = re.search(pattern, text, re.I)
        if match:
            return float(match.group(1))
    return None


def extract_due_date(text: str) -> date | None:
    lowered = text.lower()
    best: int | None = None
    for phrase, offset in TEMPORAL_HINTS.items():
        if phrase in lowered and offset > 0 and (best is None or offset < best):
            best = offset
    return date.today() + timedelta(days=best) if best else None


def extract_customer(text: str, known_products: list[str]) -> str | None:
    """A person's name: a capitalised Latin word that is nothing else we know.

    Kept language-agnostic on purpose — names stay in Latin script even when
    the surrounding sentence is Telugu or Hindi.
    """
    product_words = {w.lower() for name in known_products for w in name.split()}
    first_token = (tokens(text) or [""])[0]

    for word in re.findall(r"\b([A-Z][a-z]{2,})\b", text):
        lowered = word.lower()
        if (
            lowered in product_words
            or lowered in STOPWORDS
            or lowered in _INTENT_WORDS
            or lowered in _TEMPORAL_WORDS
            or lowered in NUMBER_WORDS
            or canonical_unit(lowered)
        ):
            continue
        # A capitalised first word is usually just sentence case ("Sold ...").
        if lowered == first_token and lowered in _INTENT_WORDS:
            continue
        return word
    return None


def product_tokens(text: str, customer: str | None = None) -> list[str]:
    """Content words left once numbers, units, verbs and filler are removed.

    Regional words for everyday goods are mapped to the English term the
    catalogue uses, so "బియ్యం" and "chawal" both reach the Rice row.
    """
    ignored = set(_INTENT_WORDS) | _TEMPORAL_WORDS | STOPWORDS
    if customer:
        ignored.update(customer.lower().split())

    kept = [
        t for t in tokens(text)
        if t not in ignored
        and t not in NUMBER_WORDS
        and not t.replace(".", "").isdigit()
        and canonical_unit(t) is None
    ]
    return [PRODUCT_ALIASES.get(t, t) for t in kept]


@dataclass
class LanguageAnalysis:
    original: str
    detected_language: str
    reply_language: str
    intent: str | None
    intent_phrase: str | None
    quantity: float | None
    unit: str | None
    price: float | None
    customer: str | None
    due_date: date | None
    product_tokens: list[str] = field(default_factory=list)


def analyse(text: str, known_products: list[str]) -> LanguageAnalysis:
    """One pass over a transcript, shared by every extraction provider."""
    detected = detect_language(text)
    intent, phrase = detect_intent(text)
    customer = extract_customer(text, known_products)

    return LanguageAnalysis(
        original=text,
        detected_language=detected,
        reply_language=primary_language(detected),
        intent=intent,
        intent_phrase=phrase,
        quantity=extract_quantity(text),
        unit=extract_unit(text),
        price=extract_price(text),
        customer=customer,
        due_date=extract_due_date(text),
        product_tokens=product_tokens(text, customer),
    )
