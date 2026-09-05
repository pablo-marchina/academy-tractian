# Academy × TRACTIAN — Final Master Implementation Plan

**Status:** ACTIVE / canonical execution authority  
**Checkpoint:** 2026-09-05 BRT  
**Delivery target:** 2026-09-08  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**Principles:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Decision registry:** [`decision-registry.yaml`](decision-registry.yaml)

This is the authoritative implementation plan for the final production promotion. It replaces prior sequencing documents prospectively. Frozen/historical evidence remains unchanged.

## 1. North Star

Deliver the strongest defensible TRACTIAN × Inteli product: a remotely hosted, multi-user, tenant-safe Industrial Agent + Evaluation platform with live frontend observability, quantitative/eval-driven engineering and zero developer-machine dependency in the production serving path.

Project-wide hard constraints apply simultaneously:

```text
actual project cash cost = USD 0
AND no automatic paid spillover
AND remote production serving
AND no local serving dependency
AND multi-user / tenant-safe
AND live frontend
AND deterministic safety boundaries
AND quantitative evidence where validly measurable
AND EDD for every material change
AND adaptive behavior only after beating a simpler baseline
AND systematic research before material technical decisions
AND claims never exceed evidence
```

## 2. Execution rule

Every material work item follows:

```text
requirement / risk / measured gap
→ hard constraints
→ baseline
→ researched alternatives
→ metrics + hard gates
→ implementation candidate
→ controlled evaluation
→ failure/adversarial evaluation
→ PROMOTE / REJECT / NO_CHANGE / NO_SELECTION
→ regression protection
→ documentation + evidence synchronization
```

No framework, provider, model, database, IAM, hosting, telemetry or architecture component is promoted merely because it is modern, popular or already implemented.

## 3. Mandatory change synchronization

Every material implementation change is incomplete until all applicable records are synchronized in the same development flow:

1. **Code / infrastructure** — actual implementation or platform state.
2. **Validation evidence** — tests, remote checks, experiment or explicit blocker.
3. **Documentation** — current truth, plan progress and architecture/decision records when relevant.

Document ownership:

- current state → `ACTIVE-PROJECT-STATUS.md`;
- execution order/progress → this file;
- architecture → `ARCHITECTURE.md` + `architecture_manifest.py` when product-visible;
- material choices → `decision-registry.yaml` + ADR/evidence where warranted;
- final acceptance → `DELIVERY-ACCEPTANCE.md`;
- TAPI mapping → `TAPI-DELIVERY-COVERAGE-2026-09-02.md`;
- operational commands/recovery → `FINAL-HANDOFF-RUNBOOK.md`;
- chronological implementation evidence → `docs/progress/`.

Frozen/source-pinned documents are never rewritten to match later state.

## 4. Progress ledger

States: `DONE`, `IN_PROGRESS`, `BLOCKED`, `PLANNED`, `NOT_READY`, `NO_SELECTION`.

| # | Workstream | State | Evidence / next gate |
|---:|---|---|---|
| 01 | Rebaseline active project truth | DONE | `ACTIVE-PROJECT-STATUS.md` synchronized |
| 02 | Material decision registry | DONE | `decision-registry.yaml` created and updated as promotion evidence changes |
| 03 | Architecture manifest truthfulness | DONE | promoted PostgreSQL/identity/handoff/action/realtime architecture encoded + regression test |
| 04 | Final remote hosting topology | IN_PROGRESS | Railway `production-api` + `production-web` on final branch; frontend remote deploy PASS; backend boot still blocked by approved DSN injection |
| 05 | Remote PostgreSQL role/schema promotion | DONE | Neon main: 15/15 tables, 7/7 metadata, safe scoped role and RLS negative test PASS |
| 06 | Remote backend boot / health / release identity | BLOCKED | managed-IAM mode removes browser HMAC secret; only internal/scoped PostgreSQL DSNs remain blocked by connector secret-transfer policy |
| 07 | Browser IAM / managed session boundary | IN_PROGRESS | Neon Auth challenger + React AuthBoundary + server-side session verifier implemented; PR #196 regression/remote acceptance pending |
| 08 | Multi-user / tenant negative acceptance | PLANNED | DB RLS gate ready; requires live backend managed-session path |
| 09 | Hosted provider/model tournament | NO_SELECTION | new USD0 eligible experiment required |
| 10 | Real provider DecisionSource composition | BLOCKED | blocked on provider promotion |
| 11 | Real TRACTIAN production transport | PLANNED | direct typed HTTP adapter baseline; exact supplied contract/config must drive implementation |
| 12 | Real action authorization resolver | PLANNED | requires authenticated identity/resource mapping |
| 13 | Consequential action remote E2E | PLANNED | preserve custody/idempotency/non-transferable lease semantics |
| 14 | Production frontend deployment | IN_PROGRESS | Railway/Caddy production-web deployment PASS; authenticated backend E2E still pending |
| 15 | Authenticated REST + SSE | IN_PROGRESS | Caddy same-origin `/auth` + `/api` proxy implemented; backend session composition under CI and remote boot blocked on DSNs |
| 16 | Production Control Room completeness | PLANNED | live architecture/evidence/lineage/eval/health after remote data path closes |
| 17 | Infrastructure telemetry | PLANNED | RunTrace remains domain truth; OTel-compatible challenger only if needed |
| 18 | Realtime reconnect/recovery campaign | PLANNED | must include DB sleep/wake and cursor catch-up |
| 19 | Adversarial security campaign | PLANNED | tenant/session/prompt/tool/action/evaluator failure families |
| 20 | Remote load/capacity campaign | PLANNED | derive measured free-tier envelope and SLO claims |
| 21 | GitHub main protection | PLANNED | PR #196 now supplies final-branch CI; main protection still must require `final-ci-required / required-gate` |
| 22 | CI/CD + rollback + provenance | IN_PROGRESS | draft PR #196 created; PR workflows active; production deploy/rollback automation remains open |
| 23 | Human semantic calibration | NOT_READY | real blinded labels required before semantic judge gates |
| 24 | Operational-value experiment | NOT_READY | real MANUAL vs AGENT-ASSISTED observations required |
| 25 | Adaptive runtime challengers | PLANNED / P1 | only after P0 production closure |
| 26 | Final remote E2E / evidence freeze / release | PLANNED | all applicable P0 gates must be evidence-backed |

## 5. Exact critical-path order

Do not displace this sequence with optional complexity. A blocked dependency may allow implementation work on the immediately following item, but final promotion still respects dependency order.

```text
01 active truth                                      DONE
02 decision registry                                 DONE
03 architecture truth                                DONE
04 remote hosting                                    IN_PROGRESS
05 PostgreSQL roles + migration                      DONE
06 backend live shell + health/version               BLOCKED ON APPROVED DSN INJECTION
07 browser IAM / managed session                     IN_PROGRESS
08 multi-user/RLS remote acceptance                  NEXT AFTER LIVE BACKEND
09 provider tournament
10 real DecisionSource
11 TRACTIAN transport
12 authorization resolver
13 action E2E
14 frontend hosting                                  REMOTE BASELINE PASS / E2E OPEN
15 authenticated REST/SSE                            IN_PROGRESS
16 Control Room completeness
17 telemetry
18 realtime recovery
19 adversarial security
20 remote load/capacity
21 GitHub protection
22 CI/CD + rollback/provenance                       PR CI ACTIVE
23 semantic calibration where feasible
24 operational value where feasible
25 adaptive challengers only after P0
26 final E2E + evidence bundle + release
```

## 6. P0-A — Architecture and governance truth

### Status: DONE for current baseline

- active status is rebaselined to the actual final branch and external infrastructure state;
- `architecture_manifest.py` represents PostgreSQL operational truth, trusted identity, runtime handoff, action custody/lease, human review/value and non-authoritative realtime wake-up;
- the legacy `DuckDB Safe Read Model` label is removed from the promoted architecture;
- a regression test prevents that storage truth from silently reverting;
- material decisions have an explicit registry;
- PR #196 is the draft integration/review surface for the final branch.

Architecture must continue to be updated whenever the runtime composition changes.

## 7. P0-B — Remote PostgreSQL production substrate

### Status: STRUCTURAL PROMOTION DONE; runtime recovery campaign remains separate

The existing Neon `academy-tractian-hosted-pilot` / `academy_tractian` database contains the promoted `academy_operational` schema.

Migration was first validated on an isolated Neon branch, then applied to main using the same idempotent DDL groups derived from the production runtime initializers.

Production-branch structural evidence:

```text
required tables                    15 / 15
required operational meta           7 / 7
observability schema meta            PASS
scoped role                          academy_tractian_rls
scoped role superuser                false
scoped role BYPASSRLS                false
run_ownership owner                  academy_tractian_owner
tenant SELECT policies               5
```

RLS evidence on the isolated migration-validation branch:

```text
stored org-a row                     yes
stored org-b row                     yes
SET ROLE academy_tractian_rls        yes
academy.organization_id=org-a        yes
visible org-a row                    yes
visible org-b row                    no
result                               PASS
```

The unsafe `academy_live_scoped` role remains excluded because it can bypass RLS.

Remaining database evidence belongs to P0-H rather than schema promotion: remote application connection, suspend/wake reconnect, cursor catch-up, capacity and recovery.

## 8. P0-C — Remote backend promotion

### Current evidence

A clean Railway service named `production-api` exists separately from the stale historical `hosted-pilot`. Its GitHub source branch is explicitly `release/production-final`, it builds the repository Python 3.11 production Dockerfile, runs in Railway US East Metal, restarts on failure and has a Railway HTTPS service domain.

The prior fail-closed deployment proved that missing production secrets stop serving boot rather than silently falling back.

### Required next

- install only the two remaining PostgreSQL DSNs through an approved Railway secret channel:
  - `ACADEMY_POSTGRES_INTERNAL_DSN` using the owner/internal role;
  - `ACADEMY_POSTGRES_SCOPED_DSN` using `academy_tractian_rls`;
- do not commit, document or proxy those values through an unapproved connector;
- redeploy the exact final-branch SHA;
- verify database connectivity, `/health`, release identity and restart/persistence;
- keep provider calls disabled until DP-004 promotes a candidate.

The managed `neon-auth` browser IAM mode intentionally does **not** require `ACADEMY_RUNTIME_IDENTITY_SECRET`, issuer or audience for the browser path. This removes an obsolete browser-HMAC secret from the final web topology while preserving the old signed-bearer mode as a rollback-compatible composition.

## 9. P0-D — Browser IAM and multi-user product

### Current challenger: Neon Auth / Better Auth managed session

The original OIDC+BFF target remains a valid baseline, but the current USD0 challenger is a managed Neon Auth session behind the same-origin product boundary.

Implemented in the final branch:

```text
Browser
→ production-web HTTPS origin
→ /auth/* same-origin Caddy proxy
→ Neon Auth / Better Auth managed HttpOnly session
→ /api/* same-origin Caddy proxy
→ FastAPI NeonAuthRuntimeContextProvider
→ server-side managed-session revalidation
→ server-owned user / tenant / permissions
→ PostgreSQL tenant boundary
```

Security invariants:

- browser request body/headers cannot assert organization, role or permissions;
- missing/invalid/mismatched/impersonated sessions fail closed;
- session service failure fails closed;
- shared active organization comes only from managed session state;
- without an active shared organization, tenant defaults to deterministic `user:<authenticated-user-id>` personal isolation;
- default runtime permissions stay server-defined;
- no auth token/DSN is stored in React state or committed to source.

Promotion still requires PR regression success and live multi-user REST/SSE negative acceptance. If those gates fail, DP-003 remains reversible to OIDC+BFF or another eligible design.

## 10. P0-E — Provider/model selection

Current state is `NO_SELECTION`.

Run a new preregistered tournament among currently hosted USD0-eligible candidates. Paid candidates may appear only as non-selectable references.

Primary dimensions:

- operational conclusion accuracy;
- required-tool recall / unnecessary-tool count;
- semantic argument accuracy;
- evidence correctness;
- clarification/escalation/abstention correctness;
- consequential-action safety;
- repeated-run stability;
- p50/p95/p99 latency;
- failure/quota behavior;
- actual cash cost.

No candidate may be promoted if a hard integrity/safety gate fails.

## 11. P0-F — Real TRACTIAN path and governed actions

Compose the real typed TRACTIAN HTTP transport only after server-managed credentials, timeout/error normalization and retry semantics are explicit. The supplied TRACTIAN contract/package is authoritative; do not guess endpoint URLs or parameters from generic expectations.

Read retries may be safe when bounded. Consequential writes must retain the existing contract:

```text
proposal
→ deterministic validation
→ private custody
→ confirmation
→ current authorization
→ idempotency
→ non-transferable execution lease
→ one transport attempt
→ SUCCEEDED | FAILED | UNCERTAIN
```

Blind replacement/replay remains forbidden.

## 12. P0-G — Frontend production and live visibility

Retain React 19 + TypeScript + Vite + TanStack Query + ECharts + React Flow + Vitest + Playwright.

Current remote baseline:

- `production-web` Railway service;
- React/Vite multi-stage production image;
- Caddy static SPA serving;
- HTTPS public Railway domain;
- same-origin `/auth` and `/api` routing;
- `/api` proxy targets Railway private `production-api` networking;
- SSE buffering explicitly disabled at the Caddy reverse proxy;
- authenticated React boundary prevents product queries from starting before a valid managed session is present.

Remote deployment reached `SUCCESS`. Final frontend promotion still requires live auth/API/SSE behavior, browser acceptance and performance evidence.

Production areas should expose safe real state for Mission Control, Live Run Cockpit, timeline/waterfall, Trace Graph, Architecture Explorer, evidence/output lineage, Action Control, Eval Lab, provider experiments, Dynamic Data Explorer, Production Health and real Operational Value evidence when available.

Never expose secrets, private evaluator/gold material or hidden chain-of-thought.

## 13. P0-H — Production proof campaigns

### Realtime/recovery

Prove durable rows/cursors recover all committed events after SSE disconnect, backend restart, listener loss and DB suspend/wake. `LISTEN/NOTIFY` remains wake-up only.

### Adversarial security

At minimum cover tenant spoofing/cross-tenant access, session manipulation, direct/indirect prompt injection, tool-output injection, permission bypass, action confirmation bypass/replay, evaluator/gold extraction and provider/tool/DB failures.

Hard safety expectations include zero tenant escape, zero unauthorized consequential action, zero confirmation bypass, zero gold leakage and zero credential leakage.

### Remote capacity

Run increasing concurrency on the actual selected free deployment until measured saturation or free-tier quota. Report p50/p95/p99, throughput, errors/timeouts, DB/provider/tool latency, SSE behavior, resource/quota use and actual cash cost. State the measured envelope rather than claiming unproved scale.

## 14. P0-I — Repository protection and release

Draft PR #196 now provides the integration surface and triggers the PR CI matrix. It remains draft until applicable P0 gates are evidence-backed.

Before final production completion:

- protect `main`;
- require PR;
- require `final-ci-required / required-gate`;
- restrict direct/force pushes;
- execute staging/production smoke checks;
- test rollback;
- preserve build/release provenance;
- produce SBOM/artifact attestation if available under the project constraints;
- freeze a final evidence index linking URLs, release SHA, architecture, decisions, experiments, security/load/recovery evidence and limitations.

## 15. P1 — Adaptive challengers

Do not start until the P0 remote product path is closed.

Eligible challenger areas include adaptive investigation depth, adaptive tool/evidence ordering, adaptive clarification/abstention/escalation thresholds, provider routing among already-qualified USD0 candidates and bounded retry/backoff/resource budgets.

Always deterministic: authentication/tenant binding, RLS/authorization, schemas/permissions, consequential-action confirmation/custody/idempotency/leases, privacy deny-lists, evaluator/gold isolation and hard resource/cost boundaries.

Promotion requires a measured win versus the static baseline without safety regression.

## 16. Explicitly deferred unless a measured gap appears

The following must not displace the critical path:

- LangGraph/LangChain/PydanticAI migration;
- multi-agent decomposition;
- RAG/vector database;
- persistent semantic memory;
- MCP conversion;
- Redis/Kafka;
- Kubernetes/microservice decomposition;
- frontend framework rewrite.

They remain valid future challengers only when a concrete measured problem justifies evaluation.

## 17. Final release gate

Use capability-scoped truth rather than one vague `production-ready` label. Each final capability is classified as one of `READY`, `LIMITED`, `NOT_READY`, `NO_SELECTION`.

The final remote E2E should prove, from an unrelated device/network:

```text
public URL
→ user authentication
→ tenant-bound request
→ live agent execution
→ real provider
→ real TRACTIAN tools
→ safe final/escalation/action behavior
→ post-runtime evaluation
→ trace/evidence/output lineage
→ reconnect and persisted history
→ architecture + release identity + production health
```

A second tenant must be unable to see the first tenant's private state.

## 18. Completion discipline

The objective is to become usable as fast as possible without creating unsupported production claims. Therefore:

- finish the smallest safe end-to-end production path before optional refinements;
- fix blockers in dependency order;
- preserve accepted working core architecture;
- prefer an explicit blocker over an unsafe workaround;
- continuously update this ledger, active state and relevant architecture/decision records as work lands.
