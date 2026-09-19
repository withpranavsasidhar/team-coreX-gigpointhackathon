from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://sudheer@localhost:5433/aria"

    # AI / voice (used from Phase 6 onward)
    ai_provider: str = "anthropic"
    anthropic_api_key: str = ""
    nlu_model: str = "claude-opus-5"
    stt_provider: str = "browser_passthrough"

    # Conversational agent (Phase 10). Any OpenAI-compatible endpoint —
    # OpenRouter, Together, a local server — configured purely by env, so no
    # provider-specific logic leaks outside the provider layer.
    ai_api_key: str = ""
    ai_base_url: str = "https://openrouter.ai/api/v1"
    ai_model: str = ""
    agent_max_tool_rounds: int = 6
    agent_request_timeout: float = 45.0

    # Translation is optional: the model understands Telugu/Hindi/mixed speech
    # directly, so translation is only used where normalisation genuinely helps.
    translation_provider: str = "none"     # none | google
    google_translate_api_key: str = ""
    google_translate_project_id: str = ""

    # A.R.I.A. Vision (Phase 11). Reuses AI_API_KEY/AI_BASE_URL but needs its
    # own model, because not every chat model can see.
    vision_model: str = ""
    vision_max_image_mb: float = 8.0
    vision_request_timeout: float = 60.0
    # Confidence bands for extracted lines. Application thresholds, not truth.
    vision_high_confidence: float = 0.90
    vision_low_confidence: float = 0.70

    # Business rule constants
    confidence_threshold: float = 0.75
    clarification_threshold: float = 0.5
    default_lead_time_days: int = 7
    consumption_lookback_days: int = 14

    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
