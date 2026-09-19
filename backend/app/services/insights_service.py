"""Derived business intelligence: alerts, stockout risk, reorder and velocity.

Every figure here is computed in Python/SQL from the event ledger. Nothing in
this module calls a language model — the reasoning layer is only ever handed
numbers that were already verified against the database.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import CONSUMPTION_EVENTS, EventType, InventoryEvent, Product
from app.services.inventory_service import average_daily_usage, list_products, stock_status
from app.services.units import to_decimal

CRITICAL_DAYS = 3
WARNING_DAYS = 7
#: Recent usage must differ from the prior period by this factor to be "unusual".
SPIKE_FACTOR = 1.8
SLUMP_FACTOR = 0.4


def consumption_between(db: Session, product_id: UUID, start: datetime, end: datetime) -> Decimal:
    total = db.execute(
        select(func.coalesce(func.sum(-InventoryEvent.delta), 0)).where(
            InventoryEvent.product_id == product_id,
            InventoryEvent.event_type.in_(list(CONSUMPTION_EVENTS)),
            InventoryEvent.occurred_at >= start,
            InventoryEvent.occurred_at < end,
        )
    ).scalar_one()
    return max(to_decimal(total), Decimal(0))


def alert_for(db: Session, product: Product) -> dict | None:
    """Stock-level alert with a plain-language reason, or None if healthy."""
    usage = average_daily_usage(db, product.id)
    status, days = stock_status(product, usage)
    if status == "healthy":
        return None

    quantity = float(product.current_quantity)
    if status == "out_of_stock":
        severity, message = "critical", f"{product.name} is out of stock."
    elif days is not None and days <= CRITICAL_DAYS:
        severity = "critical"
        message = (
            f"{product.name} may run out in about {days:.0f} day"
            f"{'s' if round(days) != 1 else ''}."
        )
    elif quantity <= float(product.minimum_quantity):
        severity = "warning"
        message = (
            f"{product.name} is at {quantity:g} {product.base_unit}, "
            f"below the minimum of {float(product.minimum_quantity):g}."
        )
    else:
        severity = "warning"
        message = f"{product.name} may run low in about {days:.0f} days at the current rate."

    return {
        "product_id": product.id,
        "product_name": product.name,
        "alert_type": "OUT_OF_STOCK" if status == "out_of_stock" else "STOCKOUT_RISK",
        "severity": severity,
        "status": status,
        "current_quantity": quantity,
        "base_unit": product.base_unit,
        "minimum_quantity": float(product.minimum_quantity),
        "avg_daily_usage": round(float(usage), 2),
        "estimated_days_to_stockout": round(days, 1) if days is not None else None,
        "message": message,
    }


def alerts(db: Session, business_id: UUID) -> list[dict]:
    found = [alert_for(db, p) for p in list_products(db, business_id)]
    found = [a for a in found if a]
    found.sort(key=lambda a: (a["severity"] != "critical", a["estimated_days_to_stockout"] or 999))
    return found


def reorder_for(db: Session, product: Product) -> dict | None:
    """Top up to cover the minimum plus expected demand over the lead time."""
    usage = average_daily_usage(db, product.id)
    lead_time = settings.default_lead_time_days
    minimum = to_decimal(product.minimum_quantity)
    current = to_decimal(product.current_quantity)

    target = minimum + usage * Decimal(lead_time)
    shortfall = target - current
    if shortfall <= 0:
        return None

    # Round up to the shop's usual order size when one is configured.
    suggested = max(shortfall, to_decimal(product.reorder_quantity))
    if suggested <= 0:
        return None

    return {
        "product_id": product.id,
        "product_name": product.name,
        "base_unit": product.base_unit,
        "current_quantity": float(current),
        "minimum_quantity": float(minimum),
        "target_quantity": round(float(target), 1),
        "suggested_quantity": round(float(suggested), 1),
        "avg_daily_usage": round(float(usage), 2),
        "reason": (
            f"Selling about {float(usage):.1f} {product.base_unit} a day. "
            f"Ordering {float(suggested):.0f} covers the {lead_time}-day lead time "
            f"and keeps you above the minimum of {float(minimum):g}."
        ),
    }


def reorder_list(db: Session, business_id: UUID) -> list[dict]:
    found = [reorder_for(db, p) for p in list_products(db, business_id)]
    found = [r for r in found if r]
    found.sort(key=lambda r: r["suggested_quantity"], reverse=True)
    return found


def unusual_movement(db: Session, business_id: UUID, window_days: int = 7) -> list[dict]:
    """Products whose recent consumption diverges sharply from the period before."""
    now = datetime.utcnow()
    recent_start = now - timedelta(days=window_days)
    prior_start = now - timedelta(days=window_days * 2)

    findings = []
    for product in list_products(db, business_id):
        recent = float(consumption_between(db, product.id, recent_start, now))
        prior = float(consumption_between(db, product.id, prior_start, recent_start))
        if prior <= 0 or recent <= 0:
            continue
        # Ignore trickle volumes, where ratios swing wildly on one extra sale.
        if max(recent, prior) < 5:
            continue

        ratio = recent / prior
        if ratio >= SPIKE_FACTOR:
            direction, change = "spike", f"{(ratio - 1) * 100:.0f}% more"
        elif ratio <= SLUMP_FACTOR:
            direction, change = "slump", f"{(1 - ratio) * 100:.0f}% less"
        else:
            continue

        findings.append({
            "product_id": product.id,
            "product_name": product.name,
            "base_unit": product.base_unit,
            "direction": direction,
            "recent_quantity": round(recent, 1),
            "prior_quantity": round(prior, 1),
            "ratio": round(ratio, 2),
            "message": (
                f"{product.name} moved {change} in the last {window_days} days "
                f"({recent:g} vs {prior:g} {product.base_unit})."
            ),
        })

    findings.sort(key=lambda f: abs(f["ratio"] - 1), reverse=True)
    return findings


def movers(db: Session, business_id: UUID, window_days: int = 14) -> dict:
    rows = []
    for product in list_products(db, business_id):
        usage = float(average_daily_usage(db, product.id, window_days))
        rows.append({
            "product_id": product.id,
            "product_name": product.name,
            "base_unit": product.base_unit,
            "avg_daily_usage": round(usage, 2),
            "current_quantity": float(product.current_quantity),
        })
    rows.sort(key=lambda r: r["avg_daily_usage"], reverse=True)
    fast = [r for r in rows if r["avg_daily_usage"] > 0][:5]
    fast_ids = {r["product_id"] for r in fast}
    # The slow list is the tail of the same ranking, not an absolute threshold:
    # in a shop where everything sells, "slowest" is still worth seeing.
    slow = [r for r in rows if r["product_id"] not in fast_ids]
    return {
        "fast_moving": fast,
        "slow_moving": sorted(slow, key=lambda r: r["avg_daily_usage"])[:5],
    }


def period_totals(db: Session, business_id: UUID, start: datetime, end: datetime,
                  event_types: set[EventType]) -> list[dict]:
    """Per-product totals for a set of event types over a window."""
    rows = db.execute(
        select(
            Product.id, Product.name, Product.base_unit,
            func.sum(func.abs(InventoryEvent.delta)),
            func.count(InventoryEvent.id),
        )
        .join(InventoryEvent, InventoryEvent.product_id == Product.id)
        .where(
            InventoryEvent.business_id == business_id,
            InventoryEvent.event_type.in_(list(event_types)),
            InventoryEvent.occurred_at >= start,
            InventoryEvent.occurred_at < end,
        )
        .group_by(Product.id, Product.name, Product.base_unit)
        .order_by(func.sum(func.abs(InventoryEvent.delta)).desc())
    ).all()

    return [
        {
            "product_id": pid,
            "product_name": name,
            "base_unit": unit,
            "quantity": round(float(total), 1),
            "event_count": count,
        }
        for pid, name, unit, total, count in rows
    ]
