# Enrichment Architecture

## Core Principle
Enrichment runs in [collector.py](../osintagency/collector.py) during collection, **not** during storage. This "enrich-then-store" pattern ensures all messages are enriched consistently and keeps enrichment logic centralized in the collection pipeline.

## Pipeline Position
Enrichers execute between message fetching and persistence:
1. Fetch messages from Telegram API
2. **Run batch enrichment** via wrapper functions
3. Persist messages to storage
4. Persist enrichment results to separate tables

The enrichment step at [collector.py:183](../osintagency/collector.py#L183) happens before any database writes.

## Batch Wrapper Pattern
Each enricher follows a consistent pattern (see [collector.py:141-157](../osintagency/collector.py#L141-L157)):
- Function name: `_detect_<feature>_for_messages(messages)`
- Input: List of message dictionaries from API
- Output: List of enrichment result dictionaries
- Error handling: Skip individual failures, continue batch processing
- Aggregation: Return all results as a single list

## Current Enrichers
**Verse Detection** ([quran_detector.py](../osintagency/services/quran_detector.py)):
- Service: `detect_verses(message_id, text) -> list[dict]`
- Wrapper: `_detect_verses_for_messages(messages)` at [collector.py:141](../osintagency/collector.py#L141)
- Persistence: `persist_detected_verses(detected_verses, message_ids, db_path)`

## New Enricher Checklist
1. **Create service module** in `osintagency/services/`:
   - Implement `detect_<feature>(message_id, raw_payload) -> list[dict]`
   - Return structured dicts with `message_id` and feature fields

2. **Add batch wrapper** in `collector.py`:
   - Function: `_detect_<feature>_for_messages(messages: List[dict]) -> list[dict]`
   - Loop messages, call service, aggregate results

3. **Extend storage schema** in `osintagency/storage/schema.py`:
   - Add Peewee model with `message_id` foreign key

4. **Implement persistence** in storage backend:
   - Add `persist_<feature>()` to `StorageBackend` interface
   - Implement in `PeeweeStorage` (delete stale rows, bulk insert)

5. **Wire into collection** in `collector.collect_messages()`:
   - Call wrapper after fetch
   - Call persistence after message storage

6. **Add tests**:
   - Unit test service with sample payloads
   - Test batch wrapper with multiple messages
   - Test persistence and retrieval

## Data Flow
```
Telegram API → fetch_messages() → [Batch] → _detect_<feature>_for_messages()
                                               ↓ (calls service)
                                    detect_<feature>(message_id, payload)
                                               ↓
[Messages] + [Enrichment Results] → persist_messages() + persist_<feature>()
                                               ↓
                               [Message Table] + [Feature Table]
```
