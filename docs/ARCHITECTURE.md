# JARVIS Architecture

## Overview

JARVIS is a fully local desktop AI assistant for Windows. The architecture emphasizes:

1. **Local-First**: No mandatory cloud dependencies
2. **Modularity**: Each component can be replaced independently
3. **Safety**: Permission system prevents accidental destruction
4. **Observability**: Real-time event streaming for debugging
5. **Extensibility**: Clean interfaces for adding tools, providers, memory backends

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TAURI DESKTOP APP                                │
│  ┌──────────────────────────┐  ┌────────────────────────────────────────┐  │
│  │      Dashboard           │  │         Voice (Phase 4/5)              │  │
│  │  ┌────────┐ ┌──────────┐ │  │  ┌──────────────────────────────────┐ │  │
│  │  │ Chat   │ │ Activity │ │  │  │ LiveKit WebRTC                    │ │  │
│  │  │ Panel  │ │ Feed     │ │  │  │  ├─ STT: Whisper (local)          │ │  │
│  │  └────────┘ └──────────┘ │  │  │  ├─ TTS: Kokoro (local)           │ │  │
│  │  ┌────────────────────┐  │  │  │  └─ VAD: Silero                   │ │  │
│  │  │    Status Bar      │  │  │  └──────────────────────────────────┘ │  │
│  │  └────────────────────┘  │  └────────────────────────────────────────┘  │
│  └──────────────┬────────────┘                                             │
│                 │ HTTP + WebSocket (127.0.0.1:8000)                       │
└─────────────────┼──────────────────────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PYTHON BACKEND (FastAPI)                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        LANGGRAPH AGENT                                │  │
│  │  UNDERSTAND → PLAN → SELECT_TOOL → EXECUTE → OBSERVE → DECIDE → RESPOND│  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│          │                    │                    │                       │
│          ▼                    ▼                    ▼                       │
│  ┌───────────────┐  ┌─────────────────┐  ┌──────────────────────────┐   │
│  │   LLM Layer   │  │  Tool Registry  │  │   Event Bus              │   │
│  │  (OmniRoute/  │  │  - Validation   │  │  - agent.started         │   │
│  │   Ollama)     │  │  - Permissions  │  │  - tool.completed        │   │
│  │               │  │  - Execution    │  │  - confirmation.required │   │
│  └───────────────┘  └─────────────────┘  └──────────────────────────┘   │
│          │                    │                                           │
│          ▼                    ▼                                           │
│  ┌───────────────┐  ┌──────────────────────────────────────────────┐    │
│  │ Memory Layer  │  │              Tools                           │    │
│  │  (SQLite)     │  │  - Applications (open/close/launch)          │    │
│  │               │  │  - Filesystem (read/write/search/list)       │    │
│  │               │  │  - Windows (sysinfo, processes, clipboard)   │    │
│  │               │  │  - Terminal (PowerShell, cmd)                │    │
│  │               │  │  - Browser (Phase 2+)                        │    │
│  └───────────────┘  └──────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Chat Request
```
User Input (Dashboard)
    │
    ▼
POST /api/chat { message, conversation_id }
    │
    ▼
run_agent() ──► EventBus.emit(agent.started)
    │
    ▼
LangGraph: understand()
    │  ├─ Build messages (system + history + user)
    │  ├─ Call LLM with tool schemas
    │  └─ If tool_calls: select first tool, set plan
    ▼
route_after_understand(): tool? → execute_tool : respond
    │
    ▼ (if tool)
execute_tool_node()
    │  ├─ registry.execute_async(tool, args, conversation_id)
    │  │   ├─ validate_arguments(schema, args)
    │  │   ├─ evaluate_permission(tool, args)
    │  │   │   └─ If CONFIRM/ADMIN: create pending action, return requires_confirmation
    │  │   └─ Run handler in thread pool
    │  ├─ EventBus.emit(tool.started/completed/failed)
    │  └─ Return ToolResult
    ▼
observe_result() - Record observation
    ▼
decide_next_step() - For Phase 1: always respond
    ▼
respond()
    │  ├─ If failed: return tool message verbatim (no LLM)
    │  └─ If success: LLM phrasing with fallback to tool message
    ▼
EventBus.emit(agent.completed)
    │
    ▼
Return final_state → ChatResponse
    │
    ▼
WebSocket: agent.response event → Dashboard updates
```

### Confirmation Flow
```
1. Tool requires CONFIRM/ADMIN
   │
   ▼
2. registry.execute() returns ToolResult(requires_confirmation=True)
   │
   ▼
3. execute_tool_node creates PendingAction in ConfirmationStore
   │   { id, tool, args, permission, reason, conversation_id }
   │
   ▼
4. EventBus.emit(confirmation.required) → Dashboard shows dialog
   │
   ▼
5. User clicks Confirm/Cancel
   │
   ▼
6. POST /api/agent/confirm { action_id, approved }
   │   or WS: confirm { action_id, approved }
   │
   ▼
7. If approved: registry.execute_async(..., confirmed=True)
   │   If cancelled: discard pending action
   │
   ▼
8. EventBus.emit(confirmation.resolved) + agent.response
```

## Key Design Decisions

### 1. No Global Agent State
All state flows through LangGraph's `AgentState` TypedDict. No module-level globals hold conversation state.

### 2. Tool Safety by Default
- Unknown tools → `TOOL_NOT_FOUND`
- Planned-but-unimplemented tools → `TOOL_NOT_IMPLEMENTED` with phase info
- Argument validation before execution
- Permission check before execution
- Destructive shell commands → auto-escalate to ADMIN

### 3. Honest Failures
- Tool failures return `success=False` with real error
- LLM never sees fake success
- `respond()` node: on failure, returns tool message verbatim (no LLM call)

### 4. Event-Driven GUI
- In-process `EventBus` with asyncio queues
- WebSocket fans out to all connected clients
- Dashboard shows real-time agent thinking, tool execution, results

### 5. Local LLM Abstraction
- `LLMProvider` protocol (generate, stream, check_health, list_models)
- `OmniRouteProvider` (OpenAI-compatible, via local gateway)
- `OllamaProvider` (native /api/chat)
- Provider selection via `LLM_PROVIDER` env var
- Tests inject `MockLLMProvider`

### 6. Configuration
- All settings from environment (`.env` for dev)
- No hardcoded secrets, no cloud endpoints
- User data in `%LOCALAPPDATA%\Jarvis\` (survives app updates)

### 6. Voice Pipeline (Future)
- LiveKit handles only audio transport
- STT: faster-whisper (local Whisper)
- TTS: Kokoro (primary) / Piper (fallback)
- VAD: Silero
- Agent logic stays in LangGraph, not in LiveKit worker

## Security Boundaries

| Boundary | Protection |
|----------|------------|
| Network | API binds to 127.0.0.1 only |
| CORS | Restricted to localhost + Tauri origins |
| Tools | Typed schemas, validation, permissions |
| Shell | No direct LLM → shell; all via typed tools |
| Secrets | Never logged (sanitized formatter) |
| Data | SQLite outside install dir, no cloud sync |

## Extensibility Points

| Extension | How |
|-----------|-----|
| New Tool | Create `ToolSpec`, register in `ToolRegistry` |
| New LLM Provider | Implement `LLMProvider`, add to `get_llm_provider()` |
| New Memory Backend | Implement `MemoryStore` protocol (Phase 3) |
| New Voice Engine | Replace STT/TTS/VAD modules (Phase 4/5) |
| New Transport | Add WebSocket event handler, or gRPC |

## Technology Choices

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Desktop | Tauri + Next.js | Small binary, web tech, native access |
| Backend | FastAPI + LangGraph | Async, typed, graph-based orchestration |
| LLM | OmniRoute → Ollama | Local gateway + local models |
| DB | SQLite (stdlib) | No server, portable, survives updates |
| Voice | LiveKit + faster-whisper + Kokoro | Self-hosted, local, low latency |
| Logging | stdlib + rotating files | No deps, sanitized, structured |
| Testing | pytest + pytest-asyncio | Fast, no network, mockable |

## Phase Roadmap

See [README.md](../README.md#development-phases) for detailed phase breakdown.