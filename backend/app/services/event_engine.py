from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ProductNotFound, ValidationFailed
from app.models import (
    Customer, EventType, InventoryEvent, PaymentStatus, Product,
    INCREASING_EVENTS, DECREASING_EVENTS,
)
from app.services.units import to_base_units, to_decimal


def compute_delta(event_type: EventType, base_quantity: Decimal) -> Decimal:
    """Signed change to stock on hand, in base units."""
    if event_type in INCREASING_EVENTS:
        return abs(base_quantity)
    if event_type in DECREASING_EVENTS:
        return -abs(base_quantity)
    if event_type == EventType.ADJUSTMENT:
        return base_quantity  # caller supplies the sign
    raise ValidationFailed(f"Unsupported event type: {event_type}")


def get_or_create_customer(db: Session, business_id: UUID, name: str | None) -> Customer | None:
    if not name or not name.strip():
        return None
    clean = name.strip()
    customer = db.execute(
        select(Customer).where(
            Customer.business_id == business_id,
            func.lower(Customer.name) == clean.lower(),
        )
    ).scalar_one_or_none()
    if customer:
        return customer
    customer = Customer(business_id=business_id, name=clean)
    db.add(customer)
    db.flush()
    return customer


def record_event(
    db: Session,
    *,
    business_id: UUID,
    product: Product,
    event_type: EventType,
    quantity,
    unit: str | None = None,
    customer_name: str | None = None,
    price=None,
    payment_status: PaymentStatus = PaymentStatus.NA,
    due_date=None,
    occurred_at: datetime | None = None,
    source: str = "manual",
    original_text: str = "",
    normalized_text: str = "",
    detected_language: str = "",
    confidence: float = 1.0,
    commit: bool = True,
) -> InventoryEvent:
    """The single path through which inventory is ever allowed to change.

    Appends an immutable ledger row and moves the product's cached quantity by
    the same delta inside one transaction, so the projection can never drift
    from the ledger through a partial write.
    """
    if event_type != EventType.ADJUSTMENT and to_decimal(quantity) <= 0:
        raise ValidationFailed("Quantity must be greater than zero.")

    if event_type == EventType.CREDIT_SALE and not (customer_name and customer_name.strip()):
        raise ValidationFailed("A credit sale needs a customer name.")

    effective_unit = unit or product.base_unit
    base_quantity = to_base_units(product, quantity, effective_unit)
    delta = compute_delta(event_type, base_quantity)

    customer = get_or_create_customer(db, business_id, customer_name)
    if event_type == EventType.CREDIT_SALE and customer and price:
        customer.outstanding_credit = to_decimal(customer.outstanding_credit) + to_decimal(price)

    event = InventoryEvent(
        business_id=business_id,
        product_id=product.id,
        customer_id=customer.id if customer else None,
        event_type=event_type,
        quantity=abs(to_decimal(quantity)) if event_type != EventType.ADJUSTMENT else to_decimal(quantity),
        unit=effective_unit,
        delta=delta,
        price=to_decimal(price) if price is not None else None,
        payment_status=payment_status,
        due_date=due_date,
        source=source,
        original_text=original_text or "",
        normalized_text=normalized_text or "",
        detected_language=detected_language or "",
        confidence=to_decimal(confidence),
        occurred_at=occurred_at or datetime.utcnow(),
    )
    db.add(event)
    product.current_quantity = to_decimal(product.current_quantity) + delta

    if commit:
        db.commit()
        db.refresh(event)
    else:
        db.flush()
    return event


def recompute_current_quantity(db: Session, product: Product) -> Decimal:
    """Re-derive stock from the ledger. The invariant the cached column must satisfy."""
    total = db.execute(
        select(func.coalesce(func.sum(InventoryEvent.delta), 0)).where(
            InventoryEvent.product_id == product.id
        )
    ).scalar_one()
    return to_decimal(total)


def load_product(db: Session, business_id: UUID, product_id: UUID) -> Product:
    product = db.execute(
        select(Product).where(Product.id == product_id, Product.business_id == business_id)
    ).scalar_one_or_none()
    if not product:
        raise ProductNotFound("That product does not exist.")
    return product
