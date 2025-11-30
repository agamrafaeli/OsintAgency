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

Here's a step plan in your AGENTS style for building a **mock NiceGUI dashboard UI** (no real data, just structure and placeholders) that includes all the components we discussed. All steps below refer to the dashboard UI implementation.


* **Dashboard UI: Verses Panel Interactions**
  In the Top Detected Verses panel, wire the time window dropdown and filter input to callbacks that log selections and update the table with filtered mock data. Ensure the table displays placeholder verse data and handles empty filter results gracefully.
  End-to-end test: Changing the time window dropdown and entering filter text updates the verses table with appropriate mock data and shows notifications for user actions.

* **Dashboard UI: Subscriptions Panel Interactions**
  In the Subscriptions & Scraping panel, wire the "Re-scrape all" and "Full reset" buttons plus all per-row actions (Re-scrape, Edit, Activate/Deactivate) to callbacks that log actions and show notifications. Ensure the table displays mock subscription data and all buttons provide user feedback.
  End-to-end test: Clicking any button in the Subscriptions panel (global or per-row) triggers appropriate notifications and updates UI state without exceptions.

* **Dashboard UI: Forwarded Channels Interactions**
  In the Forwarded Channels table within the Forwarded from & Discovery panel, wire the per-row "Add as subscription" buttons to callbacks that log actions, show notifications, and toggle button state to "Subscribed" label. Display mock forwarded channel data in the table.
  End-to-end test: Clicking "Add as subscription" on any forwarded channel row shows a notification and changes the button to a "Subscribed" label without exceptions.

* **Dashboard UI: Add Channel Interactions**
  In the Add Channel card, wire the Telegram link input to parse and display the channel name reactively, and wire the "Add subscription" button to validate input, log the action, show notifications for success/error cases (duplicate, invalid format, empty), and reset the form on success.
  End-to-end test: Entering various Telegram links (valid, invalid, duplicate, empty) and clicking "Add subscription" produces appropriate validation messages and notifications without exceptions.



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
