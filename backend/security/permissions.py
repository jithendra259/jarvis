"""Permission layer for tool execution.

Levels
  SAFE    - read-only or standard desktop action, executed immediately
            (open an application, read a file, list processes).
  CONFIRM - changes files or state; JARVIS must explain the action and wait
            for an explicit user confirmation.
  ADMIN   - destructive, security or system level operations. Requires
            confirmation *and* an elevated (administrator) backend.

Destructive commands produced by an LLM are never executed blindly: the
command text is inspected and escalated to ADMIN when it contains known
dangerous operations.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional, Tuple

from logger.logger import logger


class PermissionLevel(str, Enum):
    SAFE = "SAFE"  # harmless read-only or standard execution
    CONFIRM = "CONFIRM"  # modifies files or state, user confirmation required
    ADMIN = "ADMIN"  # critical administrative / destructive operation


# Registry of base tool permission ratings. Tools not listed default to CONFIRM.
TOOL_PERMISSIONS: Dict[str, PermissionLevel] = {
    # Applications
    "open_application": PermissionLevel.SAFE,
    "close_application": PermissionLevel.CONFIRM,
    "launch_application": PermissionLevel.SAFE,
    # System information
    "get_system_information": PermissionLevel.SAFE,
    "get_running_processes": PermissionLevel.SAFE,
    "get_active_window": PermissionLevel.SAFE,
    "take_screenshot": PermissionLevel.SAFE,
    "get_clipboard": PermissionLevel.SAFE,
    "set_clipboard": PermissionLevel.SAFE,
    # Filesystem
    "read_file": PermissionLevel.SAFE,
    "list_directory": PermissionLevel.SAFE,
    "search_files": PermissionLevel.SAFE,
    "write_file": PermissionLevel.CONFIRM,
    "create_directory": PermissionLevel.CONFIRM,
    "move_file": PermissionLevel.CONFIRM,
    "copy_file": PermissionLevel.SAFE,
    "delete_file": PermissionLevel.ADMIN,
    # Terminal and system commands
    "run_powershell": PermissionLevel.CONFIRM,
    "run_command": PermissionLevel.CONFIRM,
    "shutdown_computer": PermissionLevel.ADMIN,
    "restart_computer": PermissionLevel.ADMIN,
}

# Command fragments that escalate a shell tool to ADMIN.
DANGEROUS_COMMAND_KEYWORDS = (
    "format",
    "del /f /s /q",
    "rmdir /s /q",
    "rm -rf",
    "reg delete",
    "reg add",
    "diskpart",
    "bcdedit",
    "cipher /w",
    "net user",
    "shutdown",
    "stop-computer",
    "restart-computer",
    "remove-item",
    "clear-disk",
    "initialize-disk",
    "set-executionpolicy",
    "invoke-webrequest",
    "curl ",
    "wget ",
)

# Tools whose `command` argument is inspected for dangerous fragments.
COMMAND_TOOLS = ("run_powershell", "run_command", "run_terminal_command")


def _matches_dangerous(command: str) -> Optional[str]:
    lowered = command.lower()
    for keyword in DANGEROUS_COMMAND_KEYWORDS:
        if keyword in lowered:
            return keyword
    return None


def evaluate_permission(
    tool_name: str,
    arguments: Optional[Dict[str, Any]] = None,
    *,
    spec_permission: Optional[PermissionLevel] = None,
) -> Tuple[PermissionLevel, Optional[str]]:
    """Return the effective permission level and an explanation when gated."""
    arguments = arguments or {}
    base_level = spec_permission or TOOL_PERMISSIONS.get(tool_name, PermissionLevel.CONFIRM)

    if tool_name in COMMAND_TOOLS:
        command = str(arguments.get("command", ""))
        keyword = _matches_dangerous(command)
        if keyword:
            logger.warning(
                "[permissions] '%s' escalated to ADMIN: command contains %r", tool_name, keyword
            )
            return PermissionLevel.ADMIN, f"Potentially dangerous command detected (contains '{keyword}')"

    if base_level == PermissionLevel.ADMIN:
        return PermissionLevel.ADMIN, f"'{tool_name}' performs critical administrative or destructive changes"
    if base_level == PermissionLevel.CONFIRM:
        return PermissionLevel.CONFIRM, f"'{tool_name}' will modify files or system state"
    return PermissionLevel.SAFE, None


__all__ = [
    "PermissionLevel",
    "TOOL_PERMISSIONS",
    "DANGEROUS_COMMAND_KEYWORDS",
    "evaluate_permission",
]
