Plan For Agents (AI-Agent-as-Service Architecture)
# Planning guidelines for agents using this file
- Before planning, make sure there exists a `AGENTS_SYSTEM_ARCH.md` file. If not, create it.
- Step scope should be not super technical, but include references to "parts" of the system
- Before performing a step assess whether it fits into the format of:
```
<STEP_NUMBER>. <STEP_NAME_IN_THREE_WORDS>
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

- Store Raw Messages
Persist the fetched posts into a lightweight local store such as SQLite with a schema matching the architecture doc. Re-run the fetcher to upsert posts and confirm duplicates are skipped.
End-to-end test: Invoking the fetcher twice leaves the stored message count unchanged except for new posts.

- Compute Aggregate Summaries
Add a tiny analysis routine that reads the stored posts and calculates counts by channel and keyword references. Emit the results as a JSON blob the UI can consume.
End-to-end test: Running `python scripts/summarize_posts.py` outputs aggregate counts for sample data.

- Render Metric Dashboard
Build a bare-bones view that surfaces the aggregate metrics, focusing on total posts and top Quran references. Keep it static and depend only on the generated JSON summary.
End-to-end test: Serving the dashboard locally shows counts that match the JSON summary.


## Documentation Update Process

When a step is completed:

1. **Confirm with a human** before removing a completed step from this file (agents/AGENTS_PLAN.md); removal is a human-only decision. Once confirmed, **remove the completed step** and, if it was the last step to be removed, write a <PLACEHOLDER> for future writings to this file of new plans.
2. **Renumber remaining steps** sequentially (Step N becomes Step N-1)
3. **Update README.md**:   
   - Changes to main features
   - Add any specific workflows that are main enough

This keeps documentation in sync with actual implementation progress.
