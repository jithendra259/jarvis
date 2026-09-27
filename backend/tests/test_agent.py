import pytest
from agent.graph import jarvis_graph
from agent.state import AgentState

@pytest.mark.asyncio
async def test_langgraph_invocation_structure():
    # Verify graph runs and maintains AgentState structure
    state = AgentState(user_input="Who are you?", conversation_id="test-session", messages=[])
    result = await jarvis_graph.ainvoke(state)
    assert "final_response" in result
    assert result["final_response"] is not None
    assert len(result["final_response"]) > 0

@pytest.mark.asyncio
async def test_langgraph_tool_selection():
    # Verify model tool calling through LangGraph
    state = AgentState(user_input="Please open Calculator", conversation_id="test-session", messages=[])
    result = await jarvis_graph.ainvoke(state)
    assert result.get("selected_tool") == "open_application"
    assert result.get("tool_result") is not None
    assert result.get("tool_result", {}).get("success") is True
