# Documentation Hub

**Status:** ACTIVE documentation index  
**Last verified:** 2026-09-08 BRT  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Current dated progress:** [`progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md`](progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md)  
**Public product:** https://production-web-production-c9d1.up.railway.app

The repository intentionally separates:

1. a **small mutable active documentation surface** for current truth;
2. a **large immutable evidence history** for experiments, ADRs, audits and earlier production states.

Do not treat an old file as current merely because it remains in Git. In particular, the 2026-09-07 V13/read-only state has been superseded by a 2026-09-08 production state with governed actions and a deployed OpenRouter V14 provider migration whose functional gate is currently failing.

## Current checkpoint in one paragraph

Production backend `5611687556b3d50c31f20fa85ede794f2500f05c` is live on Railway with OpenRouter V14 pinned to `nvidia/nemotron-3-super-120b-a12b:free`; production frontend is `4364364266c6a88d4affd85cb3a734c774cd42c8`; supplied TRACTIAN API is `47561c1175181b508139e23e6e39b555c1347d57`. Governed action transport passed a controlled 5/5 production smoke. However, the real authenticated B204 OpenRouter→agent→TRACTIAN functional matrix is 0/3 because the first provider response ends with `finish_reason=length`, so no TRACTIAN tool is reached. A bounded follow-up comparison was blocked by HTTP 429 and remains `INCONCLUSIVE`.

## Start by task

### Use or learn the product

- [`GETTING-STARTED.md`](GETTING-STARTED.md) — task-driven Home / Analyses / Technical flow and safe prompting.
- [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md) — read first if behavior/provider/action state matters.
- [`RELEASE-0-ACCEPTANCE.md`](RELEASE-0-ACCEPTANCE.md) — immutable original Release 0 evidence, not current production state.

### Need exact current facts

- [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md) — mutable current state and hosted identities.
- [`progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md`](progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md) — full chronology/evidence for governed actions, Verification V1, V14 and the failing functional gate.
- [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md) — final Definition of Done and current ledger.
- [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md) — dependency-ordered closure plan.
- [`TAPI-DELIVERY-COVERAGE-2026-09-02.md`](TAPI-DELIVERY-COVERAGE-2026-09-02.md) — updated TAPI crosswalk.
- [`CODEBASE-MAP.md`](CODEBASE-MAP.md) — current code ownership including V14/provider diagnostics/governed actions.
- [`../CHANGELOG.md`](../CHANGELOG.md) — notable human-readable evolution.

### Understand architecture/security

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — current OpenRouter V14, `AgentController`/`HarnessRunner`, RLS/realtime and governed action architecture.
- [`SECURITY-MODEL.md`](SECURITY-MODEL.md) — active threat model including provider truncation/rate-limit, action authority and branch-governance threats.
- [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md) — engineering/governance constitution.
- [`adr/README.md`](adr/README.md) — accepted decision history.
- [`DOCUMENTATION-GUIDE.md`](DOCUMENTATION-GUIDE.md) — documentation lifecycle/anti-drift rules.

### Operate / recover

- [`FINAL-HANDOFF-RUNBOOK.md`](FINAL-HANDOFF-RUNBOOK.md) — production smoke, exact-SHA promotion, rollback/recovery.
- [`GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md`](GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md) — action rollout/rollback and current 5-action governed boundary.
- [`PLAYWRIGHT-ACCEPTANCE.md`](PLAYWRIGHT-ACCEPTANCE.md) — browser/product acceptance contract.
- [`BRANCH-PROTECTION.md`](BRANCH-PROTECTION.md) — required gate and external enforcement procedure; latest observed `main.protected=false`.
- [`VERIFICATION-PROTOCOL-V1.md`](VERIFICATION-PROTOCOL-V1.md) — independent/claim-bounded verification protocol.

### Record/present the project

The presentation pack is current-user-facing material and should use the mutable status documents above for final identities/claims. Never read a historical V13 or Release 0 SHA from an old evidence file into a current presentation without labeling it historical.

- [`presentation/README.md`](presentation/README.md)
- [`presentation/EXACT-5-MIN-RECORDING-SCRIPT.md`](presentation/EXACT-5-MIN-RECORDING-SCRIPT.md)
- [`presentation/05-MIN-TECHNICAL-SCREENPLAY.md`](presentation/05-MIN-TECHNICAL-SCREENPLAY.md)
- [`presentation/SCREEN-SHOT-LIST.md`](presentation/SCREEN-SHOT-LIST.md)
- [`presentation/ARCHITECTURE-OVERLAYS.md`](presentation/ARCHITECTURE-OVERLAYS.md)
- [`presentation/RECORDING-CHECKLIST.md`](presentation/RECORDING-CHECKLIST.md)

### Chronological/research evidence

- [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md) — historical chronology.
- [`progress/2026-09-07-release0-live-hardening-v13.md`](progress/2026-09-07-release0-live-hardening-v13.md) — preserved V13 episode.
- [`progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md`](progress/2026-09-08-openrouter-v14-governed-actions-functional-acceptance.md) — current material episode.
- [`progress/`](progress/) — append-only progress/evidence notes.
- [`research/`](research/) and root [`../research/`](../research/) — experiment/evidence trees.

## Canonical ownership

| Question | Mutable owner |
|---|---|
| Where are we now? | `ACTIVE-PROJECT-STATUS.md` |
| What happened in the latest material episode? | latest dated `progress/*` note |
| What are we doing next? | `DELIVERY-PLAN.md` |
| What architecture is promoted? | `ARCHITECTURE.md` |
| What must be true at final delivery? | `DELIVERY-ACCEPTANCE.md` |
| What does the TAPI map to? | `TAPI-DELIVERY-COVERAGE-2026-09-02.md` |
| Where does code live? | `CODEBASE-MAP.md` |
| How do I operate/recover it? | `FINAL-HANDOFF-RUNBOOK.md` |
| How do I operate governed actions? | `GOVERNED-ACTIONS-PRODUCTION-RUNBOOK.md` |
| What changed for humans? | root `CHANGELOG.md` |
| Why was a durable decision made? | ADR / decision registry |

The root `README.md` is an entrypoint, not a competing status database.

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
- `BRANCH-PROTECTION.md`;
- `VERIFICATION-PROTOCOL-V1.md`;
- `DOCUMENTATION-GUIDE.md`;
- root `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md` as relevant;
- current presentation material.

### FROZEN / HISTORICAL — preserve

Do **not** rewrite later state into:

- `CURRENT-PROJECT-STATUS.md` — legacy mutable-looking file already hash-pinned by freeze evidence;
- `RUBRIC-TO-EVIDENCE.md` and other hash-pinned freeze artifacts;
- accepted/frozen ADRs;
- `research/frozen/*` and consumed manifests/results;
- existing date-stamped `docs/progress/*` notes;
- date-stamped audits/preregistrations/preflights;
- blind/locked/custody evidence;
- original Release 0 acceptance records.

When a historical claim becomes obsolete, update active owners and add a new dated progress record. **Never edit history to make the project look cleaner.**

### SUPERSEDED compatibility paths

- `PROJECT-PLAN.md` → `DELIVERY-PLAN.md`;
- `NEXT-STEPS.md` → `DELIVERY-PLAN.md`;
- `ARCHITECTURE-ROADMAP.md` → `ARCHITECTURE.md`;
- `REPOSITORY-GUIDE.md` → this hub + `CONTRIBUTING.md`.

## Anti-drift update rule

For every material production change:

```text
observe exact hosted state
→ update ACTIVE-PROJECT-STATUS
→ update owning architecture/acceptance/runbook docs
→ add append-only dated evidence note
→ update README/docs index/changelog/presentation references
→ keep historical/frozen evidence untouched
```

The 2026-09-08 synchronization follows that rule. It intentionally replaces stale current-state references to Cloudflare/read-only V13 in mutable owners while preserving the files that historically proved those earlier states.