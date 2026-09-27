"""LLM provider abstraction.

The agent never talks to a model endpoint directly: it depends on
`LLMProvider`. The default and only bundled implementations are local
(OmniRoute -> Ollama). Additional providers can be registered later without
touching the graph, the tools or the API.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional

from pydantic import BaseModel, Field


class LLMToolCall(BaseModel):
    """A structured tool call requested by the model."""

    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    """Normalised completion returned by every provider."""

    content: Optional[str] = None
    tool_calls: List[LLMToolCall] = Field(default_factory=list)
    model: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None

    @property
    def has_tool_call(self) -> bool:
        return bool(self.tool_calls)


class LLMProvider(ABC):
    """Interface implemented by every language-model backend."""

    name: str = "abstract"

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        """Produce a completion, optionally with structured tool calls."""

    @abstractmethod
    def stream(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Yield text deltas as they are produced."""

    @abstractmethod
    async def check_health(self) -> bool:
        """Return True when the provider endpoint is reachable."""

    async def list_models(self) -> List[str]:
        """Return the model identifiers the provider exposes."""
        return []


__all__ = ["LLMToolCall", "LLMResponse", "LLMProvider"]
