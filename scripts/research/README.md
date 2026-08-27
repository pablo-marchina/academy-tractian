# Research Scripts — Lifecycle and Safety Guide

`scripts/research/` contains executable research, evaluation, validation and evidence-generation code accumulated across multiple experimental generations.

The existence of a script does **not** mean it is currently authorized to run.

## Before executing a script

1. read `docs/CURRENT-PROJECT-STATUS.md` and identify the current authorized gate;
2. locate the frozen manifest/result/authorization governing that execution;
3. verify any required source Git blob/path pins;
4. verify allowed data/evaluator/provider access boundaries;
5. run provider-free/structural checks first where the protocol requires them;
6. stop if the script would cross into a later gate.

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

## Current C4 boundary

The current canonical packet is `research/results/p12-c4-complete-packet-freeze-2026-08-26.json` and the next gate is `DETERMINISTIC_SCORING`.

The current scoring work must execute deterministic scoring only. A historical scorer that also invokes bootstrap, LOGO, slices or later evaluations must not be run monolithically before those gates are separately authorized.

No additional C4 provider generation is authorized by the current packet freeze.

## Production code

Research runners are not automatically production code. Validated behavior may later be translated into the production implementation only after the production-fit comparison and architecture-freeze process in `docs/PROJECT-PLAN.md`.
