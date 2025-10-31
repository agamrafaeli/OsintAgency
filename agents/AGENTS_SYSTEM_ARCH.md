# Agents System Architecture

## Quick Map
- **Data Schema**: Posts from telegram channels (text content, image, timestamp, user_id, channel_id)
- **Data Acquisition**: `scripts/fetch_channel.py` streams raw posts (id, timestamp, text) for a configured channel using Telegram API credentials loaded from `.env`.
- **UI**: Lightweight open source
