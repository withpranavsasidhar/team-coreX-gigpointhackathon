from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_business
from app.database import get_db
from app.models import Business
from app.schemas import EventCreate, EventOut
from app.services import inventory_service
from app.services.event_engine import load_product, record_event

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventOut, status_code=201)
def create_event(
    payload: EventCreate,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    product = load_product(db, business.id, payload.product_id)
    event = record_event(
        db,
        business_id=business.id,
        product=product,
        event_type=payload.event_type,
        quantity=payload.quantity,
        unit=payload.unit,
        customer_name=payload.customer_name,
        price=payload.price,
        payment_status=payload.payment_status,
        due_date=payload.due_date,
        occurred_at=payload.occurred_at,
        source=payload.source,
        original_text=payload.original_text,
        normalized_text=payload.normalized_text,
        detected_language=payload.detected_language,
        confidence=payload.confidence,
    )
    customer_name = event.customer.name if event.customer else None
    return inventory_service.event_to_dict(event, product.name, customer_name)


@router.get("", response_model=list[EventOut])
def list_events(
    limit: int = 100,
    product_id: UUID | None = None,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    return inventory_service.list_events(db, business.id, limit=limit, product_id=product_id)
