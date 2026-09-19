from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessNotFound, ValidationFailed
from app.database import get_db
from app.models import Business


def require_business(
    business_id: UUID,
    x_user_id: str | None = Header(None, alias="X-User-Id"),
    user_id: str | None = None,
    db: Session = Depends(get_db),
) -> Business:
    """Every data route is scoped through here, so an unscoped query is not expressible."""
    business = db.execute(select(Business).where(Business.id == business_id)).scalar_one_or_none()
    if not business:
        raise BusinessNotFound("Unknown business. Complete business setup first.")

    auth_user_id = x_user_id or user_id
    if auth_user_id and business.owner_id:
        if str(business.owner_id) != str(auth_user_id):
            raise ValidationFailed("You do not have access to this business.")

    return business


