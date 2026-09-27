"""Shared pytest fixtures.

Unit tests never touch the real machine, the network, or large models: the LLM
provider is replaced by `MockLLMProvider` and every test writes to a temporary
JARVIS data directory.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest  # noqa: E402

from llm.client import LLMProvider, LLMResponse, LLMToolCall  # noqa: E402

os.environ.setdefault("JARVIS_ENV", "test")


class MockLLMProvider(LLMProvider):
    """Deterministic provider: scripted tool call, then scripted answer."""

    name = "mock"

    def __init__(
        self,
        *,
        tool_call: Optional[LLMToolCall] = None,
        content: str = "Mocked reply.",
        responses: Optional[List[LLMResponse]] = None,
    ) -> None:
        self.tool_call = tool_call
        self.content = content
        self.responses = responses
        self.calls: List[Dict[str, Any]] = []
        self.online = True

    async def check_health(self) -> bool:
        return self.online

    async def list_models(self) -> List[str]:
        return ["mock-model"]

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        self.calls.append({"messages": messages, "tools": tools, "model": model})
        if self.responses:
            return self.responses.pop(0)
        if self.tool_call is not None:
            return LLMResponse(content=None, tool_calls=[self.tool_call], model="mock-model")
        return LLMResponse(content=self.content, model="mock-model")

    async def stream(self, messages: List[Dict[str, Any]], model: Optional[str] = None):
        for word in self.content.split():
            yield word + " "


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    """Point every settings-derived path at a temporary directory."""
    from config.settings import Settings

    monkeypatch.setenv("JARVIS_DATA_DIR", str(tmp_path / "Jarvis"))
    monkeypatch.setenv("JARVIS_HOST", "127.0.0.1")
    monkeypatch.setenv("JARVIS_PORT", "8000")

    snapshot = Settings.from_env()
    snapshot.ensure_data_dirs()
    yield snapshot


@pytest.fixture
def mock_llm():
    """Install a MockLLMProvider as the active provider."""

    def _install(**kwargs) -> MockLLMProvider:
        from llm import set_llm_provider

        provider = MockLLMProvider(**kwargs)
        set_llm_provider(provider)
        return provider

    yield _install
    from llm import reset_llm_provider

    reset_llm_provider()


@pytest.fixture
def clean_registry():
    """Restore the global tool registry after a test mutates it."""
    from tools.registry import registry

    original = dict(registry._tools)
    yield registry
    registry._tools.clear()
    registry._tools.update(original)


@pytest.fixture
def temp_data_dir() -> Path:
    return Path(tempfile.mkdtemp(prefix="jarvis-test-"))


@pytest.fixture(autouse=True)
def reset_confirmation_store():
    from agent.confirmations import store

    store.clear()
    yield
    store.clear()
