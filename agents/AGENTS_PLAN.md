Plan For Agents (AI-Agent-as-Service Architecture)
# Planning guidelines for agents using this file
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

- Backend Analytics Service
  Add `fetch_analytics_summary()` method to `storage/backends/peewee/fetch.py` that aggregates data from `StoredMessage`, `Subscription`, and `DetectedVerse` tables. Return counts for active subscriptions, total messages, detected verses, and date ranges matching the structure in `mock_data.get_mock_analytics_summary()`.
  End-to-end test: New fetch method returns accurate analytics data matching current database state when called through storage interface.

- Frontend Analytics Integration
  Update `dashboard/panels/analytics_summary_panel.py` to call real storage backend via `fetch_analytics_summary()` instead of importing from `mock_data`. Replace `get_mock_analytics_summary()` call at line 13 with actual database query through storage interface.
  End-to-end test: Dashboard displays real-time analytics that update when database content changes (verify by adding a message and refreshing dashboard).

- Remove Analytics Mock
  Delete `get_mock_analytics_summary()` function from `dashboard/mock_data.py` (lines 140-148). Verify no remaining imports of this function exist in the codebase.
  End-to-end test: Dashboard still works correctly and `grep -r "get_mock_analytics_summary" osintagency/` returns no results.


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
