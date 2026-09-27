from openai import AsyncOpenAI, OpenAI
from typing import AsyncGenerator, List, Dict, Any, Optional
from .config import OMNIROUTE_BASE_URL, OMNIROUTE_API_KEY, DEFAULT_MODEL

class OmniRouteClient:
    """OpenAI-compatible client connecting Jarvis directly to OmniRoute gateway."""

    def __init__(self, base_url: str = OMNIROUTE_BASE_URL, api_key: str = OMNIROUTE_API_KEY):
        self.base_url = base_url
        self.api_key = api_key
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        self.async_client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = DEFAULT_MODEL,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ):
        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = await self.async_client.chat.completions.create(**kwargs)
        return response

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str = DEFAULT_MODEL,
    ) -> AsyncGenerator[str, None]:
        response = await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

omni_client = OmniRouteClient()
