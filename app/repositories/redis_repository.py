import json
from typing import Any

import redis.asyncio as aioredis


class RedisRepository:
    """
    Handles persistence of chat session data in Redis.
    """

    def __init__(
        self,
        client: aioredis.Redis,
        session_ttl_seconds: int,
    ) -> None:
        self.client = client
        self.session_ttl_seconds = session_ttl_seconds

    @staticmethod
    def _session_key(session_id: str) -> str:
        return f"chat:session:{session_id}"

    async def get_history(
        self,
        session_id: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the most recent messages for a session.
        """

        key = self._session_key(session_id)

        raw_messages = await self.client.lrange(
            key,
            -limit,
            -1,
        )

        return [
            json.loads(message)
            for message in raw_messages
        ]

    async def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        """
        Append a message to the session history
        and refresh the session TTL.
        """

        key = self._session_key(session_id)

        message = json.dumps(
            {
                "role": role,
                "content": content,
            }
        )

        await self.client.rpush(key, message)

        # Sliding expiration:
        # every new message keeps the session alive.
        await self.client.expire(
            key,
            self.session_ttl_seconds,
        )

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a chat session.
        """

        key = self._session_key(session_id)

        deleted = await self.client.delete(key)

        return bool(deleted)