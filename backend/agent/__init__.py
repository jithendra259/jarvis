"""JARVIS agent package: LangGraph orchestration, state, events, confirmations.

Attributes are resolved lazily so importing a leaf module (for example
`agent.events` from the tool layer) never triggers the graph import cycle.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "AgentState",
    "EventType",
    "event_bus",
    "initial_state",
    "jarvis_graph",
    "run_agent",
]

_EXPORTS = {
    "AgentState": ("agent.state", "AgentState"),
    "initial_state": ("agent.state", "initial_state"),
    "EventType": ("agent.events", "EventType"),
    "event_bus": ("agent.events", "event_bus"),
    "jarvis_graph": ("agent.graph", "jarvis_graph"),
    "run_agent": ("agent.runner", "run_agent"),
}


def __getattr__(name: str) -> Any:
    target = _EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module 'agent' has no attribute {name!r}")
    module_name, attribute = target
    import importlib

    return getattr(importlib.import_module(module_name), attribute)
