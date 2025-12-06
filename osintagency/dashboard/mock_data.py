"""
Mock data for the dashboard UI.

This module centralizes all mock/placeholder data used across dashboard panels.
"""


def get_mock_verses(time_window="All time", filter_text=""):
    """
    Get mock data for the verses table with optional filtering.

    Args:
        time_window: Filter by time range (Last 24h, Last 7d, Last 30d, All time)
        filter_text: Filter by sura or ayah number (partial match)

    Returns:
        List of verse dictionaries matching the filters
    """
    from datetime import datetime, timedelta

    # Base mock data
    all_verses = [
        {
            "sura": 1,
            "ayah": 1,
            "mentions": 42,
            "channels": 8,
            "first_seen": "2025-11-15",
            "last_seen": "2025-11-29"
        },
        {
            "sura": 2,
            "ayah": 255,
            "mentions": 38,
            "channels": 12,
            "first_seen": "2025-11-10",
            "last_seen": "2025-11-30"
        },
        {
            "sura": 3,
            "ayah": 185,
            "mentions": 25,
            "channels": 6,
            "first_seen": "2025-11-20",
            "last_seen": "2025-11-28"
        },
        {
            "sura": 18,
            "ayah": 10,
            "mentions": 19,
            "channels": 5,
            "first_seen": "2025-11-12",
            "last_seen": "2025-11-27"
        },
        {
            "sura": 36,
            "ayah": 82,
            "mentions": 15,
            "channels": 4,
            "first_seen": "2025-11-18",
            "last_seen": "2025-11-25"
        },
    ]

    # Filter by time window
    if time_window != "All time":
        today = datetime(2025, 11, 30)  # Mock "today" for consistent testing

        if time_window == "Last 24h":
            cutoff_date = today - timedelta(days=1)
        elif time_window == "Last 7d":
            cutoff_date = today - timedelta(days=7)
        elif time_window == "Last 30d":
            cutoff_date = today - timedelta(days=30)
        else:
            cutoff_date = datetime.min

        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        all_verses = [
            v for v in all_verses
            if v["last_seen"] >= cutoff_str
        ]

    # Filter by text (search in sura or ayah)
    if filter_text:
        all_verses = [
            v for v in all_verses
            if filter_text in str(v["sura"]) or filter_text in str(v["ayah"])
        ]

    return all_verses


def get_mock_subscriptions():
    """Get mock data for the subscriptions table."""
    return [
        {
            "channel_id": "@example_channel_1",
            "name": "Tech News Daily",
            "active": True,
            "messages_stored": 1523,
            "verses_detected": 42,
            "first_message_date": "2025-10-15",
            "last_message_date": "2025-11-30",
            "last_scrape_at": "2025-11-30 14:35:22"
        },
        {
            "channel_id": "@example_channel_2",
            "name": "Islamic Studies",
            "active": True,
            "messages_stored": 3847,
            "verses_detected": 215,
            "first_message_date": "2025-09-01",
            "last_message_date": "2025-11-29",
            "last_scrape_at": "2025-11-29 22:10:15"
        },
        {
            "channel_id": "@example_channel_3",
            "name": "Community Chat",
            "active": False,
            "messages_stored": 892,
            "verses_detected": 8,
            "first_message_date": "2025-11-10",
            "last_message_date": "2025-11-20",
            "last_scrape_at": "2025-11-20 09:45:00"
        },
        {
            "channel_id": "@example_channel_4",
            "name": "Quran Reflections",
            "active": True,
            "messages_stored": 2156,
            "verses_detected": 387,
            "first_message_date": "2025-08-20",
            "last_message_date": "2025-11-30",
            "last_scrape_at": "2025-11-30 16:20:44"
        },
    ]


def get_mock_forwarded_channels():
    """Get mock data for the forwarded channels table."""
    return [
        {
            "source_channel": "@quran_reflections",
            "times_referenced": 18,
            "first_seen": "2025-11-10",
            "last_seen": "2025-11-29",
            "already_subscribed": False
        },
        {
            "source_channel": "@islamic_wisdom",
            "times_referenced": 12,
            "first_seen": "2025-11-15",
            "last_seen": "2025-11-30",
            "already_subscribed": True
        },
        {
            "source_channel": "@hadith_daily",
            "times_referenced": 9,
            "first_seen": "2025-11-18",
            "last_seen": "2025-11-28",
            "already_subscribed": False
        },
        {
            "source_channel": "@community_news",
            "times_referenced": 7,
            "first_seen": "2025-11-12",
            "last_seen": "2025-11-27",
            "already_subscribed": False
        },
        {
            "source_channel": "@spiritual_quotes",
            "times_referenced": 5,
            "first_seen": "2025-11-20",
            "last_seen": "2025-11-25",
            "already_subscribed": True
        },
    ]
