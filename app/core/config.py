from functools import lru_cache
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """

    app_name: str = "Isolated Session Chat API"
    app_version: str = "1.0.0"
    environment: str = "development"

    # LLM
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    default_model: str = "gpt-4o-mini"
    default_temperature: float = 0.7

    # Redis
    # redis_host: str = os.environ.get("REDIS_URL", "redis")
    redis_url: str = os.environ.get("REDIS_URL", "redis://redis:6379")


    redis_port: int = 6379
    redis_db: int = 0

    # Session configuration
    session_ttl_seconds: int = 3600
    max_history_messages: int = 10

    # API rate limiting
    rate_limit_per_minute: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def api_key(self) -> str:
        """Return the configured OpenAI API key."""
        if not self.openai_api_key:
            raise RuntimeError("No OpenAI API key configured. Set OPENAI_API_KEY.")
        return self.openai_api_key

    @property
    def base_url(self) -> str:
        """Return the configured OpenAI base URL."""
        return self.openai_base_url


settings = Settings()


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    Caching prevents environment configuration from being
    recreated on every request.
    """
    return Settings()