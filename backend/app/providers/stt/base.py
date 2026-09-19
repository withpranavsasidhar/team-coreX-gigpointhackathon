from abc import ABC, abstractmethod


class SpeechToTextProvider(ABC):
    """Swappable speech backend.

    The MVP transcribes in the browser, so only text crosses the network and no
    audio is ever uploaded or stored. This interface exists so a server-side
    engine can be added later without touching the voice pipeline.
    """

    name: str = "base"
    #: True when the client is expected to send text rather than audio.
    client_side: bool = False

    @abstractmethod
    def transcribe(self, audio: bytes, language_hint: str | None = None) -> str:
        ...


class BrowserPassthroughProvider(SpeechToTextProvider):
    name = "browser_passthrough"
    client_side = True

    def transcribe(self, audio: bytes, language_hint: str | None = None) -> str:
        raise NotImplementedError(
            "Speech is transcribed in the browser for this deployment; "
            "the server receives text, not audio."
        )
