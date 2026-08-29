from typing import AsyncGenerator

import redis.asyncio as aioredis
from openai import AsyncOpenAI

from clients.llm_client import LLMClient
from core.config import get_settings
from repositories.redis_repository import RedisRepository
from services.chat_service import ChatService


settings = get_settings()

redis_client: aioredis.Redis | None = None
openai_client: AsyncOpenAI | None = None


async def init_dependencies() -> None:
    """
    Initialize external service clients.
    """

    global redis_client
    global openai_client

    redis_client = aioredis.Redis.from_url(
    settings.redis_url,
    decode_responses=True,
    )

    openai_client = AsyncOpenAI(
        base_url=settings.base_url,
        api_key=settings.api_key,
    )


async def close_dependencies() -> None:
    """
    Close external service clients.
    """

    global redis_client
    global openai_client

    if redis_client:
        await redis_client.aclose()

    if openai_client:
        await openai_client.close()


def get_chat_service() -> ChatService:
    """
    Build the ChatService with its dependencies.
    """

    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")

    if openai_client is None:
        raise RuntimeError("OpenAI client is not initialized.")

    redis_repository = RedisRepository(
        client=redis_client,
        session_ttl_seconds=settings.session_ttl_seconds,
    )

    llm_client = LLMClient(
        client=openai_client,
        model=settings.default_model,
    )

    return ChatService(
        redis_repository=redis_repository,
        llm_client=llm_client,
        max_history_messages=settings.max_history_messages,
    )