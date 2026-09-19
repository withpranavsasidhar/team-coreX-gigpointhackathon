"""Voice pipeline orchestration and the confidence policy.

Sequence: transcript -> language detection -> understanding -> product
resolution -> confidence check -> (execute | confirm | clarify). The AI
proposes; this module and the Business Event Engine decide whether anything is
written.

Replies come back in the owner's chosen language. The ledger always stores the
English restatement, so history and search stay language-neutral.
"""
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Business, EventType, PaymentStatus, Product
from app.providers.ai import get_ai_provider
from app.services import conversation, inventory_service
from app.services.event_engine import record_event
from app.services.language import detect_language, primary_language
from app.services.product_matcher import match_product
from app.services.vocabulary import SUPPORTED_LANGUAGES, describe, phrase_for

RECORDED = "recorded"
AMENDED = "amended"
NEEDS_CONFIRMATION = "needs_confirmation"
NEEDS_CLARIFICATION = "needs_clarification"
REJECTED = "rejected"


def _resolve_reply_language(preferred: str | None, detected: str) -> str:
    """An explicit preference wins; otherwise reply in the language spoken."""
    if preferred:
        base = preferred.split("-")[0]
        if base in SUPPORTED_LANGUAGES:
            return base
    return primary_language(detected)


def _catalogue_payload(products: list[Product], limit: int = 8) -> list[dict]:
    """The whole shelf, offered when the speaker named no product at all."""
    return [
        {
            "product_id": p.id,
            "name": p.name,
            "base_unit": p.base_unit,
            "current_quantity": float(p.current_quantity),
            "score": 0.0,
        }
        for p in products[:limit]
    ]


def _candidates_payload(candidates) -> list[dict]:
    return [
        {
            "product_id": c.product.id,
            "name": c.product.name,
            "base_unit": c.product.base_unit,
            "current_quantity": float(c.product.current_quantity),
            "score": c.score,
        }
        for c in candidates
    ]


def process_transcript(db: Session, business: Business, transcript: str,
                       language_hint: str | None = None,
                       reply_language: str | None = None,
                       source: str = "voice") -> dict:
    """Interpret one spoken turn, then record what the assistant did about it.

    Every turn is logged — recorded, confirmed, clarified or rejected alike —
    so the assistant's behaviour stays auditable and the next turn has context
    to resolve a follow-up against.
    """
    result = _interpret(db, business, transcript, language_hint, reply_language, source)

    created = result.get("created_event") or {}
    conversation.log_interaction(
        db,
        business_id=business.id,
        kind="command",
        transcript=result.get("transcript", ""),
        normalized_text=result.get("normalized_text", "") or "",
        detected_language=result.get("detected_language", "") or "",
        intent=result.get("event_type", "") or "",
        status=result.get("status", ""),
        confidence=result.get("confidence", 0.0) or 0.0,
        provider=result.get("provider", "") or "",
        response_text=result.get("message", ""),
        source=source,
        event_id=created.get("id"),
        product_id=result.get("product_id"),
    )
    return result


def _interpret(db: Session, business: Business, transcript: str,
               language_hint: str | None = None,
               reply_language: str | None = None,
               source: str = "voice") -> dict:
    text = (transcript or "").strip()
    detected = detect_language(text) if text else (language_hint or "en")
    reply_lang = _resolve_reply_language(reply_language or business.default_language, detected)

    base = {
        "transcript": text,
        "candidates": [],
        "product_id": None,
        "product_name": None,
        "created_event": None,
        "notes": [],
        "detected_language": detected,
        "reply_language": reply_lang,
    }

    if not text:
        return {**base, "status": REJECTED, "confidence": 0.0,
                "message": phrase_for(reply_lang, "no_speech")}

    products: list[Product] = inventory_service.list_products(db, business.id)
    if not products:
        return {**base, "status": REJECTED, "confidence": 0.0,
                "message": phrase_for(reply_lang, "no_products")}

    # "Actually, 15." only means something in the light of the previous turn.
    # Resolve that before asking the model to read it as a standalone sentence.
    followup = conversation.resolve_followup(db, business.id, text)
    if followup and followup["kind"] == "amendment":
        turn = followup["turn"]
        try:
            outcome = conversation.apply_amendment(
                db,
                business_id=business.id,
                turn=turn,
                new_quantity=followup["quantity"],
                transcript=text,
                detected_language=detected,
                source=source,
            )
        except ValueError as exc:
            return {**base, "status": REJECTED, "confidence": 0.0, "message": str(exc)}

        payload = {
            **base,
            "status": AMENDED if outcome["amended"] else RECORDED,
            "confidence": 1.0,
            "message": outcome["message"],
            "product_id": turn.product_id,
            "product_name": outcome["product_name"],
            "event_type": EventType.ADJUSTMENT.value,
            "quantity": followup["quantity"],
            "unit": turn.unit,
            "amended_from": turn.quantity,
            "resulting_quantity": outcome["resulting_quantity"],
            "resulting_unit": outcome["resulting_unit"],
            "notes": ["Corrected the previous entry by recording the difference."],
        }
        if outcome["amended"]:
            event = outcome["event"]
            payload["created_event"] = inventory_service.event_to_dict(
                event, outcome["product_name"], None
            )
        return payload

    provider = get_ai_provider()
    extracted = provider.extract_event(text, [p.name for p in products])

    match = match_product(extracted.product_guess, products)
    model_confidence = max(0.0, min(float(extracted.confidence), 1.0))
    # An assured model with an unclear product is still an unclear result.
    overall = round(min(model_confidence, match.score), 2)

    payload = {
        **base,
        "event_type": extracted.event_type,
        "quantity": extracted.quantity,
        "unit": extracted.unit or (match.best.product.base_unit if match.best else None),
        "customer_name": extracted.customer,
        "price": extracted.price,
        "payment_status": extracted.payment_status,
        "due_date": extracted.due_date,
        "normalized_text": extracted.normalized_text,
        "detected_language": extracted.detected_language or detected,
        "provider": extracted.provider,
        "model_confidence": round(model_confidence, 2),
        "match_confidence": round(match.score, 2),
        "confidence": overall,
        "candidates": _candidates_payload(match.candidates),
        "notes": list(extracted.notes),
    }

    # A sentence can be perfectly understood yet name no product at all
    # ("Ramesh two boxes teesukunnadu"). That is a question to ask, not a
    # dead end, so offer the catalogue instead of rejecting.
    if not extracted.product_guess.strip():
        return {**payload, "status": NEEDS_CLARIFICATION,
                "message": phrase_for(reply_lang, "which_product_missing"),
                "candidates": _catalogue_payload(products)}

    if not match.candidates:
        return {**payload, "status": REJECTED,
                "message": phrase_for(reply_lang, "no_match", guess=extracted.product_guess)}

    best = match.best
    payload["product_id"] = best.product.id
    payload["product_name"] = best.product.name

    # Never pick between products that the text does not separate.
    if match.ambiguous:
        return {**payload, "status": NEEDS_CLARIFICATION,
                "message": phrase_for(reply_lang, "which_product")}

    if extracted.quantity is None or extracted.quantity <= 0:
        return {**payload, "status": NEEDS_CLARIFICATION,
                "message": phrase_for(reply_lang, "how_many")}

    if extracted.event_type == EventType.CREDIT_SALE.value and not extracted.customer:
        return {**payload, "status": NEEDS_CONFIRMATION,
                "message": phrase_for(reply_lang, "who_credit")}

    if overall < settings.clarification_threshold:
        return {**payload, "status": NEEDS_CLARIFICATION,
                "message": phrase_for(reply_lang, "unsure")}

    if overall < settings.confidence_threshold:
        return {**payload, "status": NEEDS_CONFIRMATION,
                "message": phrase_for(reply_lang, "confirm")}

    event = record_event(
        db,
        business_id=business.id,
        product=best.product,
        event_type=EventType(extracted.event_type),
        quantity=extracted.quantity,
        unit=extracted.unit,
        customer_name=extracted.customer,
        price=extracted.price,
        payment_status=PaymentStatus(extracted.payment_status),
        due_date=extracted.due_date,
        source="voice",
        original_text=text,
        normalized_text=extracted.normalized_text,
        detected_language=extracted.detected_language or detected,
        confidence=overall,
    )
    db.refresh(best.product)

    spoken_unit = extracted.unit or best.product.base_unit
    return {
        **payload,
        "status": RECORDED,
        "message": describe(
            reply_lang, extracted.event_type, extracted.quantity,
            spoken_unit, best.product.name, extracted.customer,
        ),
        "created_event": inventory_service.event_to_dict(
            event, best.product.name, event.customer.name if event.customer else None
        ),
        # Resulting stock is a base-unit figure, so it must be reported with the
        # base unit — not the unit the speaker happened to use.
        "resulting_quantity": float(best.product.current_quantity),
        "resulting_unit": best.product.base_unit,
    }
