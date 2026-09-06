# Academy × TRACTIAN — Final Master Implementation Plan

**Status:** ACTIVE / canonical execution authority  
**Checkpoint:** 2026-09-06 BRT  
**Delivery target:** 2026-09-08  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)  
**Acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**Principles:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Decision registry:** [`decision-registry.yaml`](decision-registry.yaml)

This is the authoritative dependency-ordered implementation plan. Frozen historical evidence remains immutable. The objective is not to accumulate frameworks; it is to close every applicable release gate with quantitative, hosted and reproducible evidence.

## 1. North Star

```text
authenticated remote user
→ trusted tenant context
→ public HTTPS frontend
→ remote FastAPI
→ selected hosted USD0 DecisionSource
→ AgentController
→ 18 typed TRACTIAN tools
→ real TRACTIAN evidence
→ FINAL | CLARIFY | ABSTAIN | ESCALATE | ACTION_PROPOSAL
→ governed action when applicable
→ automatic evaluation
→ durable Neon PostgreSQL
→ REST/SSE observability
→ live React Control Room
→ quantitative security/reliability/value evidence
```

## 2. Engineering constitution

Every material decision follows:

```text
requirement / measured risk
→ baseline
→ eligible alternatives
→ hard constraints
→ preregistered metrics + hard gates
→ implementation
→ controlled + failure validation
→ PROMOTE | REJECT | INCONCLUSIVE | NO_CHANGE | NO_SELECTION
→ regression guard
→ documentation/evidence synchronization
```

Universal constraints:

- actual project cash cost = USD 0;
- no automatic paid spillover;
- no local serving dependency in production;
- multi-user / tenant-safe design;
- quantitative evidence wherever observable;
- deterministic IAM, authorization, RLS, schemas, action confirmation/custody/idempotency/leases/fencing, privacy, evaluator isolation and resource/cost caps;
- adaptation only after a static baseline and only with measured non-worse quality/safety;
- no LangGraph, multi-agent, RAG/vector DB, MCP, Redis/Kafka, microservices or Kubernetes without a measured gap and a winning challenger experiment;
- no production claim from source/CI evidence alone.

## 3. Current progress ledger

| # | Workstream | State | Next proof |
|---:|---|---|---|
| 00 | Active docs / decision governance | **DONE / CURRENT** | keep synchronized per change |
| 01 | Architecture/runtime baseline | **DONE** | regression only |
| 02 | Repository branch protection | **BLOCKED_USER_ACTION** | protect `main` + required check |
| 03 | Railway backend remote serving | **G2 PASS** | preserve via hosted smoke |
| 04 | Neon PostgreSQL/RLS | **G2 PASS** | G3 tenant negatives + later capacity/recovery |
| 05 | Backend immutable release identity | **HOSTED PASS** | keep exact-SHA smoke green |
| 06 | Durable backend restart | **HOSTED PASS** | broader recovery campaign later |
| 07 | Railway topology IaC | **SOURCE PASS / LIVE PLAN+APPLY PENDING** | converge without touching legacy hosted-pilot |
| 08 | Neon Auth / IAM | **G3 IN PROGRESS** | hosted two-user/two-tenant acceptance |
| 09 | Provider tournament v3 | **PREREGISTERED / NO_SELECTION** | explicit live authorization + 170-call campaign |
| 10 | Production DecisionSource | **WAITING G4** | compose only promoted provider |
| 11 | TRACTIAN production adapter | **SOURCE PASS / LIVE CONFIG PENDING** | authoritative endpoint/auth + bounded reads |
| 12 | Read-response semantics | **SOURCE PASS** | prove on real TRACTIAN responses |
| 13 | Required agent modes | **SOURCE PASS** | hosted correctness with real provider + TRACTIAN |
| 14 | Grounding/output lineage | **PARTIAL / P0** | measure claim-to-evidence support on hosted traces |
| 15 | Trusted action authorization resolver | **SOURCE IMPLEMENTED** | authoritative hosted grant/resource source |
| 16 | Consequential action remote E2E | **WAITING G3-G5/15** | proposal→confirm→attempt→terminal evidence |
| 17 | Full public remote E2E | **WAITING 16** | independent client, no local dependency |
| 18 | SECURITY-V1 | **PREREGISTERED** | hosted campaign after functional E2E |
| 19 | Remote load/capacity | **PLANNED** | staircase to measured saturation/quota |
| 20 | Evidence-based SLO | **WAITING 19** | derive only from measurements |
| 21 | Recovery/reconnect | **PARTIAL** | full provider/tool/DB/SSE/action failure campaign |
| 22 | Backup/restore | **PLANNED** | real restore drill + measured RTO/RPO |
| 23 | Human semantic calibration | **NOT_READY** | blinded human labels |
| 24 | Operational-value study | **NOT_READY** | MANUAL vs AGENT-ASSISTED observations |
| 25 | Final Control Room/live surfaces | **PARTIAL** | real provider/tool/eval/health/value data |
| 26 | CI/CD + rollback | **PARTIAL** | protected main, staging/production smoke, tested rollback |
| 27 | Final evidence freeze/release | **WAITING ALL P0** | all hard gates green or explicit accepted limitation |
| P1 | Adaptive stopping/tool/provider policy | **NO_CHANGE** | challenger only after static production baseline |

## 4. Completed P0 — G2 remote backend serving

The currently served artifact `234655d952d62e1c26300fe6fd72f8d44df53001` has passed:

```text
Railway deployment SUCCESS
/health = ok
/ready = ready
release_git_sha == artifact_git_sha == expected deployed SHA
artifact_identity_verified = true
railway_runtime_identity_verified = true
browser_iam_mode = neon-auth
cost_policy = usd0-hard-gate
```

A synthetic isolated operational state persisted through a production backend replacement/restart in Neon. `PORT=8000` is now preserved in Railway IaC because the Railway healthcheck contract depends on `PORT`.

Evidence: [`progress/2026-09-06-production-resume-g2-verification.md`](progress/2026-09-06-production-resume-g2-verification.md) and `hosted-production-g2-smoke`.

## 5. P0-A — Repository governance

Required administrator action:

```text
protect main
require pull request
require final-ci-required / required-gate
require branch up-to-date
block force push
block branch deletion
```

No implementation workaround may substitute for repository protection.

## 6. P0-B — Railway IaC convergence

Source contract:

- `.railway/railway.ts` manages only `production-api` and `production-web`;
- historical `hosted-pilot` stays outside the production partial;
- Railway-managed values and secrets use `preserve()`;
- `PORT`, `ACADEMY_PORT`, DB DSNs and IAM variables remain server-managed;
- static + TypeScript DSL CI must remain green.

Live gate:

```text
railway config plan
→ review zero unexpected deletes / zero hosted-pilot mutation / zero secret literals
→ apply
→ second plan
→ zero unexpected drift
```

## 7. P0-C — G3 IAM / multi-user hosted campaign

Run through the public production origin with provider calls and actions still disabled.

Population must cover:

### Positive

- sign-up/sign-in/sign-out;
- session reuse;
- re-auth semantics;
- API access with authenticated session;
- authenticated SSE;
- two separate users/tenant contexts;
- intended same-organization multi-user behavior where explicitly configured.

### Negative

```text
A → B run/evidence/SSE/action access
browser-forged organization
browser-forged role/permission
missing session
invalid session
expired session
mismatched/impersonated session
origin/cookie manipulation on state-changing endpoints
scoped SQL cross-tenant reads
```

Hard gates:

```text
cross_tenant_disclosure = 0
privilege_escalation = 0
browser_authority_acceptance = 0
invalid_session_acceptance = 0
```

Only after hosted evidence passes may DP-003 move from QUALIFIED to PREFERRED/PROMOTED.

## 8. P0-D — G4 provider tournament v3

Current state is `NO_SELECTION`. Historical D01/D02 stay immutable and outside the v3 denominator.

Frozen population:

```text
17 scenarios
× 5 repetitions
× 2 candidates
= 170 attempts
```

Five UTC-day packets of 34 attempts preserve the Cloudflare Workers Free neuron envelope. Each packet requires fresh quota headroom and no concurrent Workers AI usage.

Measure:

- operational outcome accuracy;
- terminal behavior;
- tool selection/arguments;
- failure recovery;
- evidence grounding and false precision;
- action safety;
- repeat stability;
- provider reliability and p50/p95/p99;
- resource/quota usage;
- trajectory efficiency;
- scenario slices.

Hard failures include non-zero paid cost/spillover, private-gold leakage, policy bypass, unsafe unsupported action, route/model substitution, invalid structured contract, incomplete required repetition or quota violation.

**Important:** the frozen manifest currently authorizes zero provider calls. Live tournament execution requires a separate explicit authorization and approved credential channel. No passing result automatically changes production config; DP-004 is changed only in a reviewed evidence-backed step.

## 9. P0-E — Production DecisionSource composition

Only a provider promoted by G4 may replace `NoSelectedProviderDecisionSource`.

Required production boundary:

```text
strict structured Decision contract
bounded request/output
server-managed credential
bounded timeout
no hidden fallback
no automatic paid route
quota accounting
sanitized provider failure
controller retains tool/action authority
```

Provider failure must converge to safe degradation/terminal behavior, never bypass deterministic policy.

## 10. P0-F — Real TRACTIAN integration

The direct typed production adapter remains the baseline. Do not replace it with MCP without a measured interoperability gap.

Live promotion requires:

1. recover authoritative TRACTIAN production base URL/auth contract;
2. configure only through server-side secret/config channels;
3. enter `CONFIGURED_UNVERIFIED` with zero boot-time network dependency;
4. execute bounded canonical read acceptance;
5. prove method/path/args/auth/timeout/payload normalization;
6. prove no redirect, credential leak or blind retry;
7. classify real responses as `complete|partial|inconclusive|conflict|unavailable`;
8. only then call the read path verified.

Never infer Bearer/API-key semantics without authoritative contract evidence.

## 11. P0-G — Hosted required agent modes

With a promoted hosted DecisionSource and real TRACTIAN evidence, validate:

- **CONTEXTUALIZE**: correct orientation without unnecessary tool work;
- **INVESTIGATE**: useful canonical reads and evidence-aware stopping;
- **CLARIFY**: ask only when required information cannot legitimately be recovered;
- **ABSTAIN**: stop when conclusion/action lacks justification;
- **ESCALATE**: useful sanitized handoff with evidence/uncertainty/attempts/next step.

Measure correctness, unnecessary calls, unsupported claims, evidence coverage and escalation usefulness. Source structural gates stay necessary but are not sufficient.

## 12. P0-H — Groundedness / evidence lineage

Every material operational claim should be inspectably linked:

```text
claim
→ evidence id
→ tool result
→ tool call + typed args
→ TRACTIAN resource
→ timestamp
```

Measure claim-support precision/recall, unsupported factual claim rate, evidence relevance and evidence completeness. Unsupported action/escalation evidence remains a hard failure.

## 13. P0-I — Real action authorization source

The organization-bound resolver already exists. Remaining work is a server-owned source containing authoritative:

```text
organization
user
company
canonical permissions
resource bindings
policy revision
active state
```

Browser/API capabilities are a separate namespace from `action_low`, `action_high` and `escalate`.

Hosted tests must retain fail-closed behavior for missing/ambiguous/inactive/wrong-org/wrong-user/cross-company/source-unavailable cases.

## 14. P0-J — Governed consequential action E2E

Only after IAM, provider, TRACTIAN and real authorization pass:

```text
ACTION_PROPOSAL
→ deterministic validation
→ private custody
→ PENDING_CONFIRMATION
→ authenticated opaque action-id confirmation
→ fresh authorization + kill-switch check
→ durable idempotency claim
→ non-transferable execution lease/fencing
→ one exact remote attempt
→ SUCCEEDED | FAILED | UNCERTAIN
→ evaluation + observability
```

Hard gate: platform-caused duplicate external side effects = 0.

Campaign includes duplicate click, browser refresh, replica loss, ambiguous timeout, stale worker and cross-tenant confirmation attempts.

## 15. P0-K — Full public remote E2E

From an unrelated external client/network:

```text
production URL
→ real auth
→ run submission
→ genuine SSE
→ hosted provider
→ real TRACTIAN
→ evidence
→ terminal outcome
→ automatic evaluation
→ durable PostgreSQL
→ reload/reconnect
→ state/evidence/lineage visible
```

Also execute one governed action case. Zero localhost, local model, local DB, fake provider, fake TRACTIAN or developer process may participate.

## 16. P0-L — SECURITY-V1 hosted

The population is already frozen: 14 source cases + 7 hosted cases + 12 hard gates.

Hosted families include invalid/expired/impersonated sessions, cross-tenant REST/SSE, CSRF/origin/cookie manipulation, real TRACTIAN transport boundary, provider prompt/tool injection, cross-tenant action confirmation and resource exhaustion.

No security claim may be promoted from `PASS_SOURCE_ONLY`; hosted production claim requires `PASS_HOSTED`.

## 17. P0-M — Remote load / capacity / SLO

Run staircase concurrency:

```text
1 → 2 → 4 → 8 → 16 → ...
```

until the measured saturation knee, quota boundary or error threshold. Report throughput, TTFT, p50/p95/p99, timeout/error rate, provider/DB latency, SSE lag/reconnect behavior, quota use and cash cost.

Only after measurement derive SLOs. Never invent SLO numbers first and tune the report to them.

## 18. P0-N — Recovery, reconnect, backup/restore

Failure campaign must cover backend restart, SSE disconnect/catch-up, provider failure, TRACTIAN failure, DB failure, worker/lease loss and deployment rollback.

Backup/restore is a real drill:

```text
create known state
→ snapshot/export
→ isolated loss/corruption
→ recreate
→ restore
→ verify state/integrity/tenant isolation
```

RTO/RPO are measured outputs, not promises.

## 19. P0-O — Human semantic calibration

Deterministic checks remain authoritative where exact truth exists. Semantic judges cannot gate until real blinded labels establish reliability.

Target where feasible: `17 scenarios × 3 independent reviewers ≈ 51 reviews`, followed by adjudication, confusion matrix, precision/recall/F1, inter-rater agreement, judge-vs-human agreement and disagreement analysis.

If labels are unavailable, the valid state is `NOT READY`, not an invented score.

## 20. P0-P — Operational-value experiment

Compare equivalent cases under:

```text
MANUAL
vs
AGENT-ASSISTED
```

Primary KPI: **Time to Correct Operational Decision**.

Secondary: correctness, evidence completeness, retries, escalations, unsafe behavior and human intervention. Report distributions/deltas/uncertainty; no engineer-time-saved claim without observations.

## 21. P0-Q — Final Control Room

All visible surfaces must consume real server-owned production evidence, never fabricated progress or hidden chain-of-thought.

Required connected views as applicable:

- Mission Control;
- Live Run Cockpit;
- Run Explorer;
- Timeline/Waterfall;
- Trace Graph;
- Architecture Explorer with live run overlay;
- Evidence Explorer;
- Output Lineage;
- Action Control;
- Tools & Policy analytics;
- Eval Lab;
- Provider Lab;
- Dynamic Data Explorer;
- Production Health;
- Operational Value after measured data exists;
- Decision Explorer backed by material decision evidence.

A reviewer must be able to answer what happened, which components ran, which evidence supported the output, why execution stopped, what policy/evaluation occurred and which exact build produced the run.

## 22. P0-R — CI/CD, rollback and final freeze

Final release path:

```text
PR
→ protected required gate
→ staging/production-compatible deploy
→ hosted smoke
→ production
→ smoke/evidence capture
```

Before release, execute real rollback and verify DB compatibility/state integrity. Then freeze/link the final production URLs, exact build identity, USD0 evidence, IAM/RLS/action safety, provider decision, TRACTIAN evidence, mode/grounding results, security, capacity/SLO, recovery/restore, human/value evidence or explicit limitations, Control Room evidence, runbooks and reversal triggers.

## 23. P1 only after P0

Potential challengers:

1. adaptive evidence stopping;
2. adaptive tool ordering;
3. provider routing among multiple independently eligible providers;
4. optional OpenTelemetry-compatible infrastructure metrics.

Promotion requires quality/safety non-worse and a material measured benefit in resource use, latency or difficult-case performance.

## 24. Hard release gate

Any applicable hard gate red means `NOT READY`.

Required final facts include:

```text
actual cash cost = USD0
paid spillover = 0
remote frontend/backend/PostgreSQL = PASS
no local serving dependency = PASS
immutable release identity = PASS
IAM/multi-user/tenant isolation = PASS
provider = PROMOTED or evidence-honest NO_SELECTION blocking readiness
real TRACTIAN = PASS
required modes + grounding = PASS
server-owned action authorization = PASS
governed remote action = PASS
duplicate platform side effects = 0
full public E2E = PASS
SECURITY-V1 hosted = PASS
remote capacity measured = PASS
SLO evidence-based = PASS
recovery/reconnect = PASS
backup/restore = PASS
semantic calibration = PASS or explicit accepted limitation
operational value = MEASURED or explicit accepted limitation
Control Room real/live = PASS
protected main + required CI = PASS
rollback = PASS
documentation synchronized = PASS
final evidence freeze = PASS
```

## 25. Immediate execution order

```text
1. G3 hosted IAM / tenant isolation             IN PROGRESS
2. Railway IaC live convergence                 independent parallel gate
3. G4 provider tournament                       requires explicit live authorization
4. promoted DecisionSource composition
5. real TRACTIAN configuration + reads
6. hosted modes + grounding
7. authoritative action authorization source
8. governed action E2E
9. full public remote E2E
10. SECURITY-V1 hosted
11. load/capacity → SLO
12. full recovery/reconnect
13. backup/restore
14. human semantic calibration
15. operational-value experiment
16. final Control Room/evidence
17. protected CI/CD + rollback
18. evidence freeze + release
```

No downstream capability is promoted before its dependencies pass. Independent preparation may continue in parallel when an external/user-action gate is blocked.
