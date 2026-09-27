import json
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from logger.logger import logger
from llm import get_llm_provider
from tools.registry import get_available_tools, execute_tool
from .state import AgentState
from .prompts import JARVIS_SYSTEM_PROMPT


async def understand_and_plan(state: AgentState) -> Dict[str, Any]:
    """
    Evaluates user input, reasons about required tools, and initiates tool selection.
    """
    user_input = state.get("user_input", "")
    messages = list(state.get("messages", []))
    
    # Ensure system prompt is present
    formatted_messages = [{"role": "system", "content": JARVIS_SYSTEM_PROMPT}]
    formatted_messages.extend(messages)
    formatted_messages.append({"role": "user", "content": user_input})

    llm = await get_llm_provider()
    tools = get_available_tools()

    logger.info(f"[LangGraph] Evaluating user input: '{user_input}'")
    try:
        response = await llm.generate(messages=formatted_messages, tools=tools)
        
        # Check if model requested a tool
        if response.tool_calls:
            tc = response.tool_calls[0]
            logger.info(f"[LangGraph] Tool selected: '{tc.name}' with args {tc.arguments}")
            return {
                "selected_tool": tc.name,
                "tool_arguments": tc.arguments,
                "intent": f"Execute {tc.name}",
                "plan": f"Launch and verify {tc.arguments.get('app_name', tc.name)}",
                "observations": [f"Selected tool '{tc.name}'"],
            }
        else:
            return {
                "final_response": response.content or "How may I assist you?",
                "selected_tool": None,
                "tool_arguments": None,
            }
    except Exception as e:
        logger.error(f"[LangGraph Understand Error] {e}")
        return {
            "error": str(e),
            "final_response": f"I encountered an error evaluating your request: {str(e)}",
        }


def should_execute_tool(state: AgentState) -> Literal["execute_tool", "end"]:
    """Conditional router determining whether to execute tool or terminate."""
    if state.get("selected_tool"):
        return "execute_tool"
    return "end"


async def execute_tool_node(state: AgentState) -> Dict[str, Any]:
    """Executes the selected tool through the permission-validated registry."""
    tool_name = state.get("selected_tool")
    tool_args = state.get("tool_arguments") or {}

    logger.info(f"[LangGraph] Executing tool: '{tool_name}'")
    result, perm_level, executed = execute_tool(tool_name, tool_args)

    obs = list(state.get("observations", []))
    obs.append(f"Result: {result.get('message', 'done')}")

    if not executed and result.get("requires_confirmation"):
        return {
            "tool_result": result,
            "requires_confirmation": True,
            "observations": obs,
            "final_response": f"This action requires your confirmation ({result.get('reason')}). Proceed?",
        }

    return {
        "tool_result": result,
        "observations": obs,
        "requires_confirmation": False,
    }


async def respond_with_result(state: AgentState) -> Dict[str, Any]:
    """Generates the final concise response confirming tool outcome."""
    user_input = state.get("user_input", "")
    tool_name = state.get("selected_tool")
    tool_result = state.get("tool_result") or {}
    
    # If confirmation was required, response was already formulated
    if state.get("requires_confirmation"):
        return {}

    llm = await get_llm_provider()
    prompt = [
        {"role": "system", "content": JARVIS_SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
        {
            "role": "assistant",
            "content": f"Executed tool '{tool_name}' with outcome: {json.dumps(tool_result)}",
        },
        {
            "role": "user",
            "content": "Provide a concise, natural confirmation of this outcome.",
        },
    ]

    try:
        response = await llm.generate(messages=prompt)
        final_text = response.content or tool_result.get("message", "Action completed.")
        return {"final_response": final_text}
    except Exception as e:
        logger.warning(f"[LangGraph Response Warning] LLM response generation failed, using direct tool message: {e}")
        return {"final_response": tool_result.get("message", "Action completed.")}


# Build and compile the LangGraph workflow
def build_agent_graph():
    builder = StateGraph(AgentState)

    builder.add_node("understand_and_plan", understand_and_plan)
    builder.add_node("execute_tool", execute_tool_node)
    builder.add_node("respond_with_result", respond_with_result)

    builder.set_entry_point("understand_and_plan")

    builder.add_conditional_edges(
        "understand_and_plan",
        should_execute_tool,
        {
            "execute_tool": "execute_tool",
            "end": END,
        },
    )

    builder.add_edge("execute_tool", "respond_with_result")
    builder.add_edge("respond_with_result", END)

    return builder.compile()


jarvis_graph = build_agent_graph()
