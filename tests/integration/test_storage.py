from datetime import datetime, timezone

import pytest

from osintagency.storage.backends.peewee import PeeweeStorage


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


def test_persist_forwarded_channels_inserts_rows(storage_backend):
    """Test that persist_forwarded_channels creates and populates ForwardedFrom table."""
    message_payload = {
        "id": 42,
        "timestamp": "2024-05-01T00:00:00",
        "text": "Forwarded message",
    }

    storage_backend.persist_messages("@channel", [message_payload])

    inserted = storage_backend.persist_forwarded_channels(
        [
            {
                "message_id": 42,
                "source_channel_id": 1005381772,
                "source_message_id": 61664,
                "detected_at": "2024-05-01T12:00:00+00:00",
            }
        ],
        message_ids=[42],
    )
    assert inserted == 1


def test_persist_forwarded_channels_refreshes_rows(storage_backend):
    """Test that persist_forwarded_channels deletes old rows before inserting new ones."""
    payload = {
        "id": 100,
        "timestamp": "2024-05-02T00:00:00",
        "text": "First version",
    }

    storage_backend.persist_messages("@analysis", [payload])

    # Insert initial forward reference
    inserted = storage_backend.persist_forwarded_channels(
        [
            {
                "message_id": 100,
                "source_channel_id": 123456,
                "source_message_id": 999,
                "detected_at": "2024-05-02T10:00:00+00:00",
            }
        ],
        message_ids=[100],
    )
    assert inserted == 1

    # Refresh with empty list should clear forwards for message 100
    cleared = storage_backend.persist_forwarded_channels(
        [],
        message_ids=[100],
    )
    assert cleared == 0


def test_persist_forwarded_channels_handles_empty_batch(storage_backend):
    """Test that persist_forwarded_channels handles empty input gracefully."""
    inserted = storage_backend.persist_forwarded_channels([], message_ids=None)
    assert inserted == 0


def test_fetch_forwarded_channels_returns_aggregated_list(storage_backend):
    """Test that fetch_forwarded_channels returns proper channel list with reference counts."""
    # Create messages
    messages = [
        {"id": 1, "timestamp": "2024-05-01T00:00:00", "text": "Message 1"},
        {"id": 2, "timestamp": "2024-05-01T01:00:00", "text": "Message 2"},
        {"id": 3, "timestamp": "2024-05-01T02:00:00", "text": "Message 3"},
        {"id": 4, "timestamp": "2024-05-01T03:00:00", "text": "Message 4"},
        {"id": 5, "timestamp": "2024-05-01T04:00:00", "text": "Message 5"},
    ]
    storage_backend.persist_messages("@channel", messages)

    # Insert forward references - channel 123 appears 3 times, channel 456 appears 2 times
    forwards = [
        {
            "message_id": 1,
            "source_channel_id": 123,
            "source_message_id": 100,
            "detected_at": "2024-05-01T12:00:00+00:00",
        },
        {
            "message_id": 2,
            "source_channel_id": 123,
            "source_message_id": 101,
            "detected_at": "2024-05-01T12:01:00+00:00",
        },
        {
            "message_id": 3,
            "source_channel_id": 456,
            "source_message_id": 200,
            "detected_at": "2024-05-01T12:02:00+00:00",
        },
        {
            "message_id": 4,
            "source_channel_id": 123,
            "source_message_id": 102,
            "detected_at": "2024-05-01T12:03:00+00:00",
        },
        {
            "message_id": 5,
            "source_channel_id": 456,
            "source_message_id": 201,
            "detected_at": "2024-05-01T12:04:00+00:00",
        },
    ]
    storage_backend.persist_forwarded_channels(
        forwards, message_ids=[1, 2, 3, 4, 5]
    )

    # Fetch aggregated channel list
    result = storage_backend.fetch_forwarded_channels()

    # Should return channels sorted by frequency (descending)
    assert len(result) == 2
    assert result[0]["source_channel_id"] == 123
    assert result[0]["reference_count"] == 3
    assert result[1]["source_channel_id"] == 456
    assert result[1]["reference_count"] == 2


def test_fetch_forwarded_channels_handles_empty_table(storage_backend):
    """Test that fetch_forwarded_channels returns empty list when no forwards exist."""
    result = storage_backend.fetch_forwarded_channels()
    assert result == []


def test_fetch_forwarded_channels_filters_null_channels(storage_backend):
    """Test that fetch_forwarded_channels excludes NULL source_channel_id entries."""
    messages = [
        {"id": 1, "timestamp": "2024-05-01T00:00:00", "text": "Message 1"},
        {"id": 2, "timestamp": "2024-05-01T01:00:00", "text": "Message 2"},
    ]
    storage_backend.persist_messages("@channel", messages)

    # Insert forwards with one NULL source_channel_id
    forwards = [
        {
            "message_id": 1,
            "source_channel_id": None,  # NULL channel
            "source_message_id": 100,
            "detected_at": "2024-05-01T12:00:00+00:00",
        },
        {
            "message_id": 2,
            "source_channel_id": 789,
            "source_message_id": 200,
            "detected_at": "2024-05-01T12:01:00+00:00",
        },
    ]
    storage_backend.persist_forwarded_channels(forwards, message_ids=[1, 2])

    result = storage_backend.fetch_forwarded_channels()

    # Should only return the non-NULL channel
    assert len(result) == 1
    assert result[0]["source_channel_id"] == 789
    assert result[0]["reference_count"] == 1


def test_fetch_analytics_summary_returns_aggregated_stats(storage_backend):
    """Test that fetch_analytics_summary returns accurate analytics data from database."""
    from osintagency.schema import Subscription, database_proxy
    from osintagency.storage.backends.peewee import operations

    # Get database connection for direct Subscription manipulation
    database = operations.get_database(storage_backend.db_path)
    database_proxy.initialize(database)

    try:
        # Create subscriptions (3 active, 1 inactive)
        with database.atomic():
            database.create_tables([Subscription], safe=True)
            Subscription.insert_many(
                [
                    {
                        "channel_id": "@channel1",
                        "name": "Channel 1",
                        "added_at": "2024-01-01T00:00:00+00:00",
                        "active": True,
                    },
                    {
                        "channel_id": "@channel2",
                        "name": "Channel 2",
                        "added_at": "2024-01-02T00:00:00+00:00",
                        "active": True,
                    },
                    {
                        "channel_id": "@channel3",
                        "name": "Channel 3",
                        "added_at": "2024-01-03T00:00:00+00:00",
                        "active": False,
                    },
                    {
                        "channel_id": "@channel4",
                        "name": "Channel 4",
                        "added_at": "2024-01-04T00:00:00+00:00",
                        "active": True,
                    },
                ]
            ).execute()

        # Create messages with different dates
        messages = [
            {
                "id": 1,
                "timestamp": "2024-01-15T10:00:00",
                "text": "Oldest message",
            },
            {
                "id": 2,
                "timestamp": "2024-02-20T15:30:00",
                "text": "Middle message",
            },
            {
                "id": 3,
                "timestamp": "2024-03-25T20:45:00",
                "text": "Newest message",
            },
        ]
        storage_backend.persist_messages("@channel1", messages)

        # Add more messages to different channels
        storage_backend.persist_messages(
            "@channel2",
            [
                {"id": 10, "timestamp": "2024-02-10T12:00:00", "text": "Message 10"},
                {"id": 11, "timestamp": "2024-02-11T13:00:00", "text": "Message 11"},
            ],
        )

        # Create detected verses
        storage_backend.persist_detected_verses(
            [
                {
                    "message_id": 1,
                    "sura": 1,
                    "ayah": 1,
                    "confidence": 0.95,
                    "is_partial": False,
                },
                {
                    "message_id": 2,
                    "sura": 2,
                    "ayah": 255,
                    "confidence": 0.88,
                    "is_partial": True,
                },
                {
                    "message_id": 3,
                    "sura": 36,
                    "ayah": 82,
                    "confidence": 0.92,
                    "is_partial": False,
                },
                {
                    "message_id": 10,
                    "sura": 18,
                    "ayah": 10,
                    "confidence": 0.90,
                    "is_partial": False,
                },
            ],
            message_ids=[1, 2, 3, 10],
        )

        # Fetch analytics summary
        result = storage_backend.fetch_analytics_summary()

        # Verify results
        assert result["active_subscriptions"] == 3  # 3 active subscriptions
        assert result["total_messages"] == 5  # 5 total messages
        assert result["detected_verses"] == 4  # 4 detected verses
        assert result["oldest_message_date"] == "2024-01-15T10:00:00"
        assert result["newest_message_date"] == "2024-03-25T20:45:00"

    finally:
        database.close()


def test_fetch_analytics_summary_handles_empty_database(storage_backend):
    """Test that fetch_analytics_summary handles empty database gracefully."""
    result = storage_backend.fetch_analytics_summary()

    # Should return zeros and None for dates when database is empty
    assert result["active_subscriptions"] == 0
    assert result["total_messages"] == 0
    assert result["detected_verses"] == 0
    assert result["oldest_message_date"] is None
    assert result["newest_message_date"] is None
