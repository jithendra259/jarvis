from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from agent.graph import jarvis_graph
from tools.system import get_hardware_info
from config.settings import settings
from logger.logger import logger
import os

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message or instruction")
    conversation_id: Optional[str] = Field("default", description="Conversation session ID")
    model: Optional[str] = Field(None, description="Optional override model")


class ChatResponse(BaseModel):
    reply: str
    actions: List[Dict[str, Any]] = []
    requires_confirmation: bool = False
    confirmation_payload: Optional[Dict[str, Any]] = None
    state: Optional[Dict[str, Any]] = None


class ConfirmRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]
    approved: bool


@router.get("/health")
async def health_check():
    """Health and service availability status."""
    from llm import get_llm_provider
    provider = await get_llm_provider()
    llm_online = await provider.check_health()

    return {
        "status": "healthy" if llm_online else "degraded",
        "service": "JARVIS Local Backend",
        "llm_provider": provider.__class__.__name__,
        "llm_online": llm_online,
        "environment": settings.JARVIS_ENV,
    }


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Main conversational endpoint: Executes request through LangGraph orchestration.
    """
    logger.info(f"[API /chat] User input: '{req.message}'")
    initial_state = {
        "user_input": req.message,
        "conversation_id": req.conversation_id or "default",
        "messages": [],
    }

    try:
        final_state = await jarvis_graph.ainvoke(initial_state)
        
        reply = final_state.get("final_response") or "Action processed."
        actions = []
        if final_state.get("selected_tool"):
            actions.append({
                "tool": final_state.get("selected_tool"),
                "arguments": final_state.get("tool_arguments"),
                "result": final_state.get("tool_result"),
            })

        return ChatResponse(
            reply=reply,
            actions=actions,
            requires_confirmation=final_state.get("requires_confirmation", False),
            confirmation_payload=final_state.get("tool_result") if final_state.get("requires_confirmation") else None,
            state={"intent": final_state.get("intent"), "plan": final_state.get("plan")},
        )
    except Exception as e:
        logger.error(f"[API /chat Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/run", response_model=ChatResponse)
async def agent_run(req: ChatRequest):
    """Direct LangGraph invocation endpoint."""
    return await chat_endpoint(req)


@router.post("/agent/confirm", response_model=ChatResponse)
async def agent_confirm(req: ConfirmRequest):
    """Executes a confirmed high-permission tool."""
    if not req.approved:
        return ChatResponse(reply=f"Action '{req.tool}' was cancelled by the user.")

    from tools.registry import TOOL_HANDLERS
    handler = TOOL_HANDLERS.get(req.tool)
    if not handler:
        raise HTTPException(status_code=400, detail=f"Tool '{req.tool}' not found.")

    try:
        result = handler(req.arguments)
        return ChatResponse(
            reply=result.get("message", f"Executed {req.tool} successfully."),
            actions=[{"tool": req.tool, "arguments": req.arguments, "result": result}],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/status")
async def system_status():
    """Hardware telemetry and resource utilization."""
    return get_hardware_info()


@router.get("/settings")
async def get_settings():
    """Returns safe, sanitized system settings."""
    return {
        "host": settings.JARVIS_HOST,
        "port": settings.JARVIS_PORT,
        "environment": settings.JARVIS_ENV,
        "default_model": settings.DEFAULT_MODEL,
        "omniroute_url": settings.OMNIROUTE_URL,
        "ollama_url": settings.OLLAMA_URL,
        "livekit_url": settings.LIVEKIT_URL,
        "database_path": str(settings.DATABASE_PATH),
        "logs_path": str(settings.LOGS_PATH),
    }


@router.get("/livekit/token")
async def livekit_token(room: str = "jarvis-room", identity: str = "user"):
    """Generates local LiveKit WebRTC access token."""
    try:
        from livekit import api as lk_api
        token = (
            lk_api.AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
            .with_identity(identity)
            .with_name(identity)
            .with_grants(
                lk_api.VideoGrants(
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
            "token": token,
            "participantToken": token,
            "serverUrl": settings.LIVEKIT_URL,
            "url": settings.LIVEKIT_URL,
            "roomName": room,
            "identity": identity,
            "status": "ready",
        }
    except Exception as e:
        logger.warning(f"[LiveKit Token Warning] LiveKit token generation fallback: {e}")
        return {
            "error": "LiveKit token generation unavailable",
            "serverUrl": settings.LIVEKIT_URL,
        }
