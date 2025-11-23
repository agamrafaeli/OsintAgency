from datetime import datetime, timezone

import pytest

from osintagency.storage.backends.peewee_backend import PeeweeStorage


@pytest.fixture(params=[PeeweeStorage])
def storage_backend(request, tmp_path):
    """Parameterized fixture providing different storage backend implementations."""
    backend_class = request.param
    db_path = tmp_path / "messages.sqlite"
    return backend_class(db_path=db_path)


def test_persist_messages_creates_table_and_upserts(storage_backend):
    first_batch = [
        {"id": 1, "timestamp": "2024-01-01T00:00:00", "text": "hello"},
    ]
    second_batch = [
        {"id": 1, "timestamp": "2024-01-02T00:00:00", "text": "updated"},
        {"id": 2, "timestamp": "2024-01-02T00:05:00", "text": "world"},
    ]

    storage_backend.persist_messages("@channel", first_batch)
    storage_backend.persist_messages("@channel", second_batch)

    rows = storage_backend.fetch_messages("@channel")
    assert [row["message_id"] for row in rows] == [1, 2]
    first_row = rows[0]
    assert first_row["channel_id"] == "@channel"
    assert first_row["posted_at"] == "2024-01-02T00:00:00"
    assert first_row["text"] == "updated"
    assert first_row["raw_payload"]["text"] == "updated"


def test_persist_messages_handles_empty_batch(storage_backend):
    storage_backend.persist_messages("@channel", [])
    rows = storage_backend.fetch_messages("@channel")
    assert rows == []


def test_persist_messages_serializes_datetime_payload(storage_backend):
    message = {
        "id": 1,
        "timestamp": "2024-01-03T00:00:00",
        "text": "live message",
        "fetched_at": datetime(2024, 1, 3, 12, 30, tzinfo=timezone.utc),
    }

    storage_backend.persist_messages("@channel", [message])
    rows = storage_backend.fetch_messages("@channel")

    assert rows[0]["raw_payload"]["fetched_at"] == message["fetched_at"].isoformat()


def test_persist_detected_verses_inserts_rows(storage_backend):
    message_payload = {
        "id": 7,
        "timestamp": "2024-04-01T00:00:00",
        "text": "Reference to ayat",
    }

    storage_backend.persist_messages("@analysis", [message_payload])

    inserted = storage_backend.persist_detected_verses(
        [
            {
                "message_id": 7,
                "sura": 1,
                "ayah": 2,
                "confidence": 0.88,
                "is_partial": True,
            }
        ],
        message_ids=[7],
    )
    assert inserted == 1


def test_persist_detected_verses_refreshes_rows(storage_backend):
    payload = {
        "id": 99,
        "timestamp": "2024-04-02T00:00:00",
        "text": "First revision",
    }

    storage_backend.persist_messages("@analysis", [payload])

    # Insert initial verse
    inserted = storage_backend.persist_detected_verses(
        [
            {
                "message_id": 99,
                "sura": 2,
                "ayah": 255,
                "confidence": 1.0,
                "is_partial": False,
            }
        ],
        message_ids=[99],
    )
    assert inserted == 1

    # Refresh with empty list should clear verses for message 99
    cleared = storage_backend.persist_detected_verses(
        [],
        message_ids=[99],
    )
    assert cleared == 0


def test_fetch_messages_filters_by_channel(storage_backend):
    """Test that fetch_messages correctly filters by channel_id."""
    messages_ch1 = [
        {"id": 1, "timestamp": "2024-01-01T10:00:00", "text": "Channel 1 message 1"},
        {"id": 2, "timestamp": "2024-01-01T11:00:00", "text": "Channel 1 message 2"},
    ]
    messages_ch2 = [
        {"id": 1, "timestamp": "2024-01-01T12:00:00", "text": "Channel 2 message 1"},
    ]

    storage_backend.persist_messages("@channel1", messages_ch1)
    storage_backend.persist_messages("@channel2", messages_ch2)

    # Fetch all messages
    all_messages = storage_backend.fetch_messages()
    assert len(all_messages) == 3

    # Fetch channel 1 only
    ch1_messages = storage_backend.fetch_messages("@channel1")
    assert len(ch1_messages) == 2
    assert all(msg["channel_id"] == "@channel1" for msg in ch1_messages)

    # Fetch channel 2 only
    ch2_messages = storage_backend.fetch_messages("@channel2")
    assert len(ch2_messages) == 1
    assert ch2_messages[0]["channel_id"] == "@channel2"
