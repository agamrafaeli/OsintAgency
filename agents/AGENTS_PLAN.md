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

1. Prime Architecture Boilerplate
Add an interaction-friendly scaffold to `agents/AGENTS_SYSTEM_ARCH.md` that mirrors the spirit of the plan file but in a lightweight way. Include a short checklist for recording current understanding, open questions, and next refinement steps.
End-to-end test: N/A

2. Flesh Architecture Notes
Expand `agents/AGENTS_SYSTEM_ARCH.md` with the current components, data flows, and integration points so contributors can see how the agents fit into the platform. Include any open questions or assumptions that still need validation.
End-to-end test: N/A


## Documentation Update Process

When a step is completed:

1. **Confirm with a human** before removing a completed step from this file (agents/AGENTS_PLAN.md); removal is a human-only decision. Once confirmed, **remove the completed step** and, if it was the last step to be removed, write a <PLACEHOLDER> for future writings to this file of new plans.
2. **Renumber remaining steps** sequentially (Step N becomes Step N-1)
3. **Update docs/05-implementation-guide.md**:
   - Update the **Status** line to reflect current completion state
   - Add any new CLI commands or usage examples
4. **Update README.md**:   
   - Changes to main features
   - Add any specific workflows that are main enough
5. **Update docs/01-executive-summary.md** if architecture changed
6. **Update docs/02-technical-agents.md** if new agents were added

This keeps documentation in sync with actual implementation progress.
