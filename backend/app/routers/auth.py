"""Authentication and Account API endpoints.

Handles User Registration, Login, and Multi-Business association.
"""
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationFailed
from app.database import get_db
from app.models import Business, User
from app.schemas import BusinessOut, BusinessSummaryOut
from app.services import auth_service, onboarding_service

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2)
    phone: str = Field(min_length=10)
    password: str = Field(min_length=4)
    confirm_password: str = Field(min_length=4)
    email: str = ""
    preferred_language: str = "en"


class LoginRequest(BaseModel):
    phone: str = Field(min_length=10)
    password: str = Field(min_length=4)


class CreateBusinessForUserRequest(BaseModel):
    user_id: UUID
    business_name: str
    business_type: str
    location: str = ""
    default_language: str = "en"
    seed_catalogue: bool = True
    seed_demo_history: bool = False


class UserOut(BaseModel):
    id: UUID
    name: str
    phone: str
    email: str
    preferred_language: str


class LoginResponse(BaseModel):
    user: UserOut
    businesses: list[BusinessOut]


@router.post("/register", response_model=LoginResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user account."""
    if payload.password != payload.confirm_password:
        raise ValidationFailed("Passwords do not match.")

    user = auth_service.register_user(
        db,
        name=payload.name,
        phone=payload.phone,
        password=payload.password,
        email=payload.email,
        preferred_language=payload.preferred_language,
    )

    return {
        "user": user,
        "businesses": [],
    }


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user account and return owned businesses."""
    user = auth_service.authenticate_user(db, phone=payload.phone, password=payload.password)
    user_businesses = auth_service.get_user_businesses(db, user.id)

    return {
        "user": user,
        "businesses": user_businesses,
    }


@router.get("/user/{user_id}/businesses", response_model=list[BusinessOut])
def list_user_businesses(user_id: UUID, db: Session = Depends(get_db)):
    """List all businesses belonging to a user account."""
    return auth_service.get_user_businesses(db, user_id)


@router.post("/user/{user_id}/businesses", response_model=BusinessSummaryOut, status_code=201)
def create_user_business(
    user_id: UUID,
    payload: CreateBusinessForUserRequest,
    db: Session = Depends(get_db),
):
    """Create a new business workspace under an existing user account."""
    user = db.get(User, user_id)
    if not user:
        raise ValidationFailed("User account not found.")

    business = onboarding_service.create_business(
        db,
        business_name=payload.business_name,
        business_type=payload.business_type,
        location=payload.location,
        default_language=payload.default_language,
        seed_catalogue=payload.seed_catalogue,
    )
    business.owner_id = user.id
    if not user.business_id:
        user.business_id = business.id

    if payload.seed_demo_history:
        onboarding_service.seed_demo_history(db, business)

    db.commit()
    db.refresh(business)
    return onboarding_service.business_summary(db, business)
