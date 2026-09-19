"""Short-term conversational memory.

What separates an assistant from a command parser is that the second sentence
may depend on the first. "Add 20 cartons of Coke." … "Actually, 15." The
second utterance names no product and no action, and is meaningless on its own.

This module keeps just enough recent context to resolve that kind of follow-up,
and implements amendments in a way that does not violate the ledger's
append-only rule: correcting a quantity appends a *new* ADJUSTMENT event for
the difference rather than rewriting history. The stock lands where the owner
meant it to, and the record still shows what actually happened.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AIInteraction, EventType, InventoryEvent, Product
from app.services.event_engine import record_event
from app.services.language import extract_quantity
from app.services.units import to_base_units, to_decimal

# How far back a bare follow-up may reach. Beyond this the owner has moved on,
# and silently amending an old entry would be worse than asking.
CONTEXT_WINDOW = timedelta(minutes=15)

# "actually make that 15", "sorry, 15", "no no, 15 kg"
AMENDMENT_MARKERS = (
    "actually", "actually make", "make that", "make it", "change it", "change that",
    "correction", "correct that", "sorry", "no no", "i meant", "instead",
    "కాదు", "సరిచేయి", "అసలు",                       # te: "not that", "correct it"
    "nahi", "नहीं", "galat", "गलत", "sahi karo",      # hi
)

# A follow-up that adds to what was just recorded rather than replacing it.
ADDITION_MARKERS = ("and", "also", "plus", "one more", "more", "inka", "aur", "और")


@dataclass
class Turn:
    """A recent assistant turn, enough to resolve a follow-up against."""
    interaction_id: UUID
    event_id: UUID | None
    product_id: UUID | None
    product_name: str
    event_type: str
    quantity: float
    unit: str
    customer_name: str | None
    created_at: datetime


def log_interaction(
    db: Session,
    *,
    business_id: UUID,
    kind: str,
    transcript: str,
    normalized_text: str = "",
    detected_language: str = "",
    intent: str = "",
    status: str = "",
    confidence: float = 0.0,
    provider: str = "",
    response_text: str = "",
    source: str = "voice",
    event_id: UUID | None = None,
    product_id: UUID | None = None,
    commit: bool = True,
) -> AIInteraction:
    """Record the turn whether or not it changed anything.

    Questions, rejections and clarifications are logged too — an assistant that
    only remembers its successes cannot explain itself.
    """
    interaction = AIInteraction(
        business_id=business_id,
        kind=kind,
        transcript=transcript or "",
        normalized_text=normalized_text or "",
        detected_language=detected_language or "",
        intent=intent or "",
        status=status or "",
        confidence=to_decimal(max(0.0, min(float(confidence or 0), 1.0))),
        provider=provider or "",
        response_text=response_text or "",
        source=source,
        event_id=event_id,
        product_id=product_id,
    )
    db.add(interaction)
    if commit:
        db.commit()
        db.refresh(interaction)
    else:
        db.flush()
    return interaction


def last_turn(db: Session, business_id: UUID) -> Turn | None:
    """The most recent turn that actually wrote something, if it is still fresh."""
    row = db.execute(
        select(AIInteraction, InventoryEvent, Product)
        .join(InventoryEvent, InventoryEvent.id == AIInteraction.event_id)
        .join(Product, Product.id == InventoryEvent.product_id)
        .where(
            AIInteraction.business_id == business_id,
            AIInteraction.event_id.is_not(None),
        )
        .order_by(AIInteraction.created_at.desc())
        .limit(1)
    ).first()
    if not row:
        return None

    interaction, event, product = row
    if datetime.utcnow() - interaction.created_at > CONTEXT_WINDOW:
        return None

    return Turn(
        interaction_id=interaction.id,
        event_id=event.id,
        product_id=product.id,
        product_name=product.name,
        event_type=event.event_type.value,
        quantity=float(event.quantity),
        unit=event.unit,
        customer_name=event.customer.name if event.customer else None,
        created_at=interaction.created_at,
    )


def recent_turns(db: Session, business_id: UUID, limit: int = 10) -> list[dict]:
    rows = db.execute(
        select(AIInteraction)
        .where(AIInteraction.business_id == business_id)
        .order_by(AIInteraction.created_at.desc())
        .limit(limit)
    ).scalars().all()
    return [
        {
            "id": r.id,
            "kind": r.kind,
            "transcript": r.transcript,
            "normalized_text": r.normalized_text,
            "detected_language": r.detected_language,
            "intent": r.intent,
            "status": r.status,
            "confidence": float(r.confidence),
            "provider": r.provider,
            "response_text": r.response_text,
            "source": r.source,
            "event_id": r.event_id,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


def looks_like_amendment(text: str) -> bool:
    """Does this sentence correct the previous one rather than stand alone?

    Requires both a correction marker and a number, so "actually that's fine"
    is not mistaken for an amendment.
    """
    lowered = (text or "").lower().strip()
    if not lowered:
        return False
    if not any(marker in lowered for marker in AMENDMENT_MARKERS):
        return False
    if any(marker in lowered for marker in ADDITION_MARKERS):
        # "actually add 5 more" is an addition, not a replacement.
        return False
    return extract_quantity(lowered) is not None


def _names_a_product(text: str, product_name: str) -> bool:
    words = {w for w in re.findall(r"[a-z]+", (text or "").lower()) if len(w) > 2}
    return any(part.lower() in words for part in product_name.split())


def apply_amendment(
    db: Session,
    *,
    business_id: UUID,
    turn: Turn,
    new_quantity: float,
    transcript: str,
    detected_language: str = "",
    source: str = "voice",
) -> dict:
    """Correct the quantity of the previous entry by appending the difference.

    The original event stays exactly as it was recorded; an ADJUSTMENT carries
    the delta needed to reach what the owner actually meant. Stock ends up
    correct and the ledger still shows the correction happened.
    """
    product = db.get(Product, turn.product_id)
    if product is None:
        raise ValueError("The product from the previous turn no longer exists.")

    original_event = db.get(InventoryEvent, turn.event_id)
    if original_event is None:
        raise ValueError("The previous entry no longer exists.")

    # Work in base units: the original and the correction may be spoken in
    # different units ("20 cartons" corrected to "15").
    old_base = to_base_units(product, Decimal(str(turn.quantity)), turn.unit)
    new_base = to_base_units(product, Decimal(str(new_quantity)), turn.unit)
    sign = Decimal(1) if to_decimal(original_event.delta) >= 0 else Decimal(-1)
    correction = (new_base - old_base) * sign

    if correction == 0:
        return {
            "amended": False,
            "message": f"That is already what I recorded — {turn.quantity:g} {turn.unit} of {turn.product_name}.",
            "product_name": turn.product_name,
            "resulting_quantity": float(product.current_quantity),
            "resulting_unit": product.base_unit,
        }

    event = record_event(
        db,
        business_id=business_id,
        product=product,
        event_type=EventType.ADJUSTMENT,
        quantity=correction,
        unit=product.base_unit,
        source=source,
        original_text=transcript,
        normalized_text=(
            f"correction: {turn.event_type} of {turn.product_name} "
            f"{turn.quantity:g} -> {new_quantity:g} {turn.unit}"
        ),
        detected_language=detected_language,
        confidence=1.0,
    )
    db.refresh(product)

    return {
        "amended": True,
        "event": event,
        "product": product,
        "product_name": turn.product_name,
        "old_quantity": turn.quantity,
        "new_quantity": new_quantity,
        "unit": turn.unit,
        "message": (
            f"Updated. I changed the entry from {turn.quantity:g} to "
            f"{new_quantity:g} {turn.unit} of {turn.product_name}. "
            f"It now stands at {float(product.current_quantity):g} {product.base_unit}."
        ),
        "resulting_quantity": float(product.current_quantity),
        "resulting_unit": product.base_unit,
    }


def resolve_followup(db: Session, business_id: UUID, text: str) -> dict | None:
    """Decide whether this utterance is a follow-up, and to what.

    Returns None when the sentence stands on its own, which is the common case
    and must stay cheap.
    """
    if not looks_like_amendment(text):
        return None

    turn = last_turn(db, business_id)
    if turn is None:
        return None

    # If the speaker names a different product, this is a new statement that
    # merely happens to start with "actually".
    if _names_a_product(text, turn.product_name) is False and re.search(
        r"\b(of|for)\b\s+\w+", (text or "").lower()
    ):
        return None

    quantity = extract_quantity(text)
    if quantity is None:
        return None

    return {"kind": "amendment", "turn": turn, "quantity": float(quantity)}
