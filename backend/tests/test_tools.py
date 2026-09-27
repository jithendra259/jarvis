"""Tool layer: validation, registry gating and honest application launching.

None of these tests launch a real application; process creation and process
discovery are monkeypatched so the suite stays fast, offline and side-effect
free.
"""

from __future__ import annotations

import pytest

from errors import ErrorCode
from security.permissions import PermissionLevel
from tools import applications as apps
from tools.base import ToolArgumentError, ToolResult, ToolSpec, validate_arguments
from tools.registry import PLANNED_TOOLS, registry

OPEN_APP_SCHEMA = {
    "type": "object",
    "properties": {"app_name": {"type": "string"}},
    "required": ["app_name"],
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# Argument validation
# ---------------------------------------------------------------------------
def test_validate_applies_defaults_and_filters_unknown_keys():
    schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "recursive": {"type": "boolean", "default": False},
        },
        "required": ["path"],
        "additionalProperties": False,
    }
    assert validate_arguments(schema, {"path": "C:/tmp"}) == {"path": "C:/tmp", "recursive": False}
    with pytest.raises(ToolArgumentError):
        validate_arguments(schema, {"path": "C:/tmp", "evil": 1})


def test_validate_rejects_missing_and_wrong_types():
    with pytest.raises(ToolArgumentError) as missing:
        validate_arguments(OPEN_APP_SCHEMA, {})
    assert "app_name" in str(missing.value)

    with pytest.raises(ToolArgumentError) as wrong_type:
        validate_arguments(OPEN_APP_SCHEMA, {"app_name": 42})
    assert "type" in str(wrong_type.value)

    with pytest.raises(ToolArgumentError):
        validate_arguments(OPEN_APP_SCHEMA, ["not", "a", "dict"])


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
def test_registry_exposes_openai_schemas():
    schemas = registry.openai_schemas()
    names = [schema["function"]["name"] for schema in schemas]
    assert "open_application" in names
    assert all(schema["type"] == "function" for schema in schemas)


def test_registry_describes_permission_levels():
    described = {entry["name"]: entry for entry in registry.describe()}
    assert described["open_application"]["permission"] == PermissionLevel.SAFE.value
    assert described["open_application"]["category"] == "applications"


def test_unknown_tool_is_reported_not_executed():
    result = registry.execute("definitely_not_a_tool", {})
    assert result.success is False
    assert result.executed is False
    assert result.error_code == ErrorCode.TOOL_NOT_FOUND
    assert "open_application" in result.message


def test_planned_tool_reports_not_implemented():
    result = registry.execute("write_file", {"path": "a", "content": "b"})
    assert result.success is False
    assert result.error_code == ErrorCode.TOOL_NOT_IMPLEMENTED
    assert "Phase 2" in result.message
    assert "write_file" in PLANNED_TOOLS


def test_invalid_arguments_never_reach_the_handler(clean_registry):
    calls = []

    def handler(arguments):
        calls.append(arguments)
        return ToolResult(tool="spy", success=True, message="ran")

    clean_registry.register(
        ToolSpec(
            name="spy",
            description="test tool",
            parameters=OPEN_APP_SCHEMA,
            handler=handler,
            permission=PermissionLevel.SAFE,
        )
    )
    result = clean_registry.execute("spy", {"wrong": 1})
    assert result.success is False
    assert result.error_code == ErrorCode.TOOL_INVALID_ARGUMENTS
    assert calls == []


def test_confirm_level_is_held_until_approved(clean_registry):
    executed = []

    def handler(arguments):
        executed.append(arguments)
        return ToolResult(tool="danger", success=True, message="done")

    clean_registry.register(
        ToolSpec(
            name="danger",
            description="test tool",
            parameters={"type": "object", "properties": {}, "additionalProperties": False},
            handler=handler,
            permission=PermissionLevel.CONFIRM,
        )
    )

    held = clean_registry.execute("danger", {})
    assert held.requires_confirmation is True
    assert held.executed is False
    assert held.permission_level == "CONFIRM"
    assert executed == []

    approved = clean_registry.execute("danger", {}, confirmed=True)
    assert approved.success is True
    assert executed == [{}]


def test_handler_exception_is_contained(clean_registry):
    def handler(arguments):
        raise RuntimeError("boom")

    clean_registry.register(
        ToolSpec(
            name="explodes",
            description="test tool",
            parameters={"type": "object", "properties": {}},
            handler=handler,
            permission=PermissionLevel.SAFE,
        )
    )
    result = clean_registry.execute("explodes", {})
    assert result.success is False
    assert "boom" in result.message
    assert result.error_code == ErrorCode.TOOL_FAILED


# ---------------------------------------------------------------------------
# open_application
# ---------------------------------------------------------------------------
def test_empty_app_name_is_rejected():
    result = apps.open_application("   ")
    assert result.success is False
    assert result.error_code == ErrorCode.TOOL_INVALID_ARGUMENTS


def test_unknown_application_is_reported(monkeypatch):
    monkeypatch.setattr(apps, "_find_start_menu_shortcut", lambda name: None)
    result = apps.open_application("Totally Unknown Editor 9000")
    assert result.success is False
    assert result.error_code == ErrorCode.TOOL_NOT_FOUND
    assert "known application" in result.message


def test_alias_lookup_is_normalised():
    assert apps._find_alias("VS Code")[0] == "code"
    assert apps._find_alias("visualstudio code") is not None
    assert apps._find_uri("Windows Settings") == "ms-settings:"


def test_start_menu_matching_uses_fuzzy_names(monkeypatch, tmp_path):
    shortcuts = tmp_path / "Start Menu"
    (shortcuts / "Microsoft").mkdir(parents=True)
    (shortcuts / "Microsoft" / "Visual Studio Code.lnk").write_text("")
    (shortcuts / "Microsoft" / "7-Zip.lnk").write_text("")
    monkeypatch.setattr(apps, "START_MENU_DIRS", [shortcuts])

    assert apps._find_start_menu_shortcut("visual studio code").name == "Visual Studio Code.lnk"
    assert apps._find_start_menu_shortcut("7zip").name == "7-Zip.lnk"
    assert apps._find_start_menu_shortcut("nothing like this exists") is None


def test_launch_failure_is_reported(monkeypatch):
    monkeypatch.setattr(apps, "_process_snapshot", lambda: {})
    monkeypatch.setattr(apps, "_launch_command", lambda command: (False, "shell", "not recognized"))
    result = apps.open_application("Notepad")
    assert result.success is False
    assert "not recognized" in result.message


def test_launch_success_requires_a_running_process(monkeypatch):
    monkeypatch.setattr(apps, "_process_snapshot", lambda: {})
    monkeypatch.setattr(apps, "_launch_command", lambda command: (True, "executable", ""))
    monkeypatch.setattr(apps, "LAUNCH_VERIFY_TIMEOUT", 0.05)
    result = apps.open_application("Notepad")
    assert result.success is False
    assert "did not start" in result.message


def test_launch_success_when_process_appears(monkeypatch):
    snapshots = iter([{}, {1234: "notepad.exe"}])
    monkeypatch.setattr(apps, "_process_snapshot", lambda: next(snapshots, {}))
    monkeypatch.setattr(apps, "_launch_command", lambda command: (True, "executable", ""))
    result = apps.open_application("Notepad")
    assert result.success is True
    assert result.message == "Notepad is open."
    assert result.data["process"] == "notepad.exe"
    assert result.data["pid"] == 1234
    assert result.data["verified_by"] == "image_name"


def test_existing_single_instance_process_counts_as_running(monkeypatch):
    monkeypatch.setattr(apps, "_process_snapshot", lambda: {99: "code.exe"})
    monkeypatch.setattr(apps, "_launch_command", lambda command: (True, "executable", ""))
    result = apps.open_application("Visual Studio Code")
    assert result.success is True
    assert result.data["verified_by"] == "image_name"


def test_uri_launch_failure_is_reported(monkeypatch):
    monkeypatch.setattr(apps, "_open_shell_target", lambda target: (False, "no handler"))
    result = apps.open_application("Windows Settings")
    assert result.success is False
    assert "ms-settings:" in result.message
