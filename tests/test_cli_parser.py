from __future__ import annotations

import io

from click.testing import CliRunner

from osintagency.cli import check_credentials_command, fetch_channel_command


def test_fetch_channel_command_uses_defaults(monkeypatch):
    captured: dict[str, object] = {}

    def fake_action(**kwargs):
        captured.update(kwargs)
        return 0

    monkeypatch.setattr(
        "osintagency.cli.commands.fetch_channel.fetch_channel_action", fake_action
    )
    runner = CliRunner()
    stdout = io.StringIO()
    stderr = io.StringIO()

    result = runner.invoke(
        fetch_channel_command,
        obj={"stdout": stdout, "stderr": stderr},
    )

    assert result.exit_code == 0
    assert captured["limit"] == 5
    assert captured["channel"] is None
    assert captured["db_path"] is None
    assert captured["log_level"] == "WARNING"
    assert captured["cleanup"] is False
    assert set(captured.keys()) == {
        "limit",
        "channel",
        "db_path",
        "log_level",
        "cleanup",
    }


def test_fetch_channel_command_handles_overrides(monkeypatch):
    captured: dict[str, object] = {}

    def fake_action(**kwargs):
        captured.update(kwargs)
        return 0

    monkeypatch.setattr(
        "osintagency.cli.commands.fetch_channel.fetch_channel_action", fake_action
    )
    runner = CliRunner()
    stdout = io.StringIO()
    stderr = io.StringIO()

    result = runner.invoke(
        fetch_channel_command,
        [
            "--limit",
            "10",
            "--channel",
            "@other",
            "--db-path",
            "/tmp/messages.sqlite3",
            "--log-level",
            "info",
            "--cleanup",
        ],
        obj={"stdout": stdout, "stderr": stderr},
    )

    assert result.exit_code == 0
    assert captured["limit"] == 10
    assert captured["channel"] == "@other"
    assert captured["db_path"] == "/tmp/messages.sqlite3"
    assert captured["log_level"] == "info"
    assert captured["cleanup"] is True
    assert set(captured.keys()) == {
        "limit",
        "channel",
        "db_path",
        "log_level",
        "cleanup",
    }


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
    stdout = io.StringIO()
    stderr = io.StringIO()

    result = runner.invoke(
        check_credentials_command,
        obj={"stdout": stdout, "stderr": stderr},
    )

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
    stdout = io.StringIO()
    stderr = io.StringIO()

    result = runner.invoke(
        check_credentials_command,
        ["--refresh-env", "--generate-session"],
        obj={"stdout": stdout, "stderr": stderr},
    )

    assert result.exit_code == 0
    assert captured["refresh_env"] is True
    assert captured["generate_session"] is True
    assert set(captured.keys()) == {"refresh_env", "generate_session"}
