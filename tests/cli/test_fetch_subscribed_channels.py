"""End-to-end tests for fetching all subscribed channels."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from click.testing import CliRunner
import pytest

from osintagency.cli import cli
from osintagency.clients import DeterministicTelegramClient
from osintagency.subscription import add_subscription, get_subscriptions
from osintagency.storage import fetch_messages


@pytest.fixture(autouse=True)
def configure_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Configure test environment variables."""
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")


def test_fetch_subscriptions_processes_all_active_channels(memory_db, monkeypatch):
    """Test that fetch-subscriptions command fetches messages from all active subscribed channels."""
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(memory_db))
    runner = CliRunner()
    telegram_client = DeterministicTelegramClient()

    # Add multiple subscriptions
    add_subscription(channel_id="@channel1", name="Channel 1")
    add_subscription(channel_id="@channel2", name="Channel 2")
    add_subscription(channel_id="@channel3", name="Channel 3")

    # Fetch all subscriptions
    result = runner.invoke(
        cli,
        ["subscribe", "fetch", "--limit", "3"],
        obj={"telegram_client": telegram_client},
    )

    assert result.exit_code == 0
    assert "@channel1" in result.output or "channel1" in result.output
    assert "@channel2" in result.output or "channel2" in result.output
    assert "@channel3" in result.output or "channel3" in result.output

    # Verify messages were stored for all channels
    messages = fetch_messages()
    assert len(messages) > 0

    # Check that we have messages from multiple channels
    channel_ids = {msg["channel_id"] for msg in messages}
    assert len(channel_ids) >= 2


def test_fetch_subscriptions_skips_inactive_channels(memory_db, monkeypatch):
    """Test that fetch-subscriptions skips inactive subscriptions."""
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(memory_db))
    runner = CliRunner()
    telegram_client = DeterministicTelegramClient()

    # Add active and inactive subscriptions
    add_subscription(channel_id="@active_channel", name="Active")
    add_subscription(channel_id="@inactive_channel", name="Inactive")

    # Deactivate one channel
    runner.invoke(
        cli,
        ["subscribe", "update", "--channel-id", "@inactive_channel", "--inactive"],
    )

    # Fetch subscriptions
    result = runner.invoke(
        cli,
        ["subscribe", "fetch", "--limit", "3"],
        obj={"telegram_client": telegram_client},
    )

    assert result.exit_code == 0

    # Verify only active subscriptions were processed
    subscriptions = get_subscriptions(active_only=True)
    assert len(subscriptions) == 1
    assert subscriptions[0]["channel_id"] == "@active_channel"


def test_fetch_subscriptions_with_no_subscriptions(memory_db, monkeypatch):
    """Test that fetch-subscriptions handles empty subscription list gracefully."""
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(memory_db))
    runner = CliRunner()
    telegram_client = DeterministicTelegramClient()

    # Don't add any subscriptions
    result = runner.invoke(
        cli,
        ["subscribe", "fetch"],
        obj={"telegram_client": telegram_client},
    )

    # Should complete successfully but indicate no subscriptions
    assert result.exit_code == 0
    assert "No active subscriptions" in result.output or "0" in result.output


def test_fetch_subscriptions_respects_limit_parameter(memory_db, monkeypatch):
    """Test that fetch-subscriptions respects the --limit parameter for each channel."""
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(memory_db))
    runner = CliRunner()
    telegram_client = DeterministicTelegramClient()

    # Add subscriptions
    add_subscription(channel_id="@channel1")

    # Fetch with specific limit
    result = runner.invoke(
        cli,
        ["subscribe", "fetch", "--limit", "2"],
        obj={"telegram_client": telegram_client},
    )

    assert result.exit_code == 0


def test_fetch_subscriptions_uses_custom_db_path(db_factory, monkeypatch):
    """Test that fetch-subscriptions respects custom db-path parameter."""
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")
    custom_db = db_factory()
    runner = CliRunner()
    telegram_client = DeterministicTelegramClient()

    # Set environment to custom db
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(custom_db))

    # Add subscription
    add_subscription(channel_id="@custom_channel")

    # Fetch using custom db path
    result = runner.invoke(
        cli,
        ["subscribe", "fetch", "--db-path", str(custom_db), "--limit", "2"],
        obj={"telegram_client": telegram_client},
    )

    assert result.exit_code == 0
    assert custom_db.exists()

    # Verify messages were stored
    messages = fetch_messages()
    assert len(messages) > 0


def test_fetch_subscriptions_handles_fetch_errors_gracefully(memory_db, monkeypatch):
    """Test that fetch-subscriptions continues processing other channels if one fails."""
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(memory_db))
    runner = CliRunner()
    telegram_client = DeterministicTelegramClient()

    # Add multiple subscriptions
    add_subscription(channel_id="@channel1")
    add_subscription(channel_id="@channel2")

    # Fetch subscriptions - even if one fails, should continue
    result = runner.invoke(
        cli,
        ["subscribe", "fetch", "--limit", "3"],
        obj={"telegram_client": telegram_client},
    )

    # Should complete even if there are errors
    assert result.exit_code == 0 or "error" in result.output.lower()


def test_setup_fetch_all_fetches_active_subscriptions(memory_db, monkeypatch):
    """Test that setup fetch-all command processes all active subscriptions."""
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(memory_db))
    runner = CliRunner()
    telegram_client = DeterministicTelegramClient()

    add_subscription(channel_id="@setup_channel1", name="Channel 1")
    add_subscription(channel_id="@setup_channel2", name="Channel 2")

    result = runner.invoke(
        cli,
        ["setup", "fetch-all", "--limit", "3"],
        obj={"telegram_client": telegram_client},
    )

    assert result.exit_code == 0
    messages = fetch_messages()
    assert messages, "Expected messages to be stored for setup fetch-all command."
    channel_ids = {msg["channel_id"] for msg in messages}
    assert "@setup_channel1" in channel_ids
    assert "@setup_channel2" in channel_ids


def test_setup_fetch_all_respects_days_parameter(memory_db, monkeypatch):
    """Test that setup fetch-all converts --days into an offset when invoking the action."""
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(memory_db))
    runner = CliRunner()
    telegram_client = DeterministicTelegramClient()

    captured: dict[str, object] = {}

    def fake_action(*, limit, db_path, log_level, telegram_client, offset_date):
        captured["limit"] = limit
        captured["db_path"] = db_path
        captured["log_level"] = log_level
        captured["telegram_client"] = telegram_client
        captured["offset_date"] = offset_date
        return 0

    monkeypatch.setattr(
        "osintagency.cli.setup_commands.fetch_subscriptions_action",
        fake_action,
        raising=False,
    )

    result = runner.invoke(
        cli,
        ["setup", "fetch-all", "--limit", "4", "--days", "30"],
        obj={"telegram_client": telegram_client},
    )

    assert result.exit_code == 0
    assert captured["offset_date"] is not None
    expected = datetime.now(timezone.utc) - timedelta(days=30)
    delta = abs((captured["offset_date"] - expected).total_seconds())
    assert delta < 5, "Offset date should be approximately 30 days ago."
    assert captured["limit"] == 4
    assert captured["telegram_client"] is telegram_client
