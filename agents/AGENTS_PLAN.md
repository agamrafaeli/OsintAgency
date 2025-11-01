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

### Data Layer: Foundations (ROADMAP_ANALYSIS_PIPELINE.md Part 1)

- Document Ephemeral Database
  Add section to `AGENTS_SYSTEM_ARCH.md` explaining that storage assumes ephemeral mode with fresh database initialization on each run. This design choice means no migration infrastructure is needed, as schema changes apply to a clean slate.
  End-to-end test: None (documentation-only step).

- Extend Schema Verses
  Add nullable `detected_verse_id` TEXT field to `StoredMessage` model in `schema.py` for linking messages to Sura:Ayah pairs. Since database operates in ephemeral mode, simply extend the model definition without migration logic.
  End-to-end test: Run fresh initialization, insert message with `detected_verse_id="2:255"`, retrieve it, verify field persists correctly.

- Build Verse Enrichment
  Implement enrichment module that extracts Quranic verse references from message text using Sura:Ayah pattern matching. This fulfills the enrichment phase architecture described in `AGENTS_SYSTEM_ARCH.md`, preparing messages for five-axis tensor analysis.
  End-to-end test: Pass message containing Quranic verse to enrichment function, verify it returns correct verse mappings, store enriched message, confirm field persists.

- Wire Enrichment Pipeline
  Integrate verse detection into the message storage flow so `detected_verse_id` populates automatically during ingestion. Update `storage.py` and collector to call enrichment before persisting messages.
  End-to-end test: Fetch channel message containing verse reference, verify `detected_verse_id` is automatically populated in database without manual intervention.

- Add Semantic Ideals Field
  Introduce `semantic_ideals` JSON array field to track tagged ideals per verse citation within each message. This enables the "Ideal" dimension of the verse×ideal×channel×time×sentiment tensor.
  End-to-end test: Store a message with `semantic_ideals` containing `["justice", "mercy"]`, fetch it, and confirm JSON parsing returns the correct array.


## Documentation Update Process

When a step is completed:

- **Update README.md**:   
   - Changes to main features
   - Add any specific workflows that are main enough
- **Update AGENTS_XXX.md**:
   - Update `AGENTS_SYSTEM_ARCH.md` if the step is big enough. If you decide not to update it, verify this with a human and explain your decision.
- **Confirm with a human** before removing a completed step from this file (agents/AGENTS_PLAN.md); removal is a human-only decision. Once confirmed, **remove the completed step** and, if it was the last step to be removed, write a <PLACEHOLDER> for future writings to this file of new plans.
- **Reorder remaining steps** as needed to keep the plan coherent.

This keeps documentation in sync with actual implementation progress.
