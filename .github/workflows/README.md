# Research Workflows — Execution Lifecycle

`.github/workflows/` contains CI, structural checks and historical/live research execution wrappers.

**Workflow presence is not authorization.** Current authorization comes from the relevant frozen gate/manifest/authorization and `docs/CURRENT-PROJECT-STATUS.md`; the allowed immediate sequence is maintained in `docs/NEXT-STEPS.md`.

This README intentionally does **not** restate the current gate.

## Lifecycle rules

- retain consumed/failed workflows when they are needed for provenance or reproducibility;
- do not rerun a one-shot/consumed workflow merely because the YAML remains present;
- prefer a new versioned workflow/authorization when a prospectively allowed material execution changes;
- pin source/runtime contracts where the frozen protocol requires it;
- separate provider-free checks from live provider execution;
- separate scientific gates when the governing authorization separates them;
- never expose provider/evaluator/blind secrets or hidden outcomes through cleanup/logging changes;
- a workflow that executes multiple scientific gates must not be used if the current authorization permits only an earlier subset.

## Historical one-shot safety

Historical one-shot/live workflows may remain in the tree when required for provenance. Their presence does not re-open consumed authorizations.

If a historical workflow is unsafe to leave triggerable, disable it prospectively while preserving the source/run provenance rather than rewriting the historical record of what executed.

## Cleanup rule

Do not bulk-delete historical workflow YAML solely because it is no longer active. First prove it is not referenced by a frozen manifest/result, Actions provenance record, ADR or reproducibility path.

Use `docs/REPOSITORY-GUIDE.md` for the full safe-cleanup and source-of-truth rules.
