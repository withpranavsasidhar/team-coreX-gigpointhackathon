from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date


@dataclass
class ExtractedEvent:
    """An unvalidated proposal from the language layer.

    `product_guess` is a name, never an id — product identity is resolved
    against the database by the matcher, so the model cannot pick a product.
    """

    event_type: str
    product_guess: str
    quantity: float | None = None
    unit: str | None = None
    price: float | None = None
    customer: str | None = None
    payment_status: str = "NA"
    due_date: date | None = None
    confidence: float = 0.0
    normalized_text: str = ""
    detected_language: str = "en"
    provider: str = ""
    notes: list[str] = field(default_factory=list)


@dataclass
class ToolCall:
    """A tool the model wants run. Arguments are unvalidated model output."""

    id: str
    name: str
    arguments: dict


@dataclass
class ChatTurn:
    """One reply from the model: prose, tool calls, or both."""

    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"
    raw_message: dict | None = None


class AIProviderError(RuntimeError):
    """The model could not be reached or refused the request.

    Raised rather than swallowed: a failed call must surface as a failure, never
    as a plausible-looking answer.
    """


class AIExtractionProvider(ABC):
    """Swappable language-understanding backend. Selected at startup by config."""

    name: str = "base"

    @abstractmethod
    def extract_event(self, text: str, known_products: list[str]) -> ExtractedEvent:
        """Turn a transcript into a structured event proposal."""

    @abstractmethod
    def answer_question(self, question: str, facts: dict, language: str = "en") -> str:
        """Phrase an answer using only the supplied facts. Used from Phase 8."""

    @property
    def is_llm(self) -> bool:
        return False

    # --- Conversational agent capability (Phase 10) ------------------------
    # Separate from extraction on purpose: the rule-based provider implements
    # extraction perfectly well but cannot hold a tool-calling conversation, and
    # must report that honestly rather than emulate it.

    @property
    def supports_tools(self) -> bool:
        return False

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.2,
    ) -> ChatTurn:
        """Run one model turn over a message history, optionally with tools."""
        raise AIProviderError(
            f"{self.name} cannot hold a tool-calling conversation. "
            "Configure AI_API_KEY and AI_MODEL to enable the A.R.I.A. agent."
        )
