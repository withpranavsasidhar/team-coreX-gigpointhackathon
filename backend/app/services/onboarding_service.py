"""Turning "I run a bakery" into a working business.

Onboarding is where the Business Context Engine earns its keep: the trade the
owner names decides the catalogue, the units and the vocabulary, without a
single line of trade-specific application code.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Business, Customer, EventType, InventoryEvent, PaymentStatus, Product, UnitConversion,
)
from app.services import business_context
from app.services.event_engine import record_event
from app.services.units import to_decimal


def create_business(
    db: Session,
    *,
    business_name: str,
    business_type: str,
    location: str = "",
    default_language: str = "en",
    seed_catalogue: bool = True,
) -> Business:
    """Create a business and, unless told otherwise, stock its usual shelves."""
    resolved = business_context.get_type(business_type)

    business = Business(
        business_name=business_name.strip() or resolved.label,
        business_type=resolved.key,
        location=location.strip(),
        default_language=default_language,
    )
    db.add(business)
    db.flush()

    if seed_catalogue:
        adopt_starter_catalogue(db, business, commit=False)

    db.commit()
    db.refresh(business)
    return business


def adopt_starter_catalogue(db: Session, business: Business, commit: bool = True) -> list[Product]:
    """Add the trade's usual products, skipping any the owner already has.

    Products start at zero stock. Nothing is invented as having been bought or
    sold — an empty shelf is honest, a fabricated history is not.
    """
    resolved = business_context.get_type(business.business_type)

    existing = {
        name.lower()
        for name in db.execute(
            select(Product.name).where(Product.business_id == business.id)
        ).scalars().all()
    }

    created: list[Product] = []
    for starter in resolved.starter_products:
        if starter.name.lower() in existing:
            continue

        product = Product(
            business_id=business.id,
            name=starter.name,
            category=starter.category,
            base_unit=starter.base_unit,
            current_quantity=0,
            minimum_quantity=to_decimal(starter.minimum_quantity),
            reorder_quantity=to_decimal(starter.reorder_quantity),
            price=to_decimal(starter.price),
        )
        db.add(product)
        db.flush()

        for unit_name, factor in starter.conversions:
            db.add(
                UnitConversion(
                    product_id=product.id,
                    unit_name=unit_name,
                    factor_to_base_unit=to_decimal(factor),
                )
            )
        created.append(product)

    if commit:
        db.commit()
    else:
        db.flush()
    return created


# --- Demo history ---------------------------------------------------------
# Used only when the owner explicitly asks for a worked example. Every row it
# writes is a real ledger event created through the real engine, and it is
# always labelled as demo data at the source. Nothing here is ever presented
# as having come from the owner's own voice.

DEMO_CUSTOMERS = ("Ramesh", "Lakshmi", "Srinivas", "Fatima", "Ravi Kumar")


def _at(day_offset: int, hour: int, now: datetime) -> datetime:
    stamp = (now - timedelta(days=day_offset)).replace(
        hour=hour, minute=random.randint(0, 59), second=0, microsecond=0
    )
    # Never write the future, even on the current day.
    return min(stamp, now - timedelta(minutes=5))


def seed_demo_history(db: Session, business: Business, days: int = 21) -> int:
    """Simulate a few weeks of trading so the analytics have something to read.

    Sales are clamped to stock actually on hand and restocks are triggered by
    the threshold, so the resulting ledger obeys the same rules live trading
    would — no negative stock, no impossible movements.
    """
    products = db.execute(
        select(Product).where(Product.business_id == business.id, Product.is_archived.is_(False))
    ).scalars().all()
    if not products:
        return 0

    already = db.execute(
        select(func.count(InventoryEvent.id)).where(InventoryEvent.business_id == business.id)
    ).scalar_one()
    if already:
        return 0

    customers = [
        Customer(business_id=business.id, name=name) for name in DEMO_CUSTOMERS
    ]
    db.add_all(customers)
    db.flush()

    now = datetime.utcnow()
    rng = random.Random(f"{business.id}")
    written = 0

    for product in products:
        reorder = float(product.reorder_quantity) or 30.0
        minimum = float(product.minimum_quantity) or 10.0
        # A daily rate that makes the opening quantity last roughly the window.
        daily = max(reorder / 9.0, 0.5)

        opening = round(reorder * rng.uniform(1.1, 1.6), 1)
        record_event(
            db, business_id=business.id, product=product,
            event_type=EventType.STOCK_IN, quantity=opening, unit=product.base_unit,
            source="demo", normalized_text="Demo opening stock",
            occurred_at=_at(days - 1, 8, now), confidence=1.0, commit=False,
        )
        written += 1
        on_hand = opening

        for day in range(days - 2, -1, -1):
            # Weekend lift, as most neighbourhood shops see.
            weekday = (now - timedelta(days=day)).weekday()
            demand = daily * rng.uniform(0.6, 1.4) * (1.35 if weekday >= 5 else 1.0)

            for _ in range(rng.randint(1, 3)):
                if on_hand <= 0:
                    break
                qty = round(min(demand / 2, on_hand) * rng.uniform(0.4, 1.0), 1)
                if qty <= 0:
                    continue

                on_credit = rng.random() < 0.12
                customer = rng.choice(customers) if on_credit else None
                record_event(
                    db, business_id=business.id, product=product,
                    event_type=EventType.CREDIT_SALE if on_credit else EventType.SALE,
                    quantity=qty, unit=product.base_unit,
                    customer_name=customer.name if customer else None,
                    price=round(qty * float(product.price), 2),
                    payment_status=PaymentStatus.CREDIT if on_credit else PaymentStatus.PAID,
                    source="demo", normalized_text="Demo sale",
                    occurred_at=_at(day, rng.randint(9, 19), now),
                    confidence=1.0, commit=False,
                )
                on_hand -= qty
                written += 1

            # Occasional spoilage, which is what makes "why is stock low"
            # interesting to ask.
            if rng.random() < 0.05 and on_hand > 2:
                loss = round(min(on_hand * 0.03, 2), 1)
                record_event(
                    db, business_id=business.id, product=product,
                    event_type=EventType.DAMAGE, quantity=loss, unit=product.base_unit,
                    source="demo", normalized_text="Demo damage",
                    occurred_at=_at(day, 11, now), confidence=1.0, commit=False,
                )
                on_hand -= loss
                written += 1

            # Restock when the shelf drops to the threshold.
            if on_hand <= minimum and day > 0:
                record_event(
                    db, business_id=business.id, product=product,
                    event_type=EventType.PURCHASE, quantity=reorder, unit=product.base_unit,
                    price=round(reorder * float(product.price) * 0.78, 2),
                    source="demo", normalized_text="Demo restock",
                    occurred_at=_at(day, 8, now), confidence=1.0, commit=False,
                )
                on_hand += reorder
                written += 1

    db.commit()
    return written


def business_summary(db: Session, business: Business) -> dict:
    """What the command centre needs to introduce a business at a glance."""
    resolved = business_context.get_type(business.business_type)
    product_count = db.execute(
        select(func.count(Product.id)).where(
            Product.business_id == business.id, Product.is_archived.is_(False)
        )
    ).scalar_one()
    event_count = db.execute(
        select(func.count(InventoryEvent.id)).where(InventoryEvent.business_id == business.id)
    ).scalar_one()

    return {
        "id": business.id,
        "business_name": business.business_name,
        "business_type": business.business_type,
        "type_label": resolved.label,
        "type_emoji": resolved.emoji,
        "descriptor": resolved.descriptor,
        "location": business.location,
        "default_language": business.default_language,
        "units": business_context.units_for(business.business_type),
        "categories": list(resolved.categories),
        "sample_utterances": list(resolved.sample_utterances),
        "product_count": product_count,
        "event_count": event_count,
        "is_configured": product_count > 0,
    }
