# Agent Data Flow

Detailed view of how data moves from Telegram collection through enrichment into dashboard-ready material.

## End-to-End Flow
```
      +--------------+      +------------------+      +---------------------------+
      | Telegram API | ---> | Fetcher Commands | ---> | Peewee ORM (SQLite store) |
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

Posts flow from the Telegram API into Click-driven fetcher commands, which pass arguments to action modules that upsert rows through Peewee models. Ingestion enforces a composite key of (`channel_id`, `message_id`) so repeat fetches update stored content without generating duplicates.

The summarization routine runs immediately after new rows land in SQLite. It scans the `messages` table, calculates aggregates, and emits JSON snapshots that downstream consumers can load without database access. During enrichment the pipeline normalizes text, extracts Quran references, keywords, and entities, stamps provenance fields, and writes channel-level rollups into a `message_metrics` table keyed by (`channel_id`, `analysis_window`).

Finally, the dashboard layer reads the freshest JSON snapshot at render time. By depending only on static assets, dashboard refreshes remain decoupled from data collection schedules while still reflecting the latest enriched metrics.
