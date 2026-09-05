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
| 02 | Material decision registry | DONE | `decision-registry.yaml` created |
| 03 | Architecture manifest truthfulness | DONE | promoted PostgreSQL/identity/handoff/action/realtime architecture encoded + regression test added |
| 04 | Final remote hosting topology | IN_PROGRESS | clean Railway `production-api` from final branch; Dockerfile + public domain configured; final eligibility/latency evidence still open |
| 05 | Remote PostgreSQL role/schema promotion | DONE | Neon main: 15/15 required tables, 7/7 metadata, safe scoped role, owner validation; cross-tenant RLS test PASS on isolated validation branch |
| 06 | Remote backend boot / health / release identity | IN_PROGRESS | public domain + non-secret configuration present; approved secret injection and live boot still pending |
| 07 | Standards-based browser IAM | PLANNED | BFF/OIDC decision and implementation required |
| 08 | Multi-user / tenant negative acceptance | PLANNED | DB boundary ready; requires browser IAM and remote E2E |
| 09 | Hosted provider/model tournament | NO_SELECTION | new USD0 eligible experiment required |
| 10 | Real provider DecisionSource composition | BLOCKED | blocked on provider promotion |
| 11 | Real TRACTIAN production transport | PLANNED | direct typed HTTP adapter baseline; exact supplied contract/config must drive implementation |
| 12 | Real action authorization resolver | PLANNED | requires authenticated identity/resource mapping |
| 13 | Consequential action remote E2E | PLANNED | preserve custody/idempotency/non-transferable lease semantics |
| 14 | Production frontend deployment | PLANNED | React/Vite stack retained; remote host/topology to be selected |
| 15 | Authenticated REST + SSE | PLANNED | same-origin/BFF preferred baseline |
| 16 | Production Control Room completeness | PLANNED | live architecture/evidence/lineage/eval/health |
| 17 | Infrastructure telemetry | PLANNED | RunTrace remains domain truth; OTel-compatible challenger |
| 18 | Realtime reconnect/recovery campaign | PLANNED | must include DB sleep/wake and cursor catch-up |
| 19 | Adversarial security campaign | PLANNED | tenant/prompt/tool/action/evaluator failure families |
| 20 | Remote load/capacity campaign | PLANNED | derive measured free-tier envelope and SLO claims |
| 21 | GitHub main protection | PLANNED | require PR + `final-ci-required / required-gate` |
| 22 | CI/CD + rollback + provenance | PLANNED | staging/prod smoke, rollback, SBOM/attestation when eligible |
| 23 | Human semantic calibration | NOT_READY | real blinded labels required before semantic judge gates |
| 24 | Operational-value experiment | NOT_READY | real MANUAL vs AGENT-ASSISTED observations required |
| 25 | Adaptive runtime challengers | PLANNED / P1 | only after P0 production closure |
| 26 | Final remote E2E / evidence freeze / release | PLANNED | all applicable P0 gates must be evidence-backed |

## 5. Exact critical-path order

Do not displace this sequence with optional complexity:

```text
01 active truth                                      DONE
02 decision registry                                 DONE
03 architecture truth                                DONE
04 remote hosting                                    IN_PROGRESS
05 PostgreSQL roles + migration                      DONE
06 backend live shell + health/version               IN_PROGRESS
07 IAM/BFF/OIDC                                      NEXT PRODUCT BLOCKER
08 multi-user/RLS acceptance
09 provider tournament
10 real DecisionSource
11 TRACTIAN transport
12 authorization resolver
13 action E2E
14 frontend hosting
15 authenticated REST/SSE
16 Control Room completeness
17 telemetry
18 realtime recovery
19 adversarial security
20 remote load/capacity
21 GitHub protection
22 CI/CD + rollback/provenance
23 semantic calibration where feasible
24 operational value where feasible
25 adaptive challengers only after P0
26 final E2E + evidence bundle + release
```

## 6. P0-A — Architecture and governance truth

### Status: DONE for current baseline

- active status is rebaselined to the actual final branch and external infrastructure state;
- `architecture_manifest.py` now represents PostgreSQL operational truth, trusted identity, runtime handoff, action custody/lease, human review/value and non-authoritative realtime wake-up;
- the legacy `DuckDB Safe Read Model` label is removed from the promoted architecture;
- a regression test prevents that storage truth from silently reverting;
- material decisions have an explicit registry.

Architecture must continue to be updated whenever the runtime composition changes.

## 7. P0-B — Remote PostgreSQL production substrate

### Status: STRUCTURAL PROMOTION DONE; runtime recovery campaign remains separate

The existing Neon `academy-tractian-hosted-pilot` / `academy_tractian` database now contains the promoted `academy_operational` schema.

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

A clean Railway service named `production-api` has been created from `release/production-final`, separate from the stale historical `hosted-pilot`. The service is configured to use the repository Dockerfile, restart on failure and expose a Railway HTTPS service domain. Non-secret fail-closed production settings are installed.

### Required next

- provide `ACADEMY_POSTGRES_INTERNAL_DSN`, `ACADEMY_POSTGRES_SCOPED_DSN` and `ACADEMY_RUNTIME_IDENTITY_SECRET` through an approved secret channel;
- update `ACADEMY_RELEASE_GIT_SHA` to the exact final-branch deployment commit;
- redeploy the current branch;
- verify database connectivity, release identity and health/readiness;
- prove restart/persistence;
- keep provider calls disabled until DP-004 promotes a candidate.

### Secret-handling rule

DSNs/signing secrets are never committed, written to project documentation or exposed to the browser. If an automation connector rejects secret transmission, use the platform secret UI or another approved native secret mechanism rather than weakening fail-closed configuration.

## 9. P0-D — Browser IAM and multi-user product

Target baseline:

```text
Browser
→ OIDC Authorization Code + PKCE
→ BFF / FastAPI
→ Secure HttpOnly session
→ server-owned user/org/permissions
→ PostgreSQL tenant boundary
```

The internal HMAC runtime bearer may remain behind this boundary but must not be marketed as end-user IAM.

Acceptance includes login/logout/session lifecycle, authenticated SSE, manipulated/expired session failure, cross-tenant REST/SSE/SQL denial and zero browser-owned privilege authority.

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

Production areas should expose safe real state for:

- Mission Control;
- Live Run Cockpit;
- Timeline/Waterfall;
- Trace Graph;
- Architecture Explorer;
- Evidence Explorer;
- Output Lineage;
- Action Control;
- Eval Lab;
- Provider Lab;
- Dynamic Data Explorer;
- Production Health;
- Operational Value when real evidence exists.

Never expose secrets, private evaluator/gold material or hidden chain-of-thought.

## 13. P0-H — Production proof campaigns

### Realtime/recovery

Prove durable rows/cursors recover all committed events after SSE disconnect, backend restart, listener loss and DB suspend/wake. `LISTEN/NOTIFY` remains wake-up only.

### Adversarial security

At minimum cover tenant spoofing/cross-tenant access, token/session manipulation, direct/indirect prompt injection, tool-output injection, permission bypass, action confirmation bypass/replay, evaluator/gold extraction and provider/tool/DB failures.

Hard safety expectations include zero tenant escape, zero unauthorized consequential action, zero confirmation bypass, zero gold leakage and zero credential leakage.

### Remote capacity

Run increasing concurrency on the actual selected free deployment until measured saturation or free-tier quota. Report p50/p95/p99, throughput, errors/timeouts, DB/provider/tool latency, SSE behavior, resource/quota use and actual cash cost. State the measured envelope rather than claiming unproved scale.

## 14. P0-I — Repository protection and release

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

Eligible challenger areas:

- adaptive investigation depth;
- adaptive tool/evidence ordering;
- adaptive clarification/abstention/escalation thresholds;
- provider routing among multiple already-qualified USD0 candidates;
- bounded retry/backoff/resource budgets.

Always deterministic:

- authentication/tenant binding;
- RLS/authorization;
- schemas/permissions;
- consequential-action confirmation/custody/idempotency/leases;
- privacy deny-lists;
- evaluator/gold isolation;
- hard resource/cost boundaries.

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

Use capability-scoped truth rather than one vague `production-ready` label. Each final capability is classified as one of:

`READY`, `LIMITED`, `NOT_READY`, `NO_SELECTION`.

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
