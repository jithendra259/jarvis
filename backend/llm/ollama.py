import json
import httpx
from typing import List, Dict, Any, Optional, AsyncGenerator
from config.settings import settings
from logger.logger import logger
from .client import LLMProvider, LLMResponse, LLMToolCall


class OllamaProvider(LLMProvider):
    """
    Local LLM provider connecting directly to Ollama at http://localhost:11434.
    """

    def __init__(
        self,
        base_url: str = settings.OLLAMA_URL,
        default_model: str = "llama3.2",
    ):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as http_client:
                resp = await http_client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        active_model = model or self.default_model
        payload = {
            "model": active_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if tools:
            payload["tools"] = tools

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
                msg = data.get("message", {})

                tool_calls: List[LLMToolCall] = []
                for tc in msg.get("tool_calls", []):
                    fn = tc.get("function", {})
                    tool_calls.append(LLMToolCall(name=fn.get("name", ""), arguments=fn.get("arguments", {})))

                return LLMResponse(
                    content=msg.get("content"),
                    tool_calls=tool_calls,
                    raw_response=data,
                )
        except Exception as e:
            logger.error(f"[Ollama Error] Chat failed on {active_model}: {e}")
            raise

    async def stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        active_model = model or self.default_model
        payload = {
            "model": active_model,
            "messages": messages,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                async for line in response.aiter_lines():
                    if line:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
