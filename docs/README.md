# Documentation Hub

**Status:** canonical documentation index  
**Current state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Delivery target:** 2026-09-08

This repository contains both active product documentation and a large scientific evidence trail. The active surface is intentionally small; historical/frozen files remain available for provenance and reproduction but are not competing sources of current truth.

## 1. Canonical active documents

Use one document per question:

| Question | Canonical document |
|---|---|
| Where are we now? | [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md) |
| What are we building next and by when? | [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md) |
| What is the architecture/stack/technique set? | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| Where does code live / where should a change go? | [`CODEBASE-MAP.md`](CODEBASE-MAP.md) |
| How does this satisfy the TAPI? | [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md) |
| What must be true for final acceptance? | [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md) |
| How do I install, reproduce and recover? | [`FINAL-HANDOFF-RUNBOOK.md`](FINAL-HANDOFF-RUNBOOK.md) |
| What evidence supports the rubric? | [`RUBRIC-TO-EVIDENCE.md`](RUBRIC-TO-EVIDENCE.md) |
| What governance rules constrain changes? | [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md) |
| Why was a material decision made? | [`adr/README.md`](adr/README.md) + `adr/*` |
| How did the project evolve? | [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md) + `progress/` |

`README.md` at repository root is a concise entrypoint only.

## 2. Documentation lifecycle

### ACTIVE

May be updated as evidence/state changes:

- `CURRENT-PROJECT-STATUS.md`
- `DELIVERY-PLAN.md`
- `ARCHITECTURE.md`
- `CODEBASE-MAP.md`
- `TAPI-DELIVERY-COVERAGE-2026-09-02.md`
- `DELIVERY-ACCEPTANCE.md`
- `FINAL-HANDOFF-RUNBOOK.md`
- `RUBRIC-TO-EVIDENCE.md`
- `PROJECT-PRINCIPLES.md`

### FROZEN / HISTORICAL

Do not rewrite to make later decisions look cleaner:

- `adr/*` after acceptance/freeze;
- `research/frozen/*`;
- frozen experiment manifests/results/closures;
- consumed/uncertain live custody evidence;
- `docs/progress/*`;
- date-stamped audits and preregistration/preflight documents.

### SUPERSEDED COMPATIBILITY PATHS

These paths are retained so old links do not become ambiguous, but they no longer carry independent mutable truth:

- `PROJECT-PLAN.md` → `DELIVERY-PLAN.md`
- `NEXT-STEPS.md` → `DELIVERY-PLAN.md`
- `ARCHITECTURE-ROADMAP.md` → `ARCHITECTURE.md`
- `REPOSITORY-GUIDE.md` → this index + `CONTRIBUTING.md`
- `FINAL-DELIVERY-OUTPUT-INVENTORY-2026-09-02.md` → TAPI coverage + acceptance

Git history preserves their prior full contents.

## 3. Evidence hierarchy

For **current repository state/authorization**:

1. exact frozen experiment evidence for its own scope;
2. `PROJECT-PRINCIPLES.md`;
3. `CURRENT-PROJECT-STATUS.md`;
4. current machine-readable checkpoint/result linked from status;
5. `DELIVERY-PLAN.md`;
6. `DELIVERY-ACCEPTANCE.md`;
7. `ARCHITECTURE.md`;
8. accepted ADRs for material decisions;
9. history/audits for context only.

For **assignment requirements**:

1. current TAPI;
2. delivered TRACTIAN project/API package;
3. executable supplied API behavior/contracts;
4. partner/kickoff guidance compatible with those sources;
5. project hypotheses/extensions.

A historical document does not become current truth merely because it remains in the repository.

## 4. Directory roles

| Path | Role |
|---|---|
| `src/academy_tractian/` | production runtime/evaluator/provider/control surfaces |
| `frontend/` | React/TypeScript product UI and browser tests |
| `research/e2/` | accepted controller/tool/trace/evaluation harness |
| `research/experiments/` | preregistration/design/eligibility artifacts |
| `research/frozen/` | immutable experiment contracts/inputs |
| `research/results/` | machine-readable results/closures/checkpoints |
| `research/live/` | intentionally committed live evidence |
| `scripts/` | thin deterministic validators/utilities/reporting CLIs |
| `tests/` | backend product/regression/integration tests |
| `docs/adr/` | material decision history |
| `docs/progress/` | chronological freeze/governance records |
| `docs/archive/` | superseded narrative/planning material already safe to archive |
| `.github/workflows/` | required CI plus preserved experimental/historical workflows |

Navigation rules for the large code/research/test/script surfaces live in:

- [`CODEBASE-MAP.md`](CODEBASE-MAP.md)
- [`../research/README.md`](../research/README.md)
- [`../scripts/README.md`](../scripts/README.md)
- [`../tests/README.md`](../tests/README.md)
- [`../.github/workflows/README.md`](../.github/workflows/README.md)

## 5. Cleanup policy

Physical relocation/deletion is allowed only when the file is proven:

```text
not frozen
AND not referenced by frozen evidence
AND not source-pinned by path/blob
AND not required for reproduction
AND not referenced by active workflows/ADRs
AND replacement/navigation is updated
```

When uncertain, prefer logical cleanup: mark lifecycle and point to the canonical document. This preserves scientific provenance while keeping the active documentation surface unambiguous.

## 6. Change synchronization

When a material state changes, update only the documents that own that question:

- state/authorization → `CURRENT-PROJECT-STATUS.md`;
- priorities/deadline → `DELIVERY-PLAN.md`;
- durable architecture/stack → `ARCHITECTURE.md` + ADR when material;
- code ownership/navigation → `CODEBASE-MAP.md`;
- requirement/DoD → TAPI coverage + `DELIVERY-ACCEPTANCE.md`;
- operator commands/recovery → `FINAL-HANDOFF-RUNBOOK.md`;
- historical event → append to progress/evidence, never copy into every active document.

This is the anti-drift rule for the remainder of the project.
