# Agents Coding Notes

Quick reference for how automation agents should interact with the **OsintAgency** repository.

## Purpose

- Describe the guardrails for AI and human collaborators touching the repo.
- Point to `agents/arch/AGENTS_SYSTEM_ARCH.md` for architecture context once it is filled in.

## Core Files

- `agents/plans/AGENTS_PLAN.md`: Source of truth for the next tasks. Always read it before modifying code.
- `agents/arch/AGENTS_SYSTEM_ARCH.md`: Architecture sketch; update it when components or data flows change.
- `agents/guides/AGENTS_TESTING.md`: Instructions for how to interact with tests in this repo
- `README.md`: External-facing description of the project. Refresh it after major user-facing updates.

## Workflow Rules

1. **Read the plan first.** Confirm the current step, clarify it if ambiguous, update the plan as progress is made, and advance the step’s deliverable before proposing new tasks.
2. **Work in TDD loops.** Write or adjust tests, watch them fail, implement changes, then rerun tests until they pass.
3. **Respect existing changes.** Never discard user edits that were already present; integrate with them instead.
4. **Document after code.** Update this README, the plan, architecture notes, and top-level docs as required by each step.

## Editing Guidelines

- Never perform git commands without approval from user.
- Use `rg` for searches; avoid slow alternatives unless unavailable.
- Keep comments purposeful—only add them when they clarify non-obvious logic.
- Inside the project there are `AGENTS_XXX.md` files. They are your instructions for editing in that folder and recursively underneath it.

## When Work Completes

1. Remove finished steps from `agents/plans/AGENTS_PLAN.md` and renumber the remainder.
2. Update documentation listed in the plan’s “Documentation Update Process” section (create missing files if needed).
3. Announce remaining TODOs or follow-up items in your final response so humans can pick up quickly, and record any scope clarifications so the next contributor inherits the context.

## Troubleshooting

- Missing tests? Write new descriptive test files; do not include step numbers in filenames.
- Unsure about architecture? Add a placeholder note in `agents/arch/AGENTS_SYSTEM_ARCH.md`, ensure a scaffold exists when Step 1 is active, and flag it in your summary.
- Sandbox errors? Explain the limitation in your summary and suggest manual follow-up steps.
