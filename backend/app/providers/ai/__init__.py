from functools import lru_cache

from app.config import settings
from app.providers.ai.base import (
    AIExtractionProvider, AIProviderError, ChatTurn, ExtractedEvent, ToolCall,
)
from app.providers.ai.rule_based import RuleBasedExtractionProvider


@lru_cache(maxsize=1)
def get_ai_provider() -> AIExtractionProvider:
    """Pick the language backend from config.

    Order of preference: an OpenAI-compatible endpoint (the conversational
    agent), then Anthropic extraction, then the deterministic rule engine.

    The rule engine is a real fallback, not a pretend one: it genuinely
    understands the trained vocabulary, and reports `is_llm = False` and
    `supports_tools = False` so the UI can say which engine answered.
    """
    if settings.ai_api_key.strip() and settings.ai_model.strip():
        from app.providers.ai.openai_compatible import OpenAICompatibleProvider

        try:
            return OpenAICompatibleProvider()
        except AIProviderError:
            # Misconfiguration must not take the app down; capabilities will
            # report that the agent is unavailable.
            return RuleBasedExtractionProvider()

    if settings.ai_provider == "anthropic" and settings.anthropic_api_key.strip():
        from app.providers.ai.anthropic_provider import AnthropicExtractionProvider

        return AnthropicExtractionProvider()

    return RuleBasedExtractionProvider()


def agent_status() -> dict:
    """Plain truth about the agent, for /voice/capabilities and Settings."""
    provider = get_ai_provider()
    configured = bool(settings.ai_api_key.strip() and settings.ai_model.strip())
    return {
        "provider": provider.name,
        "model": settings.ai_model.strip() or settings.nlu_model,
        "is_llm": provider.is_llm,
        "agent_available": provider.supports_tools,
        "configured": configured,
        "reason": (
            None
            if provider.supports_tools
            else (
                "AI_API_KEY and AI_MODEL are set but the provider could not start."
                if configured
                else "AI is not configured yet. Set AI_API_KEY and AI_MODEL to enable the A.R.I.A. agent."
            )
        ),
    }


__all__ = [
    "AIExtractionProvider", "AIProviderError", "ChatTurn", "ExtractedEvent",
    "ToolCall", "get_ai_provider", "agent_status",
]
