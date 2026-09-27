import os
from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai as lk_openai, silero

from llm.config import OMNIROUTE_BASE_URL, OMNIROUTE_API_KEY, DEFAULT_MODEL
from tools.registry import registry

load_dotenv()

def prewarm(proc: JobProcess):
    # Preload Silero VAD (Voice Activity Detection)
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # OmniRoute as the LLM layer using OpenAI plugin
    omni_llm = lk_openai.LLM(
        base_url=OMNIROUTE_BASE_URL,
        api_key=OMNIROUTE_API_KEY,
        model=DEFAULT_MODEL,
    )

    # Real-time Voice Assistant pipeline
    assistant = VoiceAssistant(
        vad=ctx.proc.userdata["vad"],
        stt=lk_openai.STT(),  # Can route to local Whisper or OmniRoute audio
        llm=omni_llm,
        tts=lk_openai.TTS(),  # Can route to local Piper or TTS
    )

    assistant.start(ctx.room)
    await assistant.say("Jarvis voice subsystem online. How can I assist you?", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )
