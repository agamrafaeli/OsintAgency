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
- Each sub-step should have a clear defined test that is added
- When developing use TDD, meaning write a test, make sure it fails, then add code and make sure the tests pass.
- Test file names must NOT contain "step" references (e.g., avoid `test_step_01_foo.py`). Tests should be named descriptively based on what they test, agnostic of when they were written or which plan step they fulfill.


## Current Steps to run

- Stabilize Data Hygiene
  Add configuration plumbing so the collector honors the `OSINTAGENCY_DB_PATH` when building isolated databases per run. Replace live Telegram calls with a deterministic ~50 LOC stub that exercises ingestion and cleanup flows.
  End-to-end test: Running the full flow for one channel and five messages creates the expected database in the configured path, deleting it leaves no residual database.

- Compute Aggregate Summaries
  Implement a lightweight analysis routine that reads stored posts and tallies counts by channel and keyword. Expose the summary as a JSON artifact consumable by downstream interfaces.
  End-to-end test: Running `python scripts/summarize_posts.py` produces aggregate counts for sample data.

- Render Metric Dashboard
  Build a static dashboard that surfaces total posts and top Quran references from the generated JSON summary. Ensure the view remains lightweight and only depends on the summary artifact for data.
  End-to-end test: Serving the dashboard locally displays counts matching the JSON summary.


## Documentation Update Process

When a step is completed:

- **Update README.md**:   
   - Changes to main features
   - Add any specific workflows that are main enough
- **Confirm with a human** before removing a completed step from this file (agents/AGENTS_PLAN.md); removal is a human-only decision. Once confirmed, **remove the completed step** and, if it was the last step to be removed, write a <PLACEHOLDER> for future writings to this file of new plans.
- **Reorder remaining steps** as needed to keep the plan coherent.

This keeps documentation in sync with actual implementation progress.
