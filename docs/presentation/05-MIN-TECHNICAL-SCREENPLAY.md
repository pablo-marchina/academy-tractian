# 5-Minute Technical Screenplay

**Audience:** technical reviewer already knows the challenge.  
**Goal:** explain the current promoted architecture, prove it with persisted hosted evidence, and state the governed-action live gap exactly.  
**Style:** no business introduction, no generic AI explanation, no feature tour.

## Timing contract

| Time | On screen | Technical point |
|---:|---|---|
| 00:00–00:28 | architecture overlay | identity, agent, tool, evidence/eval/action boundaries |
| 00:28–00:55 | signed-in **Home** + identity overlay | browser is not authority; managed-session resilience |
| 00:55–01:25 | PRIMARY R310 run | V13 asset grounding via server-owned identity/fleet discovery |
| 01:25–02:05 | **Technical → Current analysis** | typed decisions, tool args, asset→point drill-down, TRACTIAN read I/O |
| 02:05–02:40 | selected **Result** + evidence | terminal decision vs `response_mode`; evidence lineage |
| 02:40–03:05 | **Analyses** → unavailable R420 run | fail closed when requested label is absent |
| 03:05–03:38 | **Technical → Quality** | post-runtime evaluator / blocking checks |
| 03:38–04:15 | **Technical → Actions** | governed custody/confirmation/idempotency/lease + truthful live 403 limitation |
| 04:15–04:40 | deployment/auth/realtime overlay | exact source, Railway snapshot discipline, Neon/Cloudflare/TRACTIAN |
| 04:40–05:00 | final recap | end-to-end auditability + explicit non-claims |

## 00:00–00:28 — Current architecture

Show:

```text
Browser / task-driven React
→ Railway production-web
→ FastAPI production-api
→ AuthenticatedRuntimeContext
→ V13 DecisionSource ↔ AgentController
→ HarnessRunner / ToolSpec
→ supplied TRACTIAN API
→ Evidence / RunTrace
→ ProductionEvaluator
→ Neon PostgreSQL
→ authenticated SSE / UI
```

Add a separate action branch:

```text
proposal
→ private custody
→ exact confirmation
→ trusted grant/resource scope
→ idempotency + lease
→ server-owned vendor actor
→ one typed write
```

Say: identity/tenant, tool authority, action authority and evaluator-private state are outside model authority.

## 00:28–00:55 — Home and identity/session boundary

Show signed-in **Home**.

```text
managed cookie
→ server validation
→ user / organization
→ AuthenticatedRuntimeContext
→ PostgreSQL org scope / RLS
```

Resilience note:

```text
GET/HEAD: ≤2 s validated-context reuse
POST/non-read: fresh validation
401 invalid ≠ 503 auth unavailable
```

Explain this was hardened after a real dashboard fan-out incident without introducing stale auth or browser authority.

## 00:55–01:25 — V13 asset grounding

Use/select `run_97b91f6e0feb91184283`.

```text
"R310" human label
→ get_current_user
→ company_id from authorized structured observation
→ list_assets_by_company
→ asset_R310 from authorized fleet
→ condition evidence
```

Key point: customer does not supply internal IDs; missing labels do not authorize another tenant.

## 01:25–02:05 — Technical current analysis / tool execution

Open **Technical → Current analysis**.

Show model/tool transition, canonical tool, arguments/resource, result/status/evidence and trace sequence.

For spectrum refinement explain:

```text
same tool family
+ more specific point_id target
= progressive drill-down, not automatically a loop
```

Execution overlay:

```text
structured TOOL decision
→ ToolSpec lookup
→ deterministic validation/policy
→ HarnessRunner
→ ProductionTractianTransport
→ typed HTTPS
→ supplied TRACTIAN API
→ normalized observation
```

## 02:05–02:40 — Result, evidence and response semantics

Return to **Result**.

```text
terminal decision = what controller does next
response_mode      = how completely evidence supports the message
```

Show `partial` on the R310 causal run. Explain probable mechanism can be useful without being fully proven root cause.

Vocabulary:

```text
complete | partial | inconclusive | conflict | unavailable
```

Show an evidence reference. Auditability comes from observable calls/args/status/evidence/events, not hidden chain-of-thought.

## 02:40–03:05 — Missing resource fail-closed

Open `run_547b2a62d84ef56a3d3d`.

R310 was authorized; R420 was absent from the authorized fleet. Correct behavior:

```text
missing label
≠ hidden-ID request
≠ other-company guess
≠ fabricated comparison
→ bounded unavailable
```

Do not present this as proof of true bilateral comparison quality.

## 03:05–03:38 — Quality / evaluator

Open **Technical → Quality**.

```text
completed RunTrace
→ ProductionEvaluator
→ deterministic structural/safety/trajectory checks
→ safe persisted evaluation
```

Mention execution-chain integrity, model-call provenance, production-trace identity, proposal-contract validity and terminal consistency where visible. Evaluator-private truth is never supplied to the running agent.

## 03:38–04:15 — Actions / consequence boundary

Open **Technical → Actions**.

Do **not** use the old `DISABLED / DENY-ALL` overlay.

Show:

```text
model proposal
→ deterministic policy
→ private exact custody
→ explicit confirmation
→ server-owned grant/resource scope
→ persistent idempotency
→ action execution lease/fencing
→ server-owned vendor actor
→ one remote action attempt
→ ACCEPTED | NOT_ACCEPTED | BLOCKED | UNCERTAIN
```

Then state the current evidence boundary:

```text
local governed architecture: implemented + CI-qualified
production composition: enabled
five-action vendor acceptance: NOT PROVEN
live blocker: update_asset_config -> HTTP 403 / accepted=false
```

Explain the failed validation deployment did not replace healthy production.

Then explain root cause in one sentence: the supplied runtime has distinct vendor actors for low-impact and high-impact/escalation permissions, so local product identity must remain the authorization/audit principal while the final TRACTIAN actor is selected server-side by company + required permission.

Do not say the corrective actor-routing branch is already merged or proven.

## 04:15–04:40 — Deployment, auth and realtime

Show:

```text
Browser
→ production-web 1bc124a...
→ production-api source 3545d75...
   ├→ Neon Auth
   ├→ Cloudflare provisional provider
   ├→ supplied TRACTIAN API 47561c...
   └→ Neon PostgreSQL
```

Mention PR #213 required gate `34164123263` passed source/artifact/browser/action-lease regressions.

Operational point:

```text
Railway generic redeploy can reuse a captured snapshot
fresh config/source evidence requires a fresh deployment snapshot
```

Realtime:

```text
runtime transition
→ PostgreSQL event row
→ commit
→ LISTEN/NOTIFY wake-up
→ durable cursor catch-up
→ authenticated SSE
→ React projection
```

## 04:40–05:00 — Final recap

End with:

```text
1 server-owned identity/tenant
2 durable run ownership
3 V13 grounded decisions
4 typed ToolSpec validation
5 HarnessRunner + remote TRACTIAN reads
6 evidence + RunTrace
7 terminal + response_mode
8 post-runtime evaluator
9 governed action custody/confirmation/idempotency/lease
10 explicit vendor acceptance required + fail-closed deployment validation
```

Final claim boundary: hosted/hardened real product with governed action machinery, but not final provider superiority, not all-read coverage, not five-action vendor readiness, not final SLO/security/recovery/value/human-usability proof.