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

Here's a step plan in your AGENTS style for building a **mock NiceGUI dashboard UI** (no real data, just structure and placeholders) that includes all the components we discussed. All steps below refer to the dashboard UI implementation.

* **Dashboard UI: Analytics Summary**
  In the dashboard, above or below the subscriptions table, add a small summary bar with labels and dummy values for total active subscriptions, total messages, total detected verses, oldest message date, and newest message date. Use simple labels and numbers to simulate aggregated analytics.
  End-to-end test: The summary bar appears consistently and shows placeholder numbers even when tables are empty or reduced to a single row.

* **Dashboard UI: Forwarded Discovery**
  In the dashboard's "Forwarded from & discovery" panel, add a table titled "Forwarded channels (by frequency)" with placeholder rows and columns for source channel, times referenced, first seen, last seen, and already subscribed. Include per-row buttons like "Add as subscription" or a static "Subscribed" label.
  End-to-end test: The table renders with mock data and clicking "Add as subscription" triggers a mock confirmation or toast without errors.

* **Dashboard UI: Add-Channel Card**
  In the dashboard, next to or below the forwarded table, add a card allowing the user to paste a Telegram link, show a parsed-channel placeholder, and optionally enter a display name. Add an "Add subscription" button and show a mock message if the "channel" already exists or is newly "added".
  End-to-end test: Pasting any string into the input and clicking "Add subscription" shows a deterministic mock response (e.g., "Pretending to add @example_channel") without crashing the app.

* **Dashboard UI: Mock Interactions**
  In the dashboard, wire all buttons and toggles across all panels to simple callbacks that log actions and show small notifications, without touching any database or external services. Ensure error handling is graceful so even invalid input just produces friendly mock messages.
  End-to-end test: A manual click-through of every button, toggle, and input across the dashboard completes without any exceptions and surfaces user-facing notifications for each action.



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
