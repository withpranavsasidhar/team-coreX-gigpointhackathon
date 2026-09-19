"""Business memory: the searchable timeline of everything that happened."""
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.dependencies import require_business
from app.database import get_db
from app.models import Business, Customer, EventType, InventoryEvent, Product
from app.services import conversation

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("")
def search_memory(
    q: str = "",
    event_type: str | None = None,
    product_id: UUID | None = None,
    customer_id: UUID | None = None,
    days: int | None = None,
    limit: int = Query(default=80, le=400),
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    """The event stream, filtered the way a person would want to filter it.

    Every filter is optional and they compose, so "damage, last 7 days, rice"
    is one query rather than three screens.
    """
    stmt = (
        select(InventoryEvent, Product.name, Product.base_unit, Customer.name)
        .join(Product, Product.id == InventoryEvent.product_id)
        .outerjoin(Customer, Customer.id == InventoryEvent.customer_id)
        .where(InventoryEvent.business_id == business.id)
    )

    if event_type:
        try:
            stmt = stmt.where(InventoryEvent.event_type == EventType(event_type))
        except ValueError:
            # An unknown filter should return nothing rather than everything —
            # silently ignoring it would misrepresent the result.
            return {"events": [], "total": 0, "filters_applied": {"event_type": event_type}}

    if product_id:
        stmt = stmt.where(InventoryEvent.product_id == product_id)
    if customer_id:
        stmt = stmt.where(InventoryEvent.customer_id == customer_id)
    if days:
        stmt = stmt.where(InventoryEvent.occurred_at >= datetime.utcnow() - timedelta(days=days))

    term = (q or "").strip()
    if term:
        like = f"%{term}%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(like),
                Customer.name.ilike(like),
                InventoryEvent.original_text.ilike(like),
                InventoryEvent.normalized_text.ilike(like),
            )
        )

    rows = db.execute(stmt.order_by(InventoryEvent.occurred_at.desc()).limit(limit)).all()

    events = [
        {
            "id": event.id,
            "product_id": event.product_id,
            "product_name": product_name,
            "base_unit": base_unit,
            "customer_name": customer_name,
            "event_type": event.event_type.value,
            "quantity": float(event.quantity),
            "unit": event.unit,
            "delta": float(event.delta),
            "price": float(event.price) if event.price is not None else None,
            "payment_status": event.payment_status.value if event.payment_status else "NA",
            "due_date": event.due_date.isoformat() if event.due_date else None,
            "source": event.source,
            "original_text": event.original_text or "",
            "normalized_text": event.normalized_text or "",
            "detected_language": event.detected_language or "",
            "confidence": float(event.confidence),
            "occurred_at": event.occurred_at.isoformat(),
        }
        for event, product_name, base_unit, customer_name in rows
    ]

    return {
        "events": events,
        "total": len(events),
        "filters_applied": {
            "q": term, "event_type": event_type, "product_id": str(product_id) if product_id else None,
            "customer_id": str(customer_id) if customer_id else None, "days": days,
        },
    }


@router.get("/interactions")
def list_interactions(
    limit: int = Query(default=20, le=100),
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    """What the assistant was asked and what it did — including the turns it refused."""
    return {"interactions": conversation.recent_turns(db, business.id, limit=limit)}


@router.get("/event-types")
def list_event_types():
    return {"event_types": [e.value for e in EventType]}
