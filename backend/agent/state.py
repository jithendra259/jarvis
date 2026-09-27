"""Typed LangGraph state for the JARVIS agent.

The state is a `TypedDict` so LangGraph can merge node updates safely and so
no agent data ever lives in uncontrolled module-level globals. Every node
returns a partial update; the graph accumulates the full state.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Sequence

try:  # Python 3.11+ ships TypedDict in typing; 3.10 needs the typing_extensions shim.
    from typing import TypedDict
except ImportError:  # pragma: no cover
    from typing_extensions import TypedDict  # type: ignore[assignment]

Intent = Literal["conversation", "tool_call", "unknown"]
ConfirmationStatus = Literal["none", "pending", "approved", "rejected", "expired"]


class AgentState(TypedDict, total=False):
    """State threaded through the JARVIS graph."""

    # Input
    user_input: str
    conversation_id: str
    messages: List[Dict[str, Any]]
    model: Optional[str]

    # Understanding / planning
    intent: Intent
    plan: Optional[str]
    tool_iterations: int

    # Tool execution
    selected_tool: Optional[str]
    tool_arguments: Optional[Dict[str, Any]]
    tool_result: Optional[Dict[str, Any]]
    tool_history: List[Dict[str, Any]]

    # Context and safety
    memory_context: Optional[str]
    requires_confirmation: bool
    confirmation_status: ConfirmationStatus
    confirmation_id: Optional[str]
    pending_action: Optional[Dict[str, Any]]

    # Output
    observations: List[str]
    final_response: Optional[str]
    error: Optional[Dict[str, Any]]


def initial_state(
    user_input: str,
    conversation_id: str = "default",
    messages: Optional[Sequence[Dict[str, Any]]] = None,
    memory_context: Optional[str] = None,
    model: Optional[str] = None,
) -> AgentState:
    """Build a fresh agent state for one turn."""
    return AgentState(
        user_input=user_input,
        conversation_id=conversation_id,
        messages=[dict(message) for message in (messages or [])],
        model=model,
        intent="unknown",
        plan=None,
        tool_iterations=0,
        selected_tool=None,
        tool_arguments=None,
        tool_result=None,
        tool_history=[],
        memory_context=memory_context,
        requires_confirmation=False,
        confirmation_status="none",
        confirmation_id=None,
        pending_action=None,
        observations=[],
        final_response=None,
        error=None,
    )


__all__ = ["AgentState", "Intent", "ConfirmationStatus", "initial_state"]
