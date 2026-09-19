from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.models import CONSUMPTION_EVENTS, Customer, InventoryEvent, Product
from app.services.units import to_decimal


def list_products(db: Session, business_id: UUID, include_archived: bool = False) -> list[Product]:
    stmt = (
        select(Product)
        .options(selectinload(Product.conversions))
        .where(Product.business_id == business_id)
        .order_by(Product.name)
    )
    if not include_archived:
        stmt = stmt.where(Product.is_archived.is_(False))
    return list(db.execute(stmt).scalars())


def average_daily_usage(db: Session, product_id: UUID, lookback_days: int | None = None) -> Decimal:
    """Consumption per day over the trailing window, in base units."""
    days = lookback_days or settings.consumption_lookback_days
    since = datetime.utcnow() - timedelta(days=days)
    consumed = db.execute(
        select(func.coalesce(func.sum(-InventoryEvent.delta), 0)).where(
            InventoryEvent.product_id == product_id,
            InventoryEvent.event_type.in_(list(CONSUMPTION_EVENTS)),
            InventoryEvent.occurred_at >= since,
        )
    ).scalar_one()
    consumed = max(to_decimal(consumed), Decimal(0))
    return consumed / Decimal(days)


def last_movement_at(db: Session, product_id: UUID) -> datetime | None:
    return db.execute(
        select(func.max(InventoryEvent.occurred_at)).where(InventoryEvent.product_id == product_id)
    ).scalar_one()


def stock_status(product: Product, avg_usage: Decimal) -> tuple[str, float | None]:
    """Classify a product and estimate days of cover remaining.

    Returns (status, estimated_days_to_stockout). Days is None when there is no
    recorded consumption — an unknown rate is reported as unknown, not as zero
    or infinity.
    """
    qty = to_decimal(product.current_quantity)
    minimum = to_decimal(product.minimum_quantity)

    days: float | None = None
    if avg_usage > 0:
        days = float(qty / avg_usage)

    if qty <= 0:
        return "out_of_stock", days
    if (days is not None and days <= 3) or qty <= minimum:
        status = "critical" if (days is not None and days <= 3) else "low"
        return status, days
    if days is not None and days <= 7:
        return "low", days
    return "healthy", days


def product_status(db: Session, product: Product) -> dict:
    avg = average_daily_usage(db, product.id)
    status, days = stock_status(product, avg)
    return {
        "id": product.id,
        "business_id": product.business_id,
        "name": product.name,
        "category": product.category,
        "base_unit": product.base_unit,
        "current_quantity": float(product.current_quantity),
        "minimum_quantity": float(product.minimum_quantity),
        "reorder_quantity": float(product.reorder_quantity),
        "price": float(product.price),
        "is_archived": product.is_archived,
        "conversions": product.conversions,
        "status": status,
        "avg_daily_usage": round(float(avg), 2),
        "estimated_days_to_stockout": round(days, 1) if days is not None else None,
        "last_movement_at": last_movement_at(db, product.id),
    }


def event_to_dict(event: InventoryEvent, product_name: str | None = None,
                  customer_name: str | None = None) -> dict:
    return {
        "id": event.id,
        "product_id": event.product_id,
        "product_name": product_name,
        "customer_id": event.customer_id,
        "customer_name": customer_name,
        "event_type": event.event_type,
        "quantity": float(event.quantity),
        "unit": event.unit,
        "delta": float(event.delta),
        "price": float(event.price) if event.price is not None else None,
        "payment_status": event.payment_status,
        "due_date": event.due_date,
        "source": event.source,
        "original_text": event.original_text or "",
        "normalized_text": event.normalized_text or "",
        "detected_language": event.detected_language or "",
        "confidence": float(event.confidence),
        "occurred_at": event.occurred_at,
    }


def list_events(db: Session, business_id: UUID, limit: int = 100,
                product_id: UUID | None = None) -> list[dict]:
    stmt = (
        select(InventoryEvent, Product.name, Customer.name)
        .join(Product, Product.id == InventoryEvent.product_id)
        .outerjoin(Customer, Customer.id == InventoryEvent.customer_id)
        .where(InventoryEvent.business_id == business_id)
        .order_by(InventoryEvent.occurred_at.desc())
        .limit(limit)
    )
    if product_id:
        stmt = stmt.where(InventoryEvent.product_id == product_id)
    return [event_to_dict(e, pname, cname) for e, pname, cname in db.execute(stmt)]


def movement_breakdown(db: Session, product_id: UUID, days: int) -> list[dict]:
    since = datetime.utcnow() - timedelta(days=days)
    rows = db.execute(
        select(
            InventoryEvent.event_type,
            func.sum(InventoryEvent.delta),
            func.count(InventoryEvent.id),
        )
        .where(InventoryEvent.product_id == product_id, InventoryEvent.occurred_at >= since)
        .group_by(InventoryEvent.event_type)
    ).all()
    return [
        {"event_type": et, "net_change": float(total), "count": count}
        for et, total, count in rows
    ]


def product_history(db: Session, product: Product, days: int = 30) -> dict:
    breakdown = movement_breakdown(db, product.id, days)
    events = list_events(db, product.business_id, limit=200, product_id=product.id)

    total_in = sum(b["net_change"] for b in breakdown if b["net_change"] > 0)
    total_out = sum(b["net_change"] for b in breakdown if b["net_change"] < 0)
    net_in_window = total_in + total_out
    opening_balance = float(product.current_quantity) - net_in_window

    return {
        "product": product_status(db, product),
        "window_days": days,
        "opening_balance": round(opening_balance, 3),
        "total_in": round(total_in, 3),
        "total_out": round(abs(total_out), 3),
        "breakdown": breakdown,
        "events": events,
    }
