# Presentation Architecture Overlays

These diagrams are intentionally simpler than [`../ARCHITECTURE.md`](../ARCHITECTURE.md). They are presentation assets, not independent architecture truth.

Use them as overlays while the live product runs. Highlight only the active path.

---

## 1. Runtime boundary overview

```mermaid
flowchart TB
    B[Browser / React]
    API[FastAPI production-api]
    CTX[AuthenticatedRuntimeContext]
    AC[AgentController]
    DS[DecisionSource]
    HR[HarnessRunner + ToolSpec]
    TR[supplied TRACTIAN API]
    EV[Evidence + RunTrace]
    PE[ProductionEvaluator]
    DB[Neon PostgreSQL]
    SSE[Authenticated SSE / UI]

    B --> API
    API --> CTX
    CTX --> AC
    AC --> DS
    DS --> AC
    AC --> HR
    HR --> TR
    TR --> HR
    HR --> EV
    EV --> AC
    AC --> PE
    PE --> DB
    EV --> DB
    DB --> SSE
    SSE --> B
```

### Highlight sequence

1. `Browser → FastAPI → AuthenticatedRuntimeContext`
2. `AgentController ↔ DecisionSource`
3. `AgentController → HarnessRunner → TRACTIAN`
4. `TRACTIAN → Evidence/RunTrace`
5. `RunTrace → ProductionEvaluator → PostgreSQL`
6. `PostgreSQL → SSE → Browser`

---

## 2. Identity / tenant authority overlay

```mermaid
flowchart LR
    S[Managed HttpOnly Session]
    V[Server-side Session Validation]
    U[Authenticated User]
    O[Active / Personal Organization Scope]
    C[AuthenticatedRuntimeContext]
    TX[PostgreSQL Transaction Scope]
    RLS[RLS]

    S --> V --> U --> O --> C --> TX --> RLS
```

### Presenter labels

- Browser-supplied tenant/role/permission values are not authority.
- Invalid or mismatched session fails closed.
- Runtime permissions are server-defined.
- RLS is independent of the LLM.

---

## 3. Agent control-flow overlay

```mermaid
flowchart LR
    REQ[Run State + Observable Context]
    AC[AgentController]
    DS[DecisionSource]
    DEC{Structured Decision}
    TOOL[TOOL_CALL]
    FIN[FINAL]
    CLA[CLARIFY]
    ABS[ABSTAIN]
    ESC[ESCALATE]
    ACT[ACTION_PROPOSAL]

    REQ --> AC --> DS --> DEC
    DEC --> TOOL
    DEC --> FIN
    DEC --> CLA
    DEC --> ABS
    DEC --> ESC
    DEC --> ACT
```

### Key line

`DecisionSource` proposes; `AgentController` owns the bounded loop.

---

## 4. Canonical tool execution overlay

```mermaid
flowchart LR
    D[Structured TOOL_CALL]
    TS[Canonical ToolSpec Lookup]
    B1[B1 Schema / Argument Validation]
    B2[B2 Permission / Resource / Policy]
    HR[HarnessRunner]
    PT[ProductionTractianTransport]
    HTTP[Typed HTTPS]
    API[supplied TRACTIAN API]
    OBS[Normalized Observation / Evidence]

    D --> TS --> B1 --> B2 --> HR --> PT --> HTTP --> API --> OBS
```

### Key lines

- The model does not directly perform network I/O.
- Tool name, arguments, validation and transport are separately observable.
- Release 0 capability contract: `13 READ live + 5 ACTION proposal-only`.

---

## 5. Evidence / trace lineage overlay

```mermaid
flowchart LR
    C[Terminal Claim / Observation]
    E[Evidence ID]
    R[Normalized Tool Result]
    T[Tool Call]
    A[Arguments]
    P[Remote Resource / Provenance]
    RT[RunTrace Event Sequence]

    C --> E --> R --> T
    T --> A
    T --> P
    T --> RT
    R --> RT
```

### Key line

Audit observable execution artifacts, not hidden chain-of-thought.

---

## 6. Terminal policy overlay

```mermaid
flowchart TB
    E{Evidence state}
    F[FINAL]
    C[CLARIFY]
    A[ABSTAIN]
    S[ESCALATE]

    E -->|sufficient + supported| F
    E -->|user-resolvable missing context| C
    E -->|no safe supported conclusion| A
    E -->|ambiguity / human judgment required| S
```

### Key line

Degraded evidence changes terminal behavior instead of forcing a fabricated answer.

---

## 7. Evaluator isolation overlay

```mermaid
flowchart LR
    RUN[Completed Runtime]
    TRACE[RunTrace]
    EVAL[ProductionEvaluator]
    GOLD[Evaluator-private Reference / Expected Path]
    DET[Deterministic Structural / Safety / Trajectory Checks]
    OUT[Safe Evaluation Projection]
    DB[Neon PostgreSQL]

    RUN --> TRACE --> EVAL
    GOLD --> EVAL
    EVAL --> DET --> OUT --> DB
```

### Important visual rule

Draw **no arrow from evaluator-private reference to runtime/model**.

### Key line

The agent cannot optimize against private gold during the run.

---

## 8. Expected vs observed overlay

```text
EXPECTED TRAJECTORY          OBSERVED RUN
───────────────────          ────────────
Tool A                       Tool A        ✓
Tool B                       Tool B        ✓
Tool C                       Tool C        ✓ / ✗
Expected evidence            Evidence      metric
Expected terminal            Terminal      ✓ / ✗
Action/escalation            Decision      ✓ / ✗
```

Show only fields that are actually evidenced for the selected run.

---

## 9. Consequential action boundary overlay

```mermaid
flowchart LR
    M[Model Decision]
    P[Action Proposal]
    V[Schema / Policy Validation]
    C[Explicit Confirmation Boundary]
    A[Authorization / Private Custody]
    I[Idempotency + Execution Lease]
    X[External Consequential Execution]

    M --> P --> V --> C --> A --> I --> X
```

Overlay label on `X`:

```text
RELEASE 0
DISABLED / DENY-ALL
```

### Key line

Proposal visibility is not execution authority.

---

## 10. Production deployment overlay

```mermaid
flowchart TB
    B[Browser]
    W[Railway production-web\nCaddy + React/Vite]
    API[Railway production-api\nFastAPI/Uvicorn]
    AUTH[Neon Auth]
    CF[Cloudflare Workers AI\nprovisional provider]
    TR[remotely hosted supplied TRACTIAN API]
    DB[Neon PostgreSQL]

    B -->|HTTPS| W
    W -->|/api/* + SSE| API
    W -->|/auth/*| AUTH
    API --> AUTH
    API --> CF
    API --> TR
    API --> DB
```

### Key lines

- Same demonstrated product is remotely hosted.
- Provider is provisional, not a final tournament winner.
- Supplied API is project-hosted remote integration, not TRACTIAN corporate production infrastructure.

---

## 11. Durable realtime overlay

```mermaid
flowchart LR
    RT[Runtime Transition]
    ROW[Immutable Event Row]
    COMMIT[PostgreSQL Commit]
    NOTIFY[LISTEN / NOTIFY Wake-up]
    CURSOR[Durable Catch-up by run_id + sequence]
    SSE[Authenticated SSE]
    UI[Idempotent React State]

    RT --> ROW --> COMMIT --> NOTIFY --> CURSOR --> SSE --> UI
```

### Key line

PostgreSQL rows/cursors are authoritative; notifications only reduce polling/latency.

---

## 12. Final 9-step recap

Use this as the last frame:

```text
1  Session validation / tenant context
2  Durable run ownership
3  AgentController + DecisionSource
4  Canonical ToolSpec validation
5  HarnessRunner + remote TRACTIAN HTTPS
6  Evidence + RunTrace
7  Explicit terminal policy
8  Post-runtime ProductionEvaluator
9  PostgreSQL projection + authenticated SSE
```

Do not add another architecture layer after this. End on the complete causal path.