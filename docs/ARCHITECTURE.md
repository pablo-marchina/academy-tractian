# Academy × TRACTIAN — Architecture

**Status:** ACTIVE canonical architecture  
**Last verified:** 2026-09-07 BRT  
**Promoted backend/runtime:** `08866da60245f58f217981b7ae668b10be45cc67`  
**Current hosted frontend UX:** `1bc124a8d4dbd029178ff8129b25452129445de7`  
**Current hosted supplied API:** `47561c1175181b508139e23e6e39b555c1347d57`

This document describes the architecture actually hosted now. Repository/source identity and hosted component identities are deliberately separate; a source merge or docs commit is not an automatic backend promotion.

## 1. System context

```mermaid
flowchart LR
    U[Authenticated industrial user/reviewer]
    S[Academy × TRACTIAN\nIndustrial Agent + Evaluation]
    A[Neon Auth]
    P[Cloudflare Workers AI]
    T[Supplied TRACTIAN API]
    D[Neon PostgreSQL]

    U -->|HTTPS questions/history/review| S
    S -->|managed session validation| A
    S -->|bounded structured decision| P
    S -->|typed HTTPS reads| T
    S -->|tenant-scoped durable state/evidence/eval| D
```

Key boundary: browser input and model output are never authority for tenant/role/permissions.

## 2. Production containers

```mermaid
flowchart TB
    B[Browser\nReact 19 SPA]
    W[production-web\nCaddy + Vite build\nRailway]
    API[production-api\nFastAPI/Uvicorn\nRailway]
    AUTH[Neon Auth]
    DB[Neon PostgreSQL\noperational + RLS + observability]
    CF[Cloudflare Workers AI\nprovisional GLM-4.7-Flash]
    TR[Supplied TRACTIAN API\n18-operation contract]

    B -->|HTTPS same origin| W
    W -->|/auth/*| AUTH
    W -->|/api/* + SSE| API
    API -->|server-managed session validation| AUTH
    API -->|TLS/psycopg| DB
    API -->|structured DecisionSource call| CF
    API -->|typed bounded HTTPS read| TR
```

| Container | Responsibility | Current state |
|---|---|---|
| browser SPA | task-driven user interaction + safe visualization | Home / Analyses / Technical; contextual result/evidence |
| `production-web` | public HTTPS origin/static serving/proxy | Caddy on Railway, `1bc124a...` |
| `production-api` | auth context, runtime, tools, policy, evaluation, REST/SSE | V13, `08866da...` |
| Neon Auth | managed session lifecycle | server-validated, bounded read-burst coalescing |
| Neon PostgreSQL | durable operational truth + tenant RLS + observability/evals | PostgreSQL + psycopg |
| Cloudflare Workers AI | provisional Release 0 decisions | `@cf/zai-org/glm-4.7-flash` |
| supplied TRACTIAN API | canonical industrial evidence | 13 read operations available; 5 action operations not externally executable in Release 0 |

## 3. Dynamic investigation flow

```mermaid
sequenceDiagram
    actor User
    participant Web as React/Caddy
    participant API as FastAPI
    participant Auth as Neon Auth
    participant DB as Neon PostgreSQL
    participant Model as Cloudflare
    participant Tool as HarnessRunner
    participant T as TRACTIAN
    participant Eval as ProductionEvaluator

    User->>Web: submit equipment question
    Web->>API: POST /api/runs (managed session)
    API->>Auth: fresh session validation for non-read request
    API->>API: derive server-owned tenant/runtime context
    API->>DB: persist run ownership/state
    API->>Model: bounded structured decision request
    Model-->>API: typed decision/tool proposal
    API->>Tool: validate + execute canonical read
    Tool->>T: typed HTTPS request
    T-->>Tool: evidence response
    Tool-->>API: normalized observation/evidence
    API->>Model: next bounded decision when needed
    Model-->>API: terminal decision + response_mode
    API->>DB: persist terminal trace/evidence
    API->>Eval: deterministic post-runtime evaluation
    Eval-->>DB: safe evaluation projection
    API-->>Web: authenticated SSE + durable catch-up
    Web-->>User: result first; Analyses/Technical on demand
```

The evaluator is post-runtime. Evaluator-private truth is not supplied to the model.

## 4. V13 Release 0 decision layer

The current serving provider wrapper is intentionally layered so each production fix stays narrow and testable:

```text
base Release 0 provider contract
→ V10: nested ID grounding + condition-evidence/stopping constraints
→ V11: response_mode epistemic semantics
→ V12: explicit human asset labels, bilateral comparisons, data-quality requirements
→ V13: initial identity grounding + completed single-asset quality suppression
```

`remote_server.py` serves `build_release_provider_decision_source_factory_v13`.

### V11 response semantics

`response_mode` is separate from terminal authority:

```text
complete      all material requested parts supported
partial       useful supported answer + material probabilistic/incomplete part
inconclusive no reliable directional answer after inspecting relevant evidence
conflict      material observations contradict
unavailable   required authorized evidence could not be obtained
```

### V12/V13 explicit-asset grounding

For investigative requests with labels like `R310`:

```text
label in user request
→ get_current_user
→ structured company_id
→ list_assets_by_company
→ structured authorized asset IDs
→ map human label to fleet resource
→ constrain subsequent tool schemas to observed IDs
```

If the label is absent, the tool surface closes and the terminal must report bounded unavailability. The model may not expand itself to another tenant/company.

For a multi-asset comparison, the runtime requires condition evidence for every requested asset present in the authorized fleet before a comparative conclusion.

### Condition and data-quality gates

- diagnostic questions require condition evidence (`get_analysis`, `get_rms`, `get_spectrum`) before terminal where required;
- baseline/data quality do not substitute for condition evidence;
- explicit data-quality questions require `get_data_quality`;
- completed single-asset `get_data_quality` is removed from the visible surface;
- `get_asset` is suppressed after fleet listing has already grounded metadata.

## 5. Tool execution boundary

```text
DecisionSource
→ structured decision/proposal

AgentController
→ bounded control flow

HarnessRunner
→ canonical tool execution boundary

B1 schema/argument validation
B2 permission/resource/policy

ProductionTractianTransport
→ real network contract, server credentials, timeout/size/redirect rules
```

A model cannot directly perform network I/O or grant itself permissions.

## 6. Progressive technical drill-down

The runtime may refine a successful read when structured output exposes a more specific point/resource:

```text
get_rms(asset_R310)
→ discover point_id
→ get_rms(asset_R310, point_id=pt_R310_de)
```

or equivalent spectrum progression.

This is not an exact duplicate loop. Stopping/redundancy evaluation should consider normalized arguments, resource target and incremental evidence contribution.

## 7. Managed identity and session resilience

```text
managed HttpOnly browser session
→ server-side Neon session validation
→ authenticated user + active/personal organization scope
→ AuthenticatedRuntimeContext
→ transaction-local PostgreSQL organization scope
→ RLS
```

Read-burst resilience:

```text
GET / HEAD
→ SHA-256(cookie) lookup
→ ≤2 s bounded validated-context cache
→ singleflight on miss
→ Neon Auth when needed

POST / non-read
→ bypass read cache
→ fresh Neon Auth validation
```

Properties:

- raw cookie is not cached;
- max 256 read contexts;
- no stale-on-error after expiry;
- invalid session = 401;
- temporary auth-service unavailability = 503 + `Retry-After: 1`;
- browser reconciles auth on managed-auth signal, focus and visibility return.

RLS remains independent from this cache and from the model.

## 8. Evidence and realtime architecture

```text
canonical runtime transition
→ sanitized immutable event row
→ authoritative (run_id, sequence) cursor
→ PostgreSQL commit
→ LISTEN/NOTIFY wake-up
→ bounded durable catch-up
→ authenticated SSE
→ idempotent React state
```

PostgreSQL rows/cursors are truth. `LISTEN/NOTIFY` is only wake-up; missed notifications cannot become missing authoritative state.

Raw secrets, private action custody, evaluator-private material and hidden chain-of-thought are excluded from browser projections.

## 9. Current UX architecture

Hosted UX is task-driven rather than globally depth-tab driven:

```text
Home
  ask one question / examples / service state
    ↓ run
Result
  conclusion + next step + contextual evidence
    ↙                         ↘
Analyses                    Technical
persisted history           analysis / quality / data / system / actions / studies
```

Technical depth still exposes the same underlying runtime/evaluation/capability evidence; it is simply organized by user task.

## 10. Capability and action boundary

```text
18 canonical operations
13 READ  → available through Release 0 read path when provider + TRACTIAN transport are enabled
5 ACTION → represented/proposal-only; external execution disabled
```

The codebase contains stronger governed action machinery (custody, confirmation, idempotency, leases/fencing, uncertainty), but **production Release 0 authorization is deny-all for consequential external execution**.

## 11. Provider boundary

- Release 0 serving: Cloudflare GLM-4.7-Flash is provisional.
- Final provider selection: frozen Provider Tournament v3 remains `NO_SELECTION`.

No hidden fallback may silently replace provider/model/route or cross into paid operation.

## 12. Release/deployment identity

Current hosted identities:

- backend/runtime `08866da60245f58f217981b7ae668b10be45cc67`;
- frontend `1bc124a8d4dbd029178ff8129b25452129445de7`;
- supplied API `47561c1175181b508139e23e6e39b555c1347d57`.

Original Release 0 acceptance remains historical at backend `082d6f...`.

Backend production artifacts bind configured release SHA to baked artifact identity and Railway runtime identity before serving a production claim. Component deployments may advance independently.

## 13. Evaluation architecture

```text
RunTrace
→ deterministic structural/safety/trajectory checks
→ safe evaluation projection
→ Technical quality/analysis surfaces
```

Current live V13 runs passed blocking checks including execution-chain integrity, model-call provenance, production-trace identity, proposal-contract validity, read-only action safety and terminal consistency.

Human semantic calibration remains separate and non-gating until real blinded labels establish reliability.

## 14. Technology decisions currently promoted

| Area | State |
|---|---|
| custom `AgentController` | promoted baseline |
| typed `HarnessRunner` / `ToolSpec` | hard execution boundary |
| FastAPI + REST/SSE | promoted |
| PostgreSQL serving truth | promoted |
| PostgreSQL LISTEN/NOTIFY wake-up | promoted; rows remain truth |
| React/Vite/Caddy | promoted task-driven frontend |
| Railway frontend/backend | hosted Release 0 |
| Neon PostgreSQL/Auth | hosted Release 0 |
| Cloudflare GLM-4.7-Flash | provisional Release 0 only |
| DuckDB | dev/benchmark compatibility only |
| RAG/vector DB | NO_CHANGE |
| persistent memory | NO_CHANGE |
| multi-agent | NO_CHANGE |
| MCP | NO_CHANGE unless measured interoperability gap appears |
| LangGraph migration | NO_CHANGE unless challenger wins |
| Redis/Kafka/Kubernetes | NO_CHANGE unless measured need appears |
| adaptive stopping/routing | not promoted; challenger/evaluator scope only |

## 15. Current non-claims

Do not claim final provider superiority, OAuth/OIDC/enterprise SSO, consequential external action readiness, full SECURITY-V1, final production capacity/SLO/HA/RTO/RPO, human semantic calibration, observed time savings, complete live coverage of all 13 reads or adaptive-policy superiority until corresponding evidence exists.