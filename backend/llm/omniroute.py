import json
import httpx
from typing import List, Dict, Any, Optional, AsyncGenerator
from openai import AsyncOpenAI
from config.settings import settings
from logger.logger import logger
from .client import LLMProvider, LLMResponse, LLMToolCall


class OmniRouteProvider(LLMProvider):
    """
    Local LLM provider connecting to OmniRoute gateway at http://localhost:20128/v1.
    OmniRoute exposes an OpenAI-compatible API interface.
    """

    def __init__(
        self,
        base_url: str = settings.OMNIROUTE_URL,
        api_key: str = settings.OMNIROUTE_API_KEY,
        default_model: str = settings.DEFAULT_MODEL,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.default_model = default_model
        self.client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as http_client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                resp = await http_client.get(f"{self.base_url}/models", headers=headers)
                return resp.status_code == 200
        except Exception as e:
            logger.debug(f"OmniRoute health check failed: {e}")
            return False

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        active_model = model or self.default_model
        kwargs: Dict[str, Any] = {
            "model": active_model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        try:
            resp = await self.client.chat.completions.create(**kwargs)
            choice = resp.choices[0]
            message = choice.message

            tool_calls: List[LLMToolCall] = []
            if message.tool_calls:
                for tc in message.tool_calls:
                    try:
                        args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                    except Exception:
                        args = {"raw": tc.function.arguments}
                    tool_calls.append(LLMToolCall(name=tc.function.name, arguments=args))

            return LLMResponse(
                content=message.content,
                tool_calls=tool_calls,
                raw_response=resp.model_dump(),
            )
        except Exception as e:
            logger.error(f"[OmniRoute Error] Chat completion failed on {active_model}: {e}")
            raise

    async def stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        active_model = model or self.default_model
        response = await self.client.chat.completions.create(
            model=active_model,
            messages=messages,
            stream=True,
        )
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
