# 5-Minute Technical Screenplay

**Audience:** technical reviewer already knows the challenge.  
**Goal:** explain the promoted architecture, prove it with hosted evidence, and show that the evaluation framework can reject an unqualified provider.  
**Provider checkpoint:** 2026-09-08 — Groq GPT-OSS-120B 85/85 = `NO_SELECTION`; production unchanged.  
**Style:** no business introduction, no generic AI explanation, no feature tour.

## Timing contract

| Time | On screen | Technical point |
|---:|---|---|
| 00:00–00:28 | architecture overlay | identity, agent, tool, evidence/eval boundaries |
| 00:28–00:55 | signed-in Home | server-owned tenant/session resilience |
| 00:55–01:25 | PRIMARY R310 run | explicit asset grounding |
| 01:25–02:05 | Technical → Current analysis | structured decisions, typed I/O, drill-down |
| 02:05–02:40 | Result + evidence | terminal vs `response_mode` |
| 02:40–03:05 | unavailable R420 run | authorized missing-resource fail-closed |
| 03:05–03:42 | Technical → Quality | post-runtime evaluation + provider rejection evidence |
| 03:42–04:08 | Technical → Actions | proposal ≠ authorization; external execution disabled |
| 04:08–04:38 | deployment/realtime overlay | production vs provider-research boundary |
| 04:38–05:00 | final recap | auditability + current non-claims |

## 00:00–00:28 — Current architecture

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

Identity/tenant, tool authority and evaluator-private state are outside model authority.

## 00:28–00:55 — Home and identity/session boundary

Show signed-in Home.

```text
managed cookie
→ server validation
→ user / organization
→ AuthenticatedRuntimeContext
→ PostgreSQL org scope / RLS
```

Resilience note:

```text
GET/HEAD: bounded validated-context reuse
POST/run create: fresh validation
401 invalid ≠ 503 auth unavailable
```

No stale-on-error or browser-owned authority.

## 00:55–01:25 — Asset grounding

Use/select the persisted R310 causal run.

```text
"R310" human label
→ get_current_user
→ company_id from structured observation
→ list_assets_by_company
→ authorized asset_R310
→ condition evidence
```

Customer does not need internal IDs. Missing labels do not authorize another tenant scope.

## 01:25–02:05 — Technical / Current analysis

Show the model/tool transition, canonical tool, arguments/resource, status/evidence and trace sequence.

```text
structured TOOL decision
→ ToolSpec lookup
→ deterministic argument/policy checks
→ HarnessRunner
→ typed HTTPS
→ supplied TRACTIAN API
→ normalized observation
```

For repeated RMS/spectrum calls, distinguish valid asset→point refinement from exact duplicate calls using arguments/resource/evidence contribution.

## 02:05–02:40 — Result and evidence semantics

Explain:

```text
terminal decision = runtime outcome
response_mode      = evidence completeness
```

Show `partial` on the R310 causal run. A useful directional mechanism can remain probabilistic. Show evidence lineage without hidden chain-of-thought.

## 02:40–03:05 — Missing resource fail-closed

Open the R420-unavailable run.

```text
missing authorized label
≠ hidden-ID request
≠ cross-tenant guess
≠ fabricated comparison
→ unavailable
```

This proves missing-resource safety, not a bilateral comparison with two real assets.

## 03:05–03:42 — Quality / evaluator and provider qualification

Show the post-runtime evaluator:

```text
completed RunTrace
→ deterministic structural/safety/trajectory checks
→ safe persisted evaluation
```

Then state the current provider evidence precisely:

```text
Groq openai/gpt-oss-120b
85/85 attempts
69/85 rubric pass = 81.18%
70/85 reliability = 82.35%
9 contract failures
selection = NO_SELECTION
```

The evaluation framework did not relax gates or hide failed attempts. Cloudflare GPT-OSS was quota-blocked in non-scored preflight and then removed from the requested path, so there is no completed Cloudflare-vs-Groq final tournament claim.

Current research asks why the Groq configuration failed: completion budget, reasoning effort and best-effort vs strict structured output.

## 03:42–04:08 — Consequential action boundary

```text
model proposal
→ deterministic validation
→ confirmation/custody/idempotency/lease architecture
→ external consequential execution
```

Mark external execution **DISABLED / DENY-ALL** for Release 0.

## 04:08–04:38 — Deployment, provider and realtime boundary

```text
Browser
→ Railway production-web
→ Railway production-api
   ├→ Neon Auth
   ├→ provisional production provider
   ├→ supplied TRACTIAN API
   └→ Neon PostgreSQL

separate QA/research execution
→ frozen provider population/runners
→ qualification evidence
→ no automatic production promotion
```

Then:

```text
runtime transition
→ PostgreSQL event row
→ commit
→ LISTEN/NOTIFY wake-up
→ durable cursor catch-up
→ authenticated SSE
→ React projection
```

Source/docs/provider-research commits do not automatically become production deployments.

## 04:38–05:00 — Final recap

```text
1 server-owned identity/tenant
2 durable run ownership
3 grounded DecisionSource + AgentController
4 typed ToolSpec validation
5 HarnessRunner + TRACTIAN reads
6 evidence + RunTrace
7 terminal + response_mode
8 post-runtime evaluator / hard gates
9 PostgreSQL + authenticated SSE + task-driven UI
```

Final claim boundary: strong current read-only product and a provider evaluation framework that has rejected the tested Groq configuration; **no final provider winner**, no consequential action readiness, no final SLO/security/value proof.
