import uvicorn
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from logger.logger import logger
from api.routes import router as api_router
from agent.graph import jarvis_graph

app = FastAPI(
    title="JARVIS Local Desktop AI Assistant",
    description="Production-grade local assistant runtime with LangGraph, OmniRoute, and Windows computer control.",
    version="1.0.0",
)

# CORS: Local frontend / Tauri desktop application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include core REST API endpoints
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "service": "JARVIS",
        "status": "online",
        "version": "1.0.0",
        "documentation": "/docs",
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Real-time WebSocket streaming events for agent activity and interaction.
    """
    await websocket.accept()
    logger.info("[WebSocket] Client connected.")
    try:
        while True:
            raw_text = await websocket.receive_text()
            data = json.loads(raw_text)
            user_msg = data.get("message", "").strip()
            conv_id = data.get("conversation_id", "default")

            if not user_msg:
                continue

            # Emit agent.started
            await websocket.send_text(json.dumps({"event": "agent.started", "message": user_msg}))

            # Emit agent.thinking
            await websocket.send_text(json.dumps({"event": "agent.thinking"}))

            state = {
                "user_input": user_msg,
                "conversation_id": conv_id,
                "messages": [],
            }

            try:
                final_state = await jarvis_graph.ainvoke(state)

                # Emit tool events if tool was called
                if final_state.get("selected_tool"):
                    await websocket.send_text(json.dumps({
                        "event": "tool.completed",
                        "tool": final_state.get("selected_tool"),
                        "result": final_state.get("tool_result"),
                    }))

                # Emit agent.completed
                await websocket.send_text(json.dumps({
                    "event": "agent.completed",
                    "reply": final_state.get("final_response"),
                    "actions": [{
                        "tool": final_state.get("selected_tool"),
                        "arguments": final_state.get("tool_arguments"),
                        "result": final_state.get("tool_result"),
                    }] if final_state.get("selected_tool") else [],
                }))
            except Exception as e:
                logger.error(f"[WebSocket Error] {e}")
                await websocket.send_text(json.dumps({
                    "event": "agent.error",
                    "error": str(e),
                }))

    except WebSocketDisconnect:
        logger.info("[WebSocket] Client disconnected.")


if __name__ == "__main__":
    logger.info(f"Starting JARVIS Backend on {settings.JARVIS_HOST}:{settings.JARVIS_PORT}")
    uvicorn.run("main:app", host=settings.JARVIS_HOST, port=settings.JARVIS_PORT, reload=True)
