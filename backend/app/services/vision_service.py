"""A.R.I.A. Vision: reading a photograph into a reviewable proposal.

This service can read, match and rank. It cannot write. Applying a reading goes
through the existing tool layer, which goes through the existing business
services, which go through the existing event engine — the same path a spoken
command takes. There is no second inventory writer here, and no second matcher:
product identity is decided by `product_matcher`, exactly as it is for voice.

Nothing is applied without a person confirming it first.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Business, VisionAnalysis
from app.providers.vision import (
    DecodedImage, VisionError, VisionReading, decode_image, get_vision_provider,
)
from app.services import business_context, inventory_service, tools
from app.services.product_matcher import match_product

# How a line's confidence is presented. Application thresholds, not truth.
HIGH = "high"
MEDIUM = "medium"
LOW = "low"

#: Below this, the best catalogue match is not convincing enough to apply on
#: its own — the line is shown with candidates and an offer to create instead.
STRONG_MATCH = 0.75

# Guidance worth giving, keyed by what the model reported seeing.
QUALITY_ADVICE = {
    "blur": "Hold the camera still and let it focus.",
    "dark": "Try better lighting.",
    "glare": "Tilt the page slightly to avoid glare.",
    "angled": "Hold the camera square to the page.",
    "cropped": "Make sure the whole list is in frame.",
    "obstructed": "Move anything covering the items.",
    "low_resolution": "Move closer, or use a higher-quality photo.",
}


@dataclass
class VisionItem:
    """One line read from an image, resolved against the real catalogue."""

    raw_name: str
    normalized_name: str
    quantity: float | None
    unit: str | None
    price: float | None
    confidence: float
    confidence_band: str
    item_note: str = ""
    # Resolution against the existing catalogue.
    product_id: str | None = None
    product_name: str | None = None
    base_unit: str | None = None
    current_quantity: float | None = None
    match_score: float = 0.0
    match_state: str = "unmatched"   # matched | ambiguous | unmatched
    candidates: list[dict] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    # True when nothing in the catalogue is a convincing match, so the owner
    # should be offered the chance to create the product. Never acted on alone.
    suggest_create: bool = False

    @property
    def ready(self) -> bool:
        """Can this line be applied without anything further from the owner?"""
        return (
            self.match_state == "matched"
            and self.quantity is not None
            and self.quantity > 0
            and not self.issues
        )

    def as_dict(self) -> dict:
        return {
            "raw_name": self.raw_name,
            "normalized_name": self.normalized_name,
            "quantity": self.quantity,
            "unit": self.unit,
            "price": self.price,
            "confidence": round(self.confidence, 2),
            "confidence_band": self.confidence_band,
            "item_note": self.item_note,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "base_unit": self.base_unit,
            "current_quantity": self.current_quantity,
            "match_score": round(self.match_score, 2),
            "match_state": self.match_state,
            "candidates": self.candidates,
            "issues": self.issues,
            "suggest_create": self.suggest_create,
            "ready": self.ready,
        }


def _band(confidence: float) -> str:
    if confidence >= settings.vision_high_confidence:
        return HIGH
    if confidence >= settings.vision_low_confidence:
        return MEDIUM
    return LOW


def _coerce_number(value) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number == number and abs(number) != float("inf") else None


def _resolve_unit(raw_unit: str | None, business: Business) -> tuple[str | None, list[str]]:
    """Map a unit the image showed onto a unit the system already knows.

    Reuses the existing vocabulary and the trade's own unit list. No second
    unit system is introduced.
    """
    from app.services.vocabulary import UNIT_VOCABULARY

    if not raw_unit or not str(raw_unit).strip():
        return None, []

    text = str(raw_unit).strip().lower()
    known = business_context.units_for(business.business_type)

    if text in known:
        return text, []
    for canonical, spellings in UNIT_VOCABULARY.items():
        if text == canonical or text in spellings:
            return canonical, []
    return None, [f"'{raw_unit}' is not a unit I recognise."]


def _match_line(item: dict, products, business: Business) -> VisionItem:
    raw_name = str(item.get("raw_name") or "").strip()
    normalized = str(item.get("normalized_name") or raw_name).strip()
    quantity = _coerce_number(item.get("quantity"))
    price = _coerce_number(item.get("price"))
    confidence = _coerce_number(item.get("confidence"))
    confidence = 0.0 if confidence is None else max(0.0, min(confidence, 1.0))

    unit, unit_issues = _resolve_unit(item.get("unit"), business)

    line = VisionItem(
        raw_name=raw_name,
        normalized_name=normalized,
        quantity=quantity,
        unit=unit,
        price=price,
        confidence=confidence,
        confidence_band=_band(confidence),
        item_note=str(item.get("item_note") or ""),
        issues=list(unit_issues),
    )

    if quantity is None:
        line.issues.append("Quantity unclear — please enter it.")
    elif quantity <= 0:
        line.issues.append("Quantity must be greater than zero.")

    # Identity is resolved by the existing matcher, against the real catalogue.
    search = normalized or raw_name
    result = match_product(search, products) if search else None
    if result and result.candidates:
        line.candidates = [
            {
                "product_id": str(c.product.id),
                "product_name": c.product.name,
                "base_unit": c.product.base_unit,
                "current_quantity": float(c.product.current_quantity),
                "score": round(c.score, 2),
            }
            for c in result.candidates
        ]
        best = result.best
        line.match_score = result.score
        if result.ambiguous:
            line.match_state = "ambiguous"
            line.issues.append("Matches more than one product — pick which one.")
        else:
            line.match_state = "matched"
            line.product_id = str(best.product.id)
            line.product_name = best.product.name
            line.base_unit = best.product.base_unit
            line.current_quantity = float(best.product.current_quantity)
            if line.unit is None and not unit_issues:
                line.unit = best.product.base_unit

        # A weak best match means the photographed item is probably something
        # the catalogue does not have yet. Offer to create it rather than
        # letting a loose word-overlap stand in for the real product.
        if result.score < STRONG_MATCH:
            line.suggest_create = True
            line.issues.append(
                f"'{search}' may not be in your catalogue — check the match, "
                "or add it as a new product."
            )
    else:
        line.match_state = "unmatched"
        line.suggest_create = True
        line.issues.append(f"'{search or 'this item'}' is not in your catalogue yet.")

    # A line the model itself was unsure of never counts as ready.
    if line.confidence_band == LOW:
        line.issues.append("Low confidence — please check this line.")

    return line


def analyze_image(
    db: Session,
    business: Business,
    image_data_uri: str,
    hint: str = "",
    conversation_id: UUID | None = None,
) -> dict:
    """Read an image and return a reviewable proposal. Writes nothing to inventory."""
    image: DecodedImage = decode_image(image_data_uri)   # raises VisionError
    provider = get_vision_provider()
    reading: VisionReading = provider.read_image(image, hint=hint)

    products = inventory_service.list_products(db, business.id)
    lines = [_match_line(item, products, business) for item in reading.items]

    unreadable = not reading.readable
    advice = [QUALITY_ADVICE[q] for q in reading.quality_issues if q in QUALITY_ADVICE]

    record = VisionAnalysis(
        business_id=business.id,
        conversation_id=conversation_id,
        document_type=reading.document_type,
        detected_language=reading.language,
        readable=reading.readable,
        quality_issues=json.dumps(reading.quality_issues),
        notes=reading.notes,
        items=json.dumps([line.as_dict() for line in lines]),
        invoice=json.dumps(reading.invoice) if reading.invoice else "",
        provider=reading.provider,
        model=reading.model,
        image_mime=image.mime,
        image_bytes=len(image.data),   # size only; the image itself is discarded
        status="analyzed",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    ready = [line for line in lines if line.ready]
    return {
        "analysis_id": str(record.id),
        "document_type": reading.document_type,
        "language": reading.language,
        "readable": reading.readable,
        "quality_issues": reading.quality_issues,
        "quality_advice": advice,
        "notes": reading.notes,
        "items": [line.as_dict() for line in lines],
        "invoice": reading.invoice,
        "summary": _summarise(lines, unreadable),
        "counts": {
            "total": len(lines),
            "ready": len(ready),
            "needs_attention": len(lines) - len(ready),
        },
        "provider": reading.provider,
        "model": reading.model,
        "status": record.status,
    }


def _summarise(lines: list[VisionItem], unreadable: bool) -> str:
    if unreadable:
        return "I couldn't read this image clearly."
    if not lines:
        return "I couldn't identify any recognisable business items in this image."

    ready = sum(1 for line in lines if line.ready)
    if ready == len(lines):
        return f"I found {len(lines)} item{'s' if len(lines) != 1 else ''}."
    if ready == 0:
        return (f"I found {len(lines)} item{'s' if len(lines) != 1 else ''}, "
                "but I need you to confirm them.")
    return (f"I found {len(lines)} items. {ready} look clear; "
            f"{len(lines) - ready} need checking.")


def get_analysis(db: Session, business: Business, analysis_id: UUID) -> VisionAnalysis:
    record = db.execute(
        select(VisionAnalysis).where(
            VisionAnalysis.id == analysis_id,
            VisionAnalysis.business_id == business.id,   # never another business's reading
        )
    ).scalar_one_or_none()
    if not record:
        raise VisionError("That image analysis could not be found.")
    return record


# Which existing tool a reading should be applied through. Every one of these
# already exists and is already tested; Vision adds no inventory writer.
ACTION_TOOLS = {
    "add_stock": "add_stock",
    "record_purchase": "record_purchase",
    "make_sale": "make_sale",
    "record_damage": "record_damage",
    "adjust_stock": "adjust_stock",
}


def apply_analysis(
    db: Session,
    business: Business,
    analysis_id: UUID,
    selections: list[dict],
    action: str = "add_stock",
) -> dict:
    """Apply confirmed lines through the existing tool layer.

    `selections` is what the owner approved after reviewing and editing — not
    what the model read. The stored reading is only used to check that the
    analysis exists and belongs to this business.
    """
    record = get_analysis(db, business, analysis_id)

    tool_name = ACTION_TOOLS.get(action)
    if not tool_name:
        raise VisionError(f"'{action}' is not an action Vision can apply.")
    if not selections:
        raise VisionError("Nothing was selected to apply.")

    # source="vision" flows into the existing event engine through the existing
    # ToolContext; the ledger's `source` column already accepts free text.
    ctx = tools.ToolContext(db=db, business=business, source="vision")

    applied, failed = [], []
    for selection in selections:
        product = (selection.get("product_name") or selection.get("product") or "").strip()
        quantity = _coerce_number(selection.get("quantity"))

        if not product:
            failed.append({"line": selection, "error": "No product was chosen for this line."})
            continue
        if quantity is None or quantity <= 0:
            failed.append({"line": selection,
                           "error": f"{product}: a quantity greater than zero is needed."})
            continue

        arguments = {"product": product, "quantity": quantity,
                     "reason": "Read from a photo by A.R.I.A. Vision"}
        if selection.get("unit"):
            arguments["unit"] = selection["unit"]
        if selection.get("price") is not None and tool_name in ("record_purchase", "make_sale"):
            price = _coerce_number(selection["price"])
            if price is not None:
                arguments["price"] = price

        result = tools.execute(ctx, tool_name, arguments)
        if result.get("error"):
            failed.append({"line": selection, "error": result["error"]})
        else:
            applied.append(result)

    if applied:
        record.status = "applied"
        record.applied_at = datetime.utcnow()
        db.commit()

    return {
        "analysis_id": str(record.id),
        "action": action,
        "applied": applied,
        "failed": failed,
        "counts": {"applied": len(applied), "failed": len(failed)},
        "summary": _apply_summary(applied, failed),
    }


def _apply_summary(applied: list[dict], failed: list[dict]) -> str:
    if not applied and failed:
        return "Nothing was applied. Nothing in your inventory was changed."
    if applied and not failed:
        parts = [f"{a['quantity']:g} {a['unit']} {a['product']}" for a in applied[:4]]
        more = f" and {len(applied) - 4} more" if len(applied) > 4 else ""
        return f"Done. Added {', '.join(parts)}{more}."
    return (f"Applied {len(applied)} item{'s' if len(applied) != 1 else ''}; "
            f"{len(failed)} could not be applied.")
