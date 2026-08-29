from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Request body for sending a chat message.
    """

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=10_000,
        description="User's message",
    )

    system_prompt: str | None = Field(
        default=None,
        max_length=5_000,
        description="Optional system instruction",
    )

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="LLM sampling temperature",
    )


class ChatResponse(BaseModel):
    """
    Response returned after processing a chat message.
    """

    session_id: str
    model: str
    response: str


class SessionClearResponse(BaseModel):
    """
    Response returned when a session is deleted.
    """

    session_id: str
    cleared: bool