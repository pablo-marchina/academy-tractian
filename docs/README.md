# Documentation Hub

**Status:** ACTIVE documentation index  
**Last verified:** 2026-09-07 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Public product:** https://production-web-production-c9d1.up.railway.app

The repository intentionally contains:

1. a **small active documentation surface** that answers current user/operator/developer/reviewer questions;
2. a **large immutable evidence history** preserving experiments, ADRs, audits and prior states.

Do not treat an old file as current truth merely because it remains in Git.

## Start by task

### Use or learn the product

- [`GETTING-STARTED.md`](GETTING-STARTED.md) — task-driven Home / Analyses / Technical flow, result/evidence semantics and safe prompting.
- [`RELEASE-0-ACCEPTANCE.md`](RELEASE-0-ACCEPTANCE.md) — immutable original Release 0 gate plus prospective live-hardening status.

### Record the 5-minute technical presentation

- [`presentation/README.md`](presentation/README.md) — entrypoint and current identities.
- [`presentation/EXACT-5-MIN-RECORDING-SCRIPT.md`](presentation/EXACT-5-MIN-RECORDING-SCRIPT.md) — exact recording path aligned to the current task-driven UI.
- [`presentation/05-MIN-TECHNICAL-SCREENPLAY.md`](presentation/05-MIN-TECHNICAL-SCREENPLAY.md) — technical intent/timing.
- [`presentation/SCREEN-SHOT-LIST.md`](presentation/SCREEN-SHOT-LIST.md) — current hosted screens/evidence.
- [`presentation/ARCHITECTURE-OVERLAYS.md`](presentation/ARCHITECTURE-OVERLAYS.md) — simplified runtime/deployment overlays.
- [`presentation/RECORDING-CHECKLIST.md`](presentation/RECORDING-CHECKLIST.md) — preflight/claim discipline.

### Perform an operation

- [`FINAL-HANDOFF-RUNBOOK.md`](FINAL-HANDOFF-RUNBOOK.md) — production smoke, exact-SHA promotion, auth diagnosis, rollback and recovery.
- [`PLAYWRIGHT-ACCEPTANCE.md`](PLAYWRIGHT-ACCEPTANCE.md) — current browser/product acceptance contract.
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md) — development workflow.

### Need exact current facts

- [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md) — mutable current state and hosted identities.
- [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md) — final-project Definition of Done and open gates.
- [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md) — assignment-to-product crosswalk.
- [`CODEBASE-MAP.md`](CODEBASE-MAP.md) — code ownership/navigation, including V10–V13 release-provider layers.
- [`decision-registry.yaml`](decision-registry.yaml) — material decision states; release qualification does not silently rewrite frozen experiments.
- [`../CHANGELOG.md`](../CHANGELOG.md) — notable product evolution.

### Understand why

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — current system context, V13 orchestration, auth resilience, dynamic flow and trust boundaries.
- [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md) — governance/engineering constitution.
- [`SECURITY-MODEL.md`](SECURITY-MODEL.md) — active threat/trust-boundary model.
- [`adr/README.md`](adr/README.md) + `adr/*` — accepted material decision history.
- [`DOCUMENTATION-GUIDE.md`](DOCUMENTATION-GUIDE.md) — documentation architecture/lifecycle.

### Chronological/research evidence

- [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md) — historical project chronology.
- [`progress/2026-09-07-release0-live-hardening-v13.md`](progress/2026-09-07-release0-live-hardening-v13.md) — current live-hardening episode, incidents, PRs, deployments and V13 run matrix.
- [`progress/`](progress/) — append-only dated progress/evidence notes.
- [`research/`](research/) — documentation/research-specific evidence notes.
- [`../research/README.md`](../research/README.md) — broader experiment/evidence tree.

## Canonical ownership

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
- root `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`;
- current presentation pack.

### FROZEN / HISTORICAL — do not rewrite later history into them

- `CURRENT-PROJECT-STATUS.md` — legacy mutable-looking filename, hash-pinned by freeze evidence;
- `RUBRIC-TO-EVIDENCE.md` — hash-pinned hard-freeze evidence;
- accepted/frozen ADRs;
- `research/frozen/*` and consumed experiment manifests/results;
- committed `docs/progress/*` notes;
- date-stamped audits, preregistrations and preflights;
- custody/blind/locked evidence.

When a frozen statement becomes outdated, add a prospective record and link from active docs. **Never rewrite old evidence to make history look cleaner.**

### SUPERSEDED compatibility paths

- `PROJECT-PLAN.md` → `DELIVERY-PLAN.md`;
- `NEXT-STEPS.md` → `DELIVERY-PLAN.md`;
- `ARCHITECTURE-ROADMAP.md` → `ARCHITECTURE.md`;
- `REPOSITORY-GUIDE.md` → this hub + `CONTRIBUTING.md`.

## Anti-drift update rule

When material state changes, update the documents that own the changed question, then add a dated append-only evidence/progress note when the event is historically material.

This 2026-09-07 sync follows that rule: frozen evidence remains untouched; active owners and presentation material are updated to the hardened V13/task-driven production state.