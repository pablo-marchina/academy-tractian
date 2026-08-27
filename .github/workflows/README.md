# Research Workflows — Execution Lifecycle

`.github/workflows/` contains CI, structural checks and historical/live research execution wrappers.

**Workflow presence is not authorization.** Current authorization comes from the relevant frozen gate/manifest/authorization and `docs/CURRENT-PROJECT-STATUS.md`.

## Lifecycle rules

- retain consumed/failed workflows when they are needed for provenance or reproducibility;
- do not rerun a one-shot/consumed workflow merely because the YAML remains present;
- prefer a new versioned workflow/authorization when a prospectively allowed material execution changes;
- pin source/runtime contracts where the frozen protocol requires it;
- separate provider-free checks from live provider execution;
- never expose provider/evaluator/blind secrets or hidden outcomes through cleanup/logging changes;
- a workflow that executes multiple scientific gates must not be used if the current authorization permits only an earlier subset.

## Current C4 boundary

The current packet is `FROZEN_COMPLETE_C4_PACKET` and the current gate is `DETERMINISTIC_SCORING`.

No additional C4 provider generation is authorized. Bootstrap, LOGO, slices, semantic evaluation, FRESH_BLIND and LEGACY_LOCKED_TEST must remain inaccessible until their own gate transitions permit them.

## Cleanup rule

Do not bulk-delete historical workflow YAML solely because it is no longer active. First prove it is not referenced by a frozen manifest/result, Actions provenance record, ADR or reproducibility path. If a workflow is dangerous to leave triggerable, disable it prospectively while retaining the historical source/provenance rather than rewriting the record of what ran.
