"""Agent runner: one entry point for text, voice and HTTP callers.

The runner owns real-time event emission and result shaping so the graph stays
free of transport concerns and every caller (REST, WebSocket, future voice
agent) observes identical behaviour.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from agent.events import EventType, event_bus
from agent.graph import jarvis_graph
from agent.state import AgentState, initial_state
from errors import JarvisError
from logger.logger import logger


async def run_agent(
    user_input: str,
    conversation_id: str = "default",
    *,
    messages: Optional[List[Dict[str, Any]]] = None,
    memory_context: Optional[str] = None,
    model: Optional[str] = None,
) -> AgentState:
    """Execute one full agent turn and return the final state."""
    text = (user_input or "").strip()
    if not text:
        return {
            "final_response": "I did not receive a request.",
            "error": {"code": "bad_request", "message": "Empty user input"},
        }

    state: AgentState = initial_state(
        user_input=text,
        conversation_id=conversation_id,
        messages=messages,
        memory_context=memory_context,
        model=model,
    )

    event_bus.emit(
        EventType.AGENT_STARTED, conversation_id=conversation_id, user_input=text
    )
    event_bus.emit(EventType.AGENT_THINKING, conversation_id=conversation_id)
    started = time.perf_counter()

    try:
        final_state: AgentState = await jarvis_graph.ainvoke(state)
    except JarvisError as exc:
        logger.error("[agent] %s: %s", exc.code, exc.message)
        event_bus.emit(
            EventType.AGENT_ERROR,
            conversation_id=conversation_id,
            code=exc.code,
            message=exc.message,
        )
        raise
    except Exception as exc:  # never let an unexpected failure escape untyped
        logger.exception("[agent] unexpected failure")
        event_bus.emit(
            EventType.AGENT_ERROR, conversation_id=conversation_id, code="agent_failed", message=str(exc)
        )
        raise

    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    final_state.setdefault("final_response", None)

    if final_state.get("plan"):
        event_bus.emit(
            EventType.AGENT_PLANNED,
            conversation_id=conversation_id,
            plan=final_state.get("plan"),
            intent=final_state.get("intent"),
        )

    event_bus.emit(
        EventType.AGENT_COMPLETED,
        conversation_id=conversation_id,
        reply=final_state.get("final_response"),
        requires_confirmation=bool(final_state.get("requires_confirmation")),
        duration_ms=duration_ms,
    )
    return final_state


__all__ = ["run_agent"]
