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

- Stage Interface Runner
  Extract a base collector interface from `osintagency/collector.py`, add a CLI stage runner that can invoke a named stage, and document the lifecycle hooks so future stages reuse it consistently. This scaffolding keeps the pipeline extensible while letting us invoke fetch or detect individually without importing storage directly.
  End-to-end test: Run `pytest tests/test_stage_runner.py` to confirm the CLI runner loads a dummy stage implementation, executes it, and reports artifacts through the storage adapter.

- Fetch Stage Module
  Refactor the existing fetch logic into a stage module that inherits from the base interface, registers itself, and exposes a CLI command such as `osintagency collect fetch`. Provide a lightweight adapter so the stage writes fetched data without circular dependencies.
  End-to-end test: Run `pytest tests/test_stage_fetch_cli.py` to ensure the CLI fetch stage can be triggered, performs its fetch, and stores artifacts through the adapter.

- Detect Stage Module
  Turn the verse-detection logic into its own stage module tied to the base interface, reuse the CLI scaffolding, and maintain compatibility with the storage adapter so it loads data from fetch artifacts and emits detected verses.
  End-to-end test: Run `pytest tests/test_stage_detect_cli.py` to assert the CLI detect stage runs independently and produces verse detections stored via the adapter.

- Stage Registry & Storage Adapter
  Introduce a registry that tracks available stages, honors configuration toggles for enabling/disabling each stage, and injects the storage adapter when wiring the CLI runner to avoid circular imports. Document how new stages can register themselves and how the registry consults configuration.
  End-to-end test: Run `pytest tests/test_stage_registry_storage.py` to verify that enabling/disabling each stage via configuration controls which stages the registry executes and that those stages persist their expected artifacts.

- Pipeline Composite CLI
  Build a CLI command that walks the registry, runs all enabled stages (fetch → detect) in order, and streams their outputs through the shared storage adapter, proving the composed flow works while still allowing single-stage CLI runs.
  End-to-end test: Run `pytest tests/test_pipeline_cli.py` to execute the full configured pipeline and confirm the final artifacts appear in storage, ensuring fetch results feed into detect.


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
