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

Detected Quranic references and other enrichments now live in dedicated tables to keep the core message row lean. Legacy per-message enrichment columns such as `quran_refs` and `analysis_version` have been removed.

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

## Detected Verses Table (`detected_verses`)

The `detected_verses` table stores normalized Quran references extracted during enrichment with confidence scoring for downstream filtering. Verse rows link back to messages using the shared `message_id` value, matching the ingestion schema.

| column name | type | notes |
| --- | --- | --- |
| `id` | INTEGER | Primary key |
| `message_id` | INTEGER | References `messages.message_id` |
| `surah` | INTEGER | Chapter number |
| `ayah` | INTEGER | Verse number |
| `confidence` | REAL | Parser confidence score for the extraction |
| `is_partial` | BOOLEAN | True when the parser detected an incomplete verse span |

`DetectedVerse` rows are created via Peewee joins against `StoredMessage` (matching on `message_id`) during enrichment or bespoke analytics queries. Channel identifiers remain on the `messages` table, so queries that need them should join against `StoredMessage` as demonstrated in `tests/test_storage.py`.
