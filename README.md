# OsintAgency

OsintAgency monitors Telegram channels for mentions of the Quran and summarizes how passages are quoted across the network. The project collects the messages, normalizes the references, and exposes a dashboard that highlights recurring themes and channel-level trends.

## Current Status

The repository is under active build-out. Follow the plans in `agents/AGENTS_PLAN.md` and the coordination notes in `agents/AGENTS_README.MD` if you are contributing.

## Getting Started

1. Copy `.env.example` to `.env` and fill in the Telegram API credentials. Provide either a user session string or a bot token along with the target channel identifier.
2. Create a virtual environment and install dependencies: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
3. Validate the environment with `python -m scripts.check_credentials --generate-session`; this confirms the configured channel, ensures the database path is writable, and can optionally sign in once to print a `TELEGRAM_SESSION_STRING`.
4. Prototype data collection via `python -m scripts.fetch_channel --limit 5` to emit a deterministic batch of stubbed posts and persist them for later analysis. Add `--cleanup` to delete the generated SQLite database when you are done.

## Data Storage

- Raw Telegram posts are written via the Peewee ORM to a SQLite database at `data/messages.sqlite3` by default.
- Override the location by setting the `OSINTAGENCY_DB_PATH` environment variable before invoking any fetch commands.
- Re-running the fetcher upserts messages keyed by channel and Telegram id, so only new posts increase the stored row count.
- Helper utilities in `osintagency.storage` expose the ORM models so tests and analytics code can query the stored messages without reaching into SQLite directly.
