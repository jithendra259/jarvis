import pytest
from security.permissions import evaluate_permission, PermissionLevel

def test_safe_permissions():
    level, reason = evaluate_permission("open_application", {"app_name": "Notepad"})
    assert level == PermissionLevel.SAFE
    assert reason is None

    level, reason = evaluate_permission("get_system_information", {})
    assert level == PermissionLevel.SAFE

def test_confirm_permissions():
    level, reason = evaluate_permission("write_file", {"path": "test.txt", "content": "hi"})
    assert level == PermissionLevel.CONFIRM
    assert reason is not None

def test_admin_destructive_escalation():
    level, reason = evaluate_permission("run_powershell", {"command": "format C: /fs:NTFS"})
    assert level == PermissionLevel.ADMIN
    assert "format" in reason

    level, reason = evaluate_permission("run_command", {"command": "rm -rf /"})
    assert level == PermissionLevel.ADMIN
