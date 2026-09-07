# Presentation Architecture Overlays

These diagrams simplify [`../ARCHITECTURE.md`](../ARCHITECTURE.md). They are presentation assets, not independent architecture truth.

## 1. Runtime boundary overview

```mermaid
flowchart TB
    B[Browser / task-driven React]
    W[Railway production-web]
    API[FastAPI production-api]
    CTX[AuthenticatedRuntimeContext]
    V13[V13 DecisionSource]
    AC[AgentController]
    HR[HarnessRunner + ToolSpec]
    TR[supplied TRACTIAN API]
    EV[Evidence + RunTrace]
    PE[ProductionEvaluator]
    DB[Neon PostgreSQL]
    SSE[Authenticated SSE / UI]

    B --> W --> API --> CTX --> AC
    AC <--> V13
    AC --> HR --> TR --> HR --> EV --> AC
    EV --> DB
    AC --> PE --> DB
    DB --> SSE --> B
```

Key line: model proposes; deterministic runtime owns authority/execution.

## 2. Identity / session / tenant overlay

```mermaid
flowchart LR
    S[Managed HttpOnly Session]
    V[Server validation]
    U[Authenticated User]
    O[Active/Personal Org]
    C[AuthenticatedRuntimeContext]
    TX[Postgres Transaction Scope]
    RLS[RLS]

    S --> V --> U --> O --> C --> TX --> RLS
```

Resilience inset:

```text
GET/HEAD → SHA256(cookie) → ≤2s validated cache → singleflight
POST/non-read → fresh validation
expired cache → never stale-on-error
401 invalid ≠ 503 unavailable
```

## 3. V13 explicit-asset grounding

```mermaid
flowchart LR
    Q[User: investigate R310]
    U[get_current_user]
    C[structured company_id]
    F[list_assets_by_company]
    A[authorized asset_R310]
    E[condition/data-quality reads]
    T[terminal]

    Q --> U --> C --> F --> A --> E --> T
```

Missing label path:

```text
label absent from authorized fleet
→ no cross-scope expansion
→ no request for hidden asset_id
→ bounded unavailable terminal
```

## 4. Canonical tool execution

```mermaid
flowchart LR
    D[Structured TOOL decision]
    TS[ToolSpec Lookup]
    B1[Schema / Argument Validation]
    B2[Permission / Resource / Policy]
    HR[HarnessRunner]
    PT[ProductionTractianTransport]
    API[Supplied TRACTIAN API]
    OBS[Observation / Evidence]

    D --> TS --> B1 --> B2 --> HR --> PT --> API --> OBS
```

## 5. Progressive technical drill-down

```mermaid
flowchart LR
    A[get_spectrum(asset_R310)]
    P[structured point_id observed]
    S[get_spectrum(asset_R310, point_id)]
    E[more specific evidence]

    A --> P --> S --> E
```

Key line: same tool name does not imply duplicate; compare arguments/resource/evidence contribution.

## 6. Evidence / trace lineage

```mermaid
flowchart LR
    C[Customer-visible claim]
    E[Evidence ID]
    R[Normalized Tool Result]
    T[Tool Call]
    A[Arguments]
    P[Remote Resource / Provenance]
    RT[RunTrace Sequence]

    C --> E --> R --> T
    T --> A
    T --> P
    T --> RT
    R --> RT
```

Audit external observable artifacts, not hidden chain-of-thought.

## 7. Terminal + response-mode overlay

```mermaid
flowchart TB
    E{Evidence state}
    D[Controller terminal decision]
    M[response_mode]
    C[complete]
    P[partial]
    I[inconclusive]
    X[conflict]
    U[unavailable]

    E --> D
    E --> M
    M --> C
    M --> P
    M --> I
    M --> X
    M --> U
```

Key line: terminal controls runtime outcome; response mode describes epistemic support. Neither grants authorization.

## 8. Evaluator isolation

```mermaid
flowchart LR
    RUN[Completed Runtime]
    TRACE[RunTrace]
    EVAL[ProductionEvaluator]
    GOLD[Evaluator-private Reference]
    DET[Deterministic Checks]
    OUT[Safe Evaluation Projection]
    DB[Neon PostgreSQL]

    RUN --> TRACE --> EVAL
    GOLD --> EVAL
    EVAL --> DET --> OUT --> DB
```

Draw no arrow from evaluator-private reference to runtime/model.

## 9. Consequential action boundary

```mermaid
flowchart LR
    M[Model Proposal]
    V[Validation]
    C[Confirmation Boundary]
    A[Authorization / Custody]
    I[Idempotency + Lease]
    X[External Consequential Execution]

    M --> V --> C --> A --> I --> X
```

Overlay on X:

```text
RELEASE 0
DISABLED / DENY-ALL
```

## 10. Production deployment

```mermaid
flowchart TB
    B[Browser]
    W[production-web\nRailway\n1bc124a...]
    API[production-api\nRailway\n08866da...]
    AUTH[Neon Auth]
    CF[Cloudflare Workers AI\nprovisional]
    TR[Supplied TRACTIAN API\n47561c...]
    DB[Neon PostgreSQL]

    B -->|HTTPS| W
    W -->|/api + SSE| API
    W -->|/auth| AUTH
    API --> AUTH
    API --> CF
    API --> TR
    API --> DB
```

## 11. Durable realtime

```mermaid
flowchart LR
    RT[Runtime Transition]
    ROW[Immutable Event Row]
    COMMIT[PostgreSQL Commit]
    NOTIFY[LISTEN/NOTIFY Wake-up]
    CURSOR[Durable Catch-up]
    SSE[Authenticated SSE]
    UI[React State]

    RT --> ROW --> COMMIT --> NOTIFY --> CURSOR --> SSE --> UI
```

PostgreSQL rows/cursors are authoritative; notification only reduces latency.

## 12. Current task-driven UI

```mermaid
flowchart TB
    H[Home\nAsk question]
    R[Result\nConclusion + evidence]
    A[Analyses\nPersisted history]
    T[Technical]
    CA[Current analysis]
    Q[Quality]
    D[Data]
    S[System]
    AC[Actions]
    ST[Studies]

    H --> R
    A --> R
    R --> T
    T --> CA
    T --> Q
    T --> D
    T --> S
    T --> AC
    T --> ST
```

## 13. Final recap

```text
1  Server-validated identity / tenant
2  Durable run ownership
3  V13 grounding + AgentController
4  ToolSpec deterministic validation
5  HarnessRunner + remote TRACTIAN I/O
6  Evidence + RunTrace
7  Terminal + response_mode semantics
8  Post-runtime ProductionEvaluator
9  PostgreSQL + authenticated SSE + task-driven UI
```

End on this complete causal path.