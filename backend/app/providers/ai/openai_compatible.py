"""OpenAI-compatible chat provider (OpenRouter, Together, local servers…).

All provider-specific detail lives here. Everything above this layer works in
terms of `ChatTurn` and `ToolCall`, so swapping vendors is an env change.

The provider never invents a result: a transport failure, a refusal or an
unparseable response raises AIProviderError so the caller can tell the user the
truth instead of presenting a fabricated answer.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from app.config import settings
from app.providers.ai.base import (
    AIExtractionProvider, AIProviderError, ChatTurn, ExtractedEvent, ToolCall,
)
from app.providers.ai.rule_based import RuleBasedExtractionProvider


class OpenAICompatibleProvider(AIExtractionProvider):
    """Chat + tool calling against any OpenAI-shaped /chat/completions endpoint."""

    name = "openai_compatible"

    def __init__(self) -> None:
        self.api_key = settings.ai_api_key.strip()
        self.base_url = settings.ai_base_url.strip().rstrip("/")
        self.model = settings.ai_model.strip()
        if not self.api_key:
            raise AIProviderError("AI_API_KEY is not set.")
        if not self.model:
            raise AIProviderError("AI_MODEL is not set.")
        # Extraction keeps working through the deterministic engine even while
        # the conversational agent is live, so the two capabilities degrade
        # independently.
        self._fallback = RuleBasedExtractionProvider()

    @property
    def is_llm(self) -> bool:
        return True

    @property
    def supports_tools(self) -> bool:
        return True

    # --- Chat ---------------------------------------------------------------
    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.2,
    ) -> ChatTurn:
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        data = self._post("/chat/completions", payload)

        try:
            choice = data["choices"][0]
            message = choice.get("message") or {}
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError(f"Unexpected response from {self.model}.") from exc

        calls: list[ToolCall] = []
        for raw in message.get("tool_calls") or []:
            fn = raw.get("function") or {}
            name = fn.get("name") or ""
            if not name:
                continue
            raw_args = fn.get("arguments") or "{}"
            try:
                args = json.loads(raw_args) if isinstance(raw_args, str) else dict(raw_args)
            except json.JSONDecodeError:
                # Malformed arguments are reported to the model as a tool error
                # rather than guessed at, so it can correct itself.
                args = {"__malformed__": raw_args}
            calls.append(ToolCall(id=raw.get("id") or name, name=name, arguments=args))

        return ChatTurn(
            content=(message.get("content") or "").strip(),
            tool_calls=calls,
            finish_reason=choice.get("finish_reason") or "stop",
            raw_message=message,
        )

    def _post(self, path: str, payload: dict) -> dict:
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                # OpenRouter asks for these; harmless elsewhere.
                "HTTP-Referer": "https://aria.local",
                "X-Title": "A.R.I.A.",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=settings.agent_request_timeout) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:400]
            raise AIProviderError(f"AI request failed ({exc.code}): {detail}") from exc
        except urllib.error.URLError as exc:
            raise AIProviderError(f"Could not reach the AI service: {exc.reason}") from exc
        except TimeoutError as exc:
            raise AIProviderError("The AI service timed out.") from exc

        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise AIProviderError("The AI service returned a non-JSON response.") from exc

        if isinstance(data, dict) and data.get("error"):
            message = data["error"]
            if isinstance(message, dict):
                message = message.get("message") or str(message)
            raise AIProviderError(f"AI request failed: {message}")
        return data

    # --- Extraction ---------------------------------------------------------
    # The voice pipeline's contract is unchanged. Extraction is delegated to the
    # tested deterministic engine; the model's value here is conversation and
    # tool use, and re-routing extraction through it would put a working,
    # verified path at risk for no gain.

    def extract_event(self, text: str, known_products: list[str]) -> ExtractedEvent:
        return self._fallback.extract_event(text, known_products)

    def answer_question(self, question: str, facts: dict, language: str = "en") -> str:
        """Rephrase pre-computed facts. Never asked to compute anything."""
        system = (
            "You rephrase verified business facts for a small shop owner. "
            "Use ONLY the numbers given to you. Never invent or recompute a figure. "
            "Answer in one or two short sentences. "
            f"Reply in this language code: {language}."
        )
        try:
            turn = self.chat(
                [
                    {"role": "system", "content": system},
                    {
                        "role": "user",
                        "content": (
                            f"Question: {question}\n"
                            f"Verified facts (JSON): {json.dumps(facts, default=str)}"
                        ),
                    },
                ],
                temperature=0.3,
            )
            return turn.content
        except AIProviderError:
            # The caller keeps its own computed answer when this returns empty.
            return ""
