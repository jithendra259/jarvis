"""Central configuration for the JARVIS local runtime.

Every value is resolved from the process environment. `backend/.env` is loaded
automatically for local development; that file is git-ignored and is the only
place machine-specific values and credentials belong.

Design rules enforced here:
  * No cloud endpoints, no credentials and no machine-specific absolute paths
    are hardcoded.
  * Every persisted artefact lives under the user data directory
    (`%LOCALAPPDATA%\\Jarvis` on Windows), never inside the install directory.
  * The configuration object is immutable and can be rebuilt from the
    environment (`Settings.from_env()`), which keeps tests hermetic.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = BACKEND_DIR.parent
ENV_FILE = BACKEND_DIR / ".env"

# Local-only defaults. These are loopback addresses, not cloud services.
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_OMNIROUTE_URL = "http://127.0.0.1:20128/v1"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_LIVEKIT_URL = "ws://127.0.0.1:7880"

# Desktop origins allowed to call the API (Next.js dev server + Tauri webview).
DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://tauri.localhost",
    "https://tauri.localhost",
    "tauri://localhost",
)


def _load_environment() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:  # pragma: no cover - python-dotenv is a hard dependency
        return
    load_dotenv(ENV_FILE, override=False)
    load_dotenv(override=False)


_load_environment()


def _str(name: str, default: str = "") -> str:
    value = os.getenv(name)
    return default if value is None else value.strip()


def _int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _default_data_dir() -> Path:    override = os.getenv("JARVIS_DATA_DIR")
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        local_app_data = os.getenv("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(local_app_data) / "Jarvis"
    xdg = os.getenv("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / "jarvis"
    return Path.home() / ".local" / "share" / "jarvis"


def _database_path(data_dir: Path) -> Path:
    override = os.getenv("DATABASE_PATH")
    if override and override.strip():
        return Path(override.strip()).expanduser()
    return data_dir / "database" / "jarvis.db"


@dataclass(frozen=True)
class Settings:
    """Immutable snapshot of the runtime configuration."""

    # --- Runtime -----------------------------------------------------------
    env: str
    host: str
    port: int
    cors_origins: Tuple[str, ...]
    log_level: str

    # --- Local LLM (OmniRoute -> Ollama) -----------------------------------
    llm_provider: str  # "auto" | "omniroute" | "ollama"
    omniroute_url: str
    omniroute_api_key: str
    ollama_url: str
    default_model: str
    fast_model: str
    reasoning_model: str
    llm_timeout_seconds: float
    llm_max_tool_iterations: int

    # --- Self-hosted LiveKit ----------------------------------------------
    livekit_url: str
    livekit_api_key: str
    livekit_api_secret: str
    livekit_room: str

    # --- Storage (outside the installation directory) ----------------------
    data_dir: Path
    database_path: Path
    models_dir: Path
    logs_dir: Path
    cache_dir: Path
    config_dir: Path
    memory_dir: Path

    # --- Voice (Phase 4/5) -------------------------------------------------
    stt_model_path: str
    stt_device: str
    stt_compute_type: str
    stt_language: str
    tts_engine: str
    tts_model_path: str
    tts_voice: str
    tts_device: str
    tts_sample_rate: int
    vad_enabled: bool
    vad_sample_rate: int

    # --- Security ----------------------------------------------------------
    confirmation_ttl_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        data_dir = _default_data_dir()
        models_dir = data_dir / "models"
        origins = tuple(
            origin.strip()
            for origin in _str("JARVIS_CORS_ORIGINS", ",".join(DEFAULT_CORS_ORIGINS)).split(",")
            if origin.strip()
        )
        return cls(
            env=_str("JARVIS_ENV", "development"),
            host=_str("JARVIS_HOST", DEFAULT_HOST),
            port=_int("JARVIS_PORT", DEFAULT_PORT),
            cors_origins=origins,
            log_level=_str("JARVIS_LOG_LEVEL", "INFO").upper(),
            llm_provider=_str("LLM_PROVIDER", "auto").lower(),
            omniroute_url=_str("OMNIROUTE_URL", DEFAULT_OMNIROUTE_URL).rstrip("/"),
            omniroute_api_key=os.getenv("OMNIROUTE_API_KEY", ""),
            ollama_url=_str("OLLAMA_URL", DEFAULT_OLLAMA_URL).rstrip("/"),
            default_model=_str("DEFAULT_MODEL", "qwen2.5:7b-instruct"),
            fast_model=_str("FAST_MODEL", "qwen2.5:3b-instruct"),
            reasoning_model=_str("REASONING_MODEL", "qwen2.5:7b-instruct"),
            llm_timeout_seconds=_float("LLM_TIMEOUT_SECONDS", 120.0),
            llm_max_tool_iterations=_int("LLM_MAX_TOOL_ITERATIONS", 3),
            livekit_url=_str("LIVEKIT_URL", DEFAULT_LIVEKIT_URL),
            livekit_api_key=os.getenv("LIVEKIT_API_KEY", ""),
            livekit_api_secret=os.getenv("LIVEKIT_API_SECRET", ""),
            livekit_room=_str("LIVEKIT_ROOM", "jarvis-room"),
            data_dir=data_dir,
            database_path=_database_path(data_dir),
            models_dir=models_dir,
            logs_dir=data_dir / "logs",
            cache_dir=data_dir / "cache",
            config_dir=data_dir / "config",
            memory_dir=data_dir / "memory",
            stt_model_path=_str("STT_MODEL_PATH", str(models_dir / "stt" / "whisper-large-v3-turbo")),
            stt_device=_str("STT_DEVICE", "auto"),
            stt_compute_type=_str("STT_COMPUTE_TYPE", "auto"),
            stt_language=_str("STT_LANGUAGE", "en"),
            tts_engine=_str("TTS_ENGINE", "kokoro").lower(),
            tts_model_path=_str("TTS_MODEL_PATH", str(models_dir / "tts" / "kokoro")),
            tts_voice=_str("TTS_VOICE", "af_heart"),
            tts_device=_str("TTS_DEVICE", "auto"),
            tts_sample_rate=_int("TTS_SAMPLE_RATE", 24000),
            vad_enabled=_bool("VAD_ENABLED", True),
            vad_sample_rate=_int("VAD_SAMPLE_RATE", 16000),
            confirmation_ttl_seconds=_int("CONFIRMATION_TTL_SECONDS", 300),
        )

    # -- helpers ------------------------------------------------------------

    def ensure_data_dirs(self) -> None:
        """Create the user data directory tree. Safe to call repeatedly."""
        for directory in (
            self.data_dir,
            self.database_path.parent,
            self.models_dir,
            self.logs_dir,
            self.cache_dir,
            self.config_dir,
            self.memory_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def livekit_configured(self) -> bool:
        return bool(self.livekit_api_key and self.livekit_api_secret and self.livekit_url)

    def public_dict(self) -> dict:
        """Configuration safe to return over the API: no secrets, no tokens."""
        return {
            "env": self.env,
            "host": self.host,
            "port": self.port,
            "llm_provider": self.llm_provider,
            "omniroute_url": self.omniroute_url,
            "omniroute_api_key_configured": bool(self.omniroute_api_key),
            "ollama_url": self.ollama_url,
            "default_model": self.default_model,
            "fast_model": self.fast_model,
            "reasoning_model": self.reasoning_model,
            "livekit_url": self.livekit_url,
            "livekit_configured": self.livekit_configured,
            "livekit_room": self.livekit_room,
            "data_dir": str(self.data_dir),
            "database_path": str(self.database_path),
            "models_dir": str(self.models_dir),
            "logs_dir": str(self.logs_dir),
            "cache_dir": str(self.cache_dir),
            "config_dir": str(self.config_dir),
            "memory_dir": str(self.memory_dir),
            "stt": {
                "model_path": self.stt_model_path,
                "device": self.stt_device,
                "compute_type": self.stt_compute_type,
                "language": self.stt_language,
            },
            "tts": {
                "engine": self.tts_engine,
                "model_path": self.tts_model_path,
                "voice": self.tts_voice,
                "device": self.tts_device,
                "sample_rate": self.tts_sample_rate,
            },
            "vad": {"enabled": self.vad_enabled, "sample_rate": self.vad_sample_rate},
            "confirmation_ttl_seconds": self.confirmation_ttl_seconds,
        }


def resolve_data_dir() -> Path:
    return _default_data_dir()


def get_settings() -> Settings:
    """Return the process-wide settings snapshot."""
    return settings


settings = Settings.from_env()

__all__ = [
    "BACKEND_DIR",
    "REPO_DIR",
    "ENV_FILE",
    "Settings",
    "settings",
    "get_settings",
    "resolve_data_dir",
]
