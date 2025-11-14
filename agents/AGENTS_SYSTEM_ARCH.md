# Agents System Architecture

## Quick Map

* CLI: `cli/cli.py` defines entry points using Click, parsing options and passing them to command modules in `cli/commands/`. Supports an optional `--days` flag for date-limited message fetching and exposes a `setup` command group (`cli/setup_commands.py`) with `cleanup` for purging the SQLite store and `fetch-channel` for targeted channel collection with a 30-day default window.

* Commands: `cli/commands/check_credentials.py` and `cli/commands/fetch_channel.py` simply forward arguments to the corresponding action modules. The `--days` option is converted into an `offset_date` filter.

* Logging: `logging_config.py` sets up loggers so info messages go to stdout and warnings/errors go to stderr, keeping CLI output structured.

* Actions: `actions/fetch_channel_action.py`, `actions/check_credentials_action.py`, and `actions/cleanup_database_action.py` perform the actual Telegram operations, using helpers from `config.py` and persistence from `storage.py`.

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
See `AGENT_SCHEMA_REFERENCE.md` for table definitions and `AGENT_DATA_FLOW.md` for ingestion and enrichment flow. Storage is ephemeral — each run creates a clean SQLite database. No migrations or backward compatibility are required.

## Documentation Decomposition Notice
This document now focuses on the system overview and component responsibilities. When ingestion, enrichment, or schema code changes, update both `AGENTS_SYSTEM_ARCH.md` and the detailed appendices (`AGENT_SCHEMA_REFERENCE.md`, `AGENT_DATA_FLOW.md`) to keep architecture and deep references in sync.

## Enrichment Layer
- Enrichment primarily lives in `osintagency/services/quran_detector.py`, which normalizes Quranic references and emits structured data destined for `DetectedVerse`.
- `detect_verses` now runs the bundled `qMatcherAnnotater` to find verbatim Quran text (after stripping tashkeel and normalizing variant Arabic forms) and returns dictionaries containing (`message_id`, `sura`, `ayah`, `confidence`, `is_partial`) so enrichment callers can bulk insert into the database without replicating parsing logic.
- The detector depends on its own `dfiles/` data bundle and matching routines, so aligning ingestion hooks with that module keeps the verse-detection logic centralized.

## Storage Interactions
- `osintagency/storage.py` wires the detector output into Peewee so each stored message includes both its raw payload and the derived `DetectedVerse` rows needed for downstream tensor analysis.
- Keep this document updated when ingestion hooks or schema changes (e.g., `semantic_ideals`) touch the enrichment/storage boundary to maintain architectural clarity.
