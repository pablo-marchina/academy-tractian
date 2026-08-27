# Systematic Research Hub

This directory is the **research evidence/history surface**, not the canonical project-status page.

For project-source truth and current planning, start with:

- [`tractian-source-baseline-2026-08-27.md`](tractian-source-baseline-2026-08-27.md) — audited updated TAPI + delivered package + kickoff baseline and discrepancies;
- [`01-requirements-matrix.md`](01-requirements-matrix.md) — reconciled requirement/partner-guidance matrix;
- [`../docs/PROJECT-PRINCIPLES.md`](../docs/PROJECT-PRINCIPLES.md) — fixed North Star and development rules;
- [`../docs/CURRENT-PROJECT-STATUS.md`](../docs/CURRENT-PROJECT-STATUS.md) — current state/authorization;
- [`../docs/NEXT-STEPS.md`](../docs/NEXT-STEPS.md) — current execution plan;
- [`../docs/DELIVERY-ACCEPTANCE.md`](../docs/DELIVERY-ACCEPTANCE.md) — final evidence obligations;
- [`../docs/ARCHITECTURE-ROADMAP.md`](../docs/ARCHITECTURE-ROADMAP.md) — integrated agent/evaluator architecture path;
- [`../docs/PROJECT-PLAN.md`](../docs/PROJECT-PLAN.md) — macro phases/deadline protection;
- [`../docs/REPOSITORY-GUIDE.md`](../docs/REPOSITORY-GUIDE.md) — source reconciliation and repository maintenance.

This README intentionally does **not** restate the current experiment gate or checkpoint. Do not infer authorization from an older numbered research record, script, workflow or filename.

## Source-baseline rule

Upstream project sources and experiment evidence answer different questions:

```text
What must we deliver?
  → updated TAPI → delivered package → executable supplied API → compatible kickoff guidance

What happened/is authorized in a specific experiment?
  → frozen manifests/results/closures → current status
```

Do not let a historical experiment redefine the assignment, and do not let a new project-summary document silently rewrite frozen experiment semantics.

## Directory semantics

- numbered Markdown files at `research/` root: chronological/systematic research history, retained for provenance;
- `tractian-source-baseline-*.md`: audited upstream-source identity and reconciliation records;
- `experiments/`: preregistrations, experiment definitions and eligibility/design artifacts;
- `frozen/`: immutable contracts, maps, inputs and authorizations;
- `fixtures/`: allowed fixture/public test material;
- `results/`: canonical machine-readable results, closures and time-specific checkpoints;
- `live/`: intentionally committed live evidence, when present;
- `execution-bundles/`: frozen/materialized execution code bundles used by historical or active experiments.

Exact experiment semantics come from the relevant frozen artifact/result, not this README.

## Historical-record policy

The large numbered E-series/BIG-B/P12 research trail is intentionally retained. Many records are historical, failed, superseded or consumed, but they remain evidence.

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

Any new material candidate or architecture change follows `PROJECT-PRINCIPLES.md` and must first map to the actual requested delivery:

```text
formal requirement / rubric objective / material risk
→ question → systematic research → alternatives + baseline
→ preregistration → quantitative controlled evaluation → robustness
→ production/partner-quality fit → ADR/decision → regression
```

The research tree is evidence for that process; it is not a substitute for it.