from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_business
from app.database import get_db
from app.models import Business
from app.schemas import ProductHistoryOut, ProductStatusOut
from app.services import inventory_service
from app.services.event_engine import load_product, recompute_current_quantity

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=list[ProductStatusOut])
def current_inventory(
    include_archived: bool = False,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    products = inventory_service.list_products(db, business.id, include_archived)
    return [inventory_service.product_status(db, p) for p in products]


@router.get("/{product_id}/history", response_model=ProductHistoryOut)
def product_history(
    product_id: UUID,
    days: int = 30,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    product = load_product(db, business.id, product_id)
    return inventory_service.product_history(db, product, days)


@router.get("/{product_id}/verify")
def verify_stock(
    product_id: UUID,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    """Audit hook: proves the cached quantity still equals the sum of the ledger."""
    product = load_product(db, business.id, product_id)
    from_ledger = recompute_current_quantity(db, product)
    cached = product.current_quantity
    return {
        "product_id": product.id,
        "cached_quantity": float(cached),
        "ledger_quantity": float(from_ledger),
        "in_sync": float(cached) == float(from_ledger),
    }
