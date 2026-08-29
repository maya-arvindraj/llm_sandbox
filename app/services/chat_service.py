import uuid

from core.config import settings
from core.prompt import SYSTEM_PROMPT
from repositories.redis_repository import RedisRepository
from clients.llm_client import LLMClient
from schemas.chat import ChatRequest, ChatResponse


class ChatService:
    """
    Coordinates chat sessions, conversation history,
    and LLM generation.
    """

    def __init__(
        self,
        redis_repository: RedisRepository,
        llm_client: LLMClient,
        max_history_messages: int,
    ) -> None:
        self.redis_repository = redis_repository
        self.llm_client = llm_client
        self.max_history_messages = max_history_messages

    async def chat(
        self,
        request: ChatRequest,
        session_id: str | None,
    ) -> ChatResponse:
        """
        Process a chat request.
        """

        # Create a session if the client didn't provide one.
        session_id = session_id or str(uuid.uuid4())

        # Retrieve previous conversation.
        history = await self.redis_repository.get_history(
            session_id=session_id,
            limit=self.max_history_messages,
        )

        # Build messages for the LLM.
        messages = []

        messages.append(
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        )

        messages.extend(history)

        messages.append(
            {
                "role": "user",
                "content": request.prompt,
            }
        )

        # Generate response.
        assistant_reply = await self.llm_client.generate_response(
            messages=messages,
            temperature=settings.default_temperature,
        )

        # Persist conversation.
        await self.redis_repository.append_message(
            session_id=session_id,
            role="user",
            content=request.prompt,
        )

        await self.redis_repository.append_message(
            session_id=session_id,
            role="assistant",
            content=assistant_reply,
        )

        return ChatResponse(
            session_id=session_id,
            model=self.llm_client.model,
            response=assistant_reply,
        )

    async def clear_session(
        self,
        session_id: str,
    ) -> bool:
        """
        Delete a chat session.
        """

        return await self.redis_repository.delete_session(
            session_id
        )