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
- `collector.collect_messages` orchestrates enrichment up front: every fetch batch is routed through `detect_verses`, and the resulting rows are passed into `storage.persist_messages`, which atomically refreshes the associated `DetectedVerse` entries before inserting the new detections.
- `collector.collect_messages` orchestrates enrichment up front: every fetch batch is routed through `detect_verses`, and the resulting rows are persisted via `storage.persist_detected_verses` after the messages themselves are stored, so enrichment can eventually run as a dedicated workload without touching the ingestion core.
- The detector depends on its own `dfiles/` data bundle and matching routines, so aligning ingestion hooks with that module keeps the verse-detection logic centralized.

## Storage Interactions
- `osintagency/storage.py` wires the detector output into Peewee so each stored message includes both its raw payload and the derived `DetectedVerse` rows needed for downstream tensor analysis.
- The storage layer now exposes `persist_detected_verses`, which normalizes detections, wipes stale rows for each processed message id, and bulk inserts replacements within a single transaction, allowing other enrichers to reuse the same code path.
- Keep this document updated when ingestion hooks or schema changes (e.g., `semantic_ideals`) touch the enrichment/storage boundary to maintain architectural clarity.

## Module Boundaries & Code Standards

### Max Source-File Size
- **Recommended Limit**: ~300 lines or 15KB.
- **Goal**: Maintain readability and ease of review.
- **Restructuring Heuristics**:
    - If a file exceeds this limit, consider splitting it into smaller, more focused modules.
    - If a module has too many imports, it might be doing too much and violating the Single Responsibility Principle.

### Module Scopes
- **Single Responsibility**: Each module should have one clear purpose.
- **Major Classes**: Prefer one major class per file. Helper classes that are tightly coupled can stay, but if they grow, move them.
- **Utilities**: Group related utility functions into dedicated modules (e.g., `utils/date_utils.py`, `utils/string_utils.py`).

### Tests & Fixtures
- **Structure**: Tests should generally mirror the structure of the code they test.
- **Fixtures**:
    - Scope fixtures to the tests that use them.
    - Use `conftest.py` levels (root, package, directory) wisely to avoid pollution.
    - Avoid "god-fixtures" that set up the entire world; prefer composable, smaller fixtures.
