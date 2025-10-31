"""End-to-end tests for date filtering functionality."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from click.testing import CliRunner

from osintagency import storage
from osintagency.cli.cli import fetch_channel_command
from osintagency.collector import DeterministicTelegramClient


@pytest.fixture(autouse=True)
def bypass_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")


def test_fetch_channel_with_days_parameter_filters_messages(
    monkeypatch: pytest.MonkeyPatch, tmp_path
):
    """
    End-to-end test: Calling fetch-channel with --days set to 7 only fetches
    messages from the last 7 days (relative to stub client's base timestamp).
    """
    # Setup environment
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@testchannel")
    db_path = tmp_path / "date_filtered.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))

    # DeterministicTelegramClient generates messages starting from 2024-01-01 00:00:00 UTC
    # with 1 minute intervals. We'll simulate fetching messages with a date filter.

    # First, fetch without date filter to see all messages
    runner = CliRunner()
    result = runner.invoke(
        fetch_channel_command,
        ["--limit", "10", "--use-stub"],
    )

    assert result.exit_code == 0
    messages = storage.fetch_messages("@testchannel", db_path=db_path)
    assert len(messages) == 10

    # Clear database
    from osintagency.collector import purge_database_file
    purge_database_file(db_path=db_path)

    # Now fetch with --days parameter
    # The stub client creates messages from 2024-01-01 00:00:00 onwards
    # Setting --days to a number will calculate offset_date = now - days
    # Since the stub messages are from 2024-01-01, and current date is much later,
    # all stub messages will be older than the offset_date and filtered out

    # To properly test this, we need messages that span the date range
    # For the stub client, all messages are from 2024-01-01, which is in the past
    # So with --days=7 (7 days ago from now), all stub messages will be filtered

    result = runner.invoke(
        fetch_channel_command,
        ["--limit", "10", "--use-stub", "--days", "7"],
    )

    assert result.exit_code == 0
    messages = storage.fetch_messages("@testchannel", db_path=db_path)
    # Since stub messages are from 2024-01-01 and we're filtering for last 7 days
    # from current date, no messages should be returned
    assert len(messages) == 0


def test_fetch_channel_without_days_parameter_gets_all_messages(
    monkeypatch: pytest.MonkeyPatch, tmp_path
):
    """Test that without --days parameter, all messages are fetched."""
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@testchannel")
    db_path = tmp_path / "no_filter.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))

    runner = CliRunner()
    result = runner.invoke(
        fetch_channel_command,
        ["--limit", "15", "--use-stub"],
    )

    assert result.exit_code == 0
    messages = storage.fetch_messages("@testchannel", db_path=db_path)
    assert len(messages) == 15

    # Verify all messages are from 2024-01-01
    for msg in messages:
        assert msg["posted_at"].startswith("2024-01-01")


def test_date_filtering_with_custom_offset_date(
    monkeypatch: pytest.MonkeyPatch, tmp_path
):
    """
    Test date filtering by directly using the collector with a specific offset_date.
    This tests the filtering logic more directly.
    """
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@testchannel")
    db_path = tmp_path / "custom_offset.sqlite3"

    from osintagency.collector import collect_messages

    client = DeterministicTelegramClient()

    # Test with offset_date that filters some messages
    # Stub messages start at 2024-01-01 00:00:00 with 1 minute intervals
    # Set offset to 2024-01-01 00:05:00 to get messages 6-10 (4 messages)
    offset_date = datetime(2024, 1, 1, 0, 5, 0, tzinfo=timezone.utc)

    outcome = collect_messages(
        limit=10,
        telegram_client=client,
        db_path=db_path,
        offset_date=offset_date,
    )

    assert outcome.stored_messages == 4
    messages = storage.fetch_messages("@testchannel", db_path=db_path)
    assert len(messages) == 4
    assert [msg["message_id"] for msg in messages] == [7, 8, 9, 10]

    # Verify all messages are newer than offset_date
    for msg in messages:
        msg_time = datetime.fromisoformat(msg["posted_at"])
        assert msg_time > offset_date
