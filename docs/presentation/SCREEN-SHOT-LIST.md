# Technical Presentation — Screen Shot List

**Current UI:** task-driven Home / Analyses / Technical  
**Current backend:** `08866da...`  
**Current frontend:** `1bc124a...`

Every shot must prove an authority, execution, evidence, uncertainty, evaluation, persistence or deployment boundary. If it proves none, cut it.

## Shot 01 — Full architecture

Show Browser → production-web → production-api → AuthenticatedRuntimeContext → V13 DecisionSource/AgentController → HarnessRunner/ToolSpec → supplied TRACTIAN API → Evidence/RunTrace → ProductionEvaluator → Neon PostgreSQL → SSE/UI.

## Shot 02 — Authenticated Home

Must show:

- hosted public product;
- signed-in state;
- Home question entry;
- service online state.

Overlay:

```text
managed session
→ server validation
→ AuthenticatedRuntimeContext
→ PostgreSQL org scope / RLS
```

Optional small line: `GET/HEAD ≤2 s validated reuse; POST fresh`.

Never show cookies/tokens/devtools secrets.

## Shot 03 — R310 grounding path

Use/select `run_97b91f6e0feb91184283` or submit equivalent prompt.

Overlay:

```text
R310 label
→ get_current_user
→ list_assets_by_company
→ asset_R310
```

Technical point: discover authorized IDs instead of asking the customer.

## Shot 04 — Technical → Current analysis

Show one complete structured path with:

- tool name;
- normalized arguments/resource;
- result/status;
- evidence reference;
- trace sequence.

Prefer spectrum from the R310 primary run.

## Shot 05 — Progressive point drill-down

Show asset-level and point-specific RMS/spectrum calls if both are visible.

Label clearly:

```text
same tool family
+ different target/point_id
= progressive drill-down, not exact duplicate
```

Do not call it a loop merely from tool name.

## Shot 06 — Result + response mode

Show primary result with `partial` and supporting evidence.

Overlay:

```text
terminal decision ≠ response_mode
partial = useful supported answer + material uncertainty
```

## Shot 07 — Evidence lineage

Show one visible chain:

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

Must show the bounded unavailable result that R420 was not found in the authorized fleet.

Technical point: no invented asset, no hidden-ID request, no cross-tenant speculation.

## Shot 09 — Technical → Quality

Show persisted deterministic evaluation for a V13 run. Prefer blocking checks such as execution-chain integrity, model-call provenance, production-trace identity, proposal-contract validity, read-only action safety and terminal consistency.

## Shot 10 — Technical → Actions

Show current action capability/control state with strong overlay:

```text
RELEASE 0
EXTERNAL CONSEQUENTIAL EXECUTION DISABLED
```

## Shot 11 — Deployment

```text
Browser
→ Railway production-web 1bc124a...
→ Railway production-api 08866da...
   ├→ Neon Auth
   ├→ Cloudflare provisional provider
   ├→ supplied TRACTIAN API 47561c...
   └→ Neon PostgreSQL
```

## Shot 12 — Session resilience

Overlay only; do not intentionally break auth while recording:

```text
invalid managed session → 401
identity service unavailable → 503 + retry
no stale-on-error
```

## Shot 13 — Durable realtime

```text
runtime event
→ PostgreSQL commit
→ LISTEN/NOTIFY wake-up
→ durable catch-up by run_id + sequence
→ authenticated SSE
→ React state
```

## Shot 14 — Final nine-step recap

```text
1 server-owned session/tenant
2 durable ownership
3 V13 grounding + AgentController
4 ToolSpec validation
5 HarnessRunner + TRACTIAN HTTPS
6 Evidence + RunTrace
7 terminal + response_mode
8 ProductionEvaluator
9 PostgreSQL + SSE + task-driven UI
```

## UI preparation

### Home

- signed in;
- service online;
- question field clean.

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
- evaluator gold/private oracle;
- hidden reasoning;
- localhost as production evidence;
- unsupported final-provider/action/SLO claims.