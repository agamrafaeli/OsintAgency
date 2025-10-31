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

- Add ability so that commands can be run using osintagency instead of `python -m ....`

- Add ability to fetch large amounts (100k and up) of messages. First brainstorm approaches on how to do this, only then do it.

- Add "setup" action: cleanup DB, fetch channel ID from last month

- Compute Aggregate Summaries
  Implement a lightweight analysis routine that reads stored posts and tallies counts by channel and keyword. Expose the summary as a JSON artifact consumable by downstream interfaces.
  End-to-end test: Running ClI command that performs just the analysis routine on the existing data produces aggregate counts for sample data.

- Render Metric Dashboard
  Build a static dashboard that surfaces total posts and top Quran references from the generated JSON summary. Ensure the view remains lightweight and only depends on the summary artifact for data.
  End-to-end test: Serving the dashboard locally displays counts matching the JSON summary.


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
