import json
from datetime import date, datetime

import anthropic

from app.config import settings
from app.core.exceptions import AIProviderError
from app.providers.ai.base import AIExtractionProvider, ExtractedEvent

EXTRACT_TOOL = {
    "name": "record_business_event",
    "description": "Extract the structured inventory event described by a shopkeeper's sentence.",
    "input_schema": {
        "type": "object",
        "properties": {
            "event_type": {
                "type": "string",
                "enum": [
                    "STOCK_IN", "PURCHASE", "RETURN", "SALE", "STOCK_OUT",
                    "CREDIT_SALE", "DAMAGE", "LOSS", "ADJUSTMENT",
                ],
            },
            "product": {
                "type": "string",
                "description": "Product name as understood, normalised to plain English. Prefer an exact name from the shop's catalogue when the speaker clearly means it.",
            },
            "quantity": {"type": "number"},
            "unit": {
                "type": "string",
                "enum": ["pieces", "kg", "litres", "bags", "cartons", "boxes", "dozens", "quintals"],
            },
            "price": {"type": "number", "description": "Total rupee amount if stated, else 0."},
            "customer": {"type": "string", "description": "Person's name for credit sales, else empty string."},
            "payment_status": {"type": "string", "enum": ["PAID", "CREDIT", "NA"]},
            "due_date": {"type": "string", "description": "ISO date (YYYY-MM-DD) if a payment date is implied, else empty string."},
            "detected_language": {
                "type": "string",
                "description": "Language of the sentence: en, te, hi, or a mix such as 'te-en'.",
            },
            "normalized_text": {
                "type": "string",
                "description": "One short plain-English restatement, e.g. 'Received 2 cartons of Coke'.",
            },
            "confidence": {
                "type": "number",
                "description": "0 to 1. Lower it honestly when the product, quantity or intent is unclear.",
            },
        },
        "required": ["event_type", "product", "confidence", "normalized_text"],
    },
}

SYSTEM_PROMPT = """You are the language-understanding layer of ARIA, a voice-first inventory \
system for small Indian shops.

Shopkeepers speak naturally and often mix a regional language (Telugu, Hindi) with English \
product names — for example "Rendu cartons Coke vachayi" means two cartons of Coke were received.

Extract the underlying business event. Rules:
- You only propose. You never decide what is in stock.
- Never invent a quantity that was not said. If it is missing, omit it and lower confidence.
- Prefer a product name from the shop's catalogue when the speaker clearly means one of them.
- If the sentence could mean several different products, lower confidence rather than picking one.
- A named person plus "will pay"/"later"/"credit" means CREDIT_SALE.
- Always call record_business_event exactly once."""


class AnthropicExtractionProvider(AIExtractionProvider):
    name = "anthropic"

    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    @property
    def is_llm(self) -> bool:
        return True

    def extract_event(self, text: str, known_products: list[str]) -> ExtractedEvent:
        catalogue = ", ".join(known_products) if known_products else "(no products yet)"
        try:
            response = self._client.messages.create(
                model=settings.nlu_model,
                max_tokens=600,
                system=f"{SYSTEM_PROMPT}\n\nThe shop's catalogue: {catalogue}.\nToday is {date.today().isoformat()}.",
                tools=[EXTRACT_TOOL],
                tool_choice={"type": "tool", "name": EXTRACT_TOOL["name"]},
                messages=[{"role": "user", "content": text}],
            )
        except Exception as exc:  # noqa: BLE001 — provider failures surface as a typed domain error
            raise AIProviderError(f"Language understanding failed: {exc}") from exc

        payload = next(
            (b.input for b in response.content if b.type == "tool_use" and b.name == EXTRACT_TOOL["name"]),
            None,
        )
        if payload is None:
            raise AIProviderError("The language model did not return a structured event.")

        return ExtractedEvent(
            event_type=payload.get("event_type", "STOCK_IN"),
            product_guess=payload.get("product", "") or "",
            quantity=payload.get("quantity"),
            unit=payload.get("unit") or None,
            price=(payload.get("price") or None),
            customer=(payload.get("customer") or None),
            payment_status=payload.get("payment_status", "NA"),
            due_date=_parse_date(payload.get("due_date")),
            confidence=float(payload.get("confidence", 0)),
            normalized_text=payload.get("normalized_text", ""),
            detected_language=payload.get("detected_language", "en"),
            provider=self.name,
        )

    def answer_question(self, question: str, facts: dict, language: str = "en") -> str:
        try:
            response = self._client.messages.create(
                model=settings.nlu_model,
                max_tokens=400,
                system=(
                    "You are ARIA, a business memory assistant for a small shop owner. "
                    "You are given pre-computed facts from the shop's ledger as JSON. "
                    "Answer using ONLY those facts — never invent or recompute a number. "
                    "Reply in 2-4 short, plain sentences."
                ),
                messages=[
                    {
                        "role": "user",
                        "content": f"Question: {question}\n\nFacts:\n{json.dumps(facts, default=str, indent=2)}",
                    }
                ],
            )
        except Exception as exc:  # noqa: BLE001
            raise AIProviderError(f"Could not generate an answer: {exc}") from exc

        return "".join(b.text for b in response.content if b.type == "text").strip()


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None
