# Technical Presentation — Screen Shot List

**Current UI:** task-driven Home / Analyses / Technical  
**Current backend source:** `3545d75...`  
**Current frontend:** `1bc124a...`

Every shot must prove an authority, execution, evidence, uncertainty, evaluation, action-safety, persistence or deployment boundary. If it proves none, cut it.

## Shot 01 — Full architecture

Show Browser → production-web → production-api → AuthenticatedRuntimeContext → V13 DecisionSource/AgentController → HarnessRunner/ToolSpec → supplied TRACTIAN API → Evidence/RunTrace → ProductionEvaluator → Neon PostgreSQL → SSE/UI, plus a separate governed-action branch.

## Shot 02 — Authenticated Home

Must show hosted product, signed-in state and Home question entry.

Overlay:

```text
managed session
→ server validation
→ AuthenticatedRuntimeContext
→ PostgreSQL org scope / RLS
```

Optional: `GET/HEAD ≤2 s validated reuse; POST/non-read fresh`.

Never show cookies/tokens/devtools secrets.

## Shot 03 — R310 grounding path

Use/select `run_97b91f6e0feb91184283`.

```text
R310 label
→ get_current_user
→ list_assets_by_company
→ asset_R310
```

Technical point: discover authorized IDs instead of asking the customer.

## Shot 04 — Technical → Current analysis

Show one structured path with tool name, normalized arguments/resource, result/status, evidence reference and trace sequence.

## Shot 05 — Progressive point drill-down

Show asset-level and point-specific RMS/spectrum calls if both are visible.

```text
same tool family
+ different target/point_id
= progressive drill-down, not exact duplicate
```

## Shot 06 — Result + response mode

Show primary result with `partial` and supporting evidence.

```text
terminal decision ≠ response_mode
partial = useful supported answer + material uncertainty
```

## Shot 07 — Evidence lineage

Show:

```text
result claim
→ evidence ID
→ normalized observation
→ tool + arguments
→ remote resource/status
```

Do not expose chain-of-thought.

## Shot 08 — Analyses / missing R420

Select `run_547b2a62d84ef56a3d3d`.

Must show bounded unavailable result: R420 was not found in the authorized fleet.

Technical point: no invented asset, hidden-ID request or cross-tenant speculation.

## Shot 09 — Technical → Quality

Show persisted deterministic evaluation for a V13 run. Prefer blocking checks such as execution-chain integrity, model-call provenance, production-trace identity, proposal-contract validity and terminal consistency.

## Shot 10 — Technical → Actions

Do **not** use the obsolete “EXTERNAL EXECUTION DISABLED” overlay.

Show the governed boundary:

```text
proposal
→ private exact custody
→ explicit confirmation
→ server-owned grant/resource scope
→ persistent idempotency
→ lease/fencing
→ server-owned vendor actor
→ one remote attempt
```

Add status overlay:

```text
LOCAL ACTION ARCHITECTURE: IMPLEMENTED / CI-QUALIFIED
5-ACTION VENDOR ACCEPTANCE: NOT PROVEN
LIVE BLOCKER: update_asset_config → HTTP 403 / accepted=false
```

## Shot 11 — Local user vs vendor actor

Overlay:

```text
local authenticated user
→ tenant/resource authorization + confirmation + audit

(company_id, required_permission)
→ server-owned TRACTIAN actor
→ vendor endpoint
```

Technical point: vendor actor is not model/browser authority. Corrective routing is still in progress; do not label it promoted.

## Shot 12 — Failed validation containment

Use an overlay/evidence reference, not secret-bearing logs:

```text
fresh Railway snapshot
→ five-action pre-deploy smoke
→ update_asset_config 403 / accepted=false
→ candidate deployment aborted
→ previous healthy production remained serving
```

Technical point: failure became evidence and containment, not a hidden retry or false success.

## Shot 13 — Deployment

```text
Browser
→ Railway production-web 1bc124a...
→ Railway production-api source 3545d75...
   ├→ Neon Auth
   ├→ Cloudflare provisional provider
   ├→ supplied TRACTIAN API 47561c...
   └→ Neon PostgreSQL
```

Optional provenance inset:

```text
generic Railway redeploy may reuse captured snapshot
fresh configuration claim requires fresh snapshot
```

## Shot 14 — Session resilience

Overlay only:

```text
invalid managed session → 401
identity service unavailable → 503 + retry
no stale-on-error
```

## Shot 15 — Durable realtime

```text
runtime event
→ PostgreSQL commit
→ LISTEN/NOTIFY wake-up
→ durable catch-up by run_id + sequence
→ authenticated SSE
→ React state
```

## Shot 16 — Final recap

```text
1 server-owned session/tenant
2 durable ownership
3 V13 grounding + AgentController
4 ToolSpec validation
5 HarnessRunner + TRACTIAN HTTPS reads
6 Evidence + RunTrace
7 terminal + response_mode
8 ProductionEvaluator
9 governed action custody + confirmation + idempotency + lease
10 server-owned vendor actor + explicit acceptance + fail-closed deployment gate
```

## UI preparation

### Home

- signed in;
- question field clean;
- avoid clutter unrelated to the user task.

### Analyses

- primary R310 run known;
- R420 unavailable run known;
- optional data-quality run known.

### Technical

- Current analysis trace readable;
- Quality evaluation loaded;
- Actions boundary visible;
- System architecture/capabilities available as fallback.

## Never show

- `.env`;
- API/provider/database keys;
- cookies/session tokens;
- authorization headers;
- private action custody;
- grants/idempotency keys/vendor actor mappings;
- evaluator gold/private oracle;
- hidden reasoning;
- localhost as production evidence;
- unsupported final-provider/5-of-5-action/SLO/usability claims.