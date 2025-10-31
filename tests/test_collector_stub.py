from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from osintagency import storage


@pytest.fixture(autouse=True)
def bypass_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")


def test_stubbed_collection_respects_db_env(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@sample")
    db_path = tmp_path / "custom_dir" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))

    from osintagency.collector import (
        CollectionOutcome,
        DeterministicTelegramClient,
        collect_messages,
        purge_database_file,
    )

    outcome = collect_messages(
        limit=5,
        telegram_client=DeterministicTelegramClient(),
    )

    assert isinstance(outcome, CollectionOutcome)
    assert outcome.channel_id == "@sample"
    assert outcome.stored_messages == 5
    assert outcome.db_path == Path(db_path)
    assert db_path.exists()

    rows = storage.fetch_messages("@sample", db_path=db_path)
    assert len(rows) == 5
    assert [row["message_id"] for row in rows] == [1, 2, 3, 4, 5]

    purge_database_file(db_path=outcome.db_path)
    assert not db_path.exists()


def test_deterministic_client_with_offset_date():
    """Test that DeterministicTelegramClient filters messages by offset_date."""
    from osintagency.collector import DeterministicTelegramClient

    client = DeterministicTelegramClient()

    # Base timestamp is 2024-01-01 00:00:00 UTC
    # Messages are generated with 1 minute intervals
    # Message 1: 2024-01-01 00:00:00
    # Message 2: 2024-01-01 00:01:00
    # Message 3: 2024-01-01 00:02:00
    # etc.

    # Test 1: No offset_date - should return all messages
    messages = client.fetch_messages("@test", limit=10)
    assert len(messages) == 10
    assert messages[0]["id"] == 1
    assert messages[9]["id"] == 10

    # Test 2: offset_date before all messages - should return all messages
    offset_date = datetime(2023, 12, 31, tzinfo=timezone.utc)
    messages = client.fetch_messages("@test", limit=10, offset_date=offset_date)
    assert len(messages) == 10

    # Test 3: offset_date that filters some messages
    # Set offset to 2024-01-01 00:05:00 - should only get messages 7-10 (strictly newer than offset)
    # Message 6 is at 00:05:00, so excluded (not strictly greater)
    offset_date = datetime(2024, 1, 1, 0, 5, 0, tzinfo=timezone.utc)
    messages = client.fetch_messages("@test", limit=10, offset_date=offset_date)
    assert len(messages) == 4
    assert messages[0]["id"] == 7
    assert messages[3]["id"] == 10

    # Verify timestamps are all newer than offset_date
    for msg in messages:
        msg_time = datetime.fromisoformat(msg["timestamp"])
        assert msg_time > offset_date

    # Test 4: offset_date after all messages - should return empty list
    offset_date = datetime(2024, 1, 1, 0, 15, 0, tzinfo=timezone.utc)
    messages = client.fetch_messages("@test", limit=10, offset_date=offset_date)
    assert len(messages) == 0


def test_collect_messages_with_offset_date(monkeypatch: pytest.MonkeyPatch, tmp_path):
    """Test that collect_messages passes offset_date to telegram client and stores filtered messages."""
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@testchannel")
    db_path = tmp_path / "test_offset.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))

    from osintagency.collector import (
        DeterministicTelegramClient,
        collect_messages,
    )

    # Test without offset_date - should get all 10 messages
    outcome = collect_messages(
        limit=10,
        telegram_client=DeterministicTelegramClient(),
    )
    assert outcome.stored_messages == 10

    rows = storage.fetch_messages("@testchannel", db_path=db_path)
    assert len(rows) == 10

    # Clear the database for next test
    from osintagency.collector import purge_database_file

    purge_database_file(db_path=db_path)

    # Test with offset_date - should only get messages newer than 5 minutes
    # Messages 7-10 should be stored (4 messages)
    offset_date = datetime(2024, 1, 1, 0, 5, 0, tzinfo=timezone.utc)
    outcome = collect_messages(
        limit=10,
        telegram_client=DeterministicTelegramClient(),
        offset_date=offset_date,
    )
    assert outcome.stored_messages == 4

    rows = storage.fetch_messages("@testchannel", db_path=db_path)
    assert len(rows) == 4
    assert [row["message_id"] for row in rows] == [7, 8, 9, 10]

    # Verify all stored messages have timestamps newer than offset_date
    for row in rows:
        msg_time = datetime.fromisoformat(row["posted_at"])
        assert msg_time > offset_date
