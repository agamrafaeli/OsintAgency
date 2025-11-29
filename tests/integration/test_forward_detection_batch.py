"""Integration tests for batch forward detection in collector."""

import pytest
from datetime import datetime, timezone
from osintagency.collector import _detect_forwards_for_messages


def test_batch_wrapper_processes_multiple_messages_with_forwards():
    """Test that batch wrapper processes multiple messages and aggregates forward detections."""
    messages = [
        {
            "id": 100,
            "text": "First message",
            "fwd_from": {
                "from_id": {
                    "_": "PeerChannel",
                    "channel_id": 12345
                },
                "channel_post": 999
            }
        },
        {
            "id": 200,
            "text": "Second message",
            "fwd_from": {
                "from_id": {
                    "_": "PeerChannel",
                    "channel_id": 67890
                },
                "channel_post": 888
            }
        }
    ]

    result = _detect_forwards_for_messages(messages)

    assert len(result) == 2
    assert result[0]["message_id"] == 100
    assert result[0]["source_channel_id"] == 12345
    assert result[0]["source_message_id"] == 999
    assert result[1]["message_id"] == 200
    assert result[1]["source_channel_id"] == 67890
    assert result[1]["source_message_id"] == 888


def test_batch_wrapper_handles_messages_without_forwards():
    """Test that batch wrapper returns empty list for messages without forwards."""
    messages = [
        {
            "id": 100,
            "text": "Regular message"
        },
        {
            "id": 200,
            "text": "Another regular message"
        }
    ]

    result = _detect_forwards_for_messages(messages)

    assert result == []


def test_batch_wrapper_handles_mixed_messages():
    """Test that batch wrapper handles mix of forwarded and non-forwarded messages."""
    messages = [
        {
            "id": 100,
            "text": "Regular message"
        },
        {
            "id": 200,
            "text": "Forwarded message",
            "fwd_from": {
                "from_id": {
                    "_": "PeerChannel",
                    "channel_id": 12345
                },
                "channel_post": 999
            }
        },
        {
            "id": 300,
            "text": "Another regular message"
        }
    ]

    result = _detect_forwards_for_messages(messages)

    assert len(result) == 1
    assert result[0]["message_id"] == 200
    assert result[0]["source_channel_id"] == 12345


def test_batch_wrapper_handles_user_forwards():
    """Test that batch wrapper filters out user forwards (only keeps channel forwards)."""
    messages = [
        {
            "id": 100,
            "text": "User forward",
            "fwd_from": {
                "from_id": {
                    "_": "PeerUser",
                    "user_id": 12345
                }
            }
        },
        {
            "id": 200,
            "text": "Channel forward",
            "fwd_from": {
                "from_id": {
                    "_": "PeerChannel",
                    "channel_id": 67890
                },
                "channel_post": 888
            }
        }
    ]

    result = _detect_forwards_for_messages(messages)

    assert len(result) == 1
    assert result[0]["message_id"] == 200
    assert result[0]["source_channel_id"] == 67890


def test_batch_wrapper_handles_malformed_payloads():
    """Test that batch wrapper continues processing despite malformed payloads."""
    messages = [
        {
            "id": 100,
            "text": "Good message",
            "fwd_from": {
                "from_id": {
                    "_": "PeerChannel",
                    "channel_id": 12345
                },
                "channel_post": 999
            }
        },
        {
            "id": 200,
            "fwd_from": {
                "from_id": {
                    "_": "PeerChannel"
                    # Missing channel_id - malformed
                }
            }
        },
        {
            "id": 300,
            "text": "Another good message",
            "fwd_from": {
                "from_id": {
                    "_": "PeerChannel",
                    "channel_id": 67890
                },
                "channel_post": 888
            }
        }
    ]

    result = _detect_forwards_for_messages(messages)

    # Should get 2 results, skipping the malformed one
    assert len(result) == 2
    assert result[0]["message_id"] == 100
    assert result[1]["message_id"] == 300


def test_batch_wrapper_handles_missing_message_id():
    """Test that batch wrapper skips messages without ID."""
    messages = [
        {
            "text": "Message without ID",
            "fwd_from": {
                "from_id": {
                    "_": "PeerChannel",
                    "channel_id": 12345
                },
                "channel_post": 999
            }
        },
        {
            "id": 200,
            "text": "Message with ID",
            "fwd_from": {
                "from_id": {
                    "_": "PeerChannel",
                    "channel_id": 67890
                },
                "channel_post": 888
            }
        }
    ]

    result = _detect_forwards_for_messages(messages)

    assert len(result) == 1
    assert result[0]["message_id"] == 200


def test_batch_wrapper_returns_correct_structure():
    """Test that batch wrapper returns correctly structured forward detections."""
    messages = [
        {
            "id": 100,
            "text": "Forwarded message",
            "fwd_from": {
                "from_id": {
                    "_": "PeerChannel",
                    "channel_id": 12345
                },
                "channel_post": 999
            }
        }
    ]

    result = _detect_forwards_for_messages(messages)

    assert len(result) == 1
    detection = result[0]

    # Verify structure matches what forward_detector.detect_forwards() returns
    assert "message_id" in detection
    assert "source_channel_id" in detection
    assert "source_message_id" in detection
    assert "detected_at" in detection

    # Verify detected_at is an ISO 8601 string (not a datetime object)
    assert isinstance(detection["detected_at"], str)
    # Verify it can be parsed as a valid ISO datetime
    datetime.fromisoformat(detection["detected_at"])
