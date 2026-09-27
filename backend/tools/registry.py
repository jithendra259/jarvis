import json
from typing import Dict, Any, List
from .applications import open_application, OPEN_APP_TOOL_SPEC

class ToolRegistry:
    """Registry managing tool schemas and execution."""

    def __init__(self):
        self._tools = {
            "open_application": open_application,
        }
        self._specs = [
            OPEN_APP_TOOL_SPEC,
        ]

    def get_specs(self) -> List[Dict[str, Any]]:
        return self._specs

    def execute(self, tool_name: str, arguments_json: str) -> Dict[str, Any]:
        if tool_name not in self._tools:
            return {"error": f"Tool '{tool_name}' not found."}

        try:
            kwargs = json.loads(arguments_json) if isinstance(arguments_json, str) else arguments_json
        except Exception as e:
            return {"error": f"Failed to parse arguments: {str(e)}"}

        func = self._tools[tool_name]
        try:
            result = func(**kwargs)
            return result
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

registry = ToolRegistry()
