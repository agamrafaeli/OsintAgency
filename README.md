# OsintAgency

OsintAgency monitors Telegram channels for mentions of the Quran and summarizes how passages are quoted across the network. The project collects the messages, normalizes the references, and exposes a dashboard that highlights recurring themes and channel-level trends.

## Current Status

The repository is under active build-out. Follow the plans in `agents/AGENTS_PLAN.md` and the coordination notes in `agents/AGENTS_README.MD` if you are contributing.

## Getting Started

1. Copy `.env.example` to `.env` and fill in the Telegram API credentials. Provide either a user session string or a bot token along with the target channel identifier.
2. Create a virtual environment and install dependencies: `python -m venv .venv && source .venv/bin/activate && pip install -e .`.
3. Validate the environment with `osintagency check-credentials --generate-session`; this confirms the configured channel, ensures the database path is writable, and can optionally sign in once to print a `TELEGRAM_SESSION_STRING`.
4. Manage channel subscriptions with the `subscribe` command suite:
   ```bash
   # Add a channel to the subscription directory
   osintagency subscribe add --channel-id @example_channel --name "Example Channel"

   # List all tracked channels (pass --format json for machine-readable output)
   osintagency subscribe list

   # Update saved metadata when a channel needs a new display name
   osintagency subscribe update --channel-id @example_channel --name "New Name"

   # Remove the subscription once monitoring is complete
   osintagency subscribe remove --channel-id @example_channel

   # Fetch a small batch from every active subscription
   osintagency subscribe fetch --limit 5

   # Fetch a larger batch but only from the last week of activity
   osintagency subscribe fetch --limit 100 --days 7
   ```
5. Prototype channel backfills with targeted fetch commands before touching production data:
   ```bash
   # Fetch the most recent five posts from the default channel using live credentials
   osintagency fetch-channel --limit 5

   # Emit a deterministic dataset by using the stub collector
   osintagency fetch-channel --limit 5 --use-stub

   # Backfill a specific channel for the prior week without affecting other data
   osintagency setup fetch-channel @example_channel --days 7

   # Bulk collect all active subscriptions with a date window cap
   osintagency setup fetch-all --limit 50 --days 30

   # Reset the message store when you need a clean slate
   osintagency setup cleanup
   ```

## Data Storage

- Raw Telegram posts are written via the Peewee ORM to a SQLite database at `data/messages.sqlite3` by default.
- Override the location by setting the `OSINTAGENCY_DB_PATH` environment variable before invoking any fetch commands.
- Re-running the fetcher upserts messages keyed by channel and Telegram id, so only new posts increase the stored row count.
- Helper utilities in `osintagency.storage` expose the ORM models so tests and analytics code can query the stored messages without reaching into SQLite directly.

## Verse Enrichment

- `osintagency.services.quran_detector.detect_verses` inspects verbatim Arabic text and identifies quoted Quran verses using the bundled matcher (`qMatcherAnnotater`), returning dictionaries containing `message_id`, `sura`, `ayah`, `confidence`, and `is_partial`.
- The matcher removes tashkeel, normalizes alternate Arabic forms, and aligns the detected verse names with canonical sura/ayah metadata from `dfiles/quran-index.xml` so the enrichment layer can attribute each quote precisely.
- The returned dictionaries can be bulk inserted directly into the `DetectedVerse` table, enabling downstream tensor analysis without needing to recompute the parsing step.
- `collect_messages` executes the detector before calling `storage.persist_messages`, then hands the normalized rows to `storage.persist_detected_verses`, which refreshes each message's `DetectedVerse` entries as an independent atomic action (paving the way for future standalone enrichment jobs).
