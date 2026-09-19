"""Vision provider abstraction.

A.R.I.A. Vision reads images through a vision-capable model. This layer holds
every provider-specific detail, exactly as the chat provider does, so the
service above it works in terms of a structured reading and never knows which
vendor produced it.

Nothing here invents content. If the model cannot be reached, cannot see, or
returns something unreadable, that is raised — never smoothed over into a
plausible-looking list of products the owner never photographed.
"""
from __future__ import annotations

import base64
import binascii
import json
import re
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import lru_cache

from app.config import settings

# What the browser may hand us. Anything else is refused before a byte is sent.
ALLOWED_MIME = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
DATA_URI_RE = re.compile(r"^data:(?P<mime>[\w./+-]+);base64,(?P<payload>.+)$", re.DOTALL)


class VisionError(RuntimeError):
    """Vision could not be performed. Always surfaced to the user as a failure."""


class VisionUnavailable(VisionError):
    """No vision-capable model is configured."""


@dataclass
class VisionReading:
    """The model's raw structured reading of an image, before any business logic."""

    document_type: str = "unknown"
    language: str = ""
    items: list[dict] = field(default_factory=list)
    invoice: dict | None = None
    readable: bool = True
    quality_issues: list[str] = field(default_factory=list)
    notes: str = ""
    provider: str = ""
    model: str = ""
    raw_text: str = ""


@dataclass
class DecodedImage:
    mime: str
    data: bytes

    @property
    def size_mb(self) -> float:
        return len(self.data) / (1024 * 1024)

    def to_data_uri(self) -> str:
        return f"data:{self.mime};base64,{base64.b64encode(self.data).decode()}"


def decode_image(data_uri: str) -> DecodedImage:
    """Validate and decode a browser data URI. Refuses anything unexpected."""
    if not data_uri or not data_uri.strip():
        raise VisionError("No image was provided.")

    match = DATA_URI_RE.match(data_uri.strip())
    if not match:
        raise VisionError("That does not look like an image file.")

    mime = match.group("mime").lower()
    if mime not in ALLOWED_MIME:
        raise VisionError(
            f"{mime} images are not supported. Use a JPG, PNG or WEBP photo."
        )

    try:
        payload = base64.b64decode(match.group("payload"), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise VisionError("That image could not be read.") from exc

    if not payload:
        raise VisionError("That image file is empty.")

    image = DecodedImage(mime="image/jpeg" if mime == "image/jpg" else mime, data=payload)
    if image.size_mb > settings.vision_max_image_mb:
        raise VisionError(
            f"That image is {image.size_mb:.1f} MB. "
            f"Please use one under {settings.vision_max_image_mb:.0f} MB."
        )
    return image


EXTRACTION_PROMPT = """You are reading a photograph for a small shop owner in India.

Report ONLY what is actually visible in this image. This is the whole job: a
figure you cannot read is worth far less than an honest "unclear".

Rules:
- Never invent a product, quantity, unit or price that is not visible.
- If a quantity is smudged, cut off, or blocked, set quantity to null and say
  why in item_note. Do not estimate it.
- Keep the text exactly as written in raw_name, including Telugu or Hindi script.
- Put your best English reading of the product in normalized_name.
- confidence is your confidence in THAT LINE, 0 to 1.
- If the photo is too blurry, dark or angled to read, set readable to false.

Reply with JSON only, in exactly this shape:

{
  "document_type": "inventory_list" | "invoice" | "shelf_photo" | "handwritten_list" | "other",
  "language": "en" | "te" | "hi" | "te-en" | "hi-en" | "mixed",
  "readable": true,
  "quality_issues": ["blur", "dark", "glare", "angled", "cropped", "obstructed"],
  "notes": "one short sentence about what this image is",
  "items": [
    {
      "raw_name": "text exactly as written",
      "normalized_name": "English product name",
      "quantity": 50,
      "unit": "kg",
      "price": null,
      "confidence": 0.94,
      "item_note": ""
    }
  ],
  "invoice": {
    "supplier": null, "invoice_number": null, "date": null, "total": null
  }
}

If you can see no business items at all, return an empty items array."""


class VisionProvider(ABC):
    name: str = "base"
    available: bool = False

    @abstractmethod
    def read_image(self, image: DecodedImage, hint: str = "") -> VisionReading:
        """Read one image into a structured reading, or raise."""


class UnavailableVisionProvider(VisionProvider):
    """The honest default when nothing is configured."""

    name = "none"
    available = False

    def __init__(self, reason: str | None = None) -> None:
        if reason:
            self.reason = reason
        elif not settings.ai_api_key.strip():
            self.reason = (
                "A.R.I.A. Vision requires a vision-capable AI model. "
                "Set AI_API_KEY and VISION_MODEL in backend .env to enable it."
            )
        elif not settings.vision_model.strip():
            self.reason = (
                "A.R.I.A. Vision requires a vision-capable AI model. "
                "Set VISION_MODEL in backend .env to enable it."
            )
        else:
            self.reason = "A.R.I.A. Vision is not connected to a vision-capable model."

    def read_image(self, image: DecodedImage, hint: str = "") -> VisionReading:
        raise VisionUnavailable(self.reason)



class OpenAICompatibleVisionProvider(VisionProvider):
    """Any OpenAI-shaped endpoint serving a multimodal model."""

    name = "openai_compatible_vision"

    @property
    def available(self) -> bool:
        return bool(settings.ai_api_key.strip() and settings.vision_model.strip())

    @property
    def api_key(self) -> str:
        return settings.ai_api_key.strip()

    @property
    def base_url(self) -> str:
        return settings.ai_base_url.strip().rstrip("/")

    @property
    def model(self) -> str:
        return settings.vision_model.strip()

    def __init__(self) -> None:
        if not self.api_key:
            raise VisionUnavailable("AI_API_KEY is not set.")
        if not self.model:
            raise VisionUnavailable("VISION_MODEL is not set.")


    def read_image(self, image: DecodedImage, hint: str = "") -> VisionReading:
        instruction = EXTRACTION_PROMPT
        if hint.strip():
            instruction += f"\n\nThe owner says this image is: {hint.strip()}"

        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": instruction},
                        {"type": "image_url",
                         "image_url": {"url": image.to_data_uri()}},
                    ],
                }
            ],
        }

        data = self._post("/chat/completions", payload)
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise VisionError("The vision model returned an unexpected response.") from exc

        if isinstance(content, list):  # some providers return content parts
            content = "".join(part.get("text", "") for part in content
                              if isinstance(part, dict))

        return self._parse(content or "")

    def _parse(self, content: str) -> VisionReading:
        text = content.strip()
        # Models often wrap JSON in a fenced block.
        fence = re.search(r"```(?:json)?\s*(.+?)```", text, re.DOTALL)
        if fence:
            text = fence.group(1).strip()
        else:
            start, end = text.find("{"), text.rfind("}")
            if start != -1 and end > start:
                text = text[start:end + 1]

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise VisionError(
                "I couldn't read a clear result from that image. Please try again."
            ) from exc

        if not isinstance(parsed, dict):
            raise VisionError("The vision model returned an unexpected result.")

        items = parsed.get("items")
        return VisionReading(
            document_type=str(parsed.get("document_type") or "unknown"),
            language=str(parsed.get("language") or ""),
            items=[i for i in (items or []) if isinstance(i, dict)],
            invoice=parsed.get("invoice") if isinstance(parsed.get("invoice"), dict) else None,
            readable=bool(parsed.get("readable", True)),
            quality_issues=[str(q) for q in (parsed.get("quality_issues") or [])],
            notes=str(parsed.get("notes") or ""),
            provider=self.name,
            model=self.model,
            raw_text=content[:4000],
        )

    def _post(self, path: str, payload: dict) -> dict:
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://aria.local",
                "X-Title": "A.R.I.A. Vision",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=settings.vision_request_timeout) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            raise VisionError(f"A.R.I.A. Vision is temporarily unavailable ({exc.code}). {detail}") from exc
        except urllib.error.URLError as exc:
            raise VisionError(
                f"A.R.I.A. Vision is temporarily unavailable: {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            raise VisionError("A.R.I.A. Vision timed out reading that image.") from exc

        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise VisionError("The vision service returned an unreadable response.") from exc

        if isinstance(data, dict) and data.get("error"):
            message = data["error"]
            if isinstance(message, dict):
                message = message.get("message") or str(message)
            raise VisionError(f"A.R.I.A. Vision is temporarily unavailable: {message}")
        return data


@lru_cache(maxsize=1)
def get_vision_provider() -> VisionProvider:

    if settings.ai_api_key.strip() and settings.vision_model.strip():
        try:
            return OpenAICompatibleVisionProvider()
        except VisionUnavailable as exc:
            return UnavailableVisionProvider(reason=str(exc))
    return UnavailableVisionProvider()


def vision_status() -> dict:
    provider = get_vision_provider()
    return {
        "provider": provider.name,
        "model": settings.vision_model.strip() or None,
        "available": provider.available,
        "reason": None if provider.available else (
            getattr(provider, "reason", None) or (
                "A.R.I.A. Vision requires a vision-capable AI model. "
                "Set AI_API_KEY and VISION_MODEL to enable it."
            )
        ),
        "max_image_mb": settings.vision_max_image_mb,
        "accepted_types": sorted(ALLOWED_MIME),
    }


__all__ = [
    "VisionProvider", "VisionReading", "VisionError", "VisionUnavailable",
    "DecodedImage", "decode_image", "get_vision_provider", "vision_status",
    "OpenAICompatibleVisionProvider", "UnavailableVisionProvider",
]
