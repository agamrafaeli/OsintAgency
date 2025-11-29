import json
from datetime import datetime

from osintagency.services import forward_detector


def test_detect_forwards_returns_empty_when_no_forward():
    """Test that messages without fwd_from return empty list."""
    payload = {
        "id": 12345,
        "message": "Regular message without forwarding",
        "fwd_from": None,
    }
    detected = forward_detector.detect_forwards(message_id=12345, raw_payload=payload)
    assert detected == []


def test_detect_forwards_returns_empty_for_user_forward():
    """Test that forwards from users (not channels) are ignored."""
    payload = {
        "id": 12346,
        "message": "Forwarded from a user",
        "fwd_from": {
            "_": "MessageFwdHeader",
            "from_id": {
                "_": "PeerUser",
                "user_id": 987654321
            },
            "date": "2025-11-29T10:00:00+00:00"
        }
    }
    detected = forward_detector.detect_forwards(message_id=12346, raw_payload=payload)
    assert detected == []


def test_detect_forwards_finds_channel_forward():
    """Test that forwards from channels are correctly detected."""
    payload = {
        "id": 12347,
        "message": "Forwarded from a channel",
        "fwd_from": {
            "_": "MessageFwdHeader",
            "from_id": {
                "_": "PeerChannel",
                "channel_id": 1005381772
            },
            "channel_post": 61664,
            "date": "2025-11-29T10:00:00+00:00"
        }
    }
    detected = forward_detector.detect_forwards(message_id=12347, raw_payload=payload)

    assert len(detected) == 1
    forward = detected[0]
    assert forward["message_id"] == 12347
    assert forward["source_channel_id"] == 1005381772
    assert forward["source_message_id"] == 61664
    assert "detected_at" in forward
    # Verify it's a valid ISO timestamp
    datetime.fromisoformat(forward["detected_at"].replace("Z", "+00:00"))


def test_detect_forwards_handles_json_string_payload():
    """Test that raw_payload can be provided as a JSON string."""
    payload_dict = {
        "id": 12348,
        "message": "Test message",
        "fwd_from": {
            "_": "MessageFwdHeader",
            "from_id": {
                "_": "PeerChannel",
                "channel_id": 2000000000
            },
            "channel_post": 100,
            "date": "2025-11-29T11:00:00+00:00"
        }
    }
    payload_str = json.dumps(payload_dict)

    detected = forward_detector.detect_forwards(message_id=12348, raw_payload=payload_str)

    assert len(detected) == 1
    assert detected[0]["source_channel_id"] == 2000000000
    assert detected[0]["source_message_id"] == 100


def test_detect_forwards_handles_malformed_payload():
    """Test that malformed payloads are handled gracefully."""
    # Invalid JSON string
    detected = forward_detector.detect_forwards(message_id=12349, raw_payload="{invalid json")
    assert detected == []

    # None payload
    detected = forward_detector.detect_forwards(message_id=12350, raw_payload=None)
    assert detected == []

    # Empty dict
    detected = forward_detector.detect_forwards(message_id=12351, raw_payload={})
    assert detected == []


def test_detect_forwards_handles_missing_channel_post():
    """Test forwards from channels without channel_post field."""
    payload = {
        "id": 12352,
        "fwd_from": {
            "_": "MessageFwdHeader",
            "from_id": {
                "_": "PeerChannel",
                "channel_id": 1005381772
            },
            # No channel_post field
            "date": "2025-11-29T10:00:00+00:00"
        }
    }
    detected = forward_detector.detect_forwards(message_id=12352, raw_payload=payload)
    # Should still detect the channel, but with None for source_message_id
    assert len(detected) == 1
    assert detected[0]["source_channel_id"] == 1005381772
    assert detected[0]["source_message_id"] is None
