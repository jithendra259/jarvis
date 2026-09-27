"""Local HTTP API for the JARVIS desktop application.

Every route is bound to loopback by default. Endpoints for capabilities that
belong to a later phase answer with an explicit `501 not_implemented` payload
instead of pretending to work.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from agent.confirmations import store as confirmation_store
from agent.events import event_bus
from agent.runner import run_agent
from config.settings import settings
from errors import ErrorCode, JarvisError, NotImplementedYet
from llm import describe_providers, get_llm_provider
from logger.logger import logger
from tools.registry import PLANNED_TOOLS, registry
from tools.system import get_hardware_info, get_service_status

router = APIRouter(tags=["jarvis"])

STARTED_AT = time.time()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User request in plain text")
    conversation_id: str = Field("default", description="Conversation identifier")
    model: Optional[str] = Field(None, description="Optional local model override")


class ToolAction(BaseModel):
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Dict[str, Any] = Field(default_factory=dict)


class ConfirmationInfo(BaseModel):
    id: str
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    permission_level: str
    reason: str


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    actions: List[ToolAction] = Field(default_factory=list)
    observations: List[str] = Field(default_factory=list)
    intent: Optional[str] = None
    plan: Optional[str] = None
    requires_confirmation: bool = False
    confirmation: Optional[ConfirmationInfo] = None
    error: Optional[Dict[str, Any]] = None


class ConfirmRequest(BaseModel):
    action_id: str = Field(..., description="Identifier returned with the confirmation request")
    approved: bool = Field(..., description="True executes the stored action, False cancels it")


# ---------------------------------------------------------------------------
# Health and status
# ---------------------------------------------------------------------------
@router.get("/health")
async def health() -> Dict[str, Any]:
    """Liveness plus local dependency availability."""
    provider = await get_llm_provider()
    llm_online = await provider.check_health()
    return {
        "service": "JARVIS Local Runtime",
        "status": "healthy" if llm_online else "degraded",
        "version": "0.1.0",
        "environment": settings.env,
        "uptime_seconds": round(time.time() - STARTED_AT, 1),
        "llm": {
            "provider": provider.name,
            "online": llm_online,
            "model": settings.default_model,
            "endpoint": settings.omniroute_url if provider.name == "omniroute" else settings.ollama_url,
        },
        "voice": {
            "livekit_configured": settings.livekit_configured,
            "livekit_url": settings.livekit_url,
            "stt_model": settings.stt_model_path,
            "tts_engine": settings.tts_engine,
            "phase": "voice pipeline arrives in Phase 4/5",
        },
        "tools": registry.names(),
    }


@router.get("/system/status")
async def system_status() -> Dict[str, Any]:
    """Hardware telemetry and local service availability."""
    hw = get_hardware_info()
    return {
        "hardware": hw,
        "runtime": get_service_status(),
        "services": await describe_providers(),
        "websocket_clients": event_bus.subscriber_count,
        "pending_confirmations": len(confirmation_store.list()),
        **hw,
    }


@router.get("/tools")
async def list_tools() -> Dict[str, Any]:
    """Implemented tools with their permission levels, plus planned tools."""
    return {
        "implemented": registry.describe(),
        "planned": [{"name": name, "phase": phase} for name, phase in sorted(PLANNED_TOOLS.items())],
    }


@router.get("/events/recent")
async def recent_events(limit: int = Query(20, ge=1, le=100)) -> Dict[str, Any]:
    """Recent activity events (debugging aid; the live stream is on /ws)."""
    return {"events": event_bus.recent(limit)}


# ---------------------------------------------------------------------------
# Conversation
# ---------------------------------------------------------------------------
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Run one full JARVIS turn (understand -> tool -> respond)."""
    logger.info("[api/chat] %s", request.message)
    state = await run_agent(
        request.message,
        conversation_id=request.conversation_id,
    )
    return _state_to_response(state, request.conversation_id)


@router.post("/agent/run", response_model=ChatResponse)
async def agent_run(request: ChatRequest) -> ChatResponse:
    """Alias of /chat kept for clients that address the agent explicitly."""
    return await chat(request)


@router.post("/agent/confirm", response_model=ChatResponse)
async def agent_confirm(request: ConfirmRequest) -> ChatResponse:
    """Execute or cancel an action the permission layer put on hold."""
    action = confirmation_store.resolve(request.action_id)
    if action is None:
        raise JarvisError(
            ErrorCode.CONFIRMATION_NOT_FOUND,
            "This confirmation is unknown or has expired. Ask JARVIS to repeat the request.",
            status_code=404,
            details={"action_id": request.action_id},
        )
    return await _apply_confirmation(action, request)


async def _apply_confirmation(action, request: ConfirmRequest) -> ChatResponse:
    if action is None:  # pragma: no cover - resolved by the caller
        raise JarvisError(
            ErrorCode.CONFIRMATION_NOT_FOUND,
            "This confirmation is unknown or has expired.",
            status_code=404,
        )

    if not request.approved:
        confirmation_store.discard(request.action_id)
        logger.info("[api/confirm] user rejected %s", action.tool)
        return ChatResponse(
            reply=f"Cancelled: {action.tool} was not executed.",
            conversation_id=action.conversation_id,
            observations=[f"User rejected {action.tool}"],
        )

    result = await registry.execute_async(
        action.tool,
        action.arguments,
        conversation_id=action.conversation_id,
        confirmed=True,
    )
    payload = result.to_dict()
    reply = result.message
    if result.success:
        logger.info("[api/confirm] executed %s", action.tool)
    else:
        logger.warning("[api/confirm] %s failed: %s", action.tool, result.message)

    return ChatResponse(
        reply=reply,
        conversation_id=action.conversation_id,
        actions=[ToolAction(tool=action.tool, arguments=action.arguments, result=payload)],
        observations=[f"Executed confirmed action {action.tool}"],
        error=None
        if result.success
        else {"code": result.error_code, "message": result.message},
    )


def _state_to_response(state: Dict[str, Any], conversation_id: str) -> ChatResponse:
    actions = [
        ToolAction(
            tool=entry.get("tool", "unknown"),
            arguments=entry.get("arguments") or {},
            result=entry.get("result") or {},
        )
        for entry in state.get("tool_history", []) or []
    ]

    confirmation: Optional[ConfirmationInfo] = None
    pending = state.get("pending_action")
    if pending:
        confirmation = ConfirmationInfo(
            id=pending.get("id", ""),
            tool=pending.get("tool", ""),
            arguments=pending.get("arguments", {}),
            permission_level=pending.get("permission_level", "CONFIRM"),
            reason=pending.get("reason", ""),
        )

    return ChatResponse(
        reply=state.get("final_response") or "I could not complete that request.",
        conversation_id=conversation_id,
        actions=actions,
        observations=list(state.get("observations", []) or []),
        intent=state.get("intent"),
        plan=state.get("plan"),
        requires_confirmation=bool(state.get("requires_confirmation")),
        confirmation=confirmation,
        error=state.get("error"),
    )


# ---------------------------------------------------------------------------
# Settings, memory, voice (later phases answer honestly)
# ---------------------------------------------------------------------------
@router.get("/settings")
async def get_settings() -> Dict[str, Any]:
    """Sanitised runtime configuration (never includes secrets)."""
    return settings.public_dict()


@router.post("/settings")
async def update_settings() -> Dict[str, Any]:
    raise NotImplementedYet("runtime settings update", "Phase 8 (service manager)")


@router.get("/memory")
async def get_memory() -> Dict[str, Any]:
    raise NotImplementedYet("long-term memory", "Phase 3 (SQLite memory)")


@router.post("/memory")
async def create_memory() -> Dict[str, Any]:
    raise NotImplementedYet("long-term memory", "Phase 3 (SQLite memory)")


class VoiceSessionRequest(BaseModel):
    room: Optional[str] = None
    identity: Optional[str] = None


@router.post("/voice/session")
async def voice_session(request: VoiceSessionRequest) -> Dict[str, Any]:
    """Mint a local LiveKit access token for the desktop voice session.

    This is real credential minting against the self-hosted server, not a stub.
    The voice pipeline itself (Whisper/VAD/Kokoro) lands in Phase 4/5.
    """
    if not settings.livekit_configured:
        raise JarvisError(
            ErrorCode.VOICE_NOT_CONFIGURED,
            "LiveKit is not configured. Set LIVEKIT_URL, LIVEKIT_API_KEY and LIVEKIT_API_SECRET "
            "in backend/.env and start a self-hosted LiveKit server on ws://127.0.0.1:7880.",
            status_code=503,
            details={"livekit_url": settings.livekit_url},
        )
    try:
        from livekit import api as livekit_api
    except ImportError as exc:
        raise JarvisError(
            ErrorCode.MISSING_DEPENDENCY,
            "The 'livekit' package is not installed in the backend environment.",
            status_code=503,
        ) from exc

    room = request.room or settings.livekit_room
    identity = request.identity or "jarvis-desktop"
    token = (
        livekit_api.AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(
            livekit_api.VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .to_jwt()
    )
    return {
        "server_url": settings.livekit_url,
        "room_name": room,
        "participant_token": token,
        "participant_name": identity,
    }


@router.get("/livekit/token")
async def livekit_token(
    room: str = Query(settings.livekit_room),
    identity: str = Query("jarvis-desktop"),
) -> Dict[str, Any]:
    """Backwards-compatible alias used by the frontend token helper."""
    return await voice_session(VoiceSessionRequest(room=room, identity=identity))


__all__ = ["router"]
