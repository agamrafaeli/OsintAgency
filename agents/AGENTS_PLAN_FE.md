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

- Repo Structure Prep
  Analyze repo structure and update documentation to reflect the new frontend initiative. This prepares the codebase for the new component.
  End-to-end test: Check `README.md` for frontend section.

- Frontend Stack Selection
  Create architecture documentation and select a lightweight tech stack with user input. This defines the technical foundation.
  End-to-end test: Verify `agents/AGENTS_FRONTEND_ARCH.md` exists.

- Design System Definition
  Define and document the visual language and design system. This ensures a consistent premium aesthetic.
  End-to-end test: Verify `agents/AGENTS_FRONTEND_DESIGN.md` exists.

- Initialize Frontend App
  Scaffold the application and set up basic tooling. This creates the starting point for development.
  End-to-end test: Verify frontend build script runs.

- Create API Server
  Implement a server to expose data and CLI actions. This connects the frontend to the backend logic.
  End-to-end test: Verify API responds to health check.

- Implement App Layout
  Build the main application shell with navigation. This establishes the user interface structure.
  End-to-end test: Verify main layout renders in browser.

- Develop Channels View
  Implement the list view for monitored channels. This provides visibility into system targets.
  End-to-end test: Verify channels list loads data.

- Develop Verses Dashboard
  Create the dashboard for displaying detected verses. This visualizes the primary output.
  End-to-end test: Verify verses appear on dashboard.


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
