# Agents System Architecture

## Quick Map

* CLI: `cli/cli.py` defines entry points using Click, parsing options and passing them to command modules in `cli/commands/`. Supports an optional `--days` flag for date-limited message fetching and exposes a `setup` command group (`cli/setup_commands.py`) with `cleanup` for purging the SQLite store and `fetch-channel` for targeted channel collection with a 30-day default window.

* Commands: `cli/commands/check_credentials.py` and `cli/commands/fetch_channel.py` simply forward arguments to the corresponding action modules. The `--days` option is converted into an `offset_date` filter.

* Logging: `logging_config.py` sets up loggers so info messages go to stdout and warnings/errors go to stderr, keeping CLI output structured.

* Actions: `actions/fetch_channel_action.py`, `actions/check_credentials_action.py`, and `actions/cleanup_database_action.py` perform the actual Telegram operations, using helpers from `config.py` and persistence from `storage.py`.

* Collector: `collector.py` implements both test and live Telegram clients, each supporting optional offset_date for bounded message fetching.

* Storage: `osintagency/storage/` provides a modular storage layer. `schema.py` defines Peewee models for the default SQLite backend.

* Enrichment: `enrichment.py` processes stored messages and generates per-channel and keyword summary JSON files.

* Display: `dashboard/` provides a NiceGUI web application for interactive data visualization and channel management.

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
                                           | NiceGUI Web Dashboard       |
                                           +-----------------------------+
```
See `AGENT_SCHEMA_REFERENCE.md` for table definitions and `AGENT_DATA_FLOW.md` for ingestion and enrichment flow. Storage is ephemeral — each run creates a clean SQLite database. No migrations or backward compatibility are required.

## Documentation Decomposition Notice
This document now focuses on the system overview and component responsibilities. When ingestion, enrichment, or schema code changes, update both `AGENTS_SYSTEM_ARCH.md` and the detailed appendices (`AGENT_SCHEMA_REFERENCE.md`, `AGENT_DATA_FLOW.md`) to keep architecture and deep references in sync.

## Web Dashboard
The NiceGUI dashboard (`osintagency/dashboard/`) provides an interactive web interface for visualizing and managing collected data. The dashboard is served via the `osintagency dashboard` CLI command.

Architecture:
- Modular panel-based design with components in `dashboard/panels/`
- Mock data centralized in `dashboard/mock_data.py`
- Main routes defined in `dashboard/app.py` (~60 lines)
- Each panel is self-contained (<100 lines) following Single Responsibility Principle

Current implementation:
- Analytics summary bar (`panels/analytics_summary_panel.py`) - displays key metrics in a grid layout:
  - Total active subscriptions
  - Total messages collected
  - Total detected verses
  - Oldest and newest message dates
  - Uses placeholder/mock data from `mock_data.py`
  - Interactive tooltips on each metric card explaining their meaning
  - Clickable cards that show notifications (future: filter/navigate based on metric)
- Three-panel vertical layout with visually separated sections
- Panel 1: "Top detected verses" (`panels/verses_panel.py`) - displays most frequently mentioned Quran verses with time window filter and search
- Panel 2: "Subscriptions & scraping" (`panels/subscriptions_panel.py`) - manages channel subscriptions with:
  - Global action buttons for bulk re-scraping and full reset
  - Table displaying channel ID, name, active status, messages stored, verses detected, dates, and last scrape timestamp
  - Per-row action buttons for re-scraping, editing, and toggling active status
  - All interactions show mock notifications (no real data operations yet)
- Panel 3: "Forwarded from & discovery" (`panels/forwarded_panel.py`) - displays channels referenced in forwarded messages with:
  - Table showing source channel, times referenced, first seen, last seen
  - Per-row "Add as subscription" button for channels not yet subscribed
  - "Subscribed" label for channels already in the subscription list
  - Add-Channel Card below the table for manual channel subscription with:
    - Telegram link input field (supports t.me/channel, @channel, or plain channel name formats)
    - Real-time parsed channel identifier display
    - Optional display name input
    - "Add subscription" button with deterministic mock responses (checks for already-subscribed channels)
  - All interactions show mock notifications (no real data operations yet)
- Runs on localhost:8080 by default
- Built with NiceGUI framework for reactive UI components

See the step-by-step plan in `AGENTS_PLAN.md` for ongoing dashboard feature development.

## Enrichment Layer
Enrichment runs in `collector.py` during collection, **not** during storage. The "enrich-then-store" pattern ensures consistent enrichment and keeps logic centralized in the collection pipeline. Enrichers run as batch operations between message fetching and persistence.

See [arch/AGENTS_ARCH_ENRICHMENT.md](arch/AGENTS_ARCH_ENRICHMENT.md) for detailed architecture, batch wrapper pattern, and new enricher checklist.

## Storage Interactions
- `osintagency/storage` exposes a facade that delegates to a configured backend (defaulting to `PeeweeStorage` backed by SQLite).
- The storage interface (`StorageBackend`) defines `persist_messages`, `fetch_messages`, and `persist_detected_verses`.
- `PeeweeStorage` (in `osintagency/storage/backends/peewee/`) implements this interface using Peewee and SQLite.
- Each backend lives in its own folder under `backends/` (e.g., `backends/peewee/`) to support multiple backend implementations.
- Data normalization logic lives in `osintagency/storage/normalization.py`, keeping backend implementations focused on database operations.
- The storage layer normalizes detections, wipes stale rows for each processed message id, and bulk inserts replacements within a single transaction.
- New storage backends can be added by creating a new folder under `backends/` and implementing the `StorageBackend` interface without modifying existing code.

## Module Boundaries & Code Standards

### Max Source-File Size
- **Recommended Limit**: ~200 lines or 10KB.
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
