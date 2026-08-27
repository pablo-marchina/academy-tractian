# Research Scripts — Lifecycle and Safety Guide

`scripts/research/` contains executable research, evaluation, validation and evidence-generation code accumulated across multiple experimental generations.

The existence of a script does **not** mean it is currently authorized to run.

## Before executing a script

1. read `docs/CURRENT-PROJECT-STATUS.md` and identify the current authorized gate;
2. read `docs/NEXT-STEPS.md` for the allowed short-horizon execution sequence;
3. locate the frozen manifest/result/authorization governing that execution;
4. verify any required source Git blob/path pins;
5. verify allowed data/evaluator/provider access boundaries;
6. run provider-free/structural checks first where the protocol requires them;
7. stop if the script would cross into a later gate.

This README intentionally does **not** restate the current gate.

## Lifecycle

Scripts may be:

- `ACTIVE` — required by the current authorized gate;
- `FROZEN_SOURCE` — source-pinned implementation used by a frozen experiment;
- `HISTORICAL` — older implementation retained for reproducibility;
- `CONSUMED_PATH` — tied to an experiment/authorization that cannot be rerun;
- `SUPERSEDED` — replaced for future work but still retained as evidence.

Do not delete or rename `FROZEN_SOURCE`, `CONSUMED_PATH` or otherwise source-pinned scripts unless a reference audit proves the path is no longer required.

## Change policy

A material semantic change requires a new version/candidate and applicable preregistration/evaluation. Do not silently change a historical source-pinned implementation in place.

Infrastructure-only fixes must remain distinguishable from candidate/semantic changes and must not be used to reinterpret an already consumed scientific attempt.

## Gate isolation

Research executables should be isolated by scientific gate whenever practical.

A historical runner/scorer that combines multiple stages may remain frozen for provenance, but it must not be executed wholesale when the current authorization permits only an earlier subset. Create a new gate-specific runner that reuses the exact frozen semantics without crossing later boundaries.

Examples of boundaries that should remain separable include:

- provider generation;
- local candidate transformation;
- deterministic private scoring;
- bootstrap/statistical analysis;
- LOGO/slices;
- semantic evaluation;
- independent/blind measurement.

## Production code

Research runners are not automatically production code. Validated behavior may later be translated into a distinct production implementation only after the applicable production-fit comparison and architecture-freeze process in `docs/ARCHITECTURE-ROADMAP.md`.
