# Systematic Research Hub

This directory is the **research evidence/history surface**, not the canonical project-status page.

For current state and authorization, always start with:

- [`../docs/CURRENT-PROJECT-STATUS.md`](../docs/CURRENT-PROJECT-STATUS.md)
- [`../docs/PROJECT-PLAN.md`](../docs/PROJECT-PLAN.md)
- [`../docs/PROJECT-PRINCIPLES.md`](../docs/PROJECT-PRINCIPLES.md)
- [`../docs/REPOSITORY-GUIDE.md`](../docs/REPOSITORY-GUIDE.md)

## Current pointer

The current C4 evidence transition is recorded by:

- `results/p12-c4-complete-packet-freeze-2026-08-26.json`
- status `FROZEN_COMPLETE_C4_PACKET`
- next gate `DETERMINISTIC_SCORING`.

Do not infer authorization from an older numbered research record, script or workflow.

## Directory semantics

- numbered Markdown files at `research/` root: chronological/systematic research history, retained for provenance;
- `experiments/`: preregistrations, experiment definitions and eligibility/design artifacts;
- `frozen/`: immutable frozen contracts, maps, inputs and authorizations;
- `fixtures/`: allowed fixture/public test material;
- `results/`: canonical machine-readable results, closures and time-specific checkpoints;
- `live/`: intentionally committed live evidence, when present.

Exact experiment semantics come from the relevant frozen artifact/result, not this README.

## Historical-record policy

The large numbered E-series/BIG-B/P12 research trail is intentionally retained. Many records are historical, failed, superseded or consumed, but they are still evidence.

Do not bulk-rename, renumber or move these files merely to make the tree visually cleaner. First prove that the path is not:

- referenced by a frozen JSON/manifest;
- pinned as a source path/blob;
- linked from a result/ADR/workflow;
- required for reproduction of a consumed or failed experiment.

Logical classification/indexing is preferred over breaking provenance.

## Evidence lifecycle

Useful interpretation labels:

```text
ACTIVE       current authorized workstream
FROZEN       immutable evidence/input/decision
CONSUMED     historical attempt that cannot be reused
HISTORICAL   retained for reproducibility/context
SUPERSEDED   replaced by stronger evidence/decision
```

A historical file may remain physically present without being active.

## Development rule

Any new material candidate or architecture change must follow `PROJECT-PRINCIPLES.md`:

```text
question → requirements → systematic research → alternatives + baseline
→ preregistration → quantitative controlled evaluation → robustness
→ production-fit → ADR/decision → regression
```

The research tree is evidence for that process; it is not a substitute for it.
