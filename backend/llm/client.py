from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel


class LLMToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class LLMResponse(BaseModel):
    content: Optional[str] = None
    tool_calls: List[LLMToolCall] = []
    raw_response: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract base class for all local and optional cloud LLM providers."""

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        """Generate a response, optionally with tool calling."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream token deltas for real-time text/voice output."""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Check if the local provider endpoint is online and responsive."""
        pass
