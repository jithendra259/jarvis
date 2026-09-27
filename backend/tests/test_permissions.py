"""Permission layer: gating, escalation and defaults."""

from __future__ import annotations

import pytest

from security.permissions import (
    DANGEROUS_COMMAND_KEYWORDS,
    PermissionLevel,
    evaluate_permission,
)


def test_open_application_is_safe():
    level, reason = evaluate_permission("open_application", {"app_name": "Notepad"})
    assert level is PermissionLevel.SAFE
    assert reason is None


def test_read_only_system_tools_are_safe():
    for tool in ("get_system_information", "get_running_processes", "get_active_window", "read_file"):
        level, _ = evaluate_permission(tool, {})
        assert level is PermissionLevel.SAFE


def test_mutating_tools_require_confirmation():
    for tool in ("write_file", "move_file", "create_directory", "run_powershell", "run_command"):
        level, reason = evaluate_permission(tool, {"command": "dir"})
        assert level in (PermissionLevel.CONFIRM, PermissionLevel.ADMIN)
        assert reason


def test_destructive_tools_require_admin():
    for tool in ("delete_file", "shutdown_computer", "restart_computer"):
        level, reason = evaluate_permission(tool, {})
        assert level is PermissionLevel.ADMIN
        assert reason


def test_unknown_tool_defaults_to_confirm_not_execution():
    level, reason = evaluate_permission("totally_unknown", {})
    assert level is PermissionLevel.CONFIRM
    assert reason


@pytest.mark.parametrize(
    "command",
    [
        "format C: /fs:NTFS",
        "rm -rf /",
        "reg delete HKLM\\SOFTWARE\\Test",
        "diskpart",
        "Remove-Item -Recurse C:\\Users",
        "Restart-Computer",
    ],
)
def test_dangerous_commands_escalate_to_admin(command):
    level, reason = evaluate_permission("run_powershell", {"command": command})
    assert level is PermissionLevel.ADMIN
    assert "dangerous" in reason.lower()


def test_benign_command_stays_confirm():
    level, _ = evaluate_permission("run_powershell", {"command": "Get-Process"})
    assert level is PermissionLevel.CONFIRM


def test_spec_permission_overrides_the_table():
    level, _ = evaluate_permission("custom_tool", {}, spec_permission=PermissionLevel.SAFE)
    assert level is PermissionLevel.SAFE


def test_dangerous_keyword_list_is_not_empty():
    assert "format" in DANGEROUS_COMMAND_KEYWORDS
