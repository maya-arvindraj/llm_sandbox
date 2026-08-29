from pydantic import BaseModel, Field, field_validator

from core.sanitizer import sanitize_input


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

    @field_validator("prompt", mode="before")
    @classmethod
    def sanitize_prompt(cls, v: str) -> str:
        """Sanitize the prompt input to remove problematic characters."""
        if isinstance(v, str):
            return sanitize_input(v)
        return v


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