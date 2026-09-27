"""Structured error types for the JARVIS runtime.

Every failure surfaced to the GUI carries a stable machine-readable `code`, a
human message and an HTTP status. One failing component (LLM, tool, voice)
must never take down the process, so callers convert failures into these
objects instead of letting exceptions escape.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class ErrorCode:
    """Stable error identifiers returned by the API."""

    # Configuration / environment
    CONFIG_INVALID = "config_invalid"
    MISSING_DEPENDENCY = "missing_dependency"

    # LLM
    LLM_UNAVAILABLE = "llm_unavailable"
    LLM_TIMEOUT = "llm_timeout"
    LLM_MALFORMED_OUTPUT = "llm_malformed_output"

    # Agent
    AGENT_FAILED = "agent_failed"
    AGENT_CANCELLED = "agent_cancelled"
    TOOL_LOOP_EXHAUSTED = "tool_loop_exhausted"

    # Tools
    TOOL_NOT_FOUND = "tool_not_found"
    TOOL_NOT_IMPLEMENTED = "tool_not_implemented"
    TOOL_INVALID_ARGUMENTS = "tool_invalid_arguments"
    TOOL_FAILED = "tool_failed"
    TOOL_PERMISSION_DENIED = "tool_permission_denied"
    TOOL_REQUIRES_CONFIRMATION = "tool_requires_confirmation"

    # Confirmation flow
    CONFIRMATION_NOT_FOUND = "confirmation_not_found"
    CONFIRMATION_EXPIRED = "confirmation_expired"

    # Voice
    VOICE_NOT_CONFIGURED = "voice_not_configured"
    VOICE_STT_UNAVAILABLE = "voice_stt_unavailable"
    VOICE_TTS_UNAVAILABLE = "voice_tts_unavailable"
    VOICE_INTERRUPTED = "voice_interrupted"

    # API
    BAD_REQUEST = "bad_request"
    INTERNAL_ERROR = "internal_error"
    NOT_IMPLEMENTED = "not_implemented"


class JarvisError(Exception):
    """Base error carrying a structured payload."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"JarvisError(code={self.code!r}, message={self.message!r})"


class ConfigurationError(JarvisError):
    def __init__(self, message: str, **details: Any) -> None:
        super().__init__(ErrorCode.CONFIG_INVALID, message, status_code=500, details=details)


class DependencyUnavailableError(JarvisError):
    def __init__(self, message: str, **details: Any) -> None:
        super().__init__(ErrorCode.MISSING_DEPENDENCY, message, status_code=503, details=details)


class LLMUnavailableError(JarvisError):
    def __init__(self, message: str, **details: Any) -> None:
        super().__init__(ErrorCode.LLM_UNAVAILABLE, message, status_code=503, details=details)


class LLMTimeoutError(JarvisError):
    def __init__(self, message: str, **details: Any) -> None:
        super().__init__(ErrorCode.LLM_TIMEOUT, message, status_code=504, details=details)


class ToolError(JarvisError):
    def __init__(
        self,
        message: str,
        *,
        code: str = ErrorCode.TOOL_FAILED,
        status_code: int = 400,
        **details: Any,
    ) -> None:
        super().__init__(code, message, status_code=status_code, details=details)


class NotImplementedYet(JarvisError):
    """Explicit marker for capabilities that belong to a later phase.

    JARVIS never pretends a capability exists: routes and tools that are not
    implemented raise this so the GUI can show an honest message.
    """

    def __init__(self, feature: str, phase: str) -> None:
        super().__init__(
            ErrorCode.NOT_IMPLEMENTED,
            f"'{feature}' is not implemented yet. Scheduled for {phase}.",
            status_code=501,
            details={"feature": feature, "phase": phase},
        )


__all__ = [
    "ErrorCode",
    "JarvisError",
    "ConfigurationError",
    "DependencyUnavailableError",
    "LLMUnavailableError",
    "LLMTimeoutError",
    "ToolError",
    "NotImplementedYet",
]
