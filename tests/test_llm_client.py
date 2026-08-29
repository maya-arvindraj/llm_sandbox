from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.clients.llm_client import LLMClient


async def test_generate_response_uses_openai_chat_payload():
    fake_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Hello from OpenAI"))]
    )
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=AsyncMock(return_value=fake_response)
            )
        )
    )

    client = LLMClient(client=fake_client, model="gpt-4o-mini")

    result = await client.generate_response(
        messages=[{"role": "user", "content": "Hi"}],
        temperature=0.7,
    )

    assert result == "Hello from OpenAI"
    fake_client.chat.completions.create.assert_awaited_once_with(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hi"}],
        temperature=0.7,
    )
