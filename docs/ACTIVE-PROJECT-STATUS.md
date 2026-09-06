# Academy × TRACTIAN — Current Project Status

**Status:** Release 0 / immediate user release in progress  
**Checkpoint:** 2026-09-06 BRT  
**Implementation branch:** `release/production-final`  
**Draft integration PR:** `#196`  
**Release 0 plan:** [`RELEASE-0-PLAN.md`](RELEASE-0-PLAN.md)  
**Release 0 acceptance:** [`RELEASE-0-ACCEPTANCE.md`](RELEASE-0-ACCEPTANCE.md)  
**Final delivery plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Final acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**Decision registry:** [`decision-registry.yaml`](decision-registry.yaml)

This file is the mutable source of truth for active execution state. Historical/frozen evidence remains immutable. The first-user release is intentionally narrower than final project completion: Release 0 ships the smallest safe **real read-only production slice**, then real-user telemetry drives quality and UX improvement while the final evidence program continues.

## 1. Immediate objective

```text
authenticated remote user
→ public HTTPS product
→ managed server-owned tenant context
→ remote FastAPI
→ real hosted USD0 DecisionSource
→ AgentController
→ typed TRACTIAN read tool
→ real TRACTIAN evidence
→ FINAL | CLARIFY | ABSTAIN | ESCALATE
→ deterministic post-runtime evaluation
→ durable Neon PostgreSQL
→ genuine REST/SSE + React UX
```

Consequential external action execution remains disabled in Release 0.

Hard constraints retained: actual project cash cost USD 0, no paid spillover, no local production dependency, no browser-owned tenant/permission authority, zero accepted cross-tenant disclosure in the release campaign, evaluator/gold isolation and evidence-honest claims.

## 2. Current state

The Release 0 pivot started from source checkpoint `6026e6aea7e6a6574640ba383fb742c62e01826e`. Documentation commits after that checkpoint do not imply a new hosted production claim until the public path is independently observed.

| Workstream | Current state | Release 0 role / next proof |
|---|---|---|
| Core AgentController + HarnessRunner | **IMPLEMENTED / REGRESSION PASS** | keep baseline |
| 18-operation typed TRACTIAN registry | **IMPLEMENTED** | representative real read first |
| Deterministic evaluator | **IMPLEMENTED** | run after genuine user path |
| Neon PostgreSQL durable truth | **HOSTED / G2 PASS** | preserve |
| Tenant RLS substrate | **HOSTED STRUCTURE PASS** | minimum two-user negatives |
| Railway production API | **HOSTED / G2 PASS** | preserve hosted smoke |
| Railway/Caddy frontend | **HOSTED** | user path/UX acceptance |
| Immutable release identity | **HOSTED / G2 PASS** | exact-SHA smoke stays mandatory |
| Neon Auth / Better Auth | **IMPLEMENTED / HOSTED ACCEPTANCE OPEN** | **RELEASE BLOCKER R0-01** |
| TRACTIAN production adapter | **IMPLEMENTED / SOURCE PASS** | **RELEASE BLOCKER R0-02: real bounded read** |
| TRACTIAN recent identity/header fixes | **LANDED** | prove against live configured endpoint |
| Provider Tournament v3 | **PREREGISTERED / FINAL NO_SELECTION** | full 170-attempt campaign moved post-release |
| Provisional release provider | **NOT YET QUALIFIED** | **RELEASE BLOCKER R0-03** |
| Production DecisionSource | **FAIL-CLOSED / NO_SELECTION** | **RELEASE BLOCKER R0-04** |
| FINAL/CLARIFY/ABSTAIN/ESCALATE structural paths | **SOURCE PASS** | genuine hosted provider + TRACTIAN proof |
| Grounding/evidence lineage | **PARTIAL** | minimum safe user evidence required |
| Realtime/persistence | **IMPLEMENTED** | public reconnect/reload smoke |
| Consequential actions | **REMOTE DENY-ALL** | correct Release 0 state |
| SECURITY-V1 full campaign | **PREREGISTERED** | post-release, except critical auth/tenant/secret negatives |
| Load/SLO/recovery/restore | **FINAL-DELIVERY WORK** | post-release except small concurrency/restart smoke |
| Human semantic calibration | **NOT READY** | post-release using real usage where permitted |
| Operational value | **NOT READY** | post-release |
| Adaptive runtime policy | **NO_CHANGE** | post-release challenger only after measured gap |
| GitHub main protection | **BLOCKED_USER_ACTION** | important governance; does not replace Release 0 runtime blockers |

## 3. What is already closed

### G2 remote foundation

The hosted production foundation has already proved, on prior exact-SHA hosted evidence:

- public Railway backend health/readiness;
- Railway/Caddy frontend hosting;
- remote Neon PostgreSQL serving substrate;
- non-superuser/NOBYPASSRLS scoped role structure;
- immutable artifact/runtime SHA verification;
- durable state surviving backend replacement/restart;
- USD0 hard-cost-policy metadata.

Do not re-open hosting/database/controller architecture unless a Release 0 blocker demonstrates a measured gap.

## 4. Release blockers in exact order

### R0-01 — Minimum hosted IAM acceptance

Must prove through the public product path:

- authentication/session lifecycle works;
- two users are independently scoped;
- cross-user/cross-tenant run/evidence/evaluation/SSE disclosure = 0;
- browser-forged organization/role/permission authority acceptance = 0;
- invalid/expired/impersonated sessions fail closed;
- RLS remains an independent boundary.

Consequential actions stay disabled.

### R0-02 — Real TRACTIAN bounded read

The direct HTTP adapter and source gates exist. Remaining release proof:

- authoritative server-side endpoint/auth configuration;
- one or more representative real reads through `ProductionTractianTransport`;
- canonical method/path/args/context;
- sanitized timeout/error behavior;
- redirect/credential leak/blind retry = 0;
- evidence persisted and visible through the real product path.

Configuration-only evidence is insufficient.

### R0-03 — Provisional USD0 provider qualification

The frozen full Provider Tournament v3 remains final-selection evidence and is not rewritten. Release 0 may separately qualify one existing USD0 Cloudflare candidate using a smaller governed campaign with honest state `PROVISIONAL_RELEASE_PROVIDER`.

Hard release constraints remain: USD0, no paid spillover, no hidden fallback, no private gold, no external action execution, explicit provider/model/route, strict DecisionSource contract and safe failure.

### R0-04 — Real production DecisionSource

Only after R0-03 may `NoSelectedProviderDecisionSource` be replaced for the user-serving composition. Production configuration must fail closed if provider calls are enabled without complete explicit provider credentials/model configuration.

### R0-05 — Genuine read-only agent vertical slice

Prove:

```text
real auth
→ real hosted model decision
→ real typed TRACTIAN read
→ real evidence
→ hosted model next decision
→ safe terminal mode
→ automatic evaluation
→ durable PostgreSQL
→ SSE/frontend
```

No provider-free/mock dependency participates.

### R0-06 — Minimum user UX/mode acceptance

Before users:

- one genuine investigation/final path;
- safe CLARIFY path;
- safe ABSTAIN path;
- safe ESCALATE path;
- evidence/lineage visible at a user-safe level;
- run history/reload and understandable failures;
- release/provider/TRACTIAN health visible to engineering view;
- hidden chain-of-thought remains private.

### R0-07 — External two-user smoke

From a fresh external browser/network: authenticate, submit a real question, observe genuine SSE/provider/TRACTIAN evidence, receive terminal result/evaluation, reload persisted state, prove second-user isolation, prove actions disabled, no local/mock dependency and observed cash cost USD0.

**When R0-01 through R0-07 pass, release immediately to users.**

## 5. Work moved behind first-user release

These remain part of the strongest final delivery but do not block Release 0:

- full 170-attempt Provider Tournament v3 and final provider promotion;
- governed consequential-action E2E;
- full hosted SECURITY-V1 population;
- full load staircase and evidence-based SLO;
- complete recovery/restore/RTO/RPO campaign;
- human semantic calibration;
- operational-value MANUAL vs AGENT-ASSISTED study;
- adaptive stopping/tool/provider challengers;
- final evidence freeze and presentation bundle.

Critical vulnerabilities found at any time can still stop or restrict the pilot.

## 6. Post-release priority

Real-user telemetry becomes the primary prioritization input:

```text
P0 auth / isolation / provider / TRACTIAN / broken-run defects
→ P1 wrong conclusions / bad tool choice / weak evidence / clarify-escalate UX
→ P1 latency, reliability and user friction
→ final tournament/security/load/recovery/action evidence
→ adaptive challengers only after measured gap
```

Do not add LangGraph, multi-agent, RAG/vector DB, MCP, Redis/Kafka, microservices, Kubernetes or persistent memory before Release 0 unless the current architecture cannot clear a concrete release blocker.

## 7. Documentation/evidence update rule

Every material change must synchronize, as applicable:

1. implementation/tests;
2. hosted/source evidence;
3. this active status;
4. `RELEASE-0-PLAN.md` / `RELEASE-0-ACCEPTANCE.md` when release semantics change;
5. PR #196 summary;
6. `decision-registry.yaml` when a material provisional/promoted decision changes;
7. chronological `docs/progress/` evidence.

Frozen historical artifacts are never rewritten to make current code appear historically valid.
