from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from osintagency.actions.fetch_channel_action import fetch_channel_action
from osintagency.collector import (
    DeterministicTelegramClient,
    TelethonTelegramClient,
)
from osintagency.config import load_telegram_config


class FakeOutcome:
    def __init__(self, channel: str) -> None:
        self.channel_id = channel
        self.stored_messages = 1
        self.db_path = Path("/tmp/messages.sqlite3")
        self.messages = [{"id": 1, "text": "hello"}]


class StubConsole:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def info(self, message: str) -> None:
        self.messages.append(message)

    def error(self, message: str) -> None:  # pragma: no cover - not used here
        self.messages.append(f"ERROR: {message}")


@pytest.mark.parametrize(
    ("channel_id", "requires_auth"),
    [("@stub", False), ("@live", True)],
)
def test_fetch_channel_action_invokes_provided_collector(
    monkeypatch: pytest.MonkeyPatch,
    channel_id: str,
    requires_auth: bool,
) -> None:
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", channel_id)
    monkeypatch.setenv("TELEGRAM_SESSION_STRING", "session")
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    calls: list[dict[str, object]] = []

    def fake_collect_messages(**kwargs):
        calls.append(kwargs)
        assert kwargs["limit"] == 2
        assert kwargs["channel_id"] == channel_id
        assert kwargs["db_path"] == "/tmp/messages.sqlite3"
        assert kwargs["telegram_client"].requires_auth is requires_auth
        return FakeOutcome(channel_id)

    action_module = importlib.import_module("osintagency.actions.fetch_channel_action")
    fake_console = StubConsole()
    monkeypatch.setattr(action_module, "get_console_logger", lambda: fake_console)
    monkeypatch.setattr(action_module, "collect_messages", fake_collect_messages)

    exit_code = fetch_channel_action(
        limit=2,
        channel_id=channel_id,
        db_path="/tmp/messages.sqlite3",
        log_level="INFO",
        telegram_client=DeterministicTelegramClient()
        if not requires_auth
        else TelethonTelegramClient(load_telegram_config(require_auth=True)),
    )

    assert exit_code == 0
    assert len(calls) == 1
    assert fake_console.messages, "Console output should include serialized message"
