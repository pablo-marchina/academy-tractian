# 5-Minute Technical Screenplay

**Audience assumption:** technical reviewer already knows the challenge.  
**Goal:** explain the promoted architecture and prove the core runtime/evaluation path with one real hosted run.  
**Style:** no business introduction, no generic AI explanation, no feature tour.

## Timing contract

| Time | On screen | Presenter action | Technical point to explain |
|---:|---|---|---|
| 00:00–00:25 | Architecture overlay — full promoted path | Start on diagram, not on a title slide | Four boundaries: identity, runtime, tool execution, evaluation/persistence |
| 00:25–00:50 | Identity/tenant zoom + authenticated product | Show signed-in session and selected run scope | Browser input is not authority; server derives trusted runtime context |
| 00:50–01:25 | Results → submit one prepared industrial request | Start one real hosted run; keep mini architecture visible | `AgentController` owns bounded control flow; `DecisionSource` returns structured decisions |
| 01:25–02:00 | Investigation + live tool call | Show tool name, arguments, validation and returned evidence | Model cannot call network directly; `HarnessRunner` + `ToolSpec` are execution boundary |
| 02:00–02:30 | Evidence + Trace/Timeline | Open evidence lineage for the same run | Evidence is normalized and traceable to tool/result/arguments; `RunTrace` records observable behavior |
| 02:30–03:00 | Results terminal + alternate ESCALATE run | Show `FINAL` or another terminal; briefly open a persisted ESCALATE | Terminal policy is explicit: FINAL / CLARIFY / ABSTAIN / ESCALATE; degraded states do not require hallucinated answers |
| 03:00–03:40 | Engineering → Evaluation / Expected vs Observed | Show deterministic metrics and trajectory comparison | Evaluator is post-runtime, isolated from model, and scores process as well as conclusion |
| 03:40–04:10 | Action Control | Show proposal state and safety boundary | 5 consequential actions are proposal-only in Release 0; model decision is not authorization |
| 04:10–04:40 | Deployment overlay | Zoom out to Railway + Neon + Cloudflare + supplied TRACTIAN API | Remote serving, durable state, realtime path, independent hosted component identities |
| 04:40–05:00 | Full architecture with numbered path | Recap the nine runtime stages | End-to-end auditability: identity → decision → tool → evidence → terminal → eval → persistence |

---

## 00:00–00:25 — Promoted architecture

### Show

Use the `Runtime boundary overview` from [`ARCHITECTURE-OVERLAYS.md`](ARCHITECTURE-OVERLAYS.md).

Keep only these primary nodes visible:

```text
Browser / React
    ↓
FastAPI production-api
    ↓
AgentController
    ↓
DecisionSource
    ↓
HarnessRunner / ToolSpec
    ↓
supplied TRACTIAN API

RunTrace → ProductionEvaluator → Neon PostgreSQL → SSE/UI
```

### Say

> “A arquitetura promovida é organizada em quatro boundaries principais: identidade e tenant, controle agentic, execução de tools e avaliação/persistência. O ponto central é que a LLM nunca possui autoridade direta sobre identidade, permissões ou I/O externo.”

Then name the control split:

> “`DecisionSource` propõe uma decisão tipada, `AgentController` controla o loop, `HarnessRunner` é a única boundary canônica de execução, e `ProductionEvaluator` roda somente depois do runtime.”

### Do not show yet

- provider tournament details;
- CI;
- action custody internals;
- every DB table;
- all 18 tools.

---

## 00:25–00:50 — Identity and tenant boundary

### Show

1. Product already authenticated.
2. If available, briefly expose the UI indicator of signed-in user / organization context.
3. Overlay:

```text
HttpOnly managed session
→ server-side session validation
→ authenticated user + organization scope
→ AuthenticatedRuntimeContext
→ PostgreSQL transaction scope
→ RLS
```

### Say

> “O navegador não escolhe tenant, role ou permissions. A sessão é validada no servidor e o backend deriva o `AuthenticatedRuntimeContext`. Esse contexto também é aplicado ao acesso persistido, com RLS como boundary independente.”

> “Isso impede que uma decisão do modelo ou um header arbitrário do browser se transforme em autoridade.”

### Technical emphasis

- fail closed on invalid/mismatched session;
- server-owned permissions;
- tenant isolation exists outside the LLM.

---

## 00:50–01:25 — Start one real run

### Show

In `Results`:

1. Use one preselected request that requires 2–3 reads.
2. Submit it.
3. Keep a compact architecture overlay visible.
4. As the run starts, highlight:

```text
Browser
→ POST /api/runs
→ FastAPI
→ persist run ownership/state
→ AgentController
→ DecisionSource
```

### Say

> “Cada run começa com um contexto autenticado persistido. O `AgentController` então monta o estado observável e chama uma interface de decisão desacoplada do provider.”

> “O provider não retorna código para executar. Ele retorna uma decisão estruturada: por exemplo uma tool call, ou um estado terminal como FINAL, CLARIFY, ABSTAIN ou ESCALATE.”

### Show if the UI exposes it

- current stage;
- selected operation;
- bounded progress;
- no raw chain-of-thought.

---

## 01:25–02:00 — Tool execution boundary

### Show

Open `Investigation` while the same run is selected.

Choose one visible tool event and keep these fields legible:

```text
tool name
arguments
validation/result state
evidence/result reference
```

Overlay:

```text
structured TOOL_CALL
→ canonical ToolSpec lookup
→ B1 schema / argument validation
→ B2 permission / resource / policy
→ HarnessRunner
→ ProductionTractianTransport
→ typed HTTPS
→ supplied TRACTIAN API
```

### Say

> “Uma proposta de tool nunca vai diretamente do modelo para a rede. Primeiro ela precisa resolver contra o registry canônico de `ToolSpec`, passar pelas validações determinísticas e somente então o `HarnessRunner` executa o transporte.”

> “Isso mantém seleção da função, construção de argumentos e execução observáveis separadamente, que são justamente dimensões avaliáveis do desafio.”

> “O contrato possui 18 operações canônicas: 13 reads estão live na Release 0 e 5 actions permanecem proposal-only.”

### Must be visually proven

At least one actual remote read should visibly return evidence before moving on.

---

## 02:00–02:30 — Evidence and trace model

### Show

Open `Evidence`, then one `Investigation` trace/timeline visualization if needed.

The same run must remain selected.

Point to this lineage:

```text
claim / observation
→ evidence ID
→ normalized tool result
→ tool call + arguments
→ remote resource / timestamp
```

Then show several structured events:

```text
decision proposed
→ tool validated
→ tool executed
→ observation/evidence created
→ next decision
```

### Say

> “O retorno da API é normalizado como evidência persistível e o runtime produz um `RunTrace` estruturado. Nós auditamos decisões, calls, args, observations, falhas e terminais; não dependemos de expor chain-of-thought privado.”

> “Isso permite relacionar a resposta final ao comportamento externo verificável que realmente aconteceu.”

---

## 02:30–03:00 — Terminal policy and failure semantics

### Show

Return to `Results` for the main run and show the terminal outcome.

Then switch to one already-persisted run showing `ESCALATE` or `ABSTAIN`.

Visible terminal vocabulary:

```text
FINAL
CLARIFY
ABSTAIN
ESCALATE
ACTION_PROPOSAL
```

### Say

> “O controller não força uma resposta final. `FINAL` exige evidência suficiente; `CLARIFY` pede informação que pode resolver a lacuna; `ABSTAIN` preserva segurança quando não há base suficiente; e `ESCALATE` entrega o caso para revisão humana.”

> “Retornos parciais, conflitantes, inconclusivos ou indisponíveis podem portanto alterar a política terminal em vez de gerar uma resposta fabricada.”

For ESCALATE, show if available:

```text
reason for escalation
collected evidence
unresolved point
recommended human next check
```

---

## 03:00–03:40 — Evaluation architecture

### Show

Open `Engineering` → evaluation surface for the main run.

First show the pipeline:

```text
completed RunTrace
→ ProductionEvaluator
→ deterministic structural / safety / trajectory checks
→ safe evaluation projection
```

Then show `Expected vs Observed` or equivalent metrics.

Prioritize these dimensions when present:

```text
function/tool selection
argument correctness/validity
trajectory / expected-read coverage
evidence correctness/coverage
terminal / operational decision
action correctness
escalation correctness
safety / failure handling
stability
```

### Say

> “O evaluator é pós-runtime. A referência usada para avaliação não entra no prompt nem fica disponível para o agente.”

> “Isso permite avaliar duas coisas separadamente: se o output final está correto e se o processo usado para chegar nele corresponde ao comportamento esperado.”

> “Quando existe regressão, conseguimos localizar se ela surgiu na seleção da função, nos argumentos, na trajetória, na evidência ou na decisão terminal.”

### If a metric is not actually available

Do not invent it. Show only the promoted/evidenced metrics currently rendered.

---

## 03:40–04:10 — Consequential action boundary

### Show

Open `Action Control` for any run with a visible action proposal, or use the capability view if no suitable proposal is persisted.

Overlay:

```text
model proposes action
→ schema/policy checks
→ proposal state
→ explicit confirmation boundary
→ authorization / custody / idempotency / lease architecture
→ external execution
```

Mark the last step clearly:

```text
RELEASE 0: EXTERNAL CONSEQUENTIAL EXECUTION DISABLED
```

### Say

> “Reads e writes não compartilham a mesma autoridade. O modelo pode propor uma ação, mas proposal não é authorization.”

> “O código possui uma arquitetura governada para confirmação, custody, idempotência e leases, porém a Release 0 mantém autorização externa consequencial em deny-all. Portanto, neste vídeo nós demonstramos a boundary sem afirmar uma execução que não está promovida.”

---

## 04:10–04:40 — Deployment and realtime

### Show

Use the deployment overlay:

```text
Browser
→ Railway production-web (Caddy / React build)
→ Railway production-api (FastAPI/Uvicorn)
   ├→ Neon Auth
   ├→ Cloudflare Workers AI
   ├→ supplied TRACTIAN API
   └→ Neon PostgreSQL
```

Then briefly show the realtime path:

```text
runtime transition
→ immutable event row
→ PostgreSQL commit
→ LISTEN/NOTIFY wake-up
→ durable catch-up read
→ authenticated SSE
→ idempotent React state
```

### Say

> “O produto demonstrado é o sistema hospedado. Frontend e backend rodam remotamente no Railway; identidade e estado durável usam Neon; decisões usam o provider hospedado provisório; e as reads acessam remotamente a API fornecida pela TRACTIAN.”

> “PostgreSQL é a fonte de verdade. `LISTEN/NOTIFY` serve apenas como wake-up; o cliente recupera eventos por cursor durável e SSE autenticado.”

> “Também separamos identidade de source merge e identidade de deployment: um commit na main não é tratado como prova automática de redeploy.”

---

## 04:40–05:00 — Technical recap

### Show

Full architecture with numbers appearing in sequence:

```text
1  Session validation / tenant context
2  Run creation + durable ownership
3  AgentController / structured DecisionSource
4  ToolSpec + deterministic validation
5  HarnessRunner + remote TRACTIAN read
6  Evidence + RunTrace
7  Safe terminal policy
8  Post-runtime ProductionEvaluator
9  PostgreSQL projection + authenticated SSE
```

### Say

> “O resultado técnico é um runtime agentic auditável: identidade e autorização ficam fora do modelo; decisões são estruturadas; tools passam por uma boundary tipada; evidências e traces são persistidos; terminais degradam de forma explícita; e a avaliação é independente do runtime.”

> “Isso nos permite não apenas executar uma investigação, mas medir exatamente como ela foi executada e localizar onde uma mudança introduz regressão.”

Stop immediately after this sentence.

---

## Hard recording rules

- One primary run from start through evaluation.
- One secondary persisted run only for ESCALATE/ABSTAIN demonstration.
- Never switch to an unrelated run without verbally stating it.
- Never display private secrets, cookies, raw auth tokens, provider keys, internal credentials or evaluator-private gold.
- Never display hidden chain-of-thought.
- Never claim consequential action execution in Release 0.
- Never claim Cloudflare as final model winner; it is provisional.
- Never call the hosted supplied API “TRACTIAN corporate production API”; it is the remotely hosted API supplied for the project.
- Prefer exact observed values over generic claims whenever the UI renders them.