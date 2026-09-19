"""Optional translation.

A.R.I.A. understands Telugu, Hindi and mixed speech as *meaning*, so
translation is deliberately not in the main path — translating "Rendu cartons
Coke vachayi" into English before understanding it would lose the business
intent, not clarify it.

Translation exists for the narrow cases where it genuinely helps: showing a
user-facing string in another language, or normalising text for a provider that
needs it. When it is not configured, callers are told so; nothing is faked.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from functools import lru_cache

from app.config import settings
from app.services.language import detect_language


class TranslationError(RuntimeError):
    """Translation was requested but could not be performed."""


class TranslationProvider(ABC):
    name: str = "base"
    available: bool = False

    @abstractmethod
    def detect_language(self, text: str) -> str:
        """Best-effort language code, or a composite like 'te-en'."""

    @abstractmethod
    def translate(self, text: str, target: str, source: str | None = None) -> str:
        """Translate, or raise TranslationError. Never returns the input silently."""

    def normalize_text(self, text: str) -> str:
        """Tidy a transcript without changing its language or meaning."""
        return " ".join((text or "").split())


class NullTranslationProvider(TranslationProvider):
    """The default. Detection still works — it is local and does not need a vendor."""

    name = "none"
    available = False

    def detect_language(self, text: str) -> str:
        return detect_language(text or "")

    def translate(self, text: str, target: str, source: str | None = None) -> str:
        raise TranslationError(
            "Translation is not configured. Set TRANSLATION_PROVIDER=google and "
            "GOOGLE_TRANSLATE_API_KEY to enable it."
        )


class GoogleTranslationProvider(TranslationProvider):
    """Google Cloud Translation v2. Credentials stay server-side."""

    name = "google"
    available = True
    ENDPOINT = "https://translation.googleapis.com/language/translate/v2"

    def __init__(self) -> None:
        self.api_key = settings.google_translate_api_key.strip()
        if not self.api_key:
            raise TranslationError("GOOGLE_TRANSLATE_API_KEY is not set.")

    def detect_language(self, text: str) -> str:
        """Local detection first: it recognises code-switching, which the API flattens.

        "Rendu cartons Coke vachayi" is Telugu *and* English; a vendor that must
        return a single code cannot express that, so the local detector wins
        whenever it sees a mix.
        """
        local = detect_language(text or "")
        if "-" in local:
            return local
        try:
            data = self._post(self.ENDPOINT + "/detect", {"q": text})
            detections = data["data"]["detections"][0][0]
            return detections.get("language") or local
        except (TranslationError, KeyError, IndexError, TypeError):
            return local

    def translate(self, text: str, target: str, source: str | None = None) -> str:
        if not (text or "").strip():
            return ""
        params = {"q": text, "target": target, "format": "text"}
        if source:
            params["source"] = source
        try:
            data = self._post(self.ENDPOINT, params)
            return data["data"]["translations"][0]["translatedText"]
        except (KeyError, IndexError, TypeError) as exc:
            raise TranslationError("Translation is temporarily unavailable.") from exc

    def _post(self, url: str, params: dict) -> dict:
        body = urllib.parse.urlencode({**params, "key": self.api_key}).encode()
        request = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            raise TranslationError("Translation is temporarily unavailable.") from exc
        except json.JSONDecodeError as exc:
            raise TranslationError("Translation returned an unreadable response.") from exc


@lru_cache(maxsize=1)
def get_translation_provider() -> TranslationProvider:
    if settings.translation_provider.strip().lower() == "google":
        try:
            return GoogleTranslationProvider()
        except TranslationError:
            return NullTranslationProvider()
    return NullTranslationProvider()


__all__ = [
    "TranslationProvider", "TranslationError", "NullTranslationProvider",
    "GoogleTranslationProvider", "get_translation_provider",
]
