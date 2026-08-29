import logging
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException

logger = logging.getLogger(__name__)

from dependencies import get_chat_service
from schemas.chat import (
    ChatRequest,
    ChatResponse,
    SessionClearResponse,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    x_session_id: Annotated[
        str | None,
        Header(alias="X-Session-ID"),
    ] = None,
) -> ChatResponse:
    """
    Send a message to the LLM using session-specific history.
    """

    service = get_chat_service()

    try:
        return await service.chat(
            request=request,
            session_id=x_session_id,
        )

    except Exception as exc:
        logger.exception(
            "Chat request failed for session=%s model=%s prompt_preview=%r",
            x_session_id,
            service.llm_client.model,
            request.prompt[:120] if request.prompt else "",
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat request.",
        ) from exc


@router.delete(
    "/session/{session_id}",
    response_model=SessionClearResponse,
)
async def clear_session(
    session_id: str,
) -> SessionClearResponse:
    """
    Clear all conversation history for a session.
    """

    service = get_chat_service()

    try:
        cleared = await service.clear_session(
            session_id
        )

        return SessionClearResponse(
            session_id=session_id,
            cleared=cleared,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to clear session.",
        ) from exc