# coding: utf-8
# -*- coding: utf8 -*-

"""
Forward metadata detection service for Telegram messages.

This module provides functionality to detect and extract forward metadata
from Telegram messages, specifically identifying when messages are forwarded
from other channels.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class DetectedForward:
    """Structured representation of a detected forward reference."""

    message_id: int
    source_channel_id: int | None
    source_message_id: int | None
    detected_at: str  # ISO 8601 timestamp

    def as_row(self) -> dict[str, object]:
        return {
            "message_id": self.message_id,
            "source_channel_id": self.source_channel_id,
            "source_message_id": self.source_message_id,
            "detected_at": self.detected_at,
        }


def detect_forwards(
    message_id: int | str, raw_payload: str | dict | None
) -> list[dict[str, object]]:
    """
    Extract forward metadata from a Telegram message payload.

    This function analyzes the raw_payload to determine if a message was
    forwarded from a channel. It only detects channel forwards (not user-to-user
    forwards) and extracts the source channel ID and original message ID.

    Args:
        message_id: The ID of the message being analyzed
        raw_payload: The raw Telegram message payload (as JSON string or dict)

    Returns:
        A list containing zero or one forward detection record. Returns:
        - Empty list if no forward metadata is present
        - Empty list if forwarded from a user (not a channel)
        - List with one dict containing forward metadata if forwarded from a channel

    Example:
        >>> payload = {
        ...     "id": 12347,
        ...     "fwd_from": {
        ...         "from_id": {"_": "PeerChannel", "channel_id": 1005381772},
        ...         "channel_post": 61664
        ...     }
        ... }
        >>> detect_forwards(12347, payload)
        [{'message_id': 12347, 'source_channel_id': 1005381772, ...}]
    """
    # Normalize message_id to int
    try:
        normalized_message_id = int(message_id)
    except (TypeError, ValueError):
        # Invalid message_id - return empty
        return []

    # Parse raw_payload if it's a JSON string
    payload_dict = _parse_payload(raw_payload)
    if payload_dict is None:
        return []

    # Extract fwd_from field
    fwd_from = payload_dict.get("fwd_from")
    if fwd_from is None:
        # No forward metadata
        return []

    # Check if forwarded from a channel (not a user)
    from_id = fwd_from.get("from_id")
    if from_id is None:
        return []

    # Only process channel forwards
    if from_id.get("_") != "PeerChannel":
        # Forwarded from user or other non-channel source
        return []

    # Extract channel ID and original message ID
    source_channel_id = from_id.get("channel_id")
    if source_channel_id is None:
        return []

    # channel_post contains the original message ID in the source channel
    source_message_id = fwd_from.get("channel_post")

    # Generate detection timestamp
    detected_at = datetime.now(timezone.utc).isoformat()

    # Create detection record
    detection = DetectedForward(
        message_id=normalized_message_id,
        source_channel_id=source_channel_id,
        source_message_id=source_message_id,
        detected_at=detected_at,
    )

    return [detection.as_row()]


def _parse_payload(raw_payload: str | dict | None) -> dict | None:
    """
    Parse raw_payload into a dictionary.

    Args:
        raw_payload: Either a JSON string or already-parsed dict

    Returns:
        Parsed dictionary or None if parsing fails
    """
    if raw_payload is None:
        return None

    if isinstance(raw_payload, dict):
        return raw_payload

    if isinstance(raw_payload, str):
        try:
            return json.loads(raw_payload)
        except (json.JSONDecodeError, ValueError):
            return None

    # Unexpected type
    return None
