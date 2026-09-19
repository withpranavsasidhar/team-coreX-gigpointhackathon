"""Authentication and Multi-Business user account service.

Provides secure password hashing via PBKDF2-HMAC-SHA256 and multi-business
management per user account.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationFailed
from app.models import Business, User


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a random 16-byte salt."""
    if not password or len(password) < 4:
        raise ValidationFailed("Password must be at least 4 characters long.")
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    )
    return f"pbkdf2_sha256$100000${salt}${derived.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plain password against a stored PBKDF2 hash."""
    if not password or not hashed or "$" not in hashed:
        return False
    parts = hashed.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False
    _, iterations_str, salt, target_hex = parts
    try:
        iterations = int(iterations_str)
        derived = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
        )
        return hmac.compare_digest(derived.hex(), target_hex)
    except Exception:
        return False


def normalize_phone(phone: str) -> str:
    """Clean phone number digits."""
    digits = "".join(c for c in str(phone or "") if c.isdigit())
    if not digits:
        raise ValidationFailed("Please enter a valid mobile number.")
    return digits


def register_user(
    db: Session,
    *,
    name: str,
    phone: str,
    password: str,
    email: str = "",
    preferred_language: str = "en",
) -> User:
    """Register a new user account by mobile number."""
    cleaned_phone = normalize_phone(phone)
    name = (name or "").strip()
    if not name:
        raise ValidationFailed("Full name is required.")

    existing = db.execute(
        select(User).where(User.phone == cleaned_phone)
    ).scalars().first()
    if existing:
        raise ValidationFailed("An account with this mobile number already exists. Please sign in.")

    user = User(
        name=name,
        phone=cleaned_phone,
        password_hash=hash_password(password),
        email=email.strip(),
        preferred_language=preferred_language,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, phone: str, password: str) -> User:
    """Authenticate user with mobile number and password."""
    cleaned_phone = normalize_phone(phone)
    user = db.execute(
        select(User).where(User.phone == cleaned_phone)
    ).scalars().first()

    if not user or not verify_password(password, user.password_hash):
        raise ValidationFailed("Invalid mobile number or password.")

    return user


def get_user_businesses(db: Session, user_id: UUID) -> Sequence[Business]:
    """Get all businesses owned by a user account."""
    businesses = db.execute(
        select(Business)
        .where(Business.owner_id == user_id)
        .order_by(Business.created_at.desc())
    ).scalars().all()

    # If the user is linked via business_id but owner_id wasn't set on legacy user
    user = db.get(User, user_id)
    if user and user.business_id:
        linked = db.get(Business, user.business_id)
        if linked and linked not in businesses:
            businesses = list(businesses) + [linked]

    return businesses
