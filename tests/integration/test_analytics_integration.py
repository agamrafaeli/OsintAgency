"""
Integration test for analytics summary using real storage backend.

This test verifies that the analytics summary integrates correctly with
the storage backend and reflects actual database content.
"""
import pytest
from osintagency.storage import fetch_analytics_summary
from osintagency.storage.backends.peewee import PeeweeStorage


@pytest.fixture
def test_storage(tmp_path):
    """Create a temporary storage backend for testing."""
    db_path = tmp_path / "test_analytics.sqlite"
    storage = PeeweeStorage(db_path=db_path)
    return storage, db_path


def test_analytics_reflects_real_database_content(test_storage):
    """
    Test that analytics summary reflects actual database content.

    This verifies the integration between the dashboard analytics panel
    and the real storage backend.
    """
    storage, db_path = test_storage

    # Initially, database should be empty
    analytics = fetch_analytics_summary(db_path=db_path)
    assert analytics["total_messages"] == 0
    assert analytics["detected_verses"] == 0
    assert analytics["oldest_message_date"] is None
    assert analytics["newest_message_date"] is None

    # Add some messages to the database
    messages_batch_1 = [
        {"id": 1, "timestamp": "2024-05-01T10:00:00", "text": "First message"},
        {"id": 2, "timestamp": "2024-05-02T15:30:00", "text": "Second message"},
    ]
    storage.persist_messages("@test_channel", messages_batch_1)

    # Analytics should now reflect the added messages
    analytics = fetch_analytics_summary(db_path=db_path)
    assert analytics["total_messages"] == 2
    assert analytics["oldest_message_date"] == "2024-05-01T10:00:00"
    assert analytics["newest_message_date"] == "2024-05-02T15:30:00"

    # Add more messages - analytics should update
    messages_batch_2 = [
        {"id": 3, "timestamp": "2024-05-03T08:00:00", "text": "Third message"},
        {"id": 4, "timestamp": "2024-05-04T12:00:00", "text": "Fourth message"},
    ]
    storage.persist_messages("@test_channel", messages_batch_2)

    # Analytics should reflect the new total
    analytics = fetch_analytics_summary(db_path=db_path)
    assert analytics["total_messages"] == 4
    assert analytics["oldest_message_date"] == "2024-05-01T10:00:00"
    assert analytics["newest_message_date"] == "2024-05-04T12:00:00"


def test_analytics_reflects_detected_verses(test_storage):
    """
    Test that analytics summary correctly counts detected verses.
    """
    storage, db_path = test_storage

    # Add messages first
    messages = [
        {"id": 1, "timestamp": "2024-05-01T10:00:00", "text": "Message with verse"},
        {"id": 2, "timestamp": "2024-05-02T10:00:00", "text": "Another message"},
    ]
    storage.persist_messages("@test_channel", messages)

    # Add detected verses
    verses = [
        {
            "message_id": 1,
            "sura": 1,
            "ayah": 1,
            "detected_at": "2024-05-01T10:00:00+00:00"
        },
        {
            "message_id": 1,
            "sura": 2,
            "ayah": 255,
            "detected_at": "2024-05-01T10:00:00+00:00"
        },
        {
            "message_id": 2,
            "sura": 3,
            "ayah": 185,
            "detected_at": "2024-05-02T10:00:00+00:00"
        },
    ]
    storage.persist_detected_verses(verses, message_ids=[1, 1, 2])

    # Analytics should count the verses
    analytics = fetch_analytics_summary(db_path=db_path)
    assert analytics["detected_verses"] == 3
    assert analytics["total_messages"] == 2
