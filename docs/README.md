# Documentation Hub

**Status:** ACTIVE documentation index  
**Last verified:** 2026-09-06 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Public product:** https://production-web-production-c9d1.up.railway.app

The repository contains two different things on purpose:

1. a **small active documentation surface** that answers current user/operator/developer/reviewer questions;
2. a **large immutable evidence history** that preserves experiments, ADRs, audits and prior states.

Do not treat an old file as current truth merely because it remains in Git.

## Start by task

### I want to use or learn the product — tutorial / quickstart

- [`GETTING-STARTED.md`](GETTING-STARTED.md) — first successful investigation and how to navigate Results/Evidence/Investigation/Engineering.
- [`RELEASE-0-ACCEPTANCE.md`](RELEASE-0-ACCEPTANCE.md) — what the live Release 0 actually proved.

### I want to perform an operation — how-to / runbook

- [`FINAL-HANDOFF-RUNBOOK.md`](FINAL-HANDOFF-RUNBOOK.md) — production smoke, promotion, diagnosis, rollback and recovery.
- [`PLAYWRIGHT-ACCEPTANCE.md`](PLAYWRIGHT-ACCEPTANCE.md) — browser/product acceptance contract.
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md) — development workflow.

### I need exact current facts — reference

- [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md) — mutable current state and evidence anchors.
- [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md) — final-project Definition of Done and open gates.
- [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md) — assignment-to-product crosswalk.
- [`CODEBASE-MAP.md`](CODEBASE-MAP.md) — code ownership/navigation.
- [`decision-registry.yaml`](decision-registry.yaml) — material decision states; release qualification does not silently rewrite frozen experiments.
- [`../CHANGELOG.md`](../CHANGELOG.md) — notable product evolution.

### I want to understand why — explanation

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — current system context, containers, dynamic flow and trust boundaries.
- [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md) — governance and engineering constitution.
- [`SECURITY-MODEL.md`](SECURITY-MODEL.md) — active threat/trust-boundary model.
- [`adr/README.md`](adr/README.md) + `adr/*` — accepted material decision history.
- [`DOCUMENTATION-GUIDE.md`](DOCUMENTATION-GUIDE.md) — documentation architecture, lifecycle and writing rules.

### I want chronological/research evidence

- [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md) — historical project chronology.
- [`progress/`](progress/) — append-only dated progress/evidence notes.
- [`research/`](research/) — documentation/research-specific evidence notes.
- [`../research/README.md`](../research/README.md) — broader experiment/evidence tree.

## Canonical ownership: one question, one mutable owner

| Question | Mutable owner |
|---|---|
| Where are we now? | `ACTIVE-PROJECT-STATUS.md` |
| What are we doing next? | `DELIVERY-PLAN.md` |
| What architecture is promoted? | `ARCHITECTURE.md` |
| What must be true at final delivery? | `DELIVERY-ACCEPTANCE.md` |
| What does the TAPI map to? | `TAPI-DELIVERY-COVERAGE-2026-09-02.md` |
| Where does code live? | `CODEBASE-MAP.md` |
| How do I operate/recover it? | `FINAL-HANDOFF-RUNBOOK.md` |
| What changed for humans? | root `CHANGELOG.md` |
| Why was a durable decision made? | ADR / decision registry |

The root `README.md` is an entrypoint, not another status database.

## Documentation lifecycle

### ACTIVE — edit prospectively

- this index;
- `GETTING-STARTED.md`;
- `ACTIVE-PROJECT-STATUS.md`;
- `DELIVERY-PLAN.md`;
- `ARCHITECTURE.md`;
- `CODEBASE-MAP.md`;
- `DELIVERY-ACCEPTANCE.md`;
- `TAPI-DELIVERY-COVERAGE-2026-09-02.md`;
- `FINAL-HANDOFF-RUNBOOK.md`;
- `PLAYWRIGHT-ACCEPTANCE.md`;
- `SECURITY-MODEL.md`;
- `DOCUMENTATION-GUIDE.md`;
- `PROJECT-PRINCIPLES.md` when governance itself changes;
- root `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`.

### FROZEN / HISTORICAL — do not rewrite later history into them

- `CURRENT-PROJECT-STATUS.md` — legacy mutable-looking filename, hash-pinned by freeze evidence;
- `RUBRIC-TO-EVIDENCE.md` — hash-pinned hard-freeze evidence;
- accepted/frozen ADRs;
- `research/frozen/*` and consumed experiment manifests/results;
- `docs/progress/*` once committed;
- date-stamped audits, preregistrations and preflights;
- custody/blind/locked evidence.

When a frozen statement becomes outdated, add a new prospective record and link from active docs. **Never rewrite the old evidence to make history look cleaner.**

### SUPERSEDED compatibility paths

These retain old links but must not contain independent mutable truth:

- `PROJECT-PLAN.md` → `DELIVERY-PLAN.md`;
- `NEXT-STEPS.md` → `DELIVERY-PLAN.md`;
- `ARCHITECTURE-ROADMAP.md` → `ARCHITECTURE.md`;
- `REPOSITORY-GUIDE.md` → this hub + `CONTRIBUTING.md`.

## Evidence hierarchy

For current repository claims:

1. exact hosted/frozen evidence for the claim's scope;
2. `PROJECT-PRINCIPLES.md`;
3. `ACTIVE-PROJECT-STATUS.md`;
4. current machine-readable result/checkpoint;
5. `DELIVERY-PLAN.md` / `DELIVERY-ACCEPTANCE.md`;
6. `ARCHITECTURE.md`;
7. accepted ADRs;
8. historical audits/progress for context.

For assignment interpretation:

1. current TAPI;
2. delivered TRACTIAN package/API contract;
3. executable supplied API behavior;
4. compatible partner/kickoff guidance;
5. project-added constraints/hypotheses.

## Anti-drift update rule

When a material state changes, update only the documents that own the changed question, then add a dated evidence/progress note if the event is historically material.

Examples:

- new promotion → active status + acceptance/runbook/changelog as applicable;
- durable architecture change → architecture + ADR + code map if needed;
- UX behavior change → getting started + Playwright contract + changelog;
- new final requirement → TAPI/acceptance + delivery plan;
- research decision → decision record/ADR + progress evidence;
- vulnerability boundary change → security model + architecture/runbook.

See [`DOCUMENTATION-GUIDE.md`](DOCUMENTATION-GUIDE.md) for the full docs-as-code contract.