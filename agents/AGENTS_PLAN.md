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

- Wire Enrichment Pipeline
  Integrate verse detection into the message storage flow so `DetectedVerse` rows are created automatically during ingestion. Update `storage.py` and the collector to call enrichment before persisting messages.
  End-to-end test: Fetch channel message containing a verse reference, verify linked `DetectedVerse` rows are automatically written without manual intervention.

- Add Semantic Ideals Field
  Introduce a `semantic_ideals` JSON array field on `DetectedVerse` to track tagged ideals per verse citation within each message. This enables the "Ideal" dimension of the verse×ideal×channel×time×sentiment tensor by attaching ideals to the normalized verse rows.
  End-to-end test: Store a message whose detected verses each carry `semantic_ideals` such as `["justice", "mercy"]`, fetch linked verse records, and confirm JSON parsing returns the correct arrays.


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
