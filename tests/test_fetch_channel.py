from __future__ import annotations

import json
from pathlib import Path

import pytest

from osintagency import storage
from osintagency.collector import collect_with_stub
from osintagency.cli import OsintAgencyCLI


@pytest.fixture(autouse=True)
def configure_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@script")
    monkeypatch.delenv("TELEGRAM_SESSION_STRING", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)


def test_main_collects_messages(tmp_path, monkeypatch: pytest.MonkeyPatch, capsys):
    db_path = tmp_path / "collector" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    cli = OsintAgencyCLI()
    exit_code = cli.fetch_channel(["--limit", "3"])

    assert exit_code == 0
    assert db_path.exists()
    rows = storage.fetch_messages("@script", db_path=db_path)
    assert len(rows) == 3

    stdout = capsys.readouterr().out.strip().splitlines()
    payloads = [json.loads(line) for line in stdout if line.strip()]
    assert [message["id"] for message in payloads] == [1, 2, 3]


def test_main_cleanup_removes_database(tmp_path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "collector" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    collect_with_stub(limit=1, db_path=db_path, channel_override="@script")
    assert db_path.exists()

    cli = OsintAgencyCLI()
    exit_code = cli.fetch_channel(["--cleanup", "--db-path", str(db_path)])

    assert exit_code == 0
    assert not db_path.exists()
