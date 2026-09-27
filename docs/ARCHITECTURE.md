# JARVIS System Architecture

JARVIS is a production-grade, privacy-first, fully local desktop AI assistant for Windows.

## Core Architectural Separation

- **Next.js & React**: Desktop frontend presentation layer.
- **Tauri**: Native Windows desktop wrapper, global hotkeys, system tray, window lifecycle, and packaging into `.exe`.
- **FastAPI**: Local REST & WebSocket runtime host on `127.0.0.1:8000`.
- **LangGraph**: Core orchestration and state management engine (`UNDERSTAND` -> `PLAN` -> `SELECT_TOOL` -> `EXECUTE_TOOL` -> `OBSERVE_RESULT` -> `RESPOND`).
- **OmniRoute / Ollama**: Local OpenAI-compatible LLM gateway at `http://localhost:20128/v1` and `http://localhost:11434`.
- **Tools System**: Modular real Windows computer control (`open_application`, file system, etc.) with strict permission checks (`SAFE`, `CONFIRM`, `ADMIN`).
- **Storage**: Persistent local state in `%LOCALAPPDATA%\Jarvis\database\`, logs in `%LOCALAPPDATA%\Jarvis\logs\`.
- **Self-Hosted LiveKit**: Real-time audio WebRTC transport at `ws://localhost:7880`.

## Flow Diagram

```
User (Text / Voice / GUI)
       │
       ▼
Next.js / Tauri GUI
       │ (REST / WebSocket)
       ▼
FastAPI (127.0.0.1:8000)
       │
       ▼
LangGraph Agent (StateGraph)
       │
       ├─► Understand & Plan ──► LLMProvider (OmniRoute / Ollama)
       │
       ├─► Security Permission Check (SAFE / CONFIRM / ADMIN)
       │
       ├─► Tool Executor ──► Windows Computer Control (open_application)
       │
       └─► Observe & Respond ──► Final Concise User Confirmation
```
