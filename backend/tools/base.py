"""Tool primitives: declarative specs, structured results, argument validation.

A tool is the only way the agent can touch the machine. Because a local LLM
produces the arguments, every call is validated against the tool's declared
JSON-schema subset *before* the handler runs, and every handler returns a
`ToolResult` that reports the real outcome - success or failure. Nothing here
ever simulates an action.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from errors import ErrorCode

# JSON schema types understood by the validator.
_TYPE_MAP: Dict[str, Tuple[type, ...]] = {
    "string": (str,),
    "number": (int, float),
    "integer": (int,),
    "boolean": (bool,),
    "array": (list, tuple),
    "object": (dict,),
}


@dataclass
class ToolResult:
    """Structured outcome of a tool execution."""

    tool: str
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    error_code: Optional[str] = None
    executed: bool = True
    requires_confirmation: bool = False
    permission_level: Optional[str] = None
    confirmation_reason: Optional[str] = None
    confirmation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["data"] = dict(self.data)
        return payload

    @classmethod
    def failure(
        cls,
        tool: str,
        message: str,
        *,
        code: str = ErrorCode.TOOL_FAILED,
        executed: bool = False,
        **data: Any,
    ) -> "ToolResult":
        return cls(
            tool=tool,
            success=False,
            message=message,
            data=data,
            error_code=code,
            executed=executed,
        )


@dataclass(frozen=True)
class ToolSpec:
    """Declarative description of a tool.

    `parameters` is a small JSON-schema subset: object with `properties`,
    `required` and `additionalProperties`. It is converted to the OpenAI
    function-calling format when handed to the LLM.
    """

    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], ToolResult]
    permission: Any  # security.permissions.PermissionLevel (typed loosely to avoid a cycle)
    category: str = "general"
    returns: str = ""
    destructive: bool = False

    def to_openai_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "permission": getattr(self.permission, "value", str(self.permission)),
            "category": self.category,
            "returns": self.returns,
            "destructive": self.destructive,
        }


class ToolArgumentError(ValueError):
    """Raised when LLM-supplied arguments do not satisfy the tool schema."""

    def __init__(self, errors: List[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


def _type_matches(value: Any, expected: str) -> bool:
    allowed = _TYPE_MAP.get(expected)
    if allowed is None:
        return True
    if expected in ("number", "integer") and isinstance(value, bool):
        return False
    return isinstance(value, allowed)


def validate_arguments(parameters: Dict[str, Any], arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate and normalise LLM-supplied arguments.

    Returns a new dict containing only declared keys, with schema defaults
    applied. Raises `ToolArgumentError` describing every problem found.
    """
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        raise ToolArgumentError([f"arguments must be an object, received {type(arguments).__name__}"])

    properties: Dict[str, Any] = parameters.get("properties", {}) or {}
    required: List[str] = list(parameters.get("required", []) or [])
    allow_extra = parameters.get("additionalProperties", False)

    errors: List[str] = []
    for name in required:
        if name not in arguments or arguments.get(name) in (None, ""):
            errors.append(f"missing required argument '{name}'")

    for key, value in arguments.items():
        schema = properties.get(key)
        if schema is None:
            if not allow_extra:
                errors.append(f"unexpected argument '{key}'")
            continue
        expected = schema.get("type")
        if expected and not _type_matches(value, expected):
            errors.append(f"argument '{key}' must be of type {expected}, received {type(value).__name__}")
            continue
        enum_values = schema.get("enum")
        if enum_values and value not in enum_values:
            errors.append(f"argument '{key}' must be one of {enum_values}, received '{value}'")

    if errors:
        raise ToolArgumentError(errors)

    normalised: Dict[str, Any] = {}
    for key, schema in properties.items():
        if key in arguments and arguments[key] is not None:
            normalised[key] = arguments[key]
        elif "default" in schema:
            normalised[key] = schema["default"]
    return normalised


__all__ = [
    "ToolResult",
    "ToolSpec",
    "ToolArgumentError",
    "validate_arguments",
]
