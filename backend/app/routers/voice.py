from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.core.dependencies import require_business
from app.database import get_db
from app.models import Business
from app.providers.ai import agent_status, get_ai_provider
from app.providers.stt import get_stt_provider
from app.providers.translation import get_translation_provider
from app.schemas import VoiceCapabilitiesOut, VoiceInterpretationOut, VoiceProcessRequest
from app.services.vocabulary import SUPPORTED_LANGUAGES
from app.services import voice_service

router = APIRouter(prefix="/voice", tags=["voice"])


@router.get("/capabilities", response_model=VoiceCapabilitiesOut)
def capabilities():
    """Lets the client tell the user plainly which engine is answering."""
    ai = get_ai_provider()
    stt = get_stt_provider()
    agent = agent_status()
    translator = get_translation_provider()

    return VoiceCapabilitiesOut(
        ai_provider=ai.name,
        llm_enabled=ai.is_llm,
        stt_provider=stt.name,
        stt_is_client_side=stt.client_side,
        confidence_threshold=settings.confidence_threshold,
        clarification_threshold=settings.clarification_threshold,
        degraded_reason=agent["reason"],
        supported_languages=SUPPORTED_LANGUAGES,
        agent_available=agent["agent_available"],
        agent_model=agent["model"] if agent["agent_available"] else None,
        translation_provider=translator.name,
        translation_available=translator.available,
    )


@router.post("/process", response_model=VoiceInterpretationOut)
def process_voice(
    payload: VoiceProcessRequest,
    business: Business = Depends(require_business),
    db: Session = Depends(get_db),
):
    return voice_service.process_transcript(
        db, business, payload.transcript, payload.language_hint, payload.reply_language
    )
