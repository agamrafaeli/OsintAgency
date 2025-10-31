# OsintAgency

OsintAgency monitors Telegram channels for mentions of the Quran and summarizes how passages are quoted across the network. The project collects the messages, normalizes the references, and exposes a dashboard that highlights recurring themes and channel-level trends.

## Current Status

The repository is under active build-out. Follow the plans in `agents/AGENTS_PLAN.md` and the coordination notes in `agents/AGENTS_README.MD` if you are contributing.

## Getting Started

1. Copy `.env.example` to `.env` and fill in the Telegram API credentials. Provide either a user session string or a bot token along with the target channel identifier.
2. Create a virtual environment and install dependencies: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
3. Validate the environment with `python -m scripts.check_credentials --generate-session`; this signs in once, prints a `TELEGRAM_SESSION_STRING`, and verifies the configured channel.
4. Prototype data collection via `python -m scripts.fetch_channel --limit 5` to stream the most recent posts to stdout.
