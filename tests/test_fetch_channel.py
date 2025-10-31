from __future__ import annotations

import json

from click.testing import CliRunner
import pytest

from osintagency import storage
from osintagency.collector import (
    DeterministicTelegramClient,
    collect_messages,
)
from osintagency.cli import cli


@pytest.fixture(autouse=True)
def configure_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@script")
    monkeypatch.delenv("TELEGRAM_SESSION_STRING", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)


def test_main_collects_messages(tmp_path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "collector" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    monkeypatch.setenv("TELEGRAM_SESSION_STRING", "session")
    runner = CliRunner()
    telegram_client = DeterministicTelegramClient()

    result = runner.invoke(
        cli,
        ["fetch-channel", "--limit", "3"],
        obj={"telegram_client": telegram_client},
    )

    assert result.exit_code == 0
    assert db_path.exists()
    rows = storage.fetch_messages("@script", db_path=db_path)
    assert len(rows) == 3

    payloads = [
        json.loads(line)
        for line in result.output.strip().splitlines()
        if line.strip()
    ]
    expected_ids = [
        message["id"]
        for message in telegram_client.fetch_messages("@script", limit=3)
    ]
    assert [message["id"] for message in payloads] == expected_ids


def test_stub_mode_collects_without_auth(tmp_path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "collector" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["fetch-channel", "--limit", "2", "--use-stub"],
    )

    assert result.exit_code == 0
    rows = storage.fetch_messages("@script", db_path=db_path)
    assert len(rows) == 2


def test_cleanup_command_removes_database(tmp_path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "collector" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    collect_messages(
        limit=1,
        db_path=db_path,
        channel_id="@script",
        telegram_client=DeterministicTelegramClient(),
    )
    assert db_path.exists()

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["cleanup-database", "--db-path", str(db_path), "--log-level", "info"],
    )

    assert result.exit_code == 0
    assert not db_path.exists()
