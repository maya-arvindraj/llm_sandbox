from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """

    app_name: str = "Isolated Session Chat API"
    app_version: str = "1.0.0"
    environment: str = "development"

    # LLM
    nvidia_api_key: str
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    default_model: str = "deepseek-ai/deepseek-v4-flash-0731"

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    # Session configuration
    session_ttl_seconds: int = 3600
    max_history_messages: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    Caching prevents environment configuration from being
    recreated on every request.
    """
    return Settings()