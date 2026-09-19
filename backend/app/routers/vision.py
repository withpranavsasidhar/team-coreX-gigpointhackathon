"""A.R.I.A. Vision endpoints.

Added alongside the existing A.R.I.A. routes, under the same /aria prefix
family. Nothing here replaces or re-implements an existing endpoint: analysis
is new work, and applying a reading delegates to the existing tool layer.
"""
import json
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import require_business
from app.database import get_db
from app.models import Business, VisionAnalysis
from app.providers.vision import VisionError, VisionUnavailable, vision_status
from app.services import vision_service

router = APIRouter(prefix="/aria/vision", tags=["vision"])


class VisionAnalyzeRequest(BaseModel):
    # A browser data URI. Validated and size-checked before anything is sent on.
    image: str = Field(min_length=32)
    hint: str = ""
    conversation_id: UUID | None = None


class VisionApplyRequest(BaseModel):
    analysis_id: UUID
    # What the owner approved after reviewing — not what the model read.
    items: list[dict]
    action: str = "add_stock"


@router.get("/status")
def status():
    """Whether Vision can run here, stated plainly."""
    return vision_status()


@router.post("/analyze")
def analyze(
    payload: VisionAnalyzeRequest,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    """Read an image. Never writes to inventory."""
    try:
        return vision_service.analyze_image(
            db, business, payload.image,
            hint=payload.hint, conversation_id=payload.conversation_id,
        )
    except VisionUnavailable as exc:
        return {"available": False, "error": str(exc), "items": [],
                "summary": "A.R.I.A. Vision requires a vision-capable AI model.",
                "counts": {"total": 0, "ready": 0, "needs_attention": 0}}
    except VisionError as exc:
        return {"available": True, "error": str(exc), "items": [],
                "summary": str(exc),
                "counts": {"total": 0, "ready": 0, "needs_attention": 0}}


@router.post("/apply")
def apply(
    payload: VisionApplyRequest,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    """Apply confirmed lines through the existing inventory tools."""
    try:
        return vision_service.apply_analysis(
            db, business, payload.analysis_id, payload.items, payload.action
        )
    except VisionError as exc:
        return {"error": str(exc), "applied": [], "failed": [],
                "counts": {"applied": 0, "failed": 0},
                "summary": "Nothing was changed."}


@router.get("/analyses")
def list_analyses(
    limit: int = 20,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    """Recent readings, so a follow-up can refer to the last image."""
    rows = db.execute(
        select(VisionAnalysis)
        .where(VisionAnalysis.business_id == business.id)
        .order_by(VisionAnalysis.created_at.desc())
        .limit(min(limit, 50))
    ).scalars().all()

    return {"analyses": [
        {
            "analysis_id": str(r.id),
            "document_type": r.document_type,
            "language": r.detected_language,
            "readable": r.readable,
            "notes": r.notes,
            "status": r.status,
            "item_count": len(json.loads(r.items or "[]")),
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]}


@router.get("/analyses/{analysis_id}")
def get_analysis(
    analysis_id: UUID,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    """One stored reading, for review or a follow-up question."""
    try:
        record = vision_service.get_analysis(db, business, analysis_id)
    except VisionError as exc:
        return {"error": str(exc)}

    return {
        "analysis_id": str(record.id),
        "document_type": record.document_type,
        "language": record.detected_language,
        "readable": record.readable,
        "quality_issues": json.loads(record.quality_issues or "[]"),
        "notes": record.notes,
        "items": json.loads(record.items or "[]"),
        "invoice": json.loads(record.invoice) if record.invoice else None,
        "status": record.status,
        "provider": record.provider,
        "model": record.model,
        "created_at": record.created_at.isoformat(),
    }
