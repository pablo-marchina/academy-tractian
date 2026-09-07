# 5-Minute Technical Screenplay

**Audience:** technical reviewer already knows the challenge.  
**Goal:** explain the current promoted architecture and prove it with one persisted V13 hosted run.  
**Style:** no business introduction, no generic AI explanation, no feature tour.

## Timing contract

| Time | On screen | Technical point |
|---:|---|---|
| 00:00–00:28 | architecture overlay | identity, agent, tool, evidence/eval boundaries |
| 00:28–00:55 | signed-in **Home** + identity overlay | browser is not authority; managed-session resilience |
| 00:55–01:25 | submit or select PRIMARY R310 run | V13 explicit asset grounding starts with server-owned identity/fleet discovery |
| 01:25–02:05 | **Technical → Current analysis** | structured decisions, tool args, asset→point drill-down, TRACTIAN I/O |
| 02:05–02:40 | selected **Result** + evidence | terminal decision versus `response_mode`; evidence lineage |
| 02:40–03:05 | **Analyses** → unavailable R420 run | fail closed when requested label is absent from authorized fleet |
| 03:05–03:42 | **Technical → Quality** | post-runtime evaluator / blocking checks |
| 03:42–04:08 | **Technical → Actions** | proposal ≠ authorization; external execution disabled |
| 04:08–04:38 | deployment/auth/realtime overlay | Railway + Neon + Cloudflare + supplied API; 401/503 session semantics |
| 04:38–05:00 | final architecture recap | end-to-end auditability and current non-claims |

## 00:00–00:28 — Current architecture

Show the runtime boundary overlay:

```text
Browser / task-driven React
→ Railway production-web
→ FastAPI production-api
→ managed AuthenticatedRuntimeContext
→ V13 DecisionSource ↔ AgentController
→ HarnessRunner / ToolSpec
→ supplied TRACTIAN API
→ Evidence / RunTrace
→ ProductionEvaluator
→ Neon PostgreSQL
→ authenticated SSE / UI
```

Say that identity/tenant, tool authority and evaluator-private state are all outside model authority.

## 00:28–00:55 — Home and identity/session boundary

Show signed-in **Home**. Keep the service state and primary question visible.

Overlay:

```text
managed cookie
→ server validation
→ user / organization
→ AuthenticatedRuntimeContext
→ PostgreSQL org scope / RLS
```

Add small resilience note:

```text
GET/HEAD: ≤2 s validated-context reuse
POST/run create: fresh validation
401 invalid ≠ 503 auth unavailable
```

Explain this was hardened after a real dashboard fan-out incident; no stale-on-error or browser authority was introduced.

## 00:55–01:25 — V13 asset grounding

Use/select `run_97b91f6e0feb91184283` or submit its equivalent R310 causal question if intentionally consuming a live run.

Overlay:

```text
"R310" human label
→ get_current_user
→ company_id from structured observation
→ list_assets_by_company
→ asset_R310 from authorized fleet
→ condition evidence
```

Key point: customer does not need to provide internal `company_id`/`asset_id`, and missing labels do not authorize another tenant scope.

## 01:25–02:05 — Technical current analysis / tool execution

Open **Technical → Current analysis** for the primary run.

Show at least:

- model/tool transition;
- canonical tool name;
- arguments/resource target;
- HTTP/result/evidence state;
- trace sequence.

For the R310 run, point out spectrum refinement. Explain that repeated `get_spectrum` names are not automatically loops: the remote path moved from asset-level to point-specific evidence. Redundancy is determined from operation + normalized args/resource + evidence contribution.

Execution overlay:

```text
structured TOOL decision
→ ToolSpec lookup
→ deterministic argument/policy checks
→ HarnessRunner
→ ProductionTractianTransport
→ typed HTTPS
→ supplied TRACTIAN API
→ normalized observation
```

## 02:05–02:40 — Result, evidence and response semantics

Return to the selected **Result** and its contextual evidence.

Explain two separate contracts:

```text
terminal decision = what controller does next
response_mode      = how completely evidence supports the message
```

Show `partial` on the R310 causal run. Explain that a probable bearing mechanism can be useful and directional while still not being fully proven root cause.

Response-mode vocabulary:

- complete;
- partial;
- inconclusive;
- conflict;
- unavailable.

Show one evidence reference linked back to a tool observation if possible. Explicitly say hidden chain-of-thought is not required or exposed.

## 02:40–03:05 — Analyses / missing resource fail-closed

Open **Analyses**, select `run_547b2a62d84ef56a3d3d`, then its result.

The prompt asked to compare R310 and R420. Authorized fleet discovery found R310 but not R420, so the correct result was `unavailable`.

Explain:

```text
missing label
≠ ask user for hidden internal ID
≠ guess another plant/company
≠ fabricate comparison
→ bounded unavailable result
```

Do not claim this proves quality of a true two-asset comparison; it proves missing-resource safety/grounding.

## 03:05–03:42 — Technical Quality / evaluator

Open **Technical → Quality** for the primary run.

Show the post-runtime pipeline:

```text
completed RunTrace
→ ProductionEvaluator
→ deterministic structural/safety/trajectory checks
→ safe persisted evaluation
```

Prioritize real persisted checks such as execution-chain integrity, model-call provenance, production-trace identity, proposal contract validity, read-only action safety and terminal consistency.

Explain evaluator-private truth is not supplied to the running agent.

## 03:42–04:08 — Technical Actions / consequence boundary

Open **Technical → Actions**.

Overlay:

```text
model may propose
→ deterministic validation
→ proposal/control state
→ confirmation/custody/idempotency/lease architecture
→ external consequential execution
```

Mark the last step:

```text
RELEASE 0: DISABLED / DENY-ALL
```

Do not imply action execution simply because action contracts exist in the codebase.

## 04:08–04:38 — Deployment, auth and realtime

Show:

```text
Browser
→ Railway production-web 1bc124a...
→ Railway production-api 08866da...
   ├→ Neon Auth
   ├→ Cloudflare provisional provider
   ├→ supplied TRACTIAN API 47561c...
   └→ Neon PostgreSQL
```

Then realtime:

```text
runtime transition
→ PostgreSQL event row
→ commit
→ LISTEN/NOTIFY wake-up
→ durable cursor catch-up
→ authenticated SSE
→ React projection
```

Explain component SHAs are tracked independently and source/docs commits do not automatically become a backend deployment.

## 04:38–05:00 — Final recap

End with:

```text
1 server-owned identity/tenant
2 durable run ownership
3 V13 grounded DecisionSource + AgentController
4 typed ToolSpec validation
5 HarnessRunner + remote TRACTIAN reads
6 evidence + RunTrace
7 terminal + response_mode
8 post-runtime evaluator
9 PostgreSQL + authenticated SSE + task-driven UI
```

Final claim boundary: strong current read-only product; not final provider superiority, not all-read live coverage, not consequential action readiness, not final SLO/security/value proof.