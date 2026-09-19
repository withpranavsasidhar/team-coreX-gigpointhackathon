"""Seeds a demo kirana store with three weeks of realistic trading history.

Every stock number that appears in the app is produced by replaying these events
through the same Business Event Engine the live API uses — nothing is written
directly to a stock column.

Run with:  python seed.py
"""
import random
from datetime import datetime, timedelta

from app.database import Base, SessionLocal, engine
from app.models import Business, EventType, InventoryEvent, PaymentStatus, User
from app.schemas import ProductCreate, UnitConversionIn
from app.services.event_engine import record_event
from app.services.product_service import create_product

random.seed(20260919)

HISTORY_DAYS = 21

# name, category, unit, opening, minimum, reorder_qty, price, conversions,
# daily_sales_range, restock_trigger, restock_amount, supplier_gap_days
PRODUCTS = [
    ("Rice", "grains", "bags", 45, 15, 40, 1250, [], (1, 3), 30, 45, 7),
    ("Wheat", "grains", "kg", 200, 40, 120, 42, [("quintals", 100)], (3, 9), 60, 150, 0),
    ("Cooking Oil", "essentials", "litres", 40, 20, 60, 145, [], (1, 3), 25, 50, 8),
    ("Biscuits", "snacks", "pieces", 400, 100, 240, 10, [("cartons", 24)], (8, 20), 150, 240, 0),
    ("Coke", "beverages", "pieces", 240, 60, 120, 40, [("cartons", 24)], (5, 15), 100, 240, 0),
    ("Maggi", "snacks", "pieces", 240, 72, 144, 14, [("boxes", 12)], (4, 12), 90, 144, 0),
    ("Milk", "dairy", "litres", 60, 15, 30, 32, [], (4, 10), 30, 60, 0),
    ("Eggs", "dairy", "pieces", 300, 72, 180, 6, [("dozens", 12)], (8, 20), 120, 240, 0),
]

CREDIT_CUSTOMERS = ["Ramesh", "Lakshmi", "Suresh"]

# A festival run on cold drinks in the closing days — gives the unusual-movement
# detector a real shift to find rather than a manufactured one.
SURGE: dict[str, tuple[int, float]] = {"Coke": (6, 2.4)}


def _at(day, hour, now):
    """Event time on `day`, never placed in the future."""
    stamp = day.replace(hour=hour, minute=random.randint(0, 59), second=0, microsecond=0)
    return min(stamp, now - timedelta(minutes=5))


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    business = Business(
        business_name="Ravi Kirana Store",
        business_type="kirana",
        location="Hyderabad",
        default_language="en",
    )
    db.add(business)
    db.commit()
    db.refresh(business)

    db.add(User(business_id=business.id, name="Ravi", phone="+91 98765 43210", preferred_language="en"))
    db.commit()

    catalog = []
    for (name, category, unit, opening, minimum, reorder, price,
         conversions, sales_range, trigger, restock_amt, gap) in PRODUCTS:
        product = create_product(
            db,
            business.id,
            ProductCreate(
                name=name,
                category=category,
                base_unit=unit,
                opening_stock=opening,
                minimum_quantity=minimum,
                reorder_quantity=reorder,
                price=price,
                conversions=[UnitConversionIn(unit_name=u, factor_to_base_unit=f) for u, f in conversions],
            ),
        )
        catalog.append((product, sales_range, trigger, restock_amt, gap))

    # Run the history through to today so "what did I sell today" has data.
    now = datetime.utcnow()
    start = now - timedelta(days=HISTORY_DAYS - 1)

    # Backdate opening stock so the ledger reads chronologically from day zero.
    for event in db.query(InventoryEvent).filter(InventoryEvent.source == "opening").all():
        event.occurred_at = start - timedelta(hours=2)
    db.commit()

    for day_offset in range(HISTORY_DAYS):
        day = start + timedelta(days=day_offset)
        days_remaining = HISTORY_DAYS - day_offset

        for product, sales_range, trigger, restock_amt, gap in catalog:
            on_hand = float(product.current_quantity)

            # Shopkeeper reorders when the shelf runs low, unless the supplier
            # has not delivered recently (which is what drains Rice and Oil).
            if on_hand < trigger and days_remaining > gap:
                record_event(
                    db,
                    business_id=business.id,
                    product=product,
                    event_type=EventType.PURCHASE,
                    quantity=restock_amt,
                    unit=product.base_unit,
                    price=float(product.price) * restock_amt * 0.8,
                    payment_status=PaymentStatus.PAID,
                    occurred_at=_at(day, 9, now),
                    normalized_text=f"Purchased {restock_amt} {product.base_unit} of {product.name}",
                    commit=False,
                )

            for _ in range(random.randint(1, 3)):
                available = float(product.current_quantity)
                if available <= 0:
                    break
                qty = round(random.randint(*sales_range) / random.choice([1, 1, 1, 2]), 1)
                surge = SURGE.get(product.name)
                if surge and days_remaining <= surge[0]:
                    qty = round(qty * surge[1], 1)
                qty = min(qty, available)
                if qty <= 0:
                    continue

                is_credit = random.random() < 0.08
                record_event(
                    db,
                    business_id=business.id,
                    product=product,
                    event_type=EventType.CREDIT_SALE if is_credit else EventType.SALE,
                    quantity=qty,
                    unit=product.base_unit,
                    customer_name=random.choice(CREDIT_CUSTOMERS) if is_credit else None,
                    price=round(float(product.price) * qty, 2),
                    payment_status=PaymentStatus.CREDIT if is_credit else PaymentStatus.PAID,
                    due_date=(day + timedelta(days=3)).date() if is_credit else None,
                    occurred_at=_at(day, random.randint(10, 19), now),
                    normalized_text=f"{'Credit sale of' if is_credit else 'Sold'} {qty} {product.base_unit} of {product.name}",
                    commit=False,
                )

            spoil_chance = 0.12 if product.name in ("Milk", "Eggs") else 0.04
            available = float(product.current_quantity)
            if random.random() < spoil_chance and available > 5:
                record_event(
                    db,
                    business_id=business.id,
                    product=product,
                    event_type=EventType.DAMAGE,
                    quantity=min(random.randint(1, 4), available),
                    unit=product.base_unit,
                    occurred_at=_at(day, 20, now),
                    normalized_text=f"Recorded damage on {product.name}",
                    commit=False,
                )

        db.commit()

    from app.services.inventory_service import product_status

    print(f"\nSeeded business: {business.business_name}  id={business.id}")
    print(f"\n{'PRODUCT':<14}{'STOCK':>9}  {'UNIT':<9}{'STATUS':<12}{'DAYS LEFT':>10}")
    print("-" * 58)
    for product, *_ in catalog:
        db.refresh(product)
        info = product_status(db, product)
        days = info["estimated_days_to_stockout"]
        print(
            f"{product.name:<14}{info['current_quantity']:>9.1f}  {product.base_unit:<9}"
            f"{info['status']:<12}{(f'{days:.1f}' if days is not None else '—'):>10}"
        )

    print(f"\n{db.query(InventoryEvent).count()} inventory events recorded over {HISTORY_DAYS} days.")
    db.close()


if __name__ == "__main__":
    seed()
