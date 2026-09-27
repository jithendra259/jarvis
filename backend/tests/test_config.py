import pytest
from config.settings import settings, JARVIS_DATA_DIR, DATABASE_DIR, LOGS_DIR, MODELS_DIR

def test_settings_paths():
    assert JARVIS_DATA_DIR.exists()
    assert DATABASE_DIR.exists()
    assert LOGS_DIR.exists()
    assert MODELS_DIR.exists()

def test_settings_defaults():
    assert settings.JARVIS_PORT == 8000
    assert settings.JARVIS_HOST in ("127.0.0.1", "0.0.0.0")
    assert "20128" in settings.OMNIROUTE_URL or "localhost" in settings.OMNIROUTE_URL
    assert settings.LIVEKIT_URL.startswith("ws")
