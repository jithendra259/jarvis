"""JARVIS LangGraph agent.

Graph shape (Phase 1):

    UNDERSTAND + PLAN + SELECT_TOOL
            |
            +--(no tool needed)--> RESPOND --> END
            |
            v
      EXECUTE_TOOL --> OBSERVE_RESULT --> DECIDE --> RESPOND --> END

`decide_next_step` is the DECIDE step: it decides whether the turn is finished
or whether a confirmation is pending. Chained tool calls (re-planning after an
observation) are enabled in a later phase through the same hook, so the graph
gains the capability without rewriting the nodes.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Literal

from langgraph.graph import END, StateGraph

from agent.confirmations import store as confirmation_store
from agent.events import EventType, event_bus
from agent.prompts import (
    JARVIS_SYSTEM_PROMPT,
    build_response_prompt,
    build_tool_section,
)
from agent.state import AgentState
from config.settings import settings
from errors import ErrorCode, JarvisError, LLMTimeoutError, LLMUnavailableError
from llm import get_llm_provider
from logger.logger import logger
from tools.registry import PLANNED_TOOLS, registry

MAX_TOOL_ITERATIONS = max(1, settings.llm_max_tool_iterations)


def _system_prompt() -> str:
    return JARVIS_SYSTEM_PROMPT.format(
        tool_section=build_tool_section(registry.names(), PLANNED_TOOLS)
    )


def _history_messages(state: AgentState) -> List[Dict[str, Any]]:
    return [dict(message) for message in state.get("messages", []) or []]


def _user_content(state: AgentState) -> str:
    parts = [state.get("user_input", "")]
    memory_context = state.get("memory_context")
    if memory_context:
        parts.insert(0, f"Relevant memory:\n{memory_context}\n")
    return "\n".join(part for part in parts if part)


# --------------------------------------------------------------------------
# UNDERSTAND / PLAN / SELECT_TOOL
# --------------------------------------------------------------------------
async def understand(state: AgentState) -> Dict[str, Any]:
    """Interpret the request, plan the action and pick a tool when needed."""
    user_content = _user_content(state)
    messages: List[Dict[str, Any]] = [{"role": "system", "content": _system_prompt()}]
    messages.extend(_history_messages(state))
    messages.append({"role": "user", "content": user_content})

    provider = await get_llm_provider()
    active_model = state.get("model")
    try:
        response = await provider.generate(
            messages=messages,
            tools=registry.openai_schemas(),
            model=active_model,
        )
    except JarvisError:
        raise
    except TimeoutError as exc:
        raise LLMTimeoutError(f"Local LLM did not respond in time: {exc}") from exc
    except Exception as exc:
        raise LLMUnavailableError(
            f"Local LLM provider is unavailable: {exc}", provider=type(provider).__name__
        ) from exc

    if response.tool_calls:
        call = response.tool_calls[0]
        if len(response.tool_calls) > 1:
            logger.info("[agent] model requested %d tool calls; executing the first", len(response.tool_calls))
        logger.info("[agent] selected tool '%s' with %s", call.name, call.arguments)
        observations = list(state.get("observations", []))
        observations.append(f"Selected tool '{call.name}' for: {state.get('user_input', '')}")
        return {
            "intent": "tool_call",
            "plan": f"Call {call.name} with {json.dumps(call.arguments, ensure_ascii=False)} and report the real result",
            "selected_tool": call.name,
            "tool_arguments": call.arguments,
            "tool_iterations": int(state.get("tool_iterations", 0)) + 1,
            "observations": observations,
            "error": None,
        }

    content = (response.content or "").strip()
    if not content:
        return {
            "intent": "unknown",
            "final_response": "I understood the request but could not produce an answer.",
            "error": {"code": ErrorCode.LLM_MALFORMED_OUTPUT, "message": "Empty completion without tool call"},
        }
    return {"intent": "conversation", "final_response": content, "error": None}


def route_after_understand(state: AgentState) -> Literal["execute_tool", "respond"]:
    """Tool requests continue to execution; chat requests answer directly."""
    if state.get("selected_tool"):
        return "execute_tool"
    return "respond"


# --------------------------------------------------------------------------
# EXECUTE_TOOL
# --------------------------------------------------------------------------
async def execute_tool_node(state: AgentState) -> Dict[str, Any]:
    """Run the selected tool through validation, permissions and the handler."""
    tool_name = state.get("selected_tool") or ""
    arguments = state.get("tool_arguments") or {}
    conversation_id = state.get("conversation_id", "default")

    result = await registry.execute_async(
        tool_name, arguments, conversation_id=conversation_id
    )
    payload = result.to_dict()

    observations = list(state.get("observations", []))
    observations.append(
        f"{tool_name}({json.dumps(arguments, ensure_ascii=False)}) -> "
        f"{'success' if result.success else 'failure'}: {result.message}"
    )
    history = list(state.get("tool_history", []))
    history.append({"tool": tool_name, "arguments": arguments, "result": payload})

    if result.requires_confirmation:
        pending = confirmation_store.create(
            tool=tool_name,
            arguments=result.data.get("arguments", arguments),
            permission_level=result.permission_level or "CONFIRM",
            reason=result.confirmation_reason or "This action needs your approval.",
            conversation_id=conversation_id,
        )
        event_bus.emit(
            EventType.CONFIRMATION_REQUIRED,
            conversation_id=conversation_id,
            tool=tool_name,
            arguments=pending.arguments,
            permission_level=pending.permission_level,
            reason=pending.reason,
            confirmation_id=pending.id,
        )
        return {
            "tool_result": payload,
            "tool_history": history,
            "observations": observations,
            "requires_confirmation": True,
            "confirmation_status": "pending",
            "confirmation_id": pending.id,
            "pending_action": pending.to_dict(),
            "final_response": (
                f"{tool_name} needs your approval: {pending.reason} "
                f"Arguments: {json.dumps(pending.arguments, ensure_ascii=False)}. "
                "Confirm in the activity panel to proceed."
            ),
        }

    return {
        "tool_result": payload,
        "tool_history": history,
        "observations": observations,
        "requires_confirmation": False,
        "confirmation_status": "none",
        "confirmation_id": None,
        "pending_action": None,
        "error": None
        if result.success
        else {"code": result.error_code or ErrorCode.TOOL_FAILED, "message": result.message},
    }


# --------------------------------------------------------------------------
# OBSERVE_RESULT
# --------------------------------------------------------------------------
async def observe_result(state: AgentState) -> Dict[str, Any]:
    """Record what actually happened; no success is ever assumed."""
    result = state.get("tool_result") or {}
    observations = list(state.get("observations", []))
    observations.append(
        f"Observed: success={bool(result.get('success'))}, "
        f"error_code={result.get('error_code')}, data={json.dumps(result.get('data', {}), default=str)[:400]}"
    )
    return {"observations": observations}


# --------------------------------------------------------------------------
# DECIDE
# --------------------------------------------------------------------------
def decide_next_step(state: AgentState) -> Literal["respond"]:
    """DECIDE: a confirmation request or a finished tool call ends the turn.

    Chained tool calls (re-entering `understand` with the new observation) are
    the documented extension point: they are enabled once the permission model
    and multi-step planning land in Phase 2.
    """
    if state.get("requires_confirmation"):
        logger.info("[agent] turn paused awaiting user confirmation")
        return "respond"
    if int(state.get("tool_iterations", 0)) >= MAX_TOOL_ITERATIONS:
        logger.warning("[agent] tool iteration limit reached (%d)", MAX_TOOL_ITERATIONS)
    return "respond"


# --------------------------------------------------------------------------
# RESPOND
# --------------------------------------------------------------------------
async def respond(state: AgentState) -> Dict[str, Any]:
    """Produce the final user-facing reply, grounded in the tool result."""
    if state.get("requires_confirmation"):
        return {}  # the question was already composed in EXECUTE_TOOL
    if not state.get("selected_tool"):
        return {}  # conversational answer produced in UNDERSTAND

    result = state.get("tool_result") or {}
    tool_name = state.get("selected_tool") or "tool"

    if not result.get("success"):
        # Never let the model dress a failure as a success: report it verbatim.
        message = result.get("message") or f"{tool_name} did not complete."
        return {"final_response": message}

    provider = await get_llm_provider()
    messages = build_response_prompt(
        user_input=state.get("user_input", ""),
        tool_name=tool_name,
        tool_result=result,
        observations=state.get("observations"),
    )
    try:
        response = await provider.generate(messages=messages, model=state.get("model"))
    except Exception as exc:
        logger.warning("[agent] response phrasing failed, using tool message: %s", exc)
        return {"final_response": result.get("message") or f"{tool_name} completed."}

    text = (response.content or "").strip()
    if not text:
        return {"final_response": result.get("message") or f"{tool_name} completed."}
    return {"final_response": text}


# --------------------------------------------------------------------------
# Graph construction
# --------------------------------------------------------------------------
def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("understand", understand)
    builder.add_node("execute_tool", execute_tool_node)
    builder.add_node("observe_result", observe_result)
    builder.add_node("respond", respond)

    builder.set_entry_point("understand")
    builder.add_conditional_edges(
        "understand",
        route_after_understand,
        {"execute_tool": "execute_tool", "respond": "respond"},
    )
    builder.add_edge("execute_tool", "observe_result")
    builder.add_edge("observe_result", "respond")
    builder.add_edge("respond", END)

    return builder.compile()


jarvis_graph = build_graph()

__all__ = [
    "jarvis_graph",
    "build_graph",
    "understand",
    "execute_tool_node",
    "observe_result",
    "decide_next_step",
    "respond",
    "MAX_TOOL_ITERATIONS",
]
