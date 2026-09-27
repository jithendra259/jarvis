"""Configuration must be environment driven, secret free and portable."""

from __future__ import annotations

import pytest

from config.settings import Settings


def test_defaults_are_local_and_loopback_only(isolated_data_dir):
    config = Settings.from_env()
    assert config.host == "127.0.0.1"
    assert config.port == 8000
    assert config.omniroute_url.startswith("http://127.0.0.1")
    assert config.ollama_url.startswith("http://127.0.0.1")
    assert config.livekit_url.startswith("ws://127.0.0.1")


def test_no_credentials_are_hardcoded(monkeypatch):
    for name in ("OMNIROUTE_API_KEY", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"):
        monkeypatch.delenv(name, raising=False)
    config = Settings.from_env()
    assert config.omniroute_api_key == ""
    assert config.livekit_api_key == ""
    assert config.livekit_api_secret == ""
    assert config.livekit_configured is False


def test_env_overrides_are_applied(monkeypatch, tmp_path):
    monkeypatch.setenv("JARVIS_PORT", "9123")
    monkeypatch.setenv("OMNIROUTE_URL", "http://127.0.0.1:9999/v1/")
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("LIVEKIT_API_KEY", "devkey")
    monkeypatch.setenv("LIVEKIT_API_SECRET", "secret")
    config = Settings.from_env()
    assert config.port == 9123
    assert config.omniroute_url == "http://127.0.0.1:9999/v1"
    assert config.llm_provider == "ollama"
    assert config.livekit_configured is True


def test_data_dir_override_keeps_state_out_of_the_repo(monkeypatch, tmp_path):
    target = tmp_path / "custom-jarvis"
    monkeypatch.setenv("JARVIS_DATA_DIR", str(target))
    monkeypatch.setenv("DATABASE_PATH", str(target / "db" / "jarvis.db"))
    config = Settings.from_env()
    config.ensure_data_dirs()
    assert config.data_dir == target
    assert config.database_path == target / "db" / "jarvis.db"
    assert config.database_path.parent.exists()
    assert config.logs_dir.exists()
    assert config.models_dir.exists()
    assert str(config.data_dir).startswith(str(tmp_path))


def test_invalid_numeric_env_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("JARVIS_PORT", "not-a-number")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "")
    config = Settings.from_env()
    assert config.port == 8000
    assert config.llm_timeout_seconds > 0


def test_public_dict_never_leaks_secrets(monkeypatch):
    monkeypatch.setenv("OMNIROUTE_API_KEY", "sk-super-secret-value")
    monkeypatch.setenv("LIVEKIT_API_SECRET", "super-secret")
    public = Settings.from_env().public_dict()
    serialised = repr(public)
    assert "sk-super-secret-value" not in serialised
    assert "super-secret" not in serialised
    assert public["omniroute_api_key_configured"] is True
    assert public["livekit_configured"] is False  # no api key set


def test_cors_origins_cover_desktop_and_dev_servers(monkeypatch):
    config = Settings.from_env()
    assert "http://localhost:3000" in config.cors_origins
    assert "http://tauri.localhost" in config.cors_origins


@pytest.mark.parametrize("attribute", ["data_dir", "logs_dir", "models_dir", "cache_dir"])
def test_directory_attributes_are_paths(attribute, isolated_data_dir):
    assert isinstance(getattr(isolated_data_dir, attribute), type(isolated_data_dir.data_dir))
