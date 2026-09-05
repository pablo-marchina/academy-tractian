# Systematic Research Hub

This directory is the **research/evidence history surface**, not the canonical project-status page.

For current project truth, start with:

- [`../docs/CURRENT-PROJECT-STATUS.md`](../docs/CURRENT-PROJECT-STATUS.md) — current state and claim authorization;
- [`../docs/DELIVERY-PLAN.md`](../docs/DELIVERY-PLAN.md) — active execution plan;
- [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) — promoted architecture and stack;
- [`../docs/DELIVERY-ACCEPTANCE.md`](../docs/DELIVERY-ACCEPTANCE.md) — acceptance obligations;
- [`../docs/PROJECT-PRINCIPLES.md`](../docs/PROJECT-PRINCIPLES.md) — governance and evaluation-driven development rules;
- [`../docs/README.md`](../docs/README.md) — documentation lifecycle and evidence hierarchy.

For upstream assignment/source reconciliation, use:

- [`tractian-source-baseline-2026-08-27.md`](tractian-source-baseline-2026-08-27.md);
- [`01-requirements-matrix.md`](01-requirements-matrix.md).

This README intentionally does **not** restate the current experiment gate. Historical filenames, workflows and scripts are not authorization.

## Directory semantics

| Path | Role |
|---|---|
| numbered Markdown files at `research/` root | legacy chronological research/evidence trail retained for provenance |
| `experiments/` | preregistration, design and experiment-eligibility material |
| `frozen/` | immutable contracts, maps, inputs and authorizations |
| `fixtures/` | allowed fixture/public test material |
| `results/` | canonical machine-readable results, closures and checkpoints |
| `live/` | intentionally committed live evidence |
| `execution-bundles/` | frozen/materialized execution code used by historical or active experiments |
| `e2/` | accepted controller/tool/trace/evaluation harness |

## Historical-record policy

The large numbered E-series/BIG-B/P12 trail remains intentionally present. Some records are failed, consumed, superseded or historical, but they are still evidence.

Do **not** bulk-rename, renumber or move those files merely to make the tree prettier. First prove that a path is not:

- referenced by a frozen JSON/manifest;
- pinned as a source path or blob;
- linked from a result, ADR or workflow;
- required for reproduction of a consumed or failed experiment.

When uncertain, classify logically and preserve the physical path.

## Lifecycle labels

```text
ACTIVE       current authorized workstream
FROZEN       immutable evidence/input/decision
CONSUMED     historical attempt that cannot be reused
HISTORICAL   retained for reproducibility/context
SUPERSEDED   replaced by stronger evidence/decision
```

A file remaining in the repository does not make it active.

## Rule for new research

Do not continue growing the loose numbered root unless a source-pinned historical protocol requires it.

New work should normally be placed as follows:

```text
research/experiments/<decision-or-experiment>/
research/frozen/<decision-or-experiment>/
research/results/<decision-or-experiment>/
```

Use stable machine-readable IDs inside artifacts; do not rely on filename order as the experiment identity.

Every material candidate follows:

```text
requirement / measured gap
→ research question
→ alternatives + baseline
→ preregistration
→ quantitative controlled evaluation
→ robustness/failure analysis
→ production fit
→ ADR / decision
→ regression
```

## Cleanup rule

Before deleting or relocating research evidence, follow the repository-wide cleanup policy in [`../docs/README.md`](../docs/README.md). The default is preservation unless reference/pinning/reproduction safety is proven.
