"""The canonical A.R.I.A. agent endpoint.

One entry point for conversation. When a real model is configured it runs the
tool-calling agent; when it is not, it says so and routes the turn to the
existing, tested deterministic engines rather than pretending to be an AI.

Which engine answered is always reported in `engine`, so the UI can tell the
truth about what the owner is talking to.
"""
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import require_business
from app.database import get_db
from app.models import Business
from app.providers.ai import agent_status, get_ai_provider
from app.services import aria_agent, query_engine, voice_service
from app.services.language import detect_language

router = APIRouter(prefix="/aria", tags=["aria"])


class AriaChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: UUID | None = None
    language: str | None = None
    source: str = "text"          # text | voice


class AriaConfirmRequest(BaseModel):
    action_id: UUID
    approved: bool = True


# Questions ask; commands assert. Used only by the fallback path, where the two
# deterministic engines are separate.
QUESTION_HINT = (
    "what", "why", "how", "who", "when", "where", "which", "show", "tell",
    "list", "is", "are", "do", "did", "does", "can", "entha", "enni", "kitna",
    "ఎం", "ఎందుకు", "ఎన్ని", "ఎవరు", "क्या", "क्यों", "कितना", "कौन",
)


def _looks_like_question(text: str) -> bool:
    lowered = (text or "").strip().lower()
    if lowered.endswith("?"):
        return True
    first = lowered.split()[0] if lowered.split() else ""
    return first in QUESTION_HINT or any(h in lowered for h in QUESTION_HINT[-8:])


@router.get("/status")
def status():
    """What the owner is actually talking to right now."""
    return agent_status()


@router.post("/chat")
def chat(
    payload: AriaChatRequest,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    provider = get_ai_provider()

    if provider.supports_tools:
        result = aria_agent.chat(
            db, business, payload.message,
            conversation_id=payload.conversation_id,
            language=payload.language, source=payload.source,
        )
        return {
            "response": result.response,
            "conversation_id": str(result.conversation_id),
            "language": result.language,
            "tool_calls": result.tool_calls,
            "requires_confirmation": result.requires_confirmation,
            "pending_action": result.pending_action,
            "status": result.status,
            "error": result.error,
            "engine": "agent",
            "provider": result.provider,
            "model": result.model,
        }

    # No model configured. Use the engines that do work, and say which.
    status_info = agent_status()
    language = payload.language or detect_language(payload.message)

    if _looks_like_question(payload.message):
        answer = query_engine.ask(db, business, payload.message, payload.language)
        return {
            "response": answer.answer,
            "conversation_id": str(payload.conversation_id) if payload.conversation_id else None,
            "language": language,
            "tool_calls": [],
            "requires_confirmation": False,
            "pending_action": None,
            "status": "completed",
            "error": None,
            "engine": "rule_engine",
            "provider": status_info["provider"],
            "model": None,
            "notice": status_info["reason"],
            "answer_payload": {
                "intent": answer.intent, "visual": answer.visual,
                "items": answer.items, "facts": answer.facts,
                "product_id": str(answer.product_id) if answer.product_id else None,
                "product_name": answer.product_name,
                "window_label": answer.window_label,
            },
        }

    interpretation = voice_service.process_transcript(
        db, business, payload.message,
        language_hint=payload.language, reply_language=payload.language,
        source=payload.source,
    )
    return {
        "response": interpretation["message"],
        "conversation_id": str(payload.conversation_id) if payload.conversation_id else None,
        "language": interpretation.get("detected_language", language),
        "tool_calls": [],
        "requires_confirmation": interpretation["status"] == "needs_confirmation",
        "pending_action": None,
        "status": (
            "completed" if interpretation["status"] in ("recorded", "amended")
            else "needs_confirmation" if interpretation["status"] == "needs_confirmation"
            else "needs_clarification" if interpretation["status"] == "needs_clarification"
            else "error"
        ),
        "error": None,
        "engine": "rule_engine",
        "provider": status_info["provider"],
        "model": None,
        "notice": status_info["reason"],
        "interpretation": interpretation,
    }


@router.post("/confirm")
def confirm(
    payload: AriaConfirmRequest,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    """Approve or cancel an action A.R.I.A. proposed."""
    result = aria_agent.confirm(db, business, payload.action_id, payload.approved)
    return {
        "response": result.response,
        "conversation_id": str(result.conversation_id),
        "tool_calls": result.tool_calls,
        "status": result.status,
        "error": result.error,
    }


@router.get("/tools")
def list_tools():
    """The tools A.R.I.A. may use, and which of them stop for confirmation."""
    from app.services import tools as tool_registry

    return {
        "tools": [
            {"name": t.name, "description": t.description, "writes": t.writes,
             "needs_confirmation": t.needs_confirmation, "tags": t.tags}
            for t in tool_registry.REGISTRY.values()
        ],
        "count": len(tool_registry.REGISTRY),
    }
