# Documentation Hub

**Status:** ACTIVE documentation index  
**Last verified:** 2026-09-08 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Current provider-selection state:** [`PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`](PROVIDER-QUALIFICATION-STATUS-2026-09-08.md)  
**Public product:** https://production-web-production-c9d1.up.railway.app

The repository intentionally separates a small mutable documentation surface from a large immutable evidence history. Never treat an old experiment/audit as current truth merely because it remains in Git.

## Start by task

### Use the product

- [`GETTING-STARTED.md`](GETTING-STARTED.md) — Home / Analyses / Technical flow and safe prompting.
- [`RELEASE-0-ACCEPTANCE.md`](RELEASE-0-ACCEPTANCE.md) — immutable original Release 0 acceptance.

### Need current facts

- [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md) — mutable overall state.
- [`PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`](PROVIDER-QUALIFICATION-STATUS-2026-09-08.md) — canonical provider-selection, Groq qualification and causal-debug state.
- [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md) — dependency-ordered next work.
- [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md) — final-project Definition of Done.
- [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md) — TAPI crosswalk.
- [`CODEBASE-MAP.md`](CODEBASE-MAP.md) — implementation ownership.
- [`../CHANGELOG.md`](../CHANGELOG.md) — notable product/research evolution.

### Understand or operate the architecture

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — promoted production architecture plus experimental provider boundary.
- [`FINAL-HANDOFF-RUNBOOK.md`](FINAL-HANDOFF-RUNBOOK.md) — operation, exact-SHA promotion, provider gate, rollback and recovery.
- [`SECURITY-MODEL.md`](SECURITY-MODEL.md) — trust/security model.
- [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md) — engineering constitution.
- [`adr/README.md`](adr/README.md) — accepted decision history.

### Presentation

- [`presentation/README.md`](presentation/README.md) — claim-safe 5-minute pack entrypoint.
- [`presentation/EXACT-5-MIN-RECORDING-SCRIPT.md`](presentation/EXACT-5-MIN-RECORDING-SCRIPT.md) — exact recording path.
- [`presentation/RECORDING-CHECKLIST.md`](presentation/RECORDING-CHECKLIST.md) — preflight and non-claims.

### Chronological / research evidence

- [`progress/2026-09-07-release0-live-hardening-v13.md`](progress/2026-09-07-release0-live-hardening-v13.md) — V13 production hardening episode.
- [`progress/2026-09-08-provider-qualification-and-causal-debug.md`](progress/2026-09-08-provider-qualification-and-causal-debug.md) — append-only provider qualification and causal-debug episode.
- [`progress/`](progress/) — dated append-only progress notes.
- [`../research/`](../research/) — frozen populations, manifests, results and broader experiments.

## Canonical ownership

| Question | Mutable owner |
|---|---|
| Where are we now? | `ACTIVE-PROJECT-STATUS.md` |
| What is the current provider decision? | `PROVIDER-QUALIFICATION-STATUS-2026-09-08.md` |
| What are we doing next? | `DELIVERY-PLAN.md` |
| What architecture is promoted? | `ARCHITECTURE.md` |
| What must be true at final delivery? | `DELIVERY-ACCEPTANCE.md` |
| What does TAPI map to? | `TAPI-DELIVERY-COVERAGE-2026-09-02.md` |
| Where does code live? | `CODEBASE-MAP.md` |
| How do I operate/promote/rollback? | `FINAL-HANDOFF-RUNBOOK.md` |
| What changed? | root `CHANGELOG.md` |

The root `README.md` remains an entrypoint, not another independent status database.

## Documentation lifecycle

### ACTIVE — edit prospectively

This hub, `GETTING-STARTED.md`, `ACTIVE-PROJECT-STATUS.md`, provider status, `DELIVERY-PLAN.md`, `ARCHITECTURE.md`, `CODEBASE-MAP.md`, `DELIVERY-ACCEPTANCE.md`, TAPI coverage, handoff/runbook, current security/browser docs, root README/CHANGELOG and the current presentation pack.

### FROZEN / HISTORICAL — do not rewrite

- `CURRENT-PROJECT-STATUS.md`;
- `RUBRIC-TO-EVIDENCE.md`;
- accepted/frozen ADRs;
- `research/frozen/*`;
- consumed experiment manifests/results;
- already committed `docs/progress/*` notes;
- date-stamped audits/preregistrations/preflights;
- custody/blind/locked evidence.

When history becomes outdated, add a prospective record and link to it. Never modify historical evidence to make an unsuccessful experiment look successful.

### SUPERSEDED compatibility paths

- `PROJECT-PLAN.md` → `DELIVERY-PLAN.md`;
- `NEXT-STEPS.md` → `DELIVERY-PLAN.md`;
- `ARCHITECTURE-ROADMAP.md` → `ARCHITECTURE.md`;
- `REPOSITORY-GUIDE.md` → this hub + `CONTRIBUTING.md`.

## 2026-09-08 anti-drift update

The provider documentation now explicitly records:

- paired Cloudflare/Groq V4 did not produce a comparative result because Cloudflare was quota-blocked and then removed from the requested path;
- Groq-only GPT-OSS-120B completed 85/85 and ended `NO_SELECTION`;
- hard gates were not weakened;
- current work is causal diagnosis of finish/schema/reasoning failures, then strict-schema challengers only if justified;
- production provider/topology were not changed by this research work.
