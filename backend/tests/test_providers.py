"""Provider layer: honest reporting, language detection, and the guarantee that
an unconfigured provider never pretends to be a configured one."""
import pytest

from app.providers.ai import agent_status, get_ai_provider
from app.providers.ai.base import AIProviderError
from app.providers.ai.rule_based import RuleBasedExtractionProvider
from app.providers.translation import (
    NullTranslationProvider, TranslationError, get_translation_provider,
)
from app.services.language import detect_language


# --- AI provider selection ------------------------------------------------

def test_without_a_key_the_rule_engine_is_used_and_declares_itself():
    get_ai_provider.cache_clear()
    provider = get_ai_provider()
    assert isinstance(provider, RuleBasedExtractionProvider)
    assert provider.is_llm is False
    assert provider.supports_tools is False


def test_rule_engine_refuses_to_fake_a_conversation():
    provider = RuleBasedExtractionProvider()
    with pytest.raises(AIProviderError) as exc:
        provider.chat([{"role": "user", "content": "hello"}])
    assert "AI_API_KEY" in str(exc.value)


def test_agent_status_tells_the_truth_when_unconfigured():
    get_ai_provider.cache_clear()
    status = agent_status()
    assert status["agent_available"] is False
    assert status["configured"] is False
    assert "not configured" in status["reason"].lower()


def test_openai_provider_refuses_to_start_without_credentials(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "ai_api_key", "")
    from app.providers.ai.openai_compatible import OpenAICompatibleProvider
    with pytest.raises(AIProviderError):
        OpenAICompatibleProvider()


def test_openai_provider_refuses_to_start_without_a_model(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "ai_api_key", "test-key")
    monkeypatch.setattr(settings, "ai_model", "")
    from app.providers.ai.openai_compatible import OpenAICompatibleProvider
    with pytest.raises(AIProviderError) as exc:
        OpenAICompatibleProvider()
    assert "AI_MODEL" in str(exc.value)


# --- translation ----------------------------------------------------------

def test_translation_is_off_by_default():
    get_translation_provider.cache_clear()
    provider = get_translation_provider()
    assert isinstance(provider, NullTranslationProvider)
    assert provider.available is False


def test_unconfigured_translation_raises_rather_than_returning_the_input():
    provider = NullTranslationProvider()
    with pytest.raises(TranslationError):
        provider.translate("hello", target="te")


def test_language_detection_works_without_any_vendor():
    provider = NullTranslationProvider()
    assert provider.detect_language("Rendu cartons Coke vachayi").startswith(("te", "en"))


# --- language detection (the existing engine, unchanged) ------------------

@pytest.mark.parametrize("text,expected_part", [
    ("Add five bags of rice", "en"),
    ("Rendu cartons Coke vachayi", "te"),
    ("రెండు కార్టన్లు వచ్చాయి", "te"),
    ("पांच बोरी चावल आया", "hi"),
])
def test_detects_language_and_code_switching(text, expected_part):
    assert expected_part in detect_language(text)
