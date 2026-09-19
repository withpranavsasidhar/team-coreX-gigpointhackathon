from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_business
from app.database import get_db
from app.models import Business
from app.schemas import InsightsOut, QueryAnswerOut, QueryRequest
from app.services import insights_service, query_engine

router = APIRouter(tags=["intelligence"])


@router.post("/query", response_model=QueryAnswerOut)
def ask_question(
    payload: QueryRequest,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    result = query_engine.ask(db, business, payload.question, payload.reply_language)
    return QueryAnswerOut(
        intent=result.intent,
        answer=result.answer,
        visual=result.visual,
        items=result.items,
        facts=result.facts,
        product_id=result.product_id,
        product_name=result.product_name,
        window_label=result.window_label,
        grounded_by=result.grounded_by,
    )


@router.get("/alerts", response_model=list[dict])
def get_alerts(
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    return insights_service.alerts(db, business.id)


@router.get("/analytics", response_model=InsightsOut)
def get_analytics(
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    velocity = insights_service.movers(db, business.id)
    return InsightsOut(
        alerts=insights_service.alerts(db, business.id),
        reorder_recommendations=insights_service.reorder_list(db, business.id),
        unusual_movement=insights_service.unusual_movement(db, business.id),
        fast_moving=velocity["fast_moving"],
        slow_moving=velocity["slow_moving"],
    )
