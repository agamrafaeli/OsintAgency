# OsintAgency

OsintAgency monitors Telegram channels for mentions of the Quran and summarizes how passages are quoted across the network. The project collects the messages, normalizes the references, and exposes a dashboard that highlights recurring themes and channel-level trends.

## Current Status

The repository is under active build-out. Follow the plans in `agents/AGENTS_PLAN.md` and the coordination notes in `agents/AGENTS_README.MD` if you are contributing.

## Getting Started

1. Copy `.env.example` to `.env` and fill in the Telegram API credentials. Provide either a user session string or a bot token along with the target channel identifier.
2. Create a virtual environment and install dependencies: `python -m venv .venv && source .venv/bin/activate && pip install -e .`.
3. Validate the environment with `osintagency check-credentials --generate-session`; this confirms the configured channel, ensures the database path is writable, and can optionally sign in once to print a `TELEGRAM_SESSION_STRING`.
4. Manage channel subscriptions:
   - Add: `osintagency subscribe add --channel-id @example_channel --name "Example Channel"`
   - List: `osintagency subscribe list` (use `--format json` for JSON output)
   - Update: `osintagency subscribe update --channel-id @example_channel --name "New Name"`
   - Remove: `osintagency subscribe remove --channel-id @example_channel`
   - Fetch all: `osintagency subscribe fetch --limit 5` to fetch messages from all active subscribed channels
   - Fetch with date filtering: `osintagency subscribe fetch --limit 100 --days 7` to fetch only messages from the last 7 days
5. Prototype data collection from a single channel via `osintagency fetch-channel --limit 5` to pull the latest posts into the local store. Add `--use-stub` to emit a deterministic batch when validating persistence. Reset the message store anytime with `osintagency setup cleanup`.

## Data Storage

- Raw Telegram posts are written via the Peewee ORM to a SQLite database at `data/messages.sqlite3` by default.
- Override the location by setting the `OSINTAGENCY_DB_PATH` environment variable before invoking any fetch commands.
- Re-running the fetcher upserts messages keyed by channel and Telegram id, so only new posts increase the stored row count.
- Helper utilities in `osintagency.storage` expose the ORM models so tests and analytics code can query the stored messages without reaching into SQLite directly.
