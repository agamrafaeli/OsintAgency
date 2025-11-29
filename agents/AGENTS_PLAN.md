Plan For Agents (AI-Agent-as-Service Architecture)
# Planning guidelines for agents using this file
- Before planning, make sure there exists a `AGENTS_SYSTEM_ARCH.md` file. If not, create it.
- Step scope should be not super technical, but include references to "parts" of the system
- Before performing a step assess whether it fits into the format of:
```
- <STEP_NAME_IN_THREE_WORDS>
  <STEP_DESCRIPTION_IN_TWO_SENTENCES>
  End-to-end test: <STEP_END_TO_END_TEST>
```
- It is allowed for steps to not have tests if they are documentation-only steps.
If not, then offer your best understanding of what the step should be. And iterate with human until the step is clear.

# Execution guidelines for agents reading from this file
When planning / executing a step from this plan:
- If a test is not well defined (step name in three words + descritpion in two sentences + test if needed) then first re-word it in `AGENTS_PLAN.md` and only then proceed.
- Generally when interacting with tests follow the guidance of `AGENTS_TESTING.md`
- When developing use TDD, meaning write a test, make sure it fails, then add code and make sure the tests pass.
- Test file names must NOT contain "step" references (e.g., avoid `test_step_01_foo.py`). Tests should be named descriptively based on what they test, agnostic of when they were written or which plan step they fulfill.
- Unless specifically asked, only do one step at a time. 

## Planned Steps


- Add Batch Wrapper
  Create `_detect_forwards_for_messages(messages)` batch wrapper in `collector.py` following the batch wrapper pattern documented in `agents/arch/AGENTS_ARCH_ENRICHMENT.md`. Process all messages and return structured forward references.
  End-to-end test: Batch wrapper processes multiple messages and returns aggregated forward detections.

- Extend Storage Schema
  Add `ForwardedFrom` table in Peewee schema with fields: `message_id` (FK), `source_channel_id`, `detected_at`. Implement `persist_forwarded_channels()` in storage backend.
  End-to-end test: Storage backend persists forward references to new table correctly.

- Wire into Collection
  Add forward detection call in `collect_messages()` after verse detection. Call `_detect_forwards_for_messages()` then `persist_forwarded_channels()` following the enrichment pattern documented in `agents/arch/AGENTS_ARCH_ENRICHMENT.md`.
  End-to-end test: Collect messages with forwards and verify both messages and forward references are persisted.

- Query Channels-to-Review
  Add `fetch_forwarded_channels()` method to storage interface returning aggregated channel references sorted by frequency. Implement in PeeweeStorage.
  End-to-end test: Query returns proper channel list with reference counts.

- Expose via CLI
  Create `list_suspect_channels_action.py` and add CLI command to display discovered channels from forward references.
  End-to-end test: CLI command returns formatted channel list from stored forward data.


## Documentation Update Process

When a step is completed:

- **Update README.md**:
   - Changes to main features
   - Add any specific workflows that are main enough

- **Update Architecture Docs**:
   - `AGENTS_SYSTEM_ARCH.md` should remain concise (under 100 lines) as a high-level overview
   - For detailed documentation, create focused files in `agents/arch/AGENTS_ARCH_<TOPIC>.md` (also under 100 lines each)
   - Update `AGENTS_SYSTEM_ARCH.md` with a brief summary and reference to the detailed doc
   - Topics should be "philosophical" rather than overly practical (avoid extensive code examples)
   - Follow the pattern established by `agents/arch/AGENTS_ARCH_ENRICHMENT.md`

- **Confirm with a human** before removing a completed step from this file (agents/AGENTS_PLAN.md); removal is a human-only decision. Once confirmed, **remove the completed step** and, if it was the last step to be removed, write a <PLACEHOLDER> for future writings to this file of new plans.

- **Reorder remaining steps** as needed to keep the plan coherent.

This keeps documentation in sync with actual implementation progress.
