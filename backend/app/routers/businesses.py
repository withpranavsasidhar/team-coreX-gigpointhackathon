from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import require_business
from app.core.exceptions import BusinessNotFound
from app.database import get_db
from app.models import Business
from app.schemas import BusinessCreate, BusinessOut


router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.post("", response_model=BusinessOut, status_code=201)
def create_business(payload: BusinessCreate, db: Session = Depends(get_db)):
    business = Business(**payload.model_dump())
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


@router.get("/current", response_model=BusinessOut)
def current_business(
    x_user_id: UUID | None = Header(None, alias="X-User-Id"),
    db: Session = Depends(get_db),
):
    """Resolve active business for authenticated user session."""
    if x_user_id:
        user_biz = db.execute(
            select(Business).where(Business.owner_id == x_user_id).order_by(Business.created_at.desc())
        ).scalars().first()
        if user_biz:
            return user_biz
    raise BusinessNotFound("No authenticated business found. Please sign in.")



@router.get("/{business_id}", response_model=BusinessOut)
def get_business(business: Business = Depends(require_business)):
    return business

