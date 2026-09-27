"""JARVIS local runtime entry point.

    python -m uvicorn main:app --host 127.0.0.1 --port 8000

The service binds to loopback only. It exposes a REST API for the desktop GUI
and a WebSocket (`/ws`) that streams real-time agent activity and accepts chat
messages over the same socket.
"""

from __future__ import annotations

import asyncio
import json
import platform
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agent.events import EventType, event_bus
from agent.runner import run_agent
from api.routes import router as api_router
from config.settings import settings
from errors import JarvisError
from logger.logger import logger

APP_VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_data_dirs()
    logger.info(
        "JARVIS runtime %s starting (env=%s, data=%s)", APP_VERSION, settings.env, settings.data_dir
    )
    logger.info("LLM: %s via %s", settings.default_model, settings.omniroute_url)
    logger.info("Ollama fallback: %s", settings.ollama_url)
    if settings.livekit_configured:
        logger.info("LiveKit (self-hosted) configured at %s", settings.livekit_url)
    else:
        logger.warning("LiveKit is not configured; voice is unavailable until Phase 4/5 setup")
    try:
        yield
    finally:
        logger.info("JARVIS runtime shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="JARVIS Local Desktop AI Assistant",
        description=(
            "Fully local Windows assistant runtime: LangGraph orchestration, "
            "OmniRoute/Ollama language models, Windows tools, SQLite memory (Phase 3), "
            "local Whisper/Kokoro voice (Phase 4/5)."
        ),
        version=APP_VERSION,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Mounted twice: /api/* for the GUI, and unprefixed shortcuts (/health, /chat).
    app.include_router(api_router, prefix="/api")
    app.include_router(api_router)

    @app.exception_handler(JarvisError)
    async def jarvis_error_handler(_request, exc: JarvisError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("[api] %s: %s", exc.code, exc.message)
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_request, exc: Exception) -> JSONResponse:
        logger.exception("[api] unhandled error")
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": str(exc), "details": {}}},
        )

    @app.get("/", tags=["jarvis"])
    async def root() -> Dict[str, Any]:
        return {
            "service": "JARVIS",
            "status": "online",
            "version": APP_VERSION,
            "platform": f"{platform.system()} {platform.release()}",
            "docs": "/docs",
            "websocket": "/ws",
        }

    @app.websocket("/ws")
    @app.websocket("/api/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        """Real-time agent activity stream; also accepts chat messages."""
        await websocket.accept()
        logger.info("[ws] client connected (%d total)", event_bus.subscriber_count + 1)
        await websocket.send_json({"type": "system.status", "status": "connected"})

        async def forward_events() -> None:
            async for event in event_bus.subscribe():
                await websocket.send_json(event)

        forward_task = asyncio.create_task(forward_events())
        try:
            while True:
                raw = await websocket.receive_text()
                await _handle_ws_message(websocket, raw)
        except WebSocketDisconnect:
            logger.info("[ws] client disconnected")
        except Exception as exc:
            logger.warning("[ws] connection error: %s", exc)
        finally:
            forward_task.cancel()

    return app


async def _handle_ws_message(websocket: WebSocket, raw: str) -> None:
    """Handle an inbound WebSocket frame: chat, confirm or ping."""
    try:
        payload = json.loads(raw)
    except ValueError:
        await websocket.send_json({"type": "agent.error", "message": "Malformed JSON payload"})
        return

    kind = payload.get("type", "chat")

    if kind == "ping":
        await websocket.send_json({"type": "pong", "timestamp": time.time()})
        return

    if kind == "model.select":
        model_name = str(payload.get("model", "")).strip()
        if model_name:
            from llm import set_active_model
            active = set_active_model(model_name)
            await websocket.send_json({"type": "model.selected", "model": active})
            return

    if kind == "chat":
        message = str(payload.get("message", "")).strip()
        conversation_id = str(payload.get("conversation_id", "default"))
        model = payload.get("model")
        if not message:
            await websocket.send_json({"type": "agent.error", "message": "Empty message"})
            return
        try:
            state = await run_agent(message, conversation_id=conversation_id, model=model)
        except JarvisError as exc:
            await websocket.send_json({"type": "agent.error", "code": exc.code, "message": exc.message})
            return
        await websocket.send_json(
            {
                "type": "agent.response",
                "conversation_id": conversation_id,
                "reply": state.get("final_response"),
                "intent": state.get("intent"),
                "plan": state.get("plan"),
                "observations": state.get("observations", []),
                "actions": state.get("tool_history", []),
                "requires_confirmation": bool(state.get("requires_confirmation")),
                "confirmation": state.get("pending_action"),
                "error": state.get("error"),
            }
        )
        return

    if kind == "confirm":
        from agent.confirmations import store as confirmation_store
        from tools.registry import registry

        action_id = str(payload.get("action_id", ""))
        approved = bool(payload.get("approved", False))
        action = confirmation_store.resolve(action_id)
        if action is None:
            await websocket.send_json(
                {
                    "type": "agent.error",
                    "code": "confirmation_not_found",
                    "message": "This confirmation is unknown or has expired.",
                }
            )
            return
        if not approved:
            confirmation_store.discard(action_id)
            await websocket.send_json(
                {"type": "agent.response", "reply": f"Cancelled: {action.tool} was not executed."}
            )
            return
        result = await registry.execute_async(
            action.tool, action.arguments, conversation_id=action.conversation_id, confirmed=True
        )
        event_bus.emit(
            EventType.CONFIRMATION_RESOLVED,
            conversation_id=action.conversation_id,
            tool=action.tool,
            approved=True,
            success=result.success,
        )
        await websocket.send_json(
            {
                "type": "agent.response",
                "reply": result.message,
                "actions": [{"tool": action.tool, "arguments": action.arguments, "result": result.to_dict()}],
                "error": None if result.success else {"code": result.error_code, "message": result.message},
            }
        )
        return

    await websocket.send_json({"type": "agent.error", "message": f"Unsupported message type '{kind}'"})


app = create_app()


def main() -> None:
    """Run the runtime with uvicorn (development convenience entry point)."""
    logger.info("Starting JARVIS on http://%s:%s", settings.host, settings.port)
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=(settings.env == "development"),
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
