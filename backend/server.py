from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import json

from livekit import api as lk_api
import os

from agent.core import agent
from llm.config import HOST, PORT

app = FastAPI(title="Jarvis Backend Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    actions: List[Dict[str, Any]]

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "jarvis-backend"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    if req.model:
        agent.model = req.model
    result = await agent.run(req.message)
    return ChatResponse(reply=result["reply"], actions=result["actions"])

@app.get("/api/livekit/token")
async def get_livekit_token(room: str = "jarvis-room", identity: str = "user"):
    api_key = os.getenv("LIVEKIT_API_KEY", "devkey")
    api_secret = os.getenv("LIVEKIT_API_SECRET", "secret")
    token = (
        lk_api.AccessToken(api_key, api_secret)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(lk_api.VideoGrants(room_join=True, room=room))
        .to_jwt()
    )
    return {"token": token, "url": os.getenv("LIVEKIT_URL", "ws://127.0.0.1:7880")}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            prompt = payload.get("message", "")
            if prompt:
                result = await agent.run(prompt)
                await websocket.send_text(json.dumps(result))
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    uvicorn.run("server:app", host=HOST, port=PORT, reload=True)
