import pytest
from tools.applications import open_application, APP_ALIASES
from tools.registry import execute_tool, get_available_tools
from security.permissions import PermissionLevel

def test_app_aliases():
    assert "code" in APP_ALIASES.get("vscode", "")
    assert "calc.exe" in APP_ALIASES.get("calculator", "")
    assert "notepad.exe" in APP_ALIASES.get("notepad", "")

def test_available_tools_list():
    tools = get_available_tools()
    assert len(tools) >= 1
    tool_names = [t["function"]["name"] for t in tools]
    assert "open_application" in tool_names

def test_execute_empty_app_name():
    result, level, executed = execute_tool("open_application", {"app_name": ""})
    assert level == PermissionLevel.SAFE
    assert result["success"] is False
    assert "empty" in result["message"].lower()

def test_execute_unknown_tool():
    result, level, executed = execute_tool("unknown_tool_xyz", {})
    assert executed is False
    assert result.get("requires_confirmation") is True or "not implemented" in result.get("message", "").lower()
