from functools import lru_cache

from app.config import settings
from app.providers.stt.base import BrowserPassthroughProvider, SpeechToTextProvider


@lru_cache(maxsize=1)
def get_stt_provider() -> SpeechToTextProvider:
    # Only the browser provider ships today; the registry keeps the seam open.
    registry = {"browser_passthrough": BrowserPassthroughProvider}
    provider_cls = registry.get(settings.stt_provider, BrowserPassthroughProvider)
    return provider_cls()


__all__ = ["SpeechToTextProvider", "get_stt_provider"]
