"""Deterministic product resolution.

Product identity is decided here, never by the language model. The model only
proposes a name; this module maps that name onto a real catalogue row, and
refuses to choose when the evidence does not separate the candidates.
"""
from dataclasses import dataclass
from difflib import SequenceMatcher

from app.models import Product

#: Below this, a candidate is not worth showing at all.
PLAUSIBLE = 0.34
#: Two candidates closer together than this are treated as indistinguishable.
AMBIGUITY_MARGIN = 0.12


@dataclass
class Candidate:
    product: Product
    score: float


@dataclass
class MatchResult:
    candidates: list[Candidate]
    ambiguous: bool

    @property
    def best(self) -> Candidate | None:
        return self.candidates[0] if self.candidates else None

    @property
    def score(self) -> float:
        return self.candidates[0].score if self.candidates else 0.0


def _score(guess: str, name: str) -> float:
    guess_l, name_l = guess.lower().strip(), name.lower().strip()
    if not guess_l:
        return 0.0
    if guess_l == name_l:
        return 1.0

    ratio = SequenceMatcher(None, guess_l, name_l).ratio()

    # Whole-word containment is strong evidence ("coke" -> "Coca Cola 500ml").
    if guess_l in name_l or name_l in guess_l:
        ratio = max(ratio, 0.88)

    # Reward shared words so "sunflower oil" beats "sunflower seeds" on overlap.
    guess_words = set(guess_l.split())
    name_words = set(name_l.split())
    if guess_words and name_words:
        overlap = len(guess_words & name_words) / len(guess_words)
        ratio = max(ratio, overlap * 0.92)

    return round(ratio, 3)


def match_product(guess: str, products: list[Product], limit: int = 4) -> MatchResult:
    scored = [Candidate(p, _score(guess, p.name)) for p in products]
    scored = [c for c in scored if c.score >= PLAUSIBLE]
    scored.sort(key=lambda c: c.score, reverse=True)
    scored = scored[:limit]

    ambiguous = (
        len(scored) >= 2
        and scored[0].score < 0.97
        and (scored[0].score - scored[1].score) < AMBIGUITY_MARGIN
    )
    return MatchResult(candidates=scored, ambiguous=ambiguous)
