# Academy × TRACTIAN — Final Master Implementation Plan

**Status:** ACTIVE / canonical execution authority  
**Checkpoint:** 2026-09-05 BRT  
**Delivery target:** 2026-09-08  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**Principles:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Decision registry:** [`decision-registry.yaml`](decision-registry.yaml)

This is the authoritative dependency-ordered implementation plan. Frozen historical evidence remains immutable.

## 1. North Star

Prove one real remote product:

```text
authenticated user
→ trusted tenant context
→ public HTTPS frontend
→ remote FastAPI
→ selected hosted model
→ typed real TRACTIAN tools
→ evidence-grounded investigation
→ FINAL | CLARIFY | ABSTAIN | ESCALATE | ACTION_PROPOSAL
→ governed consequential action when applicable
→ automatic evaluation
→ durable PostgreSQL persistence
→ REST/SSE observability
→ live Control Room
→ quantitative security/reliability/value evidence
```

## 2. Engineering rules

Every material change follows:

```text
requirement / measured risk
→ baseline
→ alternatives
→ hard constraints
→ metrics + gates
→ implementation
→ controlled + failure validation
→ PROMOTE | REJECT | INCONCLUSIVE | NO_CHANGE | NO_SELECTION
→ regression guard
→ documentation/evidence synchronization
```

Do not add LangGraph, multi-agent, MCP, RAG/vector DB, Redis/Kafka, microservices or Kubernetes without a measured gap and challenger experiment. Deterministic boundaries remain authoritative for identity, authorization, RLS, schemas, action confirmation, custody, idempotency, leases/fencing, secrets, hard limits and evaluator-gold isolation.

## 3. Progress ledger

| # | Workstream | State | Current evidence / next gate |
|---:|---|---|---|
| 01 | Architecture/runtime baseline | DONE | PostgreSQL + SSE + runtime handoff + action leases + evaluator + frontend regression |
| 02 | Decision registry / active docs | DONE | current mutable truth separated from frozen evidence |
| 03 | Main branch protection | BLOCKED_USER_ACTION | admin write unavailable through current GitHub connector |
| 04 | Railway topology reproducibility | IN_PROGRESS | `.railway/railway.ts`, static validator and CI versioned; live plan/apply pending |
| 04A | Backend release artifact identity | DONE_SOURCE_GATE | baked Railway Git SHA + OCI label + boot cross-check; `a9356e…` required CI PASS; hosted parity pending |
| 05 | Neon schema/RLS promotion | DONE | 15/15 tables, 7/7 metadata, NOBYPASSRLS scoped role, RLS negative PASS |
| 06 | Railway frontend production | DONE | HTTPS `production-web`, Caddy same-origin auth/API/SSE, deploy SUCCESS |
| 07 | Railway backend boot | BLOCKED_USER_ACTION | exactly two PostgreSQL DSNs absent; next deploy must pass release identity v3 |
| 08 | Live IAM / multi-user acceptance | WAITING_DEPENDENCY | offline negative-gap hardening done; hosted acceptance requires #07 |
| 09 | Provider tournament | PREREGISTERED / NO_SELECTION | v3: 17 fresh scenarios × 5 reps/candidate; USD0 quota packets + validator/test gate; live runs not executed |
| 10 | Real DecisionSource composition | WAITING_DEPENDENCY | requires #09 promotion |
| 11 | TRACTIAN production adapter/composition | ADAPTER_IMPLEMENTED | hardened direct HTTP adapter + fail-closed UNCONFIGURED/CONFIGURED_UNVERIFIED states; live contract/reachability pending |
| 12 | Real authorization resolver | WAITING_DEPENDENCY | requires live identity/resource mapping |
| 13 | Consequential action remote E2E | WAITING_DEPENDENCY | requires #08-#12 |
| 14 | Full remote public E2E | WAITING_DEPENDENCY | requires #08-#13 |
| 15 | Adversarial security campaign | PLANNED | hosted functional system required |
| 16 | Load/capacity campaign | PLANNED | hosted provider/TRACTIAN path required |
| 17 | Restart/reconnect/recovery campaign | PLANNED | hosted functional backend required |
| 18 | Backup/restore drill | PLANNED | remote durable path required |
| 19 | Human semantic calibration | NOT_READY | blinded human labels required |
| 20 | Operational-value experiment | NOT_READY | MANUAL vs AGENT-ASSISTED observations required |
| 21 | Control Room final live surfaces | PLANNED | real provider/tool/eval data required |
| 22 | Optional OTel infrastructure telemetry | P1 | only if measured observability gap appears |
| 23 | Adaptive Evidence Stopping | P1 | only after static production baseline |
| 24 | Release/rollback/evidence freeze | WAITING_DEPENDENCY | all P0 hard gates green |

## 4. Exact execution order

```text
A. protect main                                      BLOCKED_USER_ACTION
B. version/validate Railway topology                 IN_PROGRESS
B.5 prove immutable backend release identity         SOURCE GATE PASS / HOSTED PROOF PENDING
C. inject two Railway PostgreSQL secrets             BLOCKED_USER_ACTION
D. boot exact-SHA backend + health/release/DB/restart
E. live IAM + two-user/two-tenant + shared-org tests
F. execute preregistered provider tournament
G. promote and compose real DecisionSource
H. compose real TRACTIAN typed transport              ADAPTER READY / LIVE CONFIG PENDING
I. validate Contextualize / Investigate / Clarify / Abstain / Escalate
J. compose real authorization resolver
K. enable and validate governed remote actions
L. full public remote E2E
M. adversarial security
N. load/capacity
O. restart/reconnect/recovery
P. backup/restore
Q. human semantic calibration
R. operational-value experiment
S. final Control Room/live evidence
T. decision/doc synchronization
U. final evidence freeze + rollback + merge/release
```

Independent preparation may continue while an external user-action gate is blocked, but no downstream capability is promoted before its dependencies are satisfied.

## 5. P0-A — Repository governance

Hard requirements: protect `main`; require PR; require `final-ci-required / required-gate`; require an up-to-date branch; disable force push and deletion.

## 6. P0-B — Reproducible Railway topology

Use current Railway Infrastructure as Code in `.railway/railway.ts`. The named `production` partial manages only `production-api` and `production-web`; historical `hosted-pilot` remains outside its scope. Railway-managed values/secrets use `preserve()`. Repository validation must reject literal DSNs/secrets or unexpected service scope. TypeScript DSL validation runs in dedicated CI. Before first apply, review `railway config plan`; any unexpected delete or `hosted-pilot` change fails the gate.

Current API deployment intent:

```text
healthcheck     /health
health timeout  60s
restart         ON_FAILURE / 5 retries
replicas        1 @ us-east4-eqdc4a
```

### P0-B.5 — Immutable release identity

A production backend image must be attributable to the exact Git commit that built it, not merely to a mutable runtime variable.

Required invariant:

```text
Railway Git-backed build SHA
= /app/.academy-release-identity.json git_sha
= OCI org.opencontainers.image.revision
= configured ACADEMY_RELEASE_GIT_SHA
= runtime RAILWAY_GIT_COMMIT_SHA when exposed
= /api/meta/release release_git_sha
= /api/meta/release artifact_git_sha
```

Missing/malformed identity or any mismatch aborts before PostgreSQL/IAM product builders open connections. At validated implementation head `a9356e217fbf7c94549849a7cdb8554a449e947b`, `production-runtime`, wheel/image smoke, clean-clone, Playwright and `final-ci-required / required-gate` all pass. Hosted exact-SHA observation remains a separate G2 gate.

## 7. P0-C — Remote backend boot

User installs, only through Railway native secrets:

```text
ACADEMY_POSTGRES_INTERNAL_DSN
ACADEMY_POSTGRES_SCOPED_DSN
```

Then: exact-SHA redeploy → `/health` 200 → `/api/meta/release` v3 exact identity equality → internal/scoped DB connections PASS → schema/stores READY → create durable state → restart → state/cursor persist. Provider calls remain disabled.

A G2 release check passes only if:

```text
release_git_sha == artifact_git_sha == expected deployed commit
artifact_identity_verified == true
railway_runtime_identity_verified == true   # when Railway exposes runtime SHA
```

## 8. P0-D — IAM + multi-tenancy

Live acceptance must prove separate tenants with zero cross-tenant REST/SSE/action access, intended same-organization multi-user behavior, browser organization/user/role/permission claims ignored or denied, invalid/expired/mismatched/impersonated sessions fail closed, and CSRF/origin/cookie/session invalidation behavior before actions are enabled.

Provider-free/offline tests may harden these boundaries while G2 is blocked, but IAM cannot be promoted to READY without hosted two-user/two-tenant evidence.

## 9. P0-E — Provider tournament

The v3 campaign is preregistered over `17 fresh canonical scenarios × 5 repetitions = 85 runs` per candidate, 170 total across the two current Cloudflare candidates. Historical D01/D02 results are excluded from the v3 denominator.

The USD0 campaign is partitioned into five UTC daily packets of 34 calls. No packet may start unless the free quota headroom passes the preregistered conservative gate; no paid spillover is authorized.

Measure outcome accuracy, tool recall/irrelevance, argument validity, evidence correctness/coverage, clarification/abstention/escalation, unsupported claims/false precision, action safety, turns/tool calls, p50/p95/p99, failures/429/quota, stability and actual cash cost. USD0, zero gold leakage, zero unsafe unsupported consequential action, policy integrity and valid structured schema are hard gates.

The only valid campaign decisions are `PROMOTE`, `REJECT`, `INCONCLUSIVE`, or `NO_SELECTION`. Preregistration alone does not select a provider.

## 10. P0-F — Real provider + TRACTIAN

Only a promoted provider replaces `NoSelectedProviderDecisionSource`.

The TRACTIAN production adapter is already implemented and source-gated independently of provider selection. Its default composition is fail-closed:

```text
NO_SELECTION provider
+ UNCONFIGURED TRACTIAN transport
+ DENY-ALL actions
```

An explicit complete endpoint/header configuration may advance TRACTIAN only to `CONFIGURED_UNVERIFIED`. Construction performs zero network I/O and therefore does not establish reachability.

The direct adapter enforces:

```text
typed canonical tool
→ exact method/path
→ canonical path encoding
→ validated query/body/header boundary
→ server-managed credentials at network edge only
→ no redirect following
→ bounded timeout and payload sizes
→ zero automatic retry
→ sanitized normalized response/error
→ evidence
```

No authentication scheme is assumed until an authoritative partner contract supplies it. Read retry remains disabled until measured proof justifies it; consequential writes never receive blind retry.

Live promotion requires authoritative endpoint/auth configuration plus bounded read acceptance. Complete, partial, inconclusive, conflicting and unavailable API behavior must remain distinguishable in controller evidence before the required agent modes are accepted.

## 11. P0-G — Required agent modes

Hosted acceptance covers Contextualize, Investigate, Clarify, Abstain, Escalate and Action Proposal, evaluated on outcome, trajectory, evidence, unnecessary calls, unsupported claims and escalation usefulness.

Offline preparation should first make read-response quality explicit so an HTTP-success response cannot silently erase partial/inconclusive/conflicting state.

## 12. P0-H — Governed actions

```text
ACTION_PROPOSAL
→ deterministic validation
→ private custody
→ PENDING_CONFIRMATION
→ authenticated confirmation
→ authorization + kill-switch revalidation
→ idempotency
→ non-transferable execution lease
→ one exact remote attempt
→ SUCCEEDED | FAILED | UNCERTAIN
→ evaluation
```

Hard gate: platform-caused duplicate consequential side effects = 0.

## 13. P0-I — Full remote E2E

From an independent external client: public HTTPS → auth → run → SSE → hosted model → real TRACTIAN → evidence → final state → automatic eval → PostgreSQL → reload/persist. Action scenario additionally proves confirmation and remote execution. Zero localhost, local DB/model, fake provider or fake TRACTIAN in production.

## 14. P0-J — Production proof campaigns

Security uses Threat → Control → Test → Evidence for prompt/tool injection, excessive agency, privilege escalation, confused deputy, tenant/SSE bypass, action replay, CSRF/session manipulation, secret/gold leakage and resource exhaustion. Capacity ramps `1,2,4,8,16,...` to saturation/quota and reports measured envelope only. Recovery covers backend/DB/SSE/provider/tool/worker/lease failures. Backup/restore is performed for real before RTO/RPO claims.

## 15. P0-K — Human/value evidence

Semantic evaluation remains non-gating until blinded human calibration; target where feasible `17 scenarios × 3 reviewers = 51 reviews`. Operational value compares MANUAL vs AGENT-ASSISTED, with primary KPI Time to Correct Operational Decision and measured distributions/deltas only.

## 16. P1 after P0 closure

Adaptive Evidence Stopping only after the static baseline and only if quality/safety are non-worse with material resource improvement. OpenTelemetry only as sanitized infrastructure telemetry; RunTrace remains semantic truth.

## 17. Hard release gate

Any red hard gate = `NOT READY`. Required: remote frontend/backend/PostgreSQL/provider/TRACTIAN; real IAM and multi-user isolation; all required modes; governed remote action; full remote E2E; security/load/recovery/backup evidence; protected main + required CI; reproducible deployment + rollback; immutable exact-SHA release identity; no local dependency/mocks/secrets/gold/cross-tenant leakage; synchronized docs and evidence.
