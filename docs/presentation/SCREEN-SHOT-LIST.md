# Technical Presentation — Screen Shot List

**Current UI:** task-driven Home / Analyses / Technical  
**Provider claim checkpoint:** Groq GPT-OSS-120B 85/85 = `NO_SELECTION`; no final provider winner.

Every shot must prove an authority, execution, evidence, uncertainty, evaluation, persistence, provider-selection or deployment boundary. If it proves none, cut it.

## Shot 01 — Full production architecture

Show Browser → production-web → production-api → AuthenticatedRuntimeContext → V13 DecisionSource/AgentController → HarnessRunner/ToolSpec → supplied TRACTIAN API → Evidence/RunTrace → ProductionEvaluator → Neon PostgreSQL → SSE/UI.

## Shot 02 — Authenticated Home

Show hosted public product, signed-in state, Home question entry and service state.

```text
managed session
→ server validation
→ AuthenticatedRuntimeContext
→ PostgreSQL org scope / RLS
```

Never show cookies/tokens/devtools secrets.

## Shot 03 — R310 grounding

Use/select the persisted R310 primary run.

```text
R310 label
→ get_current_user
→ list_assets_by_company
→ authorized asset_R310
```

Technical point: discover authorized IDs instead of asking the customer.

## Shot 04 — Technical → Current analysis

Show one structured path with tool name, normalized arguments/resource, result/status, evidence reference and trace sequence.

## Shot 05 — Progressive drill-down

Show asset-level and point-specific RMS/spectrum calls if visible.

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

```text
result claim
→ evidence ID
→ normalized observation
→ tool + arguments
→ remote resource/status
```

Do not expose chain-of-thought.

## Shot 08 — Analyses / missing R420

Show the bounded unavailable result: R420 was not found in the authorized fleet. No invented asset, hidden-ID request or cross-tenant speculation.

## Shot 09 — Technical → Quality

Show persisted deterministic evaluation for a hosted V13 run. Prefer execution-chain integrity, model-call provenance, production-trace identity, proposal-contract validity, read-only action safety and terminal consistency.

If adding a provider-research overlay, use only the canonical current result:

```text
Groq GPT-OSS-120B
85/85
rubric pass 81.18%
reliability 82.35%
contract failures 9
NO_SELECTION
```

Label it **research qualification / not production promotion**.

## Shot 10 — Technical → Actions

```text
RELEASE 0
EXTERNAL CONSEQUENTIAL EXECUTION DISABLED
```

## Shot 11 — Deployment / separation of concerns

```text
Browser
→ Railway production-web
→ Railway production-api
   ├→ Neon Auth
   ├→ provisional production provider
   ├→ supplied TRACTIAN API
   └→ Neon PostgreSQL

QA/provider research
→ frozen benchmark runners
→ NO automatic production promotion
```

Do not replace the production-provider box with Groq unless Groq has later passed the required gates and production was explicitly promoted.

## Shot 12 — Session resilience

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

## Shot 14 — Provider qualification boundary

Optional if the provider story is included in the video. Show a sanitized evidence/result surface or text overlay, never credentials/raw provider payloads.

```text
frozen 17×5 population
→ Groq 85/85
→ unchanged hard gates
→ NO_SELECTION
→ causal diagnosis
→ no production promotion
```

Do not show partial contaminated causal runs as if they were the completed 21/21 matrix.

## Shot 15 — Final recap

```text
1 server-owned session/tenant
2 durable ownership
3 grounded DecisionSource + AgentController
4 ToolSpec validation
5 HarnessRunner + TRACTIAN HTTPS
6 Evidence + RunTrace
7 terminal + response_mode
8 deterministic evaluation / hard gates
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
- protected benchmark material;
- raw provider response containing sensitive material;
- hidden reasoning;
- localhost as production evidence;
- unsupported final-provider/action/SLO claims;
- wording that Groq “won” or that Cloudflare-vs-Groq final comparison completed.
