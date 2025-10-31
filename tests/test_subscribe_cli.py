"""Tests for the subscribe CLI command group."""

from __future__ import annotations

from click.testing import CliRunner
import pytest

from osintagency.cli import cli
from osintagency.subscription import get_subscriptions


@pytest.fixture(autouse=True)
def configure_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Configure test environment variables."""
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")


def test_subscribe_add_command_adds_channel_by_id(tmp_path, monkeypatch):
    """Test that subscribe add command successfully adds a subscription by channel ID."""
    db_path = tmp_path / "subscriptions" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["subscribe", "add", "--channel-id", "@test_channel", "--name", "Test Channel"],
    )

    assert result.exit_code == 0
    assert "Subscribed to @test_channel" in result.output

    # Verify subscription was stored
    subscriptions = get_subscriptions(db_path=db_path)
    assert len(subscriptions) == 1
    assert subscriptions[0]["channel_id"] == "@test_channel"
    assert subscriptions[0]["name"] == "Test Channel"
    assert subscriptions[0]["active"] is True


def test_subscribe_add_command_requires_channel_id(tmp_path, monkeypatch):
    """Test that subscribe add command requires channel-id parameter."""
    db_path = tmp_path / "subscriptions" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    result = runner.invoke(cli, ["subscribe", "add"])

    assert result.exit_code != 0
    assert "channel-id" in result.output.lower() or "required" in result.output.lower()


def test_subscribe_add_command_with_optional_name(tmp_path, monkeypatch):
    """Test that subscribe add command works without optional name parameter."""
    db_path = tmp_path / "subscriptions" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    result = runner.invoke(cli, ["subscribe", "add", "--channel-id", "@anonymous_channel"])

    assert result.exit_code == 0
    assert "Subscribed to @anonymous_channel" in result.output

    # Verify subscription was stored without name
    subscriptions = get_subscriptions(db_path=db_path)
    assert len(subscriptions) == 1
    assert subscriptions[0]["channel_id"] == "@anonymous_channel"
    assert subscriptions[0]["name"] is None


def test_subscribe_add_command_updates_existing_subscription(tmp_path, monkeypatch):
    """Test that subscribe add command updates an existing subscription."""
    db_path = tmp_path / "subscriptions" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # Add initial subscription
    result1 = runner.invoke(
        cli,
        ["subscribe", "add", "--channel-id", "@update_test", "--name", "Old Name"],
    )
    assert result1.exit_code == 0

    # Update the subscription
    result2 = runner.invoke(
        cli,
        ["subscribe", "add", "--channel-id", "@update_test", "--name", "New Name"],
    )
    assert result2.exit_code == 0
    assert "Subscribed to @update_test" in result2.output

    # Verify only one subscription exists with updated name
    subscriptions = get_subscriptions(db_path=db_path)
    assert len(subscriptions) == 1
    assert subscriptions[0]["channel_id"] == "@update_test"
    assert subscriptions[0]["name"] == "New Name"


def test_subscribe_add_command_with_custom_db_path(tmp_path, monkeypatch):
    """Test that subscribe add command respects custom db-path parameter."""
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")
    custom_db_path = tmp_path / "custom" / "database.sqlite3"
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "subscribe",
            "add",
            "--channel-id",
            "@custom_path_channel",
            "--db-path",
            str(custom_db_path),
        ],
    )

    assert result.exit_code == 0
    assert custom_db_path.exists()

    # Verify subscription was stored in custom path
    subscriptions = get_subscriptions(db_path=custom_db_path)
    assert len(subscriptions) == 1
    assert subscriptions[0]["channel_id"] == "@custom_path_channel"


def test_subscribe_list_command_shows_subscriptions(tmp_path, monkeypatch):
    """Test that subscribe list command shows all subscriptions."""
    db_path = tmp_path / "subscriptions" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # Add some subscriptions
    runner.invoke(cli, ["subscribe", "add", "--channel-id", "@channel1", "--name", "Channel 1"])
    runner.invoke(cli, ["subscribe", "add", "--channel-id", "@channel2", "--name", "Channel 2"])

    # List subscriptions
    result = runner.invoke(cli, ["subscribe", "list"])

    assert result.exit_code == 0
    assert "@channel1" in result.output
    assert "@channel2" in result.output
    assert "Channel 1" in result.output
    assert "Channel 2" in result.output


def test_subscribe_list_command_empty_database(tmp_path, monkeypatch):
    """Test that subscribe list command handles empty database."""
    db_path = tmp_path / "subscriptions" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # First create the database by adding and removing a subscription
    runner.invoke(cli, ["subscribe", "add", "--channel-id", "@temp"])
    runner.invoke(cli, ["subscribe", "remove", "--channel-id", "@temp"])

    result = runner.invoke(cli, ["subscribe", "list"])

    assert result.exit_code == 0
    assert "No subscriptions found" in result.output


def test_subscribe_list_command_json_format(tmp_path, monkeypatch):
    """Test that subscribe list command supports JSON output."""
    db_path = tmp_path / "subscriptions" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # Add a subscription
    runner.invoke(cli, ["subscribe", "add", "--channel-id", "@json_test", "--name", "JSON Test"])

    # List in JSON format
    result = runner.invoke(cli, ["subscribe", "list", "--format", "json"])

    assert result.exit_code == 0
    assert '"channel_id": "@json_test"' in result.output
    assert '"name": "JSON Test"' in result.output


def test_subscribe_update_command_updates_name(tmp_path, monkeypatch):
    """Test that subscribe update command can update subscription name."""
    db_path = tmp_path / "subscriptions" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # Add subscription
    runner.invoke(cli, ["subscribe", "add", "--channel-id", "@update_name", "--name", "Old Name"])

    # Update name
    result = runner.invoke(
        cli,
        ["subscribe", "update", "--channel-id", "@update_name", "--name", "New Name"],
    )

    assert result.exit_code == 0
    assert "Updated subscription for @update_name" in result.output

    # Verify update
    subscriptions = get_subscriptions(db_path=db_path)
    assert subscriptions[0]["name"] == "New Name"


def test_subscribe_update_command_updates_active_status(tmp_path, monkeypatch):
    """Test that subscribe update command can update active status."""
    db_path = tmp_path / "subscriptions" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # Add subscription
    runner.invoke(cli, ["subscribe", "add", "--channel-id", "@active_test"])

    # Deactivate
    result = runner.invoke(
        cli,
        ["subscribe", "update", "--channel-id", "@active_test", "--inactive"],
    )

    assert result.exit_code == 0

    # Verify deactivation
    subscriptions = get_subscriptions(active_only=False, db_path=db_path)
    assert subscriptions[0]["active"] is False


def test_subscribe_update_command_requires_parameters(tmp_path, monkeypatch):
    """Test that subscribe update command requires at least one update parameter."""
    db_path = tmp_path / "subscriptions" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # Add subscription
    runner.invoke(cli, ["subscribe", "add", "--channel-id", "@param_test"])

    # Try to update without any parameters
    result = runner.invoke(
        cli,
        ["subscribe", "update", "--channel-id", "@param_test"],
    )

    assert result.exit_code != 0
    assert "At least one of" in result.output


def test_subscribe_update_command_not_found(tmp_path, monkeypatch):
    """Test that subscribe update command handles non-existent subscription."""
    db_path = tmp_path / "subscriptions" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # First create the database by adding and removing a subscription
    runner.invoke(cli, ["subscribe", "add", "--channel-id", "@temp"])
    runner.invoke(cli, ["subscribe", "remove", "--channel-id", "@temp"])

    result = runner.invoke(
        cli,
        ["subscribe", "update", "--channel-id", "@nonexistent", "--name", "Test"],
    )

    assert result.exit_code != 0
    assert "not found" in result.output


def test_subscribe_remove_command_removes_subscription(tmp_path, monkeypatch):
    """Test that subscribe remove command removes a subscription."""
    db_path = tmp_path / "subscriptions" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # Add subscription
    runner.invoke(cli, ["subscribe", "add", "--channel-id", "@remove_test"])

    # Remove it
    result = runner.invoke(cli, ["subscribe", "remove", "--channel-id", "@remove_test"])

    assert result.exit_code == 0
    assert "Removed subscription for @remove_test" in result.output

    # Verify removal
    subscriptions = get_subscriptions(db_path=db_path)
    assert len(subscriptions) == 0


def test_subscribe_remove_command_not_found(tmp_path, monkeypatch):
    """Test that subscribe remove command handles non-existent subscription."""
    db_path = tmp_path / "subscriptions" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # First create the database by adding and removing a subscription
    runner.invoke(cli, ["subscribe", "add", "--channel-id", "@temp"])
    runner.invoke(cli, ["subscribe", "remove", "--channel-id", "@temp"])

    result = runner.invoke(cli, ["subscribe", "remove", "--channel-id", "@nonexistent"])

    assert result.exit_code != 0
    assert "not found" in result.output
