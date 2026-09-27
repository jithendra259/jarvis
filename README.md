# JARVIS - Fully Local Desktop AI Assistant

A production-quality, fully local JARVIS-style desktop AI assistant for Windows. Built with privacy, low latency, and extensibility as core principles.

## Features

- **Fully Local**: No mandatory cloud APIs. Runs entirely on your Windows machine.
- **Voice & Text**: Interact via chat UI or voice (via self-hosted LiveKit + local Whisper/Kokoro).
- **Windows Control**: Open applications, manage files, run commands, get system info.
- **Persistent Memory**: SQLite-based conversation history and long-term memory.
- **Modular Architecture**: Clean separation of concerns - replace any component independently.
- **Safety First**: Permission system with confirmation required for destructive actions.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Tauri Desktop App (Next.js + React)                           │
│  ├─ Dashboard: Chat, Activity Feed, System Status              │
│  └─ Voice: LiveKit WebRTC (Phase 4/5)                          │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/WebSocket (localhost only)
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  Python Backend (FastAPI + LangGraph)                          │
│  ├─ Agent: Understand → Plan → Execute → Observe → Respond     │
│  ├─ Tools: Applications, Filesystem, Terminal, Windows         │
│  ├─ Memory: SQLite (conversations, facts, tasks)               │
│  ├─ LLM: OmniRoute → Ollama (local models)                     │
│  └─ Voice: LiveKit Agent + Whisper STT + Kokoro TTS (Phase 4/5)│
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- **Windows 10/11**
- **Python 3.11+** (3.12+ recommended)
- **Node.js 20+** (for frontend/Tauri)
- **Rust** (for Tauri - `rustup`)

### Local LLM Setup (Required)

JARVIS needs a local LLM. Two options:

**Option A: OmniRoute (Recommended)**
```bash
# OmniRoute runs a local gateway that routes to Ollama
# Download from: https://github.com/omniroute/omniroute
# Start on port 20128
omniroute serve --port 20128
```

**Option B: Ollama Direct**
```bash
# Install Ollama from https://ollama.com
ollama serve
# Pull a model
ollama pull qwen2.5:7b-instruct
```

### Backend Setup

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
# Copy and edit .env with your settings
cp .env.example .env
# Start the backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup

```bash
cd frontend
npm install
# Start dev server
npm run dev
# In another terminal, start Tauri
npm run tauri dev
```

### Build Desktop App

```bash
cd frontend
npm run tauri build
# Output: src-tauri/target/release/bundle/msi/*.msi
```

## Configuration

All configuration via environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `JARVIS_HOST` | API bind address | `127.0.0.1` |
| `JARVIS_PORT` | API port | `8000` |
| `OMNIROUTE_URL` | OmniRoute endpoint | `http://127.0.0.1:20128/v1` |
| `OLLAMA_URL` | Ollama endpoint | `http://127.0.0.1:11434` |
| `DEFAULT_MODEL` | Default LLM model | `qwen2.5:7b-instruct` |
| `LIVEKIT_URL` | Self-hosted LiveKit | `ws://127.0.0.1:7880` |
| `STT_MODEL_PATH` | Whisper model path | `%LOCALAPPDATA%\Jarvis\models\stt\...` |
| `TTS_MODEL_PATH` | Kokoro model path | `%LOCALAPPDATA%\Jarvis\models\tts\...` |

Data is stored in `%LOCALAPPDATA%\Jarvis\` (outside install directory for auto-updates).

## Development Phases

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | ✅ | Core: Backend + LangGraph + OmniRoute + `open_application` tool + Dashboard |
| 2 | 📋 | Filesystem, Terminal, System tools + Permission system |
| 3 | 📋 | SQLite Memory (conversations, facts, tasks) |
| 4 | 📋 | Local Whisper STT + VAD + Kokoro TTS |
| 5 | 📋 | Self-hosted LiveKit + Voice Agent + Interruptions |
| 6 | ✅ | Next.js Dashboard (Chat, Activity, Status) |
| 7 | 📋 | Tauri Integration (system tray, hotkeys, native menus) |
| 8 | 📋 | Service Manager (auto-start Ollama, OmniRoute, LiveKit) |
| 9 | 📋 | Windows Packaging (.exe/.msi) |
| 10 | 📋 | Auto-updater (GitHub Releases) |

## Project Structure

```
jarvis/
├── backend/                 # Python FastAPI + LangGraph runtime
│   ├── agent/               # LangGraph agent (graph, state, prompts, runner)
│   ├── api/                 # FastAPI routes (chat, confirm, system, voice)
│   ├── config/              # Environment-driven settings
│   ├── errors/              # Structured error types
│   ├── llm/                 # LLM providers (OmniRoute, Ollama)
│   ├── logger/              # Sanitized logging
│   ├── security/            # Permission system (SAFE/CONFIRM/ADMIN)
│   ├── tools/               # Tool registry + implementations
│   │   ├── applications.py  # open_application (real Windows launch)
│   │   ├── base.py          # ToolSpec, validation, ToolResult
│   │   └── registry.py      # ToolRegistry with events
│   ├── tests/               # Unit tests (mock LLM, no network)
│   ├── main.py              # FastAPI app + WebSocket
│   └── requirements.txt
├── frontend/                # Next.js + Tauri desktop app
│   ├── src/
│   │   ├── app/             # App Router pages (/, /voice)
│   │   ├── components/
│   │   │   ├── jarvis/      # Dashboard (ChatPanel, ActivityFeed, StatusBar)
│   │   │   └── ui/          # shadcn/ui primitives
│   │   ├── hooks/           # useJarvisWebSocket
│   │   ├── lib/             # jarvis-api client
│   │   └── app-config.ts    # UI config (local mode default)
│   └── src-tauri/           # Tauri Rust backend
├── docs/                    # Documentation
├── scripts/                 # Helper scripts
└── .github/                 # CI/CD workflows
```

## Safety & Permissions

Tools are classified by permission level:

- **SAFE**: `open_application`, `get_system_information`, `read_file` - executed immediately
- **CONFIRM**: `write_file`, `run_powershell`, `move_file` - requires user confirmation
- **ADMIN**: `delete_file`, `shutdown_computer`, dangerous commands - requires admin + confirmation

The LLM never executes code directly - all actions go through the typed tool registry with validation.

## Testing

```bash
# Backend tests
cd backend
.\.venv\Scripts\python.exe -m pytest tests/ -v

# Frontend build
cd frontend
npm run build
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Installation](docs/INSTALLATION.md)
- [Development](docs/DEVELOPMENT.md)
- [Local Models](docs/LOCAL_MODELS.md)
- [Tools](docs/TOOLS.md)
- [Security](docs/SECURITY.md)
- [Windows Build](docs/BUILD_WINDOWS.md)

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest` (backend) and `npm run build` (frontend)
5. Submit a PR

---

**JARVIS** - Your local desktop AI assistant. No cloud required.