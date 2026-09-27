import json
import os
import sys
from pathlib import Path
from typing import Annotated, Callable, Optional
from dotenv import load_dotenv

# Ensure the backend root directory is on sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from livekit import agents, rtc
from livekit.agents import llm
from livekit.plugins import openai as lk_openai, silero

from llm.config import OMNIROUTE_BASE_URL, OMNIROUTE_API_KEY, DEFAULT_MODEL
from tools.registry import registry

load_dotenv()


def create_jarvis_tools(get_room: Callable[[], Optional[rtc.Room]]):
    """Factory to register Jarvis tools with LiveKit function calling & data channel broadcast."""

    @llm.function_tool(
        description="Opens an installed Windows desktop application like VS Code, Notepad, Calculator, Chrome, Explorer, or Terminal."
    )
    async def open_desktop_application(
        app_name: Annotated[
            str,
            "Name of the application to launch, e.g., 'VS Code', 'Notepad', 'Calculator', 'Chrome', 'Terminal'",
        ],
    ) -> str:
        """Executes the open_application tool and notifies the UI over the WebRTC data channel."""
        print(f"--> [Jarvis Voice Tool] Executing open_application: {app_name}")
        result = registry.execute("open_application", {"app_name": app_name})

        # Broadcast action over LiveKit WebRTC data channel to frontend
        room = get_room()
        if room and room.local_participant:
            try:
                payload = json.dumps({
                    "type": "assistant_action",
                    "action": "open_application",
                    "app_name": app_name,
                    "result": result,
                })
                await room.local_participant.publish_data(
                    payload.encode("utf-8"),
                    topic="assistant_action",
                    reliable=True,
                )
                print(f"--> [Jarvis Voice Tool] Broadcasted action packet for '{app_name}'")
            except Exception as e:
                print(f"--> [Jarvis Voice Tool Broadcast Warning]: {e}")

        return result.get("message", f"Opened {app_name}.")

    return [open_desktop_application]


def prewarm(proc: agents.JobProcess):
    """Preload VAD in process userdata."""
    try:
        proc.userdata["vad"] = silero.VAD.load()
        print("--> [Jarvis Voice Prewarm] Silero VAD loaded.")
    except Exception as e:
        print(f"--> [Jarvis Voice Prewarm Warning] Silero VAD not loaded: {e}")


async def entrypoint(ctx: agents.JobContext):
    """LiveKit WebRTC voice session entry point for Jarvis."""
    print("--> [Jarvis Voice] Incoming voice session, connecting to room...")
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.AUDIO_ONLY)

    # 1. OmniRoute as the LLM layer using OpenAI plugin
    omni_llm = lk_openai.LLM(
        base_url=OMNIROUTE_BASE_URL,
        api_key=OMNIROUTE_API_KEY,
        model=DEFAULT_MODEL,
    )

    # 2. Attach tools with room-aware data channel broadcasting
    tools = create_jarvis_tools(lambda: ctx.room)

    # 3. Synchronize frontend client context
    @ctx.room.on("data_received")
    def on_data_received(packet):
        topic = getattr(packet, "topic", None)
        if topic in ("client_context", "page_context"):
            try:
                data = json.loads(packet.data.decode("utf-8"))
                print(f"--> [Jarvis Voice] Client context: {data}")
            except Exception:
                pass

    # 4. Clean shutdown when user disconnects
    @ctx.room.on("participant_disconnected")
    def on_participant_disconnected(participant):
        if len(ctx.room.remote_participants) == 0:
            print("--> [Jarvis Voice] Remote participant disconnected. Shutting down job.")
            ctx.shutdown(reason="remote participant left")

    # 5. Define Agent instructions and personality
    agent = agents.Agent(
        instructions=(
            "You are JARVIS, an advanced personal AI desktop assistant running on Windows. "
            "You have direct access to system tools to open applications and perform user tasks. "
            "When asked to open an app or run a command, invoke the corresponding tool immediately. "
            "Keep voice responses concise, conversational, and direct."
        ),
        tools=tools,
        llm=omni_llm,
    )

    # 6. Instantiate Voice Session
    session = agents.AgentSession(
        vad=ctx.proc.userdata.get("vad"),
        stt=lk_openai.STT(base_url=OMNIROUTE_BASE_URL, api_key=OMNIROUTE_API_KEY),
        llm=omni_llm,
        tts=lk_openai.TTS(base_url=OMNIROUTE_BASE_URL, api_key=OMNIROUTE_API_KEY),
    )

    await session.start(room=ctx.room, agent=agent)
    await session.say("Jarvis voice subsystem online. How can I assist you?", allow_interruptions=True)
    print("--> [Jarvis Voice] Voice session running and greeting delivered.")


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )
