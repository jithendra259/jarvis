# Installation Guide

## System Requirements

- **OS**: Windows 10 (1909+) or Windows 11
- **CPU**: x64 (AVX2 recommended for local inference)
- **RAM**: 8 GB minimum (16 GB+ recommended for local LLMs)
- **GPU**: NVIDIA GPU with 6+ GB VRAM recommended (CUDA 11.8+)
- **Disk**: 10 GB free space (models + app)

## Prerequisites

### 1. Install Python 3.11+

```powershell
# Option A: winget
winget install Python.Python.3.12

# Option B: Download from python.org
# https://www.python.org/downloads/windows/
```

Verify:
```powershell
python --version
# Should show 3.11.x or 3.12.x
```

### 2. Install Node.js 20+

```powershell
# Option A: winget
winget install OpenJS.NodeJS.LTS

# Option B: Download from nodejs.org
# https://nodejs.org/
```

Verify:
```powershell
node --version
npm --version
```

### 3. Install Rust (for Tauri)

```powershell
# Install rustup
winget install Rustlang.Rustup

# Restart terminal, then:
rustup default stable
rustup target add x86_64-pc-windows-msvc
```

Verify:
```powershell
cargo --version
rustc --version
```

### 4. Install System Dependencies

```powershell
# Visual Studio Build Tools (for native modules)
winget install Microsoft.VisualStudio.2022.BuildTools --override "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"

# Or full Visual Studio Community
winget install Microsoft.VisualStudio.2022.Community
```

## Local LLM Setup (Required)

JARVIS requires a local LLM. Choose one:

### Option A: OmniRoute + Ollama (Recommended)

OmniRoute provides a local OpenAI-compatible gateway that routes to Ollama.

```powershell
# 1. Install Ollama
winget install Ollama.Ollama

# 2. Start Ollama service
ollama serve

# 3. Pull a model (in another terminal)
ollama pull qwen2.5:7b-instruct

# 4. Install OmniRoute (download from GitHub releases)
# https://github.com/omniroute/omniroute/releases
# Extract and run:
omniroute serve --port 20128
```

### Option B: Ollama Direct

```powershell
# Install Ollama
winget install Ollama.Ollama
ollama serve
ollama pull qwen2.5:7b-instruct
```

### Recommended Models

| Use Case | Model | Size | Quality |
|----------|-------|------|---------|
| General Chat | `qwen2.5:7b-instruct` | 4.7 GB | Excellent |
| Fast Responses | `qwen2.5:3b-instruct` | 2.0 GB | Good |
| Reasoning | `qwen2.5:7b-instruct` | 4.7 GB | Excellent |
| Code | `codellama:7b-instruct` | 3.8 GB | Good |
| Multilingual | `aya:8b` | 4.9 GB | Excellent |

## JARVIS Backend Setup

```powershell
# Clone repository
git clone https://github.com/yourusername/jarvis.git
cd jarvis

# Backend setup
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your settings (OMNIROUTE_URL, OLLAMA_URL, etc.)

# Run backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Verify backend:
```powershell
# Health check
Invoke-RestMethod http://127.0.0.1:8000/api/health

# Test chat
$body = @{ message = "Open Notepad"; conversation_id = "test" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/chat -Method Post -Body $body -ContentType "application/json"
```

## JARVIS Frontend Setup

```powershell
# Frontend setup (in separate terminal)
cd frontend
npm install

# Development
npm run dev
# Opens http://localhost:3000

# With Tauri (native desktop)
npm run tauri dev
```

## Desktop App Build

```powershell
cd frontend
npm run tauri build

# Output:
# src-tauri/target/release/bundle/msi/jarvis_*.msi (Windows Installer)
# src-tauri/target/release/jarvis.exe (Standalone executable)
```

## Voice Setup (Phase 4/5)

### LiveKit Server (Self-Hosted)

```powershell
# Using Docker
docker run --rm -p 7880:7880 \
  -e LIVEKIT_KEYS="devkey=secret" \
  livekit/livekit-server --dev

# Or build from source
# https://github.com/livekit/livekit
```

### Local STT (Whisper)

```powershell
# Models auto-download on first use to %LOCALAPPDATA%\Jarvis\models\stt\
# Or pre-download:
pip install faster-whisper
# Model: whisper-large-v3-turbo (~1.5 GB)
```

### Local TTS (Kokoro)

```powershell
# Models auto-download on first use to %LOCALAPPDATA%\Jarvis\models\tts\kokoro\
# Voice: af_heart (default), af_bella, am_adam, etc.
```

### Configure Voice

Edit `backend/.env`:
```env
LIVEKIT_URL=ws://127.0.0.1:7880
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret

STT_MODEL_PATH=%LOCALAPPDATA%\Jarvis\models\stt\whisper-large-v3-turbo
TTS_ENGINE=kokoro
TTS_MODEL_PATH=%LOCALAPPDATA%\Jarvis\models\tts\kokoro
TTS_VOICE=af_heart
VAD_ENABLED=true
```

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (must be 3.11+)
- Check `.venv` activation: `.\.venv\Scripts\activate`
- Check port 8000 not in use: `netstat -an | findstr 8000`

### LLM Connection Failed
- Verify OmniRoute/Ollama running: `curl http://127.0.0.1:20128/v1/models`
- Check `.env` has correct URLs
- Check firewall allows localhost connections

### Frontend Build Fails
- Clear cache: `Remove-Item -Recurse -Force .next, node_modules; npm install`
- Check Node.js version: `node --version` (20+)
- Check for TypeScript errors: `npm run build`

### Tauri Build Fails
- Update Rust: `rustup update`
- Clean build: `cd src-tauri && cargo clean && cd .. && npm run tauri build`
- Ensure Visual Studio Build Tools installed

### Voice Not Working
- Check LiveKit server: `curl -v http://127.0.0.1:7880`
- Check microphone permissions in Windows Settings
- Check `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` match server

## Data Directory

JARVIS stores all user data in:
```
%LOCALAPPDATA%\Jarvis\
├── database\jarvis.db      # SQLite database
├── models\                 # Downloaded AI models
│   ├── stt\                # Whisper models
│   └── tts\                # Kokoro/Piper models
├── logs\                   # Application logs
├── config\                 # User configuration
├── cache\                  # Temporary cache
└── memory\                 # Long-term memory (Phase 3)
```

This location is outside the installation directory so data survives app updates.

## Uninstall

```powershell
# Remove installed app
# Settings > Apps > Installed apps > JARVIS > Uninstall

# Remove user data (optional)
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\Jarvis"
```

## Next Steps

1. Read [Architecture](ARCHITECTURE.md) for system design
2. Read [Development](DEVELOPMENT.md) for contributing
3. Read [Local Models](LOCAL_MODELS.md) for model management
4. Read [Tools](TOOLS.md) for available tools
5. Read [Security](SECURITY.md) for safety model