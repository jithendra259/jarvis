"""Tool registry: the single gate between the LLM and the operating system.

Responsibilities
  1. Expose the implemented tools to the LLM as OpenAI function schemas.
  2. Validate LLM-supplied arguments against the tool schema.
  3. Evaluate the permission level and refuse unsafe actions without an
     explicit user confirmation.
  4. Run the handler and normalise the outcome into a `ToolResult`.
  5. Emit real-time activity events for the GUI.

The registry never invents a result: unknown tools, unimplemented tools,
invalid arguments and failed executions all produce explicit failures.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

from agent.events import EventType, event_bus
from errors import ErrorCode
from logger.logger import logger
from security.permissions import PermissionLevel, evaluate_permission
from tools.applications import OPEN_APPLICATION_SPEC
from tools.base import ToolArgumentError, ToolResult, ToolSpec, validate_arguments

# Tools named in the JARVIS specification that are not implemented yet.
# They are answered honestly instead of being silently simulated.
PLANNED_TOOLS: Dict[str, str] = {
    # Applications (Phase 2)
    "close_application": "Phase 2",
    "launch_application": "Phase 2",
    # Filesystem (Phase 2)
    "read_file": "Phase 2",
    "write_file": "Phase 2",
    "search_files": "Phase 2",
    "list_directory": "Phase 2",
    "create_directory": "Phase 2",
    "move_file": "Phase 2",
    "copy_file": "Phase 2",
    "delete_file": "Phase 2",
    # Windows (Phase 2)
    "get_system_information": "Phase 2",
    "get_running_processes": "Phase 2",
    "get_active_window": "Phase 2",
    "take_screenshot": "Phase 2",
    "get_clipboard": "Phase 2",
    "set_clipboard": "Phase 2",
    # Terminal (Phase 2)
    "run_powershell": "Phase 2",
    "run_command": "Phase 2",
    # Browser (Phase 2+)
    "open_browser": "Phase 2",
    "browse_to": "Phase 2",
    "extract_page_text": "Phase 2",
}


class ToolRegistry:
    """Registry of implemented tools plus the permission/validation gate."""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolSpec] = {}

    # -- registration -------------------------------------------------------

    def register(self, spec: ToolSpec) -> ToolSpec:
        if spec.name in self._tools:
            raise ValueError(f"Tool '{spec.name}' is already registered")
        self._tools[spec.name] = spec
        logger.info("[registry] registered tool '%s' (%s)", spec.name, spec.category)
        return spec

    def get(self, name: str) -> Optional[ToolSpec]:
        return self._tools.get(name)

    def names(self) -> List[str]:
        return sorted(self._tools)

    def describe(self) -> List[Dict[str, Any]]:
        return [self._tools[name].to_dict() for name in self.names()]

    def openai_schemas(self) -> List[Dict[str, Any]]:
        return [self._tools[name].to_openai_schema() for name in self.names()]

    # -- execution ----------------------------------------------------------

    def execute(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
        *,
        conversation_id: Optional[str] = None,
        confirmed: bool = False,
    ) -> ToolResult:
        """Validate permissions and arguments, then run the tool."""
        spec = self._tools.get(name)
        if spec is None:
            if name in PLANNED_TOOLS:
                phase = PLANNED_TOOLS[name]
                message = f"Tool '{name}' is not implemented yet ({phase})."
                logger.info("[registry] %s", message)
                return ToolResult(
                    tool=name,
                    success=False,
                    message=message,
                    error_code=ErrorCode.TOOL_NOT_IMPLEMENTED,
                    executed=False,
                    data={"phase": phase, "arguments": arguments or {}},
                )
            message = f"Unknown tool '{name}'. Available tools: {', '.join(self.names())}."
            logger.warning("[registry] %s", message)
            return ToolResult(
                tool=name,
                success=False,
                message=message,
                error_code=ErrorCode.TOOL_NOT_FOUND,
                executed=False,
                data={"available_tools": self.names()},
            )

        try:
            validated = validate_arguments(spec.parameters, arguments)
        except ToolArgumentError as exc:
            message = f"Invalid arguments for '{name}': {'; '.join(exc.errors)}"
            logger.warning("[registry] %s", message)
            return ToolResult(
                tool=name,
                success=False,
                message=message,
                error_code=ErrorCode.TOOL_INVALID_ARGUMENTS,
                executed=False,
                data={"errors": exc.errors, "arguments": arguments or {}},
            )

        level, reason = evaluate_permission(name, validated, spec_permission=spec.permission)
        if not confirmed and level in (PermissionLevel.CONFIRM, PermissionLevel.ADMIN):
            logger.info("[registry] '%s' held at %s: %s", name, level.value, reason)
            return ToolResult(
                tool=name,
                success=False,
                message=f"'{name}' requires your confirmation.",
                executed=False,
                requires_confirmation=True,
                permission_level=level.value,
                confirmation_reason=reason,
                data={"arguments": validated, "permission_level": level.value},
            )

        event_bus.emit(
            EventType.TOOL_STARTED,
            conversation_id=conversation_id,
            tool=name,
            arguments=validated,
        )
        started = time.perf_counter()
        try:
            result = spec.handler(validated)
        except Exception as exc:  # a broken tool must never kill the agent
            logger.exception("[registry] tool '%s' raised", name)
            result = ToolResult.failure(
                name,
                f"Tool '{name}' failed: {exc}",
                code=ErrorCode.TOOL_FAILED,
                executed=False,
            )
        duration_ms = round((time.perf_counter() - started) * 1000, 2)

        if not isinstance(result, ToolResult):  # pragma: no cover - handler contract
            result = ToolResult.failure(
                name,
                f"Tool '{name}' returned an invalid result type.",
                code=ErrorCode.TOOL_FAILED,
            )

        result.permission_level = result.permission_level or level.value
        payload = result.to_dict()
        payload["duration_ms"] = duration_ms
        if result.success:
            event_bus.emit(
                EventType.TOOL_COMPLETED,
                conversation_id=conversation_id,
                tool=name,
                message=result.message,
                result=payload,
                duration_ms=duration_ms,
            )
        else:
            event_bus.emit(
                EventType.TOOL_FAILED,
                conversation_id=conversation_id,
                tool=name,
                message=result.message,
                error_code=result.error_code,
                result=payload,
                duration_ms=duration_ms,
            )
        return result

    async def execute_async(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
        *,
        conversation_id: Optional[str] = None,
        confirmed: bool = False,
    ) -> ToolResult:
        """Run a tool off the event loop (handlers are blocking OS calls)."""
        return await asyncio.to_thread(
            self.execute,
            name,
            arguments,
            conversation_id=conversation_id,
            confirmed=confirmed,
        )


registry = ToolRegistry()
registry.register(OPEN_APPLICATION_SPEC)


def get_registry() -> ToolRegistry:
    return registry


def get_available_tools() -> List[Dict[str, Any]]:
    """OpenAI-compatible schemas for the tools exposed to the LLM."""
    return registry.openai_schemas()


def execute_tool(
    name: str,
    arguments: Optional[Dict[str, Any]] = None,
    *,
    conversation_id: Optional[str] = None,
    confirmed: bool = False,
) -> ToolResult:
    return registry.execute(name, arguments, conversation_id=conversation_id, confirmed=confirmed)


__all__ = [
    "ToolRegistry",
    "registry",
    "get_registry",
    "get_available_tools",
    "execute_tool",
    "PLANNED_TOOLS",
]
