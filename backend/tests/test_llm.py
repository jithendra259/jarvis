import pytest
from llm.client import LLMProvider, LLMResponse, LLMToolCall

class MockLLMProvider(LLMProvider):
    async def check_health(self) -> bool:
        return True

    async def generate(self, messages, tools=None, model=None, temperature=0.2) -> LLMResponse:
        last_msg = messages[-1]["content"] if messages else ""
        if "open" in last_msg.lower():
            return LLMResponse(
                content=None,
                tool_calls=[LLMToolCall(name="open_application", arguments={"app_name": "Notepad"})],
            )
        return LLMResponse(content="I am a local assistant.")

    async def stream(self, messages, model=None):
        yield "Hello"
        yield " from"
        yield " JARVIS"

@pytest.mark.asyncio
async def test_mock_llm_conversational():
    provider = MockLLMProvider()
    resp = await provider.generate([{"role": "user", "content": "Hello"}])
    assert resp.content == "I am a local assistant."
    assert len(resp.tool_calls) == 0

@pytest.mark.asyncio
async def test_mock_llm_tool_call():
    provider = MockLLMProvider()
    resp = await provider.generate([{"role": "user", "content": "Open Notepad"}])
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].name == "open_application"
    assert resp.tool_calls[0].arguments.get("app_name") == "Notepad"
