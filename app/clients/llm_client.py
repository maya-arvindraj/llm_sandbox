from typing import Any

from openai import AsyncOpenAI


class LLMClient:
    """
    Client responsible for communicating with the LLM provider.
    """

    def __init__(
        self,
        client: AsyncOpenAI,
        model: str,
    ) -> None:
        self.client = client
        self.model = model

    async def generate_response(
        self,
        messages: list[dict[str, Any]],
        temperature: float,
    ) -> str:
        """
        Send messages to the LLM and return the assistant response.
        """

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            extra_body={
                "chat_template_kwargs": {
                    "thinking": True,
                    "reasoning_effort": "high",
                }
            },
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "LLM returned an empty response."
            )

        return content