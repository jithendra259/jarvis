"""LLM provider selection.

Resolution order follows `LLM_PROVIDER`:

  auto      -> OmniRoute first (it fronts Ollama), Ollama as fallback
  omniroute -> OmniRoute only
  ollama    -> Ollama only

The selected provider is cached after the first successful probe. Tests can
inject a provider with `set_llm_provider` / `reset_llm_provider`.
"""

from __future__ import annotations

from typing import List, Optional

from config.settings import settings
from errors import LLMUnavailableError
from llm.client import LLMProvider, LLMResponse, LLMToolCall
from llm.ollama import OllamaProvider
from llm.omniroute import OmniRouteProvider
from logger.logger import logger

_provider: Optional[LLMProvider] = None
_active_model: Optional[str] = None


def get_active_model() -> str:
    """Return the currently selected model, falling back to settings."""
    return _active_model or settings.default_model


def set_active_model(model: str) -> str:
    """Set the process-wide active model for subsequent requests."""
    global _active_model, _provider
    clean = model.strip()
    _active_model = clean
    if _provider is not None:
        _provider.default_model = clean
    return _active_model


async def get_llm_provider() -> LLMProvider:
    """Return the active local provider, probing endpoints when required."""
    global _provider
    if _provider is not None:
        return _provider

    preference = (settings.llm_provider or "auto").lower()
    candidates: List[LLMProvider] = []
    if preference in ("auto", "omniroute"):
        candidates.append(OmniRouteProvider())
    if preference in ("auto", "ollama"):
        candidates.append(OllamaProvider())

    if not candidates:  # unknown preference: fall back to auto behaviour
        logger.warning("Unknown LLM_PROVIDER '%s'; using auto detection", preference)
        candidates = [OmniRouteProvider(), OllamaProvider()]

    for candidate in candidates:
        if await candidate.check_health():
            logger.info("LLM provider selected: %s (%s)", candidate.name, settings.default_model)
            _provider = candidate
            return candidate

    # Nothing answered the probe: return the preferred provider so the caller
    # receives a structured "unavailable" error with actionable guidance.
    _provider = candidates[0]
    logger.warning("No local LLM endpoint answered; defaulting to %s", _provider.name)
    return _provider


async def describe_providers() -> List[dict]:
    """Health snapshot of every configured local provider."""
    snapshot = []
    for provider in (OmniRouteProvider(), OllamaProvider()):
        online = await provider.check_health()
        models: List[str] = await provider.list_models() if online else []
        snapshot.append(
            {
                "name": provider.name,
                "online": online,
                "models": models,
                "default_model": provider.default_model,
            }
        )
    return snapshot


def set_llm_provider(provider: Optional[LLMProvider]) -> None:
    """Override the cached provider (used by tests and future providers)."""
    global _provider
    _provider = provider


def reset_llm_provider() -> None:
    set_llm_provider(None)


def require_llm_provider() -> LLMProvider:
    provider = _provider
    if provider is None:
        raise LLMUnavailableError("LLM provider has not been initialised yet.")
    return provider


__all__ = [
    "LLMProvider",
    "LLMResponse",
    "LLMToolCall",
    "OmniRouteProvider",
    "OllamaProvider",
    "get_llm_provider",
    "get_active_model",
    "set_active_model",
    "describe_providers",
    "set_llm_provider",
    "reset_llm_provider",
    "require_llm_provider",
]
