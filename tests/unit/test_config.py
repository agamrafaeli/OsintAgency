import importlib

import pytest

from osintagency.config import ConfigurationError, TelegramConfig, load_telegram_config


def _clear_env(monkeypatch):
    for key in (
        "TELEGRAM_API_ID",
        "TELEGRAM_API_HASH",
        "TELEGRAM_TARGET_CHANNEL",
        "TELEGRAM_SESSION_STRING",
        "TELEGRAM_BOT_TOKEN",
    ):
        monkeypatch.delenv(key, raising=False)


def test_load_config_with_session(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TELEGRAM_API_ID", "4321")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@channel")
    monkeypatch.setenv("TELEGRAM_SESSION_STRING", "session")

    config = load_telegram_config(refresh_env=True)

    assert isinstance(config, TelegramConfig)
    assert config.api_id == 4321
    assert config.api_hash == "hash"
    assert config.target_channel == "@channel"
    assert config.auth_mode == "session"


def test_load_config_with_bot_token(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TELEGRAM_API_ID", "4321")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@channel")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot:token")

    config = load_telegram_config(refresh_env=True)

    assert config.auth_mode == "bot"
    assert config.session_string is None
    assert config.bot_token == "bot:token"


def test_missing_authentication_raises(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TELEGRAM_API_ID", "4321")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@channel")

    with pytest.raises(ConfigurationError):
        load_telegram_config(refresh_env=True)


def test_load_config_without_auth_when_not_required(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TELEGRAM_API_ID", "4321")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@channel")

    config = load_telegram_config(refresh_env=True, require_auth=False)

    assert config.session_string is None
    assert config.bot_token is None


def test_require_session_rejects_bot(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TELEGRAM_API_ID", "4321")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@channel")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot:token")

    config = load_telegram_config(refresh_env=True)

    with pytest.raises(ConfigurationError):
        config.require_session()
