from __future__ import annotations

from click.testing import CliRunner

from osintagency.cli import (
    check_credentials_command,
    cleanup_database_command,
    fetch_channel_command,
)
from osintagency.collector import (
    DeterministicTelegramClient,
    TelethonTelegramClient,
)


def test_fetch_channel_command_uses_defaults(monkeypatch):
    captured: dict[str, object] = {}

    def fake_action(**kwargs):
        captured.update(kwargs)
        return 0
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@default")
    monkeypatch.setenv("TELEGRAM_SESSION_STRING", "session")
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setattr(
        "osintagency.cli.commands.fetch_channel.fetch_channel_action", fake_action
    )
    runner = CliRunner()
    result = runner.invoke(fetch_channel_command)

    assert result.exit_code == 0
    assert captured["limit"] == 5
    assert captured["channel_id"] is None
    assert captured["db_path"] is None
    assert captured["log_level"] == "WARNING"
    assert isinstance(captured["telegram_client"], TelethonTelegramClient)
    assert set(captured.keys()) == {
        "limit",
        "channel_id",
        "db_path",
        "log_level",
        "telegram_client",
    }


def test_fetch_channel_command_handles_overrides(monkeypatch):
    captured: dict[str, object] = {}

    def fake_action(**kwargs):
        captured.update(kwargs)
        return 0
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@default")
    monkeypatch.setenv("TELEGRAM_SESSION_STRING", "session")
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setattr(
        "osintagency.cli.commands.fetch_channel.fetch_channel_action", fake_action
    )
    runner = CliRunner()
    telegram_client = DeterministicTelegramClient()

    result = runner.invoke(
        fetch_channel_command,
        [
            "--limit",
            "10",
            "--channel-id",
            "@other",
            "--db-path",
            "/tmp/messages.sqlite3",
            "--log-level",
            "info",
            "--use-stub",
        ],
        obj={"telegram_client": telegram_client},
    )

    assert result.exit_code == 0
    assert captured["limit"] == 10
    assert captured["channel_id"] == "@other"
    assert captured["db_path"] == "/tmp/messages.sqlite3"
    assert captured["log_level"] == "info"
    assert isinstance(captured["telegram_client"], DeterministicTelegramClient)
    assert set(captured.keys()) == {
        "limit",
        "channel_id",
        "db_path",
        "log_level",
        "telegram_client",
    }
    assert captured["telegram_client"] is telegram_client


def test_cleanup_database_command_uses_defaults(monkeypatch):
    captured: dict[str, object] = {}

    def fake_action(**kwargs):
        captured.update(kwargs)
        return 0

    monkeypatch.setattr(
        "osintagency.cli.commands.cleanup_database.cleanup_database_action",
        fake_action,
    )
    runner = CliRunner()
    result = runner.invoke(cleanup_database_command)

    assert result.exit_code == 0
    assert captured["db_path"] is None
    assert captured["log_level"] == "WARNING"
    assert set(captured.keys()) == {"db_path", "log_level"}


def test_cleanup_database_command_handles_overrides(monkeypatch):
    captured: dict[str, object] = {}

    def fake_action(**kwargs):
        captured.update(kwargs)
        return 3

    monkeypatch.setattr(
        "osintagency.cli.commands.cleanup_database.cleanup_database_action",
        fake_action,
    )
    runner = CliRunner()
    result = runner.invoke(
        cleanup_database_command,
        ["--db-path", "/tmp/messages.sqlite3", "--log-level", "info"],
    )

    assert result.exit_code == 3
    assert captured["db_path"] == "/tmp/messages.sqlite3"
    assert captured["log_level"] == "info"
    assert set(captured.keys()) == {"db_path", "log_level"}


def test_check_credentials_command_uses_defaults(monkeypatch):
    captured: dict[str, object] = {}

    def fake_action(**kwargs):
        captured.update(kwargs)
        return 0

    monkeypatch.setattr(
        "osintagency.cli.commands.check_credentials.check_credentials_action",
        fake_action,
    )
    runner = CliRunner()
    result = runner.invoke(check_credentials_command)

    assert result.exit_code == 0
    assert captured["refresh_env"] is False
    assert captured["generate_session"] is False
    assert set(captured.keys()) == {"refresh_env", "generate_session"}


def test_check_credentials_command_handles_flags(monkeypatch):
    captured: dict[str, object] = {}

    def fake_action(**kwargs):
        captured.update(kwargs)
        return 0

    monkeypatch.setattr(
        "osintagency.cli.commands.check_credentials.check_credentials_action",
        fake_action,
    )
    runner = CliRunner()
    result = runner.invoke(
        check_credentials_command,
        ["--refresh-env", "--generate-session"],
    )

    assert result.exit_code == 0
    assert captured["refresh_env"] is True
    assert captured["generate_session"] is True
    assert set(captured.keys()) == {"refresh_env", "generate_session"}
