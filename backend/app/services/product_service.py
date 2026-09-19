from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateProduct, ValidationFailed
from app.models import EventType, InventoryEvent, Product, UnitConversion
from app.schemas import ProductCreate, ProductUpdate
from app.services.event_engine import record_event
from app.services.units import to_decimal


def _assert_name_available(db: Session, business_id: UUID, name: str, exclude_id: UUID | None = None):
    stmt = select(Product).where(
        Product.business_id == business_id,
        func.lower(Product.name) == name.strip().lower(),
    )
    if exclude_id:
        stmt = stmt.where(Product.id != exclude_id)
    if db.execute(stmt).scalar_one_or_none():
        raise DuplicateProduct(f'A product named "{name}" already exists.')


def _apply_conversions(db: Session, product: Product, conversions) -> None:
    for existing in list(product.conversions):
        db.delete(existing)
    product.conversions = []
    for rule in conversions or []:
        if rule.unit_name == product.base_unit:
            raise ValidationFailed("A conversion rule cannot target the product's own base unit.")
        db.add(
            UnitConversion(
                product_id=product.id,
                unit_name=rule.unit_name,
                factor_to_base_unit=to_decimal(rule.factor_to_base_unit),
            )
        )


def create_product(db: Session, business_id: UUID, payload: ProductCreate) -> Product:
    _assert_name_available(db, business_id, payload.name)

    product = Product(
        business_id=business_id,
        name=payload.name.strip(),
        category=payload.category,
        base_unit=payload.base_unit,
        current_quantity=0,
        minimum_quantity=to_decimal(payload.minimum_quantity),
        reorder_quantity=to_decimal(payload.reorder_quantity),
        price=to_decimal(payload.price),
    )
    db.add(product)
    db.flush()

    _apply_conversions(db, product, payload.conversions)
    db.flush()
    db.refresh(product)

    # Opening stock is itself a ledger entry, so current stock stays fully
    # explainable as the sum of every event that ever touched this product.
    if payload.opening_stock and payload.opening_stock > 0:
        record_event(
            db,
            business_id=business_id,
            product=product,
            event_type=EventType.STOCK_IN,
            quantity=payload.opening_stock,
            unit=payload.base_unit,
            source="opening",
            normalized_text=f"Opening stock of {payload.opening_stock} {payload.base_unit}",
            commit=False,
        )

    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, payload: ProductUpdate) -> Product:
    data = payload.model_dump(exclude_unset=True)

    if "name" in data and data["name"]:
        _assert_name_available(db, product.business_id, data["name"], exclude_id=product.id)
        product.name = data["name"].strip()

    if data.get("base_unit") and data["base_unit"] != product.base_unit:
        has_events = db.execute(
            select(func.count(InventoryEvent.id)).where(InventoryEvent.product_id == product.id)
        ).scalar_one()
        if has_events:
            raise ValidationFailed(
                "The base unit cannot be changed after stock movements have been recorded, "
                "because past quantities were stored against the original unit."
            )
        product.base_unit = data["base_unit"]

    for field in ("category", "minimum_quantity", "reorder_quantity", "price"):
        if field in data and data[field] is not None:
            setattr(product, field, data[field])

    if "conversions" in data and data["conversions"] is not None:
        _apply_conversions(db, product, payload.conversions)

    db.commit()
    db.refresh(product)
    return product


def set_archived(db: Session, product: Product, archived: bool) -> Product:
    """Archive instead of delete — the ledger references this product forever."""
    product.is_archived = archived
    db.commit()
    db.refresh(product)
    return product
