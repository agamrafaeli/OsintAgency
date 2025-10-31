from __future__ import annotations

import json
from io import StringIO

import pytest

from osintagency import storage
from osintagency.cli import main


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
    stdout = StringIO()

    exit_code = main(["fetch-channel", "--limit", "2"], stdout=stdout)

    assert exit_code == 0
    assert db_path.exists()
    rows = storage.fetch_messages("@method", db_path=db_path)
    assert len(rows) == 2
    payloads = [
        json.loads(line)
        for line in stdout.getvalue().strip().splitlines()
        if line.strip()
    ]
    assert [message["id"] for message in payloads] == [1, 2]


def test_check_credentials_method_success(tmp_path, monkeypatch):
    db_path = tmp_path / "storage" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(["check-credentials"], stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert "Credential check succeeded." in stdout.getvalue()
    assert stderr.getvalue() == ""


def test_check_credentials_generate_session_requires_telethon(tmp_path, monkeypatch):
    db_path = tmp_path / "session" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        ["check-credentials", "--generate-session"],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 1
    assert "Telethon must be installed" in stderr.getvalue()
