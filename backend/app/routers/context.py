"""Business context and onboarding: which trade this is, and what that implies."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_business
from app.core.exceptions import ValidationFailed
from app.database import get_db
from app.models import Business
from app.schemas import (
    BusinessOnboard, BusinessOut, BusinessSummaryOut, BusinessTypeOut,
)
from app.services import business_context, onboarding_service

router = APIRouter(tags=["context"])


@router.get("/business-types", response_model=list[BusinessTypeOut])
def list_business_types():
    """The onboarding menu of trades A.R.I.A. already knows how to run."""
    return business_context.describe_types()


@router.post("/business-types/detect")
def detect_business_type(payload: dict):
    """Map a spoken sentence — "I run a bakery" — onto a known trade.

    Returns a null key rather than a guess when the trade is unfamiliar, so the
    caller asks instead of configuring the wrong catalogue.
    """
    text = str(payload.get("text", ""))
    key = business_context.match_type_from_speech(text)
    if not key:
        return {"matched": False, "key": None, "label": None, "text": text}
    resolved = business_context.get_type(key)
    return {
        "matched": True,
        "key": resolved.key,
        "label": resolved.label,
        "descriptor": resolved.descriptor,
        "emoji": resolved.emoji,
        "starter_product_names": [p.name for p in resolved.starter_products],
        "units": list(resolved.units),
        "text": text,
    }


@router.post("/businesses/onboard", response_model=BusinessSummaryOut, status_code=201)
def onboard_business(payload: BusinessOnboard, db: Session = Depends(get_db)):
    """Create a business from a chosen trade or from what the owner said."""
    business_type = payload.business_type
    if not business_type and payload.spoken_description:
        business_type = business_context.match_type_from_speech(payload.spoken_description)
    if not business_type:
        raise ValidationFailed(
            "I could not tell what kind of business that is. Pick one from the list "
            "so I set up the right catalogue and units."
        )

    business = onboarding_service.create_business(
        db,
        business_name=payload.business_name,
        business_type=business_type,
        location=payload.location,
        default_language=payload.default_language,
        seed_catalogue=payload.seed_catalogue,
    )

    if payload.seed_demo_history:
        onboarding_service.seed_demo_history(db, business)

    return onboarding_service.business_summary(db, business)


@router.get("/businesses/summary", response_model=BusinessSummaryOut)
def business_summary(
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    """Everything the command centre needs to introduce this business."""
    return onboarding_service.business_summary(db, business)


@router.post("/businesses/adopt-catalogue", response_model=BusinessSummaryOut)
def adopt_catalogue(
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    """Add the trade's usual products to an existing business."""
    onboarding_service.adopt_starter_catalogue(db, business)
    return onboarding_service.business_summary(db, business)


@router.post("/businesses/seed-demo", response_model=BusinessSummaryOut)
def seed_demo(
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    """Write a few weeks of demo trading, clearly sourced as demo in the ledger."""
    onboarding_service.seed_demo_history(db, business)
    return onboarding_service.business_summary(db, business)


@router.get("/units")
def list_units(business: Business = Depends(require_business)):
    """Units this trade uses first, then the rest the system understands."""
    return {
        "units": business_context.units_for(business.business_type),
        "natural": list(business_context.get_type(business.business_type).units),
    }
