# Systematic Research Hub

This directory is the **research evidence/history surface**, not the canonical project-status page.

For current state, authorization and execution order, always start with:

- [`../docs/CURRENT-PROJECT-STATUS.md`](../docs/CURRENT-PROJECT-STATUS.md)
- [`../docs/NEXT-STEPS.md`](../docs/NEXT-STEPS.md)
- [`../docs/ARCHITECTURE-ROADMAP.md`](../docs/ARCHITECTURE-ROADMAP.md)
- [`../docs/PROJECT-PLAN.md`](../docs/PROJECT-PLAN.md)
- [`../docs/PROJECT-PRINCIPLES.md`](../docs/PROJECT-PRINCIPLES.md)
- [`../docs/REPOSITORY-GUIDE.md`](../docs/REPOSITORY-GUIDE.md)

This README intentionally does **not** restate the current experiment gate or checkpoint. Do not infer authorization from an older numbered research record, script, workflow or filename.

## Directory semantics

- numbered Markdown files at `research/` root: chronological/systematic research history, retained for provenance;
- `experiments/`: preregistrations, experiment definitions and eligibility/design artifacts;
- `frozen/`: immutable contracts, maps, inputs and authorizations;
- `fixtures/`: allowed fixture/public test material;
- `results/`: canonical machine-readable results, closures and time-specific checkpoints;
- `live/`: intentionally committed live evidence, when present;
- `execution-bundles/`: frozen/materialized execution code bundles used by historical or active experiments.

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
