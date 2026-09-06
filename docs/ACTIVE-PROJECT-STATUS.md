# Academy × TRACTIAN — Current Project Status

**Status:** production implementation / hosted promotion in progress  
**Checkpoint:** 2026-09-06 BRT  
**Current `main`:** `12b4753d3e39c86f7c68f0ea7b4f321549049fc7`  
**Implementation branch:** `release/production-final`  
**Draft integration PR:** `#196`  
**Currently served backend artifact:** `234655d952d62e1c26300fe6fd72f8d44df53001`  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**Decision registry:** [`decision-registry.yaml`](decision-registry.yaml)

This file is the mutable source of truth for current state. Historical/frozen evidence remains immutable. A source/CI pass is not promoted to a hosted claim unless independently observed on the public production path.

## 1. North Star

```text
authenticated remote user
→ trusted server-owned tenant context
→ public HTTPS frontend
→ remote FastAPI
→ selected hosted USD0 DecisionSource
→ AgentController
→ 18 typed TRACTIAN operations
→ real TRACTIAN evidence
→ FINAL | CLARIFY | ABSTAIN | ESCALATE | ACTION_PROPOSAL
→ governed action when applicable
→ deterministic + calibrated evaluation
→ durable Neon PostgreSQL
→ REST/SSE observability
→ live React Control Room
→ quantitative security/reliability/value evidence
```

Hard constraints remain: actual project cash cost USD 0, no paid spillover, no local serving dependency, multi-user/tenant safety, deterministic security boundaries, evaluator-gold isolation and evidence-honest claims.

## 2. Executive status

| Workstream | Current state | Evidence / next gate |
|---|---|---|
| Core agent runtime | **IMPLEMENTED / REGRESSION PASS** | AgentController + HarnessRunner + bounded execution |
| Deterministic evaluator | **IMPLEMENTED** | runtime/evaluator isolation retained |
| TRACTIAN registry | **IMPLEMENTED** | 18 operations / 17 paths |
| PostgreSQL operational truth | **HOSTED / G2 PASS** | Neon `academy_tractian`, restart persistence proved |
| Tenant RLS substrate | **HOSTED STRUCTURE PASS** | promoted `academy_tractian_rls` is non-superuser/NOBYPASSRLS |
| Realtime | **IMPLEMENTED / SOURCE PASS** | durable rows/cursors + LISTEN/NOTIFY + catch-up; hosted multi-user proof is G3 |
| Action safety | **IMPLEMENTED / SOURCE PASS** | custody, idempotency, lease/fencing, UNCERTAIN semantics |
| React Control Room | **HOSTED** | `production-web` HTTPS online; final real-data surfaces remain later gate |
| Railway backend | **HOSTED / G2 PASS** | public API online, `/health` and `/ready` pass |
| Immutable release identity | **HOSTED / G2 PASS** | current smoke proves configured == baked == Railway runtime SHA |
| Railway IaC | **SOURCE PASS / LIVE CONVERGENCE PENDING** | `PORT` healthcheck contract now preserved; live plan/apply still required |
| Neon Auth / Better Auth | **PROVISIONED / G3 IN PROGRESS** | browser + backend code exists; hosted two-user/two-tenant campaign next |
| Provider tournament v3 | **PREREGISTERED / NO_SELECTION** | live calls require separately authorized campaign |
| Production DecisionSource | **FAIL-CLOSED / NO_SELECTION** | no provider promoted yet |
| TRACTIAN HTTP adapter | **IMPLEMENTED / SOURCE PASS** | live partner endpoint/auth still not proved |
| Read semantics | **SOURCE-GATED** | hosted real-response proof pending |
| Required non-action modes | **SOURCE-GATED** | hosted provider + TRACTIAN proof pending |
| Trusted action authorization resolver | **SOURCE IMPLEMENTED** | organization-bound, server-owned, fail-closed; real hosted source composition pending |
| Consequential actions | **REMOTE DENY-ALL** | enable only after G3/G4/G5/authorization pass |
| SECURITY-V1 | **PREREGISTERED** | 14 source + 7 hosted cases; hosted execution downstream of functional path |
| Remote capacity/SLO | **NOT PROVED** | run after full hosted provider/TRACTIAN path |
| Recovery/reconnect | **PARTIAL** | backend restart persistence proved; full failure campaign pending |
| Backup/restore | **NOT PROVED** | real restore drill pending |
| Human semantic calibration | **NOT READY** | blinded labels required |
| Operational value | **NOT READY** | MANUAL vs AGENT-ASSISTED observations required |
| Adaptive runtime policy | **NO_CHANGE** | static baseline first; challenger only after P0 |
| GitHub `main` protection | **BLOCKED_USER_ACTION** | repository admin action required |

## 3. G2 — Remote backend serving: PASS

G2 is now closed for the currently served backend artifact `234655d952d62e1c26300fe6fd72f8d44df53001`.

### 3.1 Secrets and fail-closed boot

The two PostgreSQL DSNs are attached to `production-api` through Railway's native secret/variable boundary. Values are not stored in Git or documentation.

The first post-secret deployment correctly rejected a stale `ACADEMY_RELEASE_GIT_SHA`, proving the baked artifact identity cannot be overridden by mutable runtime metadata.

### 3.2 Healthcheck contract

Railway healthchecks require the service `PORT`. The API already listened on `ACADEMY_PORT=8000`; `PORT=8000` was added and `.railway/railway.ts` now preserves it so future IaC convergence cannot silently break the healthcheck boundary.

Hosted Railway evidence then showed:

```text
Application startup complete
Uvicorn: 0.0.0.0:8000
GET /health: 200 OK
Railway healthcheck: PASS
```

### 3.3 Reproducible hosted smoke

`.github/workflows/hosted-production-g2-smoke.yml` + `scripts/production_hosted_g2_smoke.py` independently query the public API. The current passing smoke proves:

```text
/health.status                         ok
/ready.status                          ready
release schema                         remote-production-release-v3
release_git_sha                        234655d952d62e1c26300fe6fd72f8d44df53001
artifact_git_sha                       234655d952d62e1c26300fe6fd72f8d44df53001
artifact_identity_verified             true
railway_runtime_identity_verified      true
environment                            production
browser_iam_mode                       neon-auth
cost_policy                            usd0-hard-gate
```

### 3.4 Durable restart proof

Before a production backend redeploy, a synthetic isolated G2 marker was persisted in the real operational tables. The backend was replaced by a new successful Railway deployment and the marker remained present afterward with the same organization/user/execution state. This proves the tested operational state is remote/durable and not tied to the API process/container.

### 3.5 Neon serving substrate

Observed production state:

```text
database                              academy_tractian
academy_operational base tables       16
required operational metadata         7 / 7
promoted scoped role                  academy_tractian_rls
scoped role superuser                 false
scoped role BYPASSRLS                 false
legacy academy_live_scoped            BYPASSRLS=true / INELIGIBLE
```

Five tenant-scoped operational/review tables retain `tenant_select` RLS policies. Historical compatibility roles are not promoted as tenant-serving evidence.

Detailed chronology: [`progress/2026-09-06-production-resume-g2-verification.md`](progress/2026-09-06-production-resume-g2-verification.md).

## 4. G3 — Live IAM / multi-user: IN PROGRESS

G2 no longer blocks IAM. Hosted G3 must prove, through the public production path:

1. sign-up/sign-in/sign-out/session lifecycle;
2. two independent users in separate tenant contexts;
3. intended same-organization multi-user behavior where configured;
4. browser-supplied organization/role/permission authority is ignored or rejected;
5. zero cross-tenant run/evidence/REST/SSE/action access;
6. invalid/expired/mismatched/impersonated sessions fail closed;
7. cookie/origin/CSRF behavior for state-changing operations;
8. RLS remains an independent boundary beneath API authorization.

No action permission is enabled during this campaign.

## 5. G4 — Provider tournament: PREREGISTERED / NO_SELECTION

The v3 protocol remains frozen at:

```text
17 scenarios × 5 repetitions × 2 candidates = 170 attempts
5 UTC-day packets × 34 attempts
USD0 / no paid fallback
```

The manifest currently authorizes zero live provider calls. Live execution requires a separate explicit authorization and an approved credential channel. No candidate may be promoted before the complete repeated campaign and hard-gate analysis.

## 6. G5 — Real TRACTIAN path: SOURCE READY / LIVE BLOCKED

Already implemented/source-gated:

- canonical 18-operation direct HTTP adapter;
- HTTPS-only remote base URL;
- exact method/path binding and canonical path encoding;
- server-owned credentials at the network boundary;
- redirects disabled;
- bounded request/response payloads and timeout;
- no automatic read/write retry;
- deterministic sanitized transport errors;
- structured read semantics `complete|partial|inconclusive|conflict|unavailable`;
- structural gates for Contextualize/Investigate/Clarify/Abstain/Escalate.

Still required:

- authoritative partner base URL/auth contract;
- server-side production configuration;
- bounded real read acceptance;
- real response-mode evidence;
- hosted agent-mode correctness with promoted DecisionSource.

Do not infer an authentication scheme.

## 7. Trusted consequential-action authorization

The source state is ahead of the older ledger. `trusted_action_authorization.py` already implements:

```text
trusted AuthenticatedRuntimeContext
→ organization/user-bound resolver
→ server-owned grant lookup
→ one unambiguous active grant
→ canonical tool permissions
→ company/resource bindings
→ ProductionActionPrincipal
```

Missing, ambiguous, inactive, wrong-user, wrong-organization, cross-company and source-failure cases deny deterministically. Browser/API capabilities are not converted into `action_low`, `action_high` or `escalate` permissions.

Remaining work is the authoritative hosted grant/resource source plus real acceptance. Until then remote actions remain **DENY-ALL**.

## 8. SECURITY-V1

`research/experiments/adversarial-security-v1-manifest.json` is preregistered and regression-locked.

```text
source cases     14
hosted cases      7
hard gates       12
provider calls authorized now       0
real TRACTIAN calls authorized now  0
production actions authorized now   0
```

`PASS_SOURCE_ONLY` never implies hosted production security readiness.

## 9. Exact dependency order from here

```text
A. main branch protection                         BLOCKED_USER_ACTION
B. G2 remote backend + durable restart             PASS
C. Railway IaC live plan/apply                     NEXT / independent
D. G3 IAM + two-user/two-tenant hosted campaign    IN_PROGRESS
E. G4 provider tournament                          WAITING explicit live authorization
F. compose promoted DecisionSource                 WAITING G4
G. configure/prove real TRACTIAN reads             WAITING authoritative config
H. hosted required agent modes + grounding         WAITING F/G
I. compose real authorization source               SOURCE READY / HOSTED PENDING
J. governed consequential action E2E                WAITING D-H/I
K. full public remote E2E                           WAITING J
L. SECURITY-V1 hosted                               WAITING K
M. load/capacity → evidence-based SLO               WAITING K
N. recovery/reconnect                               PARTIAL / full campaign after K
O. backup/restore                                   WAITING stable hosted path
P. human semantic calibration                      WAITING functional system
Q. operational-value experiment                    WAITING functional system
R. final Control Room/live evidence                 WAITING real data
S. protected CI/CD + tested rollback                WAITING P0 closure
T. final evidence freeze + release                  WAITING all hard gates
```

Independent work may proceed in parallel, but no downstream capability is promoted before its prerequisites pass.

## 10. Non-claims

Do **not** claim yet:

- overall production readiness;
- Railway IaC live convergence;
- IAM/multi-tenant hosted acceptance;
- selected hosted provider;
- real TRACTIAN reachability/reads;
- hosted correctness of all required modes;
- real consequential-action authorization/execution;
- hosted adversarial-security pass;
- measured capacity/SLO/HA/RTO/RPO;
- human-calibrated semantic judge;
- engineer-time savings;
- adaptive-runtime superiority;
- distributed exactly-once external side effects.

## 11. Update rule

Every material change must synchronize, as applicable:

1. implementation/infrastructure;
2. regression/hosted validation evidence;
3. this status file;
4. `DELIVERY-PLAN.md`;
5. `decision-registry.yaml` when a material decision changes;
6. chronological `docs/progress/` evidence.

Frozen historical artifacts are never rewritten to make current code appear historically valid.
