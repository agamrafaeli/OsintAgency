from __future__ import annotations

import importlib
import json
import sys

from click.testing import CliRunner
import pytest

from osintagency import storage
from osintagency.cli import cli
from osintagency.clients import DeterministicTelegramClient


@pytest.fixture(autouse=True)
def configure_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@method")
    monkeypatch.delenv("TELEGRAM_SESSION_STRING", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)


def test_fetch_channel_method_uses_provided_stream(tmp_path, monkeypatch):
    db_path = tmp_path / "collector" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    monkeypatch.setenv("TELEGRAM_SESSION_STRING", "session")
    runner = CliRunner()
    telegram_client = DeterministicTelegramClient()

    result = runner.invoke(
        cli,
        ["fetch-channel", "--limit", "2"],
        obj={"telegram_client": telegram_client},
    )

    assert result.exit_code == 0
    assert db_path.exists()
    rows = storage.fetch_messages("@method", db_path=db_path)
    assert len(rows) == 2
    payloads = [
        json.loads(line)
        for line in result.output.strip().splitlines()
        if line.strip()
    ]
    expected_ids = [
        message["id"]
        for message in telegram_client.fetch_messages("@method", limit=2)
    ]
    assert [message["id"] for message in payloads] == expected_ids


def test_fetch_channel_stub_mode_writes_messages(tmp_path, monkeypatch):
    db_path = tmp_path / "collector" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["fetch-channel", "--limit", "2", "--use-stub"],
    )

    assert result.exit_code == 0
    rows = storage.fetch_messages("@method", db_path=db_path)
    assert len(rows) == 2


def test_check_credentials_method_success(tmp_path, monkeypatch):
    db_path = tmp_path / "storage" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    runner = CliRunner()

    result = runner.invoke(cli, ["check-credentials"])

    assert result.exit_code == 0
    assert "Credential check succeeded." in result.output
    assert "Telethon must be installed" not in result.output


def test_check_credentials_generate_session_requires_telethon(tmp_path, monkeypatch):
    db_path = tmp_path / "session" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))

    called: list[bool] = []

    def fake_generate_session(config):
        called.append(True)
        print("Telethon must be installed", file=sys.stderr)
        return None

    check_credentials_module = importlib.import_module(
        "osintagency.actions.check_credentials_action"
    )
    monkeypatch.setattr(
        check_credentials_module,
        "_generate_session_string",
        fake_generate_session,
    )
    runner = CliRunner()

    result = runner.invoke(cli, ["check-credentials", "--generate-session"])

    assert result.exit_code == 1
    assert called, "Generate session routine should be invoked"
    assert "Telethon must be installed" in result.output
