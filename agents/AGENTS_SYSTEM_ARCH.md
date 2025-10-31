# Agents System Architecture

## Quick Map

* CLI: `cli/cli.py` defines entry points using Click, parsing options and passing them to command modules in `cli/commands/`. Supports an optional `--days` flag for date-limited message fetching.

* Commands: `cli/commands/check_credentials.py` and `cli/commands/fetch_channel.py` simply forward arguments to the corresponding action modules. The `--days` option is converted into an `offset_date` filter.

* Logging: `logging_config.py` sets up loggers so info messages go to stdout and warnings/errors go to stderr, keeping CLI output structured.

* Actions: `actions/fetch_channel_action.py` and `actions/check_credentials_action.py` perform the actual Telegram operations, using helpers from `config.py` and persistence from `storage.py`.

* Collector: `collector.py` implements both test and live Telegram clients, each supporting optional offset_date for bounded message fetching.

* Storage: `schema.py` defines Peewee models that store messages in SQLite, keyed by channel and message ID to prevent duplicates.

* Enrichment: `enrichment.py` processes stored messages and generates per-channel and keyword summary JSON files.

* Display: `dashboard/` contains static files that visualize the latest summary with counts, highlights, and visibility.

## Storage and Display Flow
```
      +--------------+      +------------------+      +---------------------------+
      | Telegram API | ---> | Fetcher Commands  | ---> | Peewee ORM (SQLite store) |
      +--------------+      +------------------+      +---------------------------+
                                      |                        |
                                      v                        v
                         +------------------+      +---------------------+
                         | Summary Routine  | ---> | JSON Snapshot Files |
                         +------------------+      +---------------------+
                                                          |
                                                          v
                                           +-----------------------------+
                                           | Static Metrics Dashboard UI |
                                           +-----------------------------+
```
Posts flow from the Telegram API into the fetcher commands, which upsert them into the Peewee-managed SQLite store keyed by channel and message identifiers.
The summarization routine runs after ingestion to scan stored posts, calculate aggregates, and emit a JSON snapshot ready for display.
The dashboard loads the latest JSON snapshot on page render, so UI refreshes stay decoupled from data collection schedules.

Raw messages are written into a `messages` table inside a lightweight SQLite database, with columns for `message_id`, `channel_id`, `posted_at`, `text`, and an optional `raw_payload` blob; a unique constraint on (`channel_id`, `message_id`) ensures duplicate fetches only update timestamp and text fields when the source edits a post.

The enrichment phase runs as a batch job right after fresh rows land, pulling unsummarized entries from the `messages` table and normalizing their text with channel-aware tokenization.
It extracts Quran references and tracked keywords into structured columns such as `quran_refs`, `keywords_found`, and `entities`, while stamping provenance fields like `analysis_version` and `processed_at` for repeatable reprocessing.
Channel-level rollups are written into an intermediate `message_metrics` table keyed by `(channel_id, analysis_window)` so downstream consumers derive aggregates without re-querying the raw feed or the Telegram API.

The display layer is a static web view that pulls the freshest view, and remains decoupled from database access or long-running jobs. Applied on top of the enriched data. It pulls a fully enriched view of the latest snapshot before rendering. It displays the combined metrics without reaching back to the database.

### Raw message schema
| column name | type | notes |
| --- | --- | --- |
| --- Direct Fetch Fields ---
| `channel_id` | TEXT | Source channel identifier; part of composite key |
| `message_id` | INTEGER | Telegram message id; part of composite key |
| `posted_at` | TIMESTAMP | Original message timestamp |
| `text` | TEXT | Normalized message body |
| `raw_payload` | BLOB | Optional JSON blob for replay |
|
| --- Calculated enrichment columns ---
| `quran_refs` | JSON | Array of referenced surah:ayah pairs extracted by parser |
| `keywords_found` | JSON | Ordered list of matched keywords |
| `entities` | JSON | Named entities (people, places) recognized from message |
| `analysis_version` | TEXT | Semantic version of enrichment pipeline |
| `processed_at` | TIMESTAMP | When the message was last enriched |

### Subscriptions table (implemented)
| column name | type | notes |
| --- | --- | --- |
| `channel_id` | TEXT | Primary key; Telegram channel identifier |
| `name` | TEXT | Human-readable channel name (nullable) |
| `added_at` | TEXT | ISO timestamp when subscription was created |
| `active` | BOOLEAN | Whether to fetch from this channel (default: true) |
| `metadata` | JSON | Optional metadata for categorization and filtering |

This table tracks which channels are monitored. Functions in `osintagency/subscription_config.py` manage this table with upsert logic for adding, filtering by active status, updating properties, and removing subscriptions.

### Channel directory table (planned for enrichment phase)
| column name | type | notes |
| --- | --- | --- |
| `channel_id` | TEXT | Primary key matching `messages.channel_id` |
| `name` | TEXT | Human-readable channel name |
| `type` | TEXT | Telegram type (public, private, supergroup) |
| `language` | TEXT | ISO language code if available |
| `metadata` | JSON | Arbitrary channel metadata captured at fetch time |
| --- Calculated enrichment columns --- | | |
| `daily_post_rate` | REAL | Rolling seven-day average of posts per day for trending indicators |
| `last_post_at` | TIMESTAMP | Timestamp of the most recent ingested message for the channel |
| `quran_reference_share` | REAL | Percentage of recent posts containing at least one Quran reference |

### Quran reference table
| column name | type | notes |
| --- | --- | --- |
| `message_id` | INTEGER | Foreign key to `messages.message_id` |
| `channel_id` | TEXT | Foreign key to `messages.channel_id` |
| `surah` | INTEGER | Chapter number |
| `ayah` | INTEGER | Verse number |
| `confidence` | REAL | Parser confidence score for the extraction |
