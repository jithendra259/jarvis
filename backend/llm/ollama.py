"""Ollama provider: direct local inference, used when OmniRoute is not running.

Ollama exposes an OpenAI-compatible endpoint as well; this provider uses the
native `/api/chat` API because it is the most stable across Ollama versions.
"""

from __future__ import annotations

import json
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from config.settings import settings
from errors import JarvisError, LLMTimeoutError, LLMUnavailableError
from llm.client import LLMProvider, LLMResponse, LLMToolCall
from logger.logger import logger


def _translate(exc: Exception, model: str) -> JarvisError:
    if isinstance(exc, (httpx.TimeoutException, TimeoutError)):
        return LLMTimeoutError(
            f"Ollama did not answer within {settings.llm_timeout_seconds:.0f}s (model '{model}').",
            model=model,
        )
    if isinstance(exc, httpx.HTTPError):
        return LLMUnavailableError(
            f"Cannot reach the local Ollama server at {settings.ollama_url}. Start it with 'ollama serve'.",
            model=model,
        )
    return LLMUnavailableError(f"Ollama request failed: {exc}", model=model)


class OllamaProvider(LLMProvider):
    """Native client for a local Ollama instance."""

    name = "ollama"

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        self.base_url = (base_url or settings.ollama_url).rstrip("/")
        self.default_model = default_model or settings.default_model
        self.timeout = timeout or settings.llm_timeout_seconds

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.5) as http:
                response = await http.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as exc:
            logger.debug("Ollama health check failed: %s", exc)
            return False

    async def list_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as http:
                response = await http.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            logger.warning("Could not list Ollama models: %s", exc)
            return []
        return [entry.get("name", "") for entry in payload.get("models", []) if entry.get("name")]

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        active_model = model or self.default_model
        payload: Dict[str, Any] = {
            "model": active_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if tools:
            payload["tools"] = tools

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            raise _translate(exc, active_model) from exc

        message = data.get("message", {})
        tool_calls = [
            LLMToolCall(
                name=call.get("function", {}).get("name", ""),
                arguments=call.get("function", {}).get("arguments", {}) or {},
            )
            for call in message.get("tool_calls", []) or []
        ]
        return LLMResponse(content=message.get("content"), tool_calls=tool_calls, model=data.get("model"))

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        active_model = model or self.default_model
        payload = {"model": active_model, "messages": messages, "stream": True}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                        except ValueError:
                            continue
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
        except Exception as exc:
            raise _translate(exc, active_model) from exc


__all__ = ["OllamaProvider"]
