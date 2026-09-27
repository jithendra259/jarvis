# Development Guide

## Getting Started

### Prerequisites
See [INSTALLATION.md](INSTALLATION.md) for system requirements and setup.

### Repository Structure
```
jarvis/
├── backend/                 # Python FastAPI runtime
│   ├── agent/               # LangGraph agent
│   ├── api/                 # REST + WebSocket endpoints
│   ├── config/              # Settings management
│   ├── errors/              # Structured errors
│   ├── llm/                 # LLM provider abstraction
│   ├── logger/              # Sanitized logging
│   ├── security/            # Permission system
│   ├── tools/               # Tool implementations
│   └── tests/               # Unit tests
├── frontend/                # Next.js + Tauri
│   ├── src/
│   │   ├── app/             # Pages (/, /voice)
│   │   ├── components/
│   │   │   ├── jarvis/      # Dashboard components
│   │   │   └── ui/          # shadcn/ui primitives
│   │   ├── hooks/           # Custom React hooks
│   │   └── lib/             # API client
│   └── src-tauri/           # Tauri Rust backend
├── docs/                    # Documentation
├── scripts/                 # Helper scripts
└── .github/                 # CI/CD
```

## Development Workflow

### Backend Development

```bash
cd backend

# Activate venv
.\.venv\Scripts\activate

# Install dev dependencies
pip install -r requirements.txt

# Run with auto-reload
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Run tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_tools.py::test_launch_success_when_process_appears -v

# Type check (if using mypy)
pip install mypy
mypy .
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Dev server (Next.js)
npm run dev
# Opens http://localhost:3000

# Tauri dev (native window)
npm run tauri dev

# Type check
npx tsc --noEmit

# Lint
npm run lint

# Build (static export)
npm run build
```

### Running Full Stack

Terminal 1 - Backend:
```bash
cd backend && .\.venv\Scripts\activate && python -m uvicorn main:app --reload
```

Terminal 2 - Frontend:
```bash
cd frontend && npm run dev
```

Terminal 3 - Tauri (optional):
```bash
cd frontend && npm run tauri dev
```

## Testing

### Backend Tests

Tests use `pytest` with `pytest-asyncio`. All tests are unit tests - no network, no real models.

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest tests/ -v

# With coverage
pip install pytest-cov
.\.venv\Scripts\python.exe -m pytest tests/ --cov=. --cov-report=term-missing
```

#### Test Organization
- `test_config.py` - Settings validation, env overrides, data dirs
- `test_permissions.py` - Permission levels, escalation, dangerous commands
- `test_tools.py` - Validation, registry, open_application (mocked)
- `test_llm.py` - MockLLMProvider, provider selection, error translation
- `test_agent.py` - Graph execution, tool flow, confirmation flow
- `test_api.py` - FastAPI endpoints with TestClient
- `test_events.py` - EventBus pub/sub, thread safety

#### Adding Tests
1. Create `tests/test_new_feature.py`
2. Use `mock_llm` fixture for LLM-dependent tests
3. Use `clean_registry` fixture for tool registry tests
4. Use `isolated_data_dir` fixture (autouse) for config tests
5. Run new test to verify

### Frontend Tests

```bash
cd frontend
# Unit tests (when added)
npm test

# E2E tests (when added)
npm run test:e2e
```

## Code Style

### Python (Backend)
- **Formatter**: `black` (line length 100)
- **Linter**: `ruff` (fast, replaces flake8/isort)
- **Types**: Full type hints required
- **Imports**: `isort` style (stdlib, third-party, local)

```bash
# Format
pip install black ruff
black .
ruff check --fix .
```

### TypeScript (Frontend)
- **Formatter**: `prettier` (via Next.js)
- **Linter**: `eslint` (Next.js config)
- **Types**: Strict mode enabled

```bash
cd frontend
npm run lint
```

## Adding a New Tool

### 1. Define ToolSpec in `tools/<name>.py`

```python
from tools.base import ToolResult, ToolSpec, validate_arguments
from security.permissions import PermissionLevel

MY_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "param1": {"type": "string", "description": "..."},
        "param2": {"type": "integer", "default": 10},
    },
    "required": ["param1"],
    "additionalProperties": False,
}

def my_tool(param1: str, param2: int = 10) -> ToolResult:
    # Real implementation - no fake success!
    try:
        result = do_real_work(param1, param2)
        return ToolResult(
            tool="my_tool",
            success=True,
            message="Work completed",
            data={"result": result},
        )
    except Exception as e:
        return ToolResult.failure(
            "my_tool",
            f"Failed: {e}",
            code="TOOL_FAILED",
        )

MY_TOOL_SPEC = ToolSpec(
    name="my_tool",
    description="Description for the LLM",
    parameters=MY_TOOL_SCHEMA,
    handler=lambda args: my_tool(args["param1"], args.get("param2", 10)),
    permission=PermissionLevel.SAFE,  # or CONFIRM/ADMIN
    category="category_name",
)
```

### 2. Register in `tools/registry.py`

```python
from .my_tool import MY_TOOL_SPEC

registry.register(MY_TOOL_SPEC)
```

### 3. Add to PLANNED_TOOLS if not implemented yet

```python
PLANNED_TOOLS = {
    "my_tool": "Phase 2",  # Will show in /api/tools and system prompt
}
```

### 4. Write Tests

```python
# tests/test_tools.py
def test_my_tool_success(monkeypatch):
    monkeypatch.setattr(tools.my_tool, "do_real_work", lambda *a: "ok")
    result = registry.execute("my_tool", {"param1": "test"})
    assert result.success is True
    assert result.data["result"] == "ok"
```

## Adding a New LLM Provider

### 1. Implement `LLMProvider` in `llm/<name>.py`

```python
from llm.client import LLMProvider, LLMResponse, LLMToolCall

class MyProvider(LLMProvider):
    name = "myprovider"
    
    async def generate(self, messages, tools=None, model=None, temperature=0.2):
        # Call your API
        return LLMResponse(content="...", tool_calls=[...])
    
    async def stream(self, messages, model=None):
        for chunk in ...:
            yield chunk
    
    async def check_health(self) -> bool:
        return True  # or actual health check
```

### 2. Register in `llm/__init__.py`

```python
from .myprovider import MyProvider

async def get_llm_provider() -> LLMProvider:
    # Add to candidate list based on settings.llm_provider
```

## Database Migrations (Phase 3+)

When schema changes:

```bash
cd backend
# Create migration script
# Run against test DB first
# Then production
```

Use `sqlite3` directly or a migration library like `sqlite-migrate`.

## Debugging

### Backend Logs
```bash
# Console output (structured)
# File logs: %LOCALAPPDATA%\Jarvis\logs\jarvis.log

# Filter by level
$env:JARVIS_LOG_LEVEL="DEBUG"
python -m uvicorn main:app --reload
```

### Frontend Debugging
- React DevTools (browser extension)
- Console logs in browser devtools
- Network tab for API calls
- WebSocket frames in Network > WS

### WebSocket Debugging
```bash
# Connect manually
wscat -c ws://127.0.0.1:8000/ws
# Send: {"type": "chat", "message": "Open Notepad", "conversation_id": "test"}
```

### LLM Debugging
```bash
# Test OmniRoute directly
curl -X POST http://127.0.0.1:20128/v1/chat/completions \
  -H "Authorization: Bearer sk-local-jarvis" \
  -H "Content-Type: application/json" \
  -d '{"model": "auto/best-chat", "messages": [{"role": "user", "content": "Hello"}]}'
```

## Common Tasks

### Update Dependencies

```bash
# Backend
cd backend
.\.venv\Scripts\python.exe -m pip list --outdated
.\.venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm outdated
npm update
```

### Reset Database
```bash
# Delete database file
Remove-Item "$env:LOCALAPPDATA\Jarvis\database\jarvis.db"
# Restart backend - auto-creates schema
```

### Add New API Endpoint
1. Add route in `backend/api/routes.py`
2. Add Pydantic models for request/response
3. Add error handling with `JarvisError`
4. Write test in `tests/test_api.py`

### Add New Dashboard Component
1. Create `frontend/src/components/jarvis/NewComponent.tsx`
2. Export from component
3. Import and use in `Dashboard.tsx`
4. Add styles with Tailwind (no custom CSS needed)

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`):
- Backend: pytest, type check
- Frontend: build, lint, type check
- Tauri: build Windows .msi

## Release Process

1. Update version in `pyproject.toml` / `package.json` / `Cargo.toml`
2. Update CHANGELOG.md
3. Tag release: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. GitHub Action builds artifacts
6. Create GitHub Release with artifacts

## Troubleshooting Development

| Issue | Solution |
|-------|----------|
| Import errors | Check `PYTHONPATH`, run from `backend/` dir |
| Port 8000 in use | `netstat -an | findstr 8000` then `taskkill /PID <pid> /F` |
| Module not found | `pip install -e .` or activate venv |
| TypeScript errors | `npx tsc --noEmit` in frontend/ |
| Tauri build fails | `rustup update`, check VS Build Tools |

## Useful Commands

```bash
# Quick backend test
cd backend && .\.venv\Scripts\python.exe -c "
from agent.runner import run_agent
import asyncio
asyncio.run(run_agent('Open Notepad'))
"

# Quick frontend type check
cd frontend && npx tsc --noEmit

# View logs
Get-Content "$env:LOCALAPPDATA\Jarvis\logs\jarvis.log" -Wait

# Clean everything
cd backend && Remove-Item -Recurse -Force .venv, __pycache__, .pytest_cache
cd ../frontend && Remove-Item -Recurse -Force .next, out, node_modules
```