from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from osintagency.actions.fetch_channel_action import fetch_channel_action


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


@pytest.mark.parametrize("use_stub, expected_channel", [(True, "@stub"), (False, "@live")])
def test_fetch_channel_action_selects_collector(
    monkeypatch: pytest.MonkeyPatch,
    use_stub: bool,
    expected_channel: str,
) -> None:
    calls: list[str] = []

    def fake_collect_with_stub(**kwargs):
        calls.append("stub")
        assert kwargs["limit"] == 2
        assert kwargs["channel_override"] == expected_channel
        assert kwargs["db_path"] == "/tmp/messages.sqlite3"
        return FakeOutcome(expected_channel)

    def fake_collect_live(**kwargs):
        calls.append("live")
        assert kwargs["limit"] == 2
        assert kwargs["channel_override"] == expected_channel
        assert kwargs["db_path"] == "/tmp/messages.sqlite3"
        return FakeOutcome(expected_channel)

    action_module = importlib.import_module("osintagency.actions.fetch_channel_action")
    fake_console = StubConsole()
    monkeypatch.setattr(action_module, "get_console_logger", lambda: fake_console)
    monkeypatch.setattr(action_module, "collect_with_stub", fake_collect_with_stub)
    monkeypatch.setattr(action_module, "collect_live", fake_collect_live)

    exit_code = fetch_channel_action(
        limit=2,
        channel=expected_channel,
        db_path="/tmp/messages.sqlite3",
        log_level="INFO",
        use_stub=use_stub,
    )

    assert exit_code == 0
    assert calls == (["stub"] if use_stub else ["live"])
    assert fake_console.messages, "Console output should include serialized message"
