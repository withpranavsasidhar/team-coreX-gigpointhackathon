from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import require_business
from app.core.exceptions import NotFound, ValidationFailed
from app.database import get_db
from app.models import Business, Customer, InventoryEvent, Payment, Product
from app.schemas import CustomerCreate, CustomerOut, PaymentCreate, PaymentOut
from app.services.units import to_decimal

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(
    payload: CustomerCreate,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    customer = Customer(business_id=business.id, **payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("", response_model=list[CustomerOut])
def list_customers(
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    return list(
        db.execute(
            select(Customer).where(Customer.business_id == business.id).order_by(Customer.name)
        ).scalars()
    )


def _load_customer(db: Session, business_id: UUID, customer_id: UUID) -> Customer:
    customer = db.execute(
        select(Customer).where(Customer.id == customer_id, Customer.business_id == business_id)
    ).scalar_one_or_none()
    if not customer:
        raise NotFound("That customer does not exist.")
    return customer


@router.get("/{customer_id}")
def customer_detail(
    customer_id: UUID,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    """Everything this shop knows about one person, in one response.

    What they took, what they paid, what they still owe — the question
    "show me everything about Ramesh" answered in full.
    """
    customer = _load_customer(db, business.id, customer_id)

    rows = db.execute(
        select(InventoryEvent, Product.name, Product.base_unit)
        .join(Product, Product.id == InventoryEvent.product_id)
        .where(InventoryEvent.customer_id == customer.id)
        .order_by(InventoryEvent.occurred_at.desc())
        .limit(100)
    ).all()

    payments = db.execute(
        select(Payment)
        .where(Payment.customer_id == customer.id)
        .order_by(Payment.occurred_at.desc())
        .limit(50)
    ).scalars().all()

    # Totals are summed in base units so different spoken units never mix.
    totals: dict[str, dict] = {}
    lifetime_value = 0.0
    for event, name, base_unit in rows:
        bucket = totals.setdefault(
            name, {"product_name": name, "base_unit": base_unit, "quantity": 0.0, "count": 0}
        )
        bucket["quantity"] += abs(float(event.delta))
        bucket["count"] += 1
        if event.price is not None:
            lifetime_value += float(event.price)

    return {
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "phone": customer.phone or "",
            "outstanding_credit": float(customer.outstanding_credit),
            "created_at": customer.created_at.isoformat(),
        },
        "totals": sorted(totals.values(), key=lambda t: t["quantity"], reverse=True),
        "lifetime_value": round(lifetime_value, 2),
        "total_paid": round(sum(float(p.amount) for p in payments), 2),
        "transaction_count": len(rows),
        "events": [
            {
                "id": event.id,
                "product_id": event.product_id,
                "product_name": name,
                "base_unit": base_unit,
                "event_type": event.event_type.value,
                "quantity": float(event.quantity),
                "unit": event.unit,
                "delta": float(event.delta),
                "price": float(event.price) if event.price is not None else None,
                "payment_status": event.payment_status.value if event.payment_status else "NA",
                "due_date": event.due_date.isoformat() if event.due_date else None,
                "occurred_at": event.occurred_at.isoformat(),
            }
            for event, name, base_unit in rows
        ],
        "payments": [
            {
                "id": p.id,
                "amount": float(p.amount),
                "note": p.note or "",
                "occurred_at": p.occurred_at.isoformat(),
            }
            for p in payments
        ],
    }


@router.post("/{customer_id}/payments", response_model=PaymentOut, status_code=201)
def record_payment(
    customer_id: UUID,
    payload: PaymentCreate,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    """Settle credit. Money moves, stock does not, so this is not a stock event."""
    customer = _load_customer(db, business.id, customer_id)

    outstanding = to_decimal(customer.outstanding_credit)
    amount = to_decimal(payload.amount)
    if amount > outstanding:
        raise ValidationFailed(
            f"{customer.name} owes ₹{float(outstanding):,.0f}. "
            f"A payment of ₹{float(amount):,.0f} is more than the outstanding amount."
        )

    payment = Payment(
        business_id=business.id,
        customer_id=customer.id,
        amount=amount,
        note=payload.note,
        source="manual",
    )
    db.add(payment)
    customer.outstanding_credit = outstanding - amount
    db.commit()
    db.refresh(payment)
    return payment
