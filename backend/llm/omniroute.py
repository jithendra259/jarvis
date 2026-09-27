"""OmniRoute provider: local OpenAI-compatible gateway (default backend).

OmniRoute runs on the user's machine at http://127.0.0.1:20128 and proxies to
a local Ollama model. Credentials are read from the environment only.
"""

from __future__ import annotations

import json
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx
from openai import APIConnectionError, APIStatusError, APITimeoutError, AsyncOpenAI

from config.settings import settings
from errors import JarvisError, LLMTimeoutError, LLMUnavailableError
from llm.client import LLMProvider, LLMResponse, LLMToolCall
from logger.logger import logger


def _translate(exc: Exception, model: str) -> JarvisError:
    """Map transport failures onto structured runtime errors."""
    if isinstance(exc, APITimeoutError):
        return LLMTimeoutError(
            f"OmniRoute did not answer within {settings.llm_timeout_seconds:.0f}s (model '{model}').",
            model=model,
        )
    if isinstance(exc, APIConnectionError):
        return LLMUnavailableError(
            f"Cannot reach the local OmniRoute gateway at {settings.omniroute_url}. "
            "Start OmniRoute (or point OMNIROUTE_URL at your local gateway).",
            model=model,
        )
    if isinstance(exc, APIStatusError):
        detail = (exc.response.text or "")[:300] if exc.response is not None else ""
        return JarvisError(
            "llm_unavailable",
            f"OmniRoute returned HTTP {exc.status_code} for model '{model}'. {detail}".strip(),
            status_code=502,
            details={"model": model, "status_code": exc.status_code},
        )
    return LLMUnavailableError(f"OmniRoute request failed: {exc}", model=model)


class OmniRouteProvider(LLMProvider):
    """OpenAI-compatible client for the local OmniRoute gateway."""

    name = "omniroute"

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        self.base_url = (base_url or settings.omniroute_url).rstrip("/")
        self.api_key = api_key if api_key is not None else settings.omniroute_api_key
        self.default_model = default_model or settings.default_model
        self.timeout = timeout or settings.llm_timeout_seconds
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key or "not-required",
            timeout=self.timeout,
            max_retries=1,
        )

    # -- health -------------------------------------------------------------

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.5) as http:
                response = await http.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                )
            return response.status_code < 500
        except Exception as exc:
            logger.debug("OmniRoute health check failed: %s", exc)
            return False

    async def list_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as http:
                response = await http.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                )
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            logger.warning("Could not list OmniRoute models: %s", exc)
            return []
        
        raw_ids = [entry.get("id", "") for entry in payload.get("data", []) if entry.get("id")]
        # Filter out non-text/image-generation models for the assistant chat dropdown
        excluded_keywords = ("aihorde", "diffusion", "image", "whisper", "sdxl", "flux", "inpainting", "waifu")
        filtered = []
        seen = set()
        for model_id in raw_ids:
            lower = model_id.lower()
            if any(kw in lower for kw in excluded_keywords):
                continue
            if model_id not in seen:
                seen.add(model_id)
                filtered.append(model_id)
        return filtered

    # -- generation ---------------------------------------------------------

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
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            completion = await self.client.chat.completions.create(**payload)
        except Exception as exc:
            raise _translate(exc, active_model) from exc

        message = completion.choices[0].message
        tool_calls: List[LLMToolCall] = []
        for raw_call in message.tool_calls or []:
            function = raw_call.function
            arguments: Dict[str, Any]
            try:
                parsed = json.loads(function.arguments) if function.arguments else {}
                arguments = parsed if isinstance(parsed, dict) else {"value": parsed}
            except (TypeError, ValueError):
                logger.warning("OmniRoute returned unparsable tool arguments for '%s'", function.name)
                arguments = {}
            tool_calls.append(LLMToolCall(name=function.name, arguments=arguments))

        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls,
            model=completion.model,
        )

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        active_model = model or self.default_model
        try:
            stream = await self.client.chat.completions.create(
                model=active_model,
                messages=messages,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as exc:
            raise _translate(exc, active_model) from exc


__all__ = ["OmniRouteProvider"]
