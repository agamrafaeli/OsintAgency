"""
Mock data for the dashboard UI.

This module centralizes all mock/placeholder data used across dashboard panels.
"""


def get_mock_verses():
    """Get mock data for the verses table."""
    return [
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


def get_mock_analytics_summary():
    """Get mock data for the analytics summary bar."""
    return {
        "active_subscriptions": 3,
        "total_messages": 8418,
        "detected_verses": 652,
        "oldest_message_date": "2025-08-20",
        "newest_message_date": "2025-11-30"
    }


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
