from typing import AsyncGenerator

import redis.asyncio as aioredis
from openai import AsyncOpenAI

from clients.llm_client import LLMClient
from core.config import get_settings
from repositories.redis_repository import RedisRepository
from services.chat_service import ChatService


settings = get_settings()

redis_client: aioredis.Redis | None = None
nvidia_client: AsyncOpenAI | None = None


async def init_dependencies() -> None:
    """
    Initialize external service clients.
    """

    global redis_client
    global nvidia_client

    redis_client = aioredis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,
    )

    nvidia_client = AsyncOpenAI(
        base_url=settings.nvidia_base_url,
        api_key=settings.nvidia_api_key,
    )


async def close_dependencies() -> None:
    """
    Close external service clients.
    """

    global redis_client
    global nvidia_client

    if redis_client:
        await redis_client.aclose()

    if nvidia_client:
        await nvidia_client.close()


def get_chat_service() -> ChatService:
    """
    Build the ChatService with its dependencies.
    """

    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")

    if nvidia_client is None:
        raise RuntimeError("NVIDIA client is not initialized.")

    redis_repository = RedisRepository(
        client=redis_client,
        session_ttl_seconds=settings.session_ttl_seconds,
    )

    llm_client = LLMClient(
        client=nvidia_client,
        model=settings.default_model,
    )

    return ChatService(
        redis_repository=redis_repository,
        llm_client=llm_client,
        max_history_messages=settings.max_history_messages,
    )