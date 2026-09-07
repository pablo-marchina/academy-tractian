# Documentation Hub

**Status:** ACTIVE documentation index  
**Last verified:** 2026-09-07 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Current merged backend source:** `3545d75c00ca30419e0f47e8b1950aa50cbbf462`  
**Public product:** https://production-web-production-c9d1.up.railway.app

The repository intentionally contains:

1. a **small active documentation surface** that answers current user/operator/developer/reviewer questions;
2. a **large immutable evidence history** preserving experiments, ADRs, audits and prior states.

Do not treat an old file as current truth merely because it remains in Git.

## Current truth in one paragraph

Release 0 is hosted, authenticated, tenant-isolated, backed by Neon PostgreSQL, uses a provisional Cloudflare provider and real typed TRACTIAN reads. The task-driven frontend is live. Governed execution for the five canonical consequential actions is implemented, CI-qualified and enabled in production configuration, but **complete 5/5 vendor acceptance is not yet proven**: the fresh production smoke safely failed on `update_asset_config` HTTP 403 under the then-current upstream identity binding. The corrective design separates the local product user from a server-owned TRACTIAN actor selected by company + required permission.

## Start by task

### Use or learn the product

- [`GETTING-STARTED.md`](GETTING-STARTED.md) — Home / result/evidence / Analyses / Technical flow, result semantics and governed-action user boundary.
- [`RELEASE-0-ACCEPTANCE.md`](RELEASE-0-ACCEPTANCE.md) — immutable original Release 0 gate plus prospective hardening context.

### Operate governed actions

- [`GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md`](GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md) — five action contracts, grants, custody, confirmation, idempotency, lease/fencing, vendor actor separation, smoke and rollback.
- [`progress/2026-09-07-production-governed-actions-ux-and-validation.md`](progress/2026-09-07-production-governed-actions-ux-and-validation.md) — append-only evidence for #211/#213, CI, Railway deployments, live 403 and corrective architecture.

### Record the 5-minute technical presentation

- [`presentation/README.md`](presentation/README.md) — entrypoint and current claim discipline.
- [`presentation/EXACT-5-MIN-RECORDING-SCRIPT.md`](presentation/EXACT-5-MIN-RECORDING-SCRIPT.md) — exact recording path.
- [`presentation/05-MIN-TECHNICAL-SCREENPLAY.md`](presentation/05-MIN-TECHNICAL-SCREENPLAY.md) — technical intent/timing.
- [`presentation/SCREEN-SHOT-LIST.md`](presentation/SCREEN-SHOT-LIST.md) — hosted screens/evidence to capture.
- [`presentation/ARCHITECTURE-OVERLAYS.md`](presentation/ARCHITECTURE-OVERLAYS.md) — simplified truthful overlays.
- [`presentation/RECORDING-CHECKLIST.md`](presentation/RECORDING-CHECKLIST.md) — preflight and claim discipline.

### Perform an operation

- [`FINAL-HANDOFF-RUNBOOK.md`](FINAL-HANDOFF-RUNBOOK.md) — production smoke, exact-SHA/fresh-snapshot promotion, auth/action diagnosis, rollback and recovery.
- [`PLAYWRIGHT-ACCEPTANCE.md`](PLAYWRIGHT-ACCEPTANCE.md) — browser/product acceptance and evidence boundaries.
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md) — development workflow.

### Need exact current facts

- [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md) — mutable current state and hosted identities.
- [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md) — final-project Definition of Done, including separate local-action vs vendor-acceptance rows.
- [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md) — dependency-ordered remaining work; vendor actor routing + 5/5 action smoke are P0.
- [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md) — assignment-to-product crosswalk.
- [`CODEBASE-MAP.md`](CODEBASE-MAP.md) — code ownership/navigation, including governed actions and current upstream-identity integration gap.
- [`decision-registry.yaml`](decision-registry.yaml) — material decision states; release qualification does not silently rewrite frozen experiments.
- [`../CHANGELOG.md`](../CHANGELOG.md) — notable product evolution.

### Understand why

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — current system context, V13 reads, action execution, auth resilience and trust boundaries.
- [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md) — governance/engineering constitution.
- [`SECURITY-MODEL.md`](SECURITY-MODEL.md) — active threat/trust-boundary model including vendor actor/confused-deputy risks.
- [`adr/README.md`](adr/README.md) + `adr/*` — accepted material decision history.
- [`DOCUMENTATION-GUIDE.md`](DOCUMENTATION-GUIDE.md) — documentation architecture/lifecycle.

### Chronological/research evidence

- [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md) — historical project chronology.
- [`progress/2026-09-07-release0-live-hardening-v13.md`](progress/2026-09-07-release0-live-hardening-v13.md) — read/auth live-hardening episode.
- [`progress/2026-09-07-production-governed-actions-ux-and-validation.md`](progress/2026-09-07-production-governed-actions-ux-and-validation.md) — governed-action rollout/live validation episode.
- [`progress/`](progress/) — append-only dated progress/evidence notes.
- [`research/`](research/) — documentation/research-specific evidence notes.
- [`../research/README.md`](../research/README.md) — broader experiment/evidence tree.

## Canonical ownership

| Question | Mutable owner |
|---|---|
| Where are we now? | `ACTIVE-PROJECT-STATUS.md` |
| What are we doing next? | `DELIVERY-PLAN.md` |
| What architecture is promoted? | `ARCHITECTURE.md` |
| How do governed actions operate? | `GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md` |
| What must be true at final delivery? | `DELIVERY-ACCEPTANCE.md` |
| What does the TAPI map to? | `TAPI-DELIVERY-COVERAGE-2026-09-02.md` |
| Where does code live? | `CODEBASE-MAP.md` |
| How do I operate/recover it? | `FINAL-HANDOFF-RUNBOOK.md` |
| What changed for humans/operators? | root `CHANGELOG.md` |
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
- `GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md`;
- `PLAYWRIGHT-ACCEPTANCE.md`;
- `SECURITY-MODEL.md`;
- `DOCUMENTATION-GUIDE.md`;
- `PROJECT-PRINCIPLES.md` when governance itself changes;
- root `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`;
- `frontend/README.md`;
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

When material state changes:

```text
update the active owner(s)
→ add a dated append-only evidence/progress note when historically material
→ preserve old frozen claims as historical truth
→ separate implemented / CI-proven / hosted-proven / vendor-proven states
```

The 2026-09-07 synchronization follows that rule. In particular, current docs must neither say “actions are still deny-all” nor say “all five actions work” while the live evidence is more nuanced.

Historical/frozen documents remain untouched.