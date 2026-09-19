"""Deterministic extraction used when no LLM key is configured.

Thin wrapper over the shared language layer (app/services/language.py), so it
understands English, Telugu, Hindi and mixed speech through exactly the same
vocabulary the LLM prompt is grounded with. It reports honestly lower
confidence than the LLM provider, so uncertain input still routes to
confirmation or clarification rather than being executed silently.
"""
from app.providers.ai.base import AIExtractionProvider, ExtractedEvent
from app.services import language
from app.services.vocabulary import describe

CONFIDENCE_CAP = 0.9

# Outgoing events that become credit when a named person is involved.
_OUTGOING = {"SALE", "STOCK_OUT"}
_CREDIT_MARKERS = ("pay", "credit", "owes", "udhar", "udhaar", "later",
                   "అప్పు", "బాకీ", "istanu", "उधार", "denge", "dunga", "baad")


class RuleBasedExtractionProvider(AIExtractionProvider):
    name = "rule_based"

    def extract_event(self, text: str, known_products: list[str]) -> ExtractedEvent:
        analysis = language.analyse(text, known_products)
        notes: list[str] = []
        confidence = 0.5

        product_guess, matched_known = self._resolve_product(analysis, known_products)
        event_type = analysis.intent

        if event_type:
            confidence += 0.2
        else:
            event_type = "SALE" if analysis.customer else "STOCK_IN"
            notes.append("No clear action word — assumed a default.")
            confidence -= 0.15

        if analysis.customer and event_type in _OUTGOING:
            if any(marker in text.lower() for marker in _CREDIT_MARKERS):
                event_type = "CREDIT_SALE"

        if analysis.quantity is not None:
            confidence += 0.2
        else:
            notes.append("No quantity detected.")
            confidence -= 0.2

        if analysis.unit:
            confidence += 0.1
        if matched_known:
            confidence += 0.1
        else:
            notes.append("Product name did not match the catalogue directly.")
            confidence -= 0.2

        payment_status = (
            "CREDIT" if event_type == "CREDIT_SALE"
            else "PAID" if event_type in ("SALE", "PURCHASE")
            else "NA"
        )

        return ExtractedEvent(
            event_type=event_type,
            product_guess=product_guess,
            quantity=analysis.quantity,
            unit=analysis.unit,
            price=analysis.price,
            customer=analysis.customer,
            payment_status=payment_status,
            due_date=analysis.due_date if event_type == "CREDIT_SALE" else None,
            confidence=round(max(0.05, min(confidence, CONFIDENCE_CAP)), 2),
            normalized_text=describe(
                "en", event_type, analysis.quantity, analysis.unit or "",
                product_guess, analysis.customer,
            ),
            detected_language=analysis.detected_language,
            provider=self.name,
            notes=notes,
        )

    @staticmethod
    def _resolve_product(analysis: language.LanguageAnalysis,
                         known_products: list[str]) -> tuple[str, bool]:
        """Prefer a catalogue name appearing verbatim, else the leftover words."""
        haystack = f"{analysis.original.lower()} {' '.join(analysis.product_tokens)}"
        best = ""
        for name in known_products:
            if name.lower() in haystack and len(name) > len(best):
                best = name
        if best:
            return best, True
        return " ".join(analysis.product_tokens[:3]).strip(), False

    def answer_question(self, question: str, facts: dict, language: str = "en") -> str:
        # Phase 8 supplies the templated fallback; unused here.
        return ""
