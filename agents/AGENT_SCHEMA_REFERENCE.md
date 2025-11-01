# Agent Schema Reference

Detailed reference for the Peewee-backed SQLite schema that supports the agent ingestion and enrichment pipeline.

## Messages Table

Raw Telegram posts are normalized into the `messages` table backed by SQLite. A composite unique constraint on (`channel_id`, `message_id`) prevents duplicate rows while allowing updates when Telegram edits a message.

| column name | type | notes |
| --- | --- | --- |
| --- Direct Fetch Fields --- | | |
| `channel_id` | TEXT | Source channel identifier; part of composite key |
| `message_id` | INTEGER | Telegram message id; part of composite key |
| `posted_at` | TIMESTAMP | Original message timestamp |
| `text` | TEXT | Normalized message body |
| `raw_payload` | BLOB | Optional JSON blob for replay |
|  |  |  |
| --- Calculated enrichment columns --- | | |
| `quran_refs` | JSON | Array of referenced surah:ayah pairs extracted by parser |
| `keywords_found` | JSON | Ordered list of matched keywords |
| `entities` | JSON | Named entities (people, places) recognized from message |
| `analysis_version` | TEXT | Semantic version of enrichment pipeline |
| `processed_at` | TIMESTAMP | When the message was last enriched |

Channel-level rollups are written into an intermediate `message_metrics` table keyed by (`channel_id`, `analysis_window`). It stores pre-aggregated counts and trend indicators so downstream consumers do not need to scan the raw feed or re-query Telegram.

## Subscriptions Table (implemented)

Tracks which channels should be fetched. Helper functions in `osintagency/subscription_config.py` upsert rows, toggle active status, and remove subscriptions.

| column name | type | notes |
| --- | --- | --- |
| `channel_id` | TEXT | Primary key; Telegram channel identifier |
| `name` | TEXT | Human-readable channel name (nullable) |
| `added_at` | TEXT | ISO timestamp when subscription was created |
| `active` | BOOLEAN | Whether to fetch from this channel (default: true) |
| `metadata` | JSON | Optional metadata for categorization and filtering |

## Channel Directory Table (planned for enrichment phase)

Captures descriptive metadata and derived metrics for each channel once the enrichment phase begins populating it.

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

## Quran Reference Table

Stores normalized Quran references extracted during enrichment with confidence scoring for downstream filtering.

| column name | type | notes |
| --- | --- | --- |
| `message_id` | INTEGER | Foreign key to `messages.message_id` |
| `channel_id` | TEXT | Foreign key to `messages.channel_id` |
| `surah` | INTEGER | Chapter number |
| `ayah` | INTEGER | Verse number |
| `confidence` | REAL | Parser confidence score for the extraction |
