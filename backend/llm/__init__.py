from .client import LLMProvider, LLMResponse, LLMToolCall
from .omniroute import OmniRouteProvider
from .ollama import OllamaProvider
from logger.logger import logger

_default_provider = None

async def get_llm_provider() -> LLMProvider:
    """
    Returns the active local LLM provider.
    Priority:
    1. OmniRoute (http://localhost:20128/v1)
    2. Ollama (http://localhost:11434)
    """
    global _default_provider
    if _default_provider is not None:
        return _default_provider

    # Try OmniRoute first
    omni = OmniRouteProvider()
    if await omni.check_health():
        logger.info("[LLM Provider] Connected to OmniRoute local gateway.")
        _default_provider = omni
        return omni

    # Fall back to Ollama
    ollama = OllamaProvider()
    if await ollama.check_health():
        logger.info("[LLM Provider] Connected to Ollama local instance.")
        _default_provider = ollama
        return ollama

    # If neither responded to check_health immediately, default to OmniRoute
    logger.warning("[LLM Provider] Neither OmniRoute nor Ollama responded to probe; defaulting to OmniRoute.")
    _default_provider = omni
    return omni

__all__ = ["LLMProvider", "LLMResponse", "LLMToolCall", "OmniRouteProvider", "OllamaProvider", "get_llm_provider"]
