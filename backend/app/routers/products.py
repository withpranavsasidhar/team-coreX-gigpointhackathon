from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_business
from app.database import get_db
from app.models import Business, SUPPORTED_UNITS
from app.schemas import ProductCreate, ProductOut, ProductUpdate
from app.services import product_service
from app.services.event_engine import load_product

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/units")
def supported_units():
    return {"units": SUPPORTED_UNITS}


@router.post("", response_model=ProductOut, status_code=201)
def create_product(
    payload: ProductCreate,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    return product_service.create_product(db, business.id, payload)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: UUID,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    return load_product(db, business.id, product_id)


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    product = load_product(db, business.id, product_id)
    return product_service.update_product(db, product, payload)


@router.post("/{product_id}/archive", response_model=ProductOut)
def archive_product(
    product_id: UUID,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    product = load_product(db, business.id, product_id)
    return product_service.set_archived(db, product, True)


@router.post("/{product_id}/restore", response_model=ProductOut)
def restore_product(
    product_id: UUID,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    product = load_product(db, business.id, product_id)
    return product_service.set_archived(db, product, False)
