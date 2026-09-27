import json
from typing import List, Dict, Any, AsyncGenerator
from llm.client import omni_client
from llm.config import DEFAULT_MODEL
from tools.registry import registry

SYSTEM_PROMPT = """You are JARVIS, an advanced personal AI desktop assistant running on Windows.
You can execute actions on the user's computer via available tools.
When asked to open an application or run a task, call the relevant tool immediately.
Always confirm actions clearly and politely."""

class JarvisAgent:
    """Core agent reasoning and tool-calling execution loop."""

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.conversation_history: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    async def run(self, user_prompt: str) -> Dict[str, Any]:
        """Execute a prompt through the OmniRoute LLM and handle any tool calls."""
        self.conversation_history.append({"role": "user", "content": user_prompt})

        tools = registry.get_specs()

        # Call OmniRoute
        response = await omni_client.chat_completion(
            messages=self.conversation_history,
            model=self.model,
            tools=tools,
        )

        message = response.choices[0].message
        actions_taken = []

        # If model requested tool calls:
        if message.tool_calls:
            self.conversation_history.append(message.model_dump())

            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = tool_call.function.arguments

                # Execute tool
                tool_output = registry.execute(func_name, func_args)
                actions_taken.append({
                    "tool": func_name,
                    "arguments": func_args,
                    "result": tool_output,
                })

                # Append tool result to conversation history
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_output),
                })

            # Get final conversational response after tool execution
            second_response = await omni_client.chat_completion(
                messages=self.conversation_history,
                model=self.model,
            )
            final_content = second_response.choices[0].message.content or "Action completed."
            self.conversation_history.append({"role": "assistant", "content": final_content})
            return {
                "reply": final_content,
                "actions": actions_taken,
            }
        else:
            final_content = message.content or ""
            self.conversation_history.append({"role": "assistant", "content": final_content})
            return {
                "reply": final_content,
                "actions": [],
            }

agent = JarvisAgent()
