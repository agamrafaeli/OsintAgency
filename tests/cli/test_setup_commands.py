from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from osintagency.cli.cli import cli


@pytest.fixture(autouse=True)
def configure_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@method")
    monkeypatch.delenv("TELEGRAM_SESSION_STRING", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)


def test_setup_cleanup_removes_existing_database(tmp_path, monkeypatch):
    """
    Test that 'osintagency setup cleanup' deletes an existing database file.

    End-to-end test: Running `osintagency setup cleanup` successfully deletes
    the database file.
    """
    db_path = tmp_path / "messages.sqlite3"
    db_path.touch()  # Create the database file
    assert db_path.exists()

    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    result = runner.invoke(cli, ["setup", "cleanup"])

    assert result.exit_code == 0
    assert not db_path.exists()


def test_setup_cleanup_handles_missing_database(tmp_path, monkeypatch):
    """Test that 'osintagency setup cleanup' handles non-existent database gracefully."""
    db_path = tmp_path / "nonexistent.sqlite3"
    assert not db_path.exists()

    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    result = runner.invoke(cli, ["setup", "cleanup"])

    assert result.exit_code == 0
    assert not db_path.exists()


def test_setup_cleanup_with_explicit_db_path(tmp_path):
    """Test that 'osintagency setup cleanup' works with --db-path parameter."""
    db_path = tmp_path / "custom.sqlite3"
    db_path.touch()
    assert db_path.exists()

    runner = CliRunner()

    result = runner.invoke(
        cli, ["setup", "cleanup", "--db-path", str(db_path)]
    )

    assert result.exit_code == 0
    assert not db_path.exists()
