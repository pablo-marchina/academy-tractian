# Academy × TRACTIAN

Produção e avaliação de agentes industriais sobre a API didática da TRACTIAN.

A entrega é uma solução única com duas capacidades integradas:

- **Agente industrial:** interpreta solicitações, consulta 18 tools tipadas da TRACTIAN, reúne evidência e decide entre orientar/finalizar, esclarecer, abster/escalar ou propor uma ação governada;
- **Framework de avaliação:** mede trajetória, seleção/argumentos de tools, evidência, segurança, falhas, estabilidade, ações e valor operacional sem expor material privado do avaliador.

## Estado final P0

Baseline aceita em `main`:

`d3bed06b132212c85b126f56708863d45f64e03e`

Post-merge `final-ci-required` run `33971230788` / run #386: **PASS**.

```text
clean-clone / reproduce-current-product                  success
full-product-browser / chromium-full-product              success
horizontal-runtime-handoff / postgres-horizontal-runtime  success
action-execution-lease / postgres-action-lease            success
required-gate                                             success
```

Estado funcional:

- runtime provider-neutral + deterministic evaluator: **implementados**;
- integração TRACTIAN: **18 operações tipadas**;
- produto multiusuário `POST /api/runs` + REST/SSE: **implementado**;
- serving persistence: **PostgreSQL**;
- observabilidade/evaluation safe read model: **PostgreSQL**;
- realtime wakeup: **PostgreSQL LISTEN/NOTIFY**, com linhas/cursor duráveis como verdade;
- tenant isolation: **PostgreSQL RLS** + bearer HMAC-SHA256 server-trusted;
- read-only cross-replica handoff: **implementado e generation-fenced**;
- consequential actions: **custody → confirmação → idempotency → non-transferable lease → execução**;
- perda de ownership de ação: **`UNCERTAIN`**, sem replacement replay;
- DuckDB: **somente extra explícito de dev/benchmark**, não dependência de produção;
- frontend React operator control room: **implementado e browser-gated**;
- clean-clone current-product reproduction: **verde e gated**;
- D01/D02 provider experiments: **USD 0 / `NO_SELECTION`**;
- semantic human calibration: **NOT READY — dados humanos reais ausentes**;
- engineer-time/business-value claim: **NOT READY — medições humanas reais ausentes**;
- adaptive runtime stopping: **não promovido**;
- branch protection: **CI pronta; enforcement GitHub ainda externo**;
- final evidence state: **`READY_FOR_HARD_FREEZE` candidate**;
- hard feature/visual/architecture freeze: **fim de 2026-09-05**;
- entrega: **2026-09-08**.

Fonte humana canônica: [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md).  
Closure P0: [`research/p0-hard-freeze-closure-2026-09-05.md`](research/p0-hard-freeze-closure-2026-09-05.md).  
Manifesto verificável: [`research/results/final-freeze-evidence-bundle-2026-09-04.json`](research/results/final-freeze-evidence-bundle-2026-09-04.json).

## Arquitetura promovida

```text
React Operator Control Room
        ↑ REST + genuine SSE
FastAPI Product / Observability API
        ↑ signed RuntimeContextProvider + tenant RLS
PostgreSQL shared serving substrate
        ├── run ownership/execution
        ├── runtime handoff queue + lease generation
        ├── action custody/idempotency/non-transferable leases
        ├── safe observability/evaluation rows
        └── semantic-review / operational-value state
        ↑
RealtimeProductionRuntime
        ↓
provider-neutral DecisionSource
        ↓
AgentController → HarnessRunner
        ↓
18-operation typed ToolSpec registry
        ↓
B1 / B2 / B3 deterministic safety boundaries
        ↓
TRACTIAN transport
        ↓
normalized evidence
        ↓
FINAL | CLARIFY | ABSTAIN | ESCALATE | action proposal
        ↓
RunTrace → ProductionEvaluator
        ↓
safe PostgreSQL projection
        ↓
REST/SSE + LISTEN/NOTIFY wakeup + durable cursor fallback
        ↓
React operator control room
```

### Read-only execution

Read-only runtime work usa lease expiring + generation token em PostgreSQL. Após expiração, outra réplica pode fazer takeover; owner stale não pode renovar/finalizar/publicar como atual.

### Ação consequencial

```text
proposal
→ deterministic validation
→ private PostgreSQL custody
→ PENDING_CONFIRMATION
→ operator confirma opaque action_id
→ authorization + kill switch revalidated
→ persistent atomic idempotency claim
→ non-transferable action execution lease
→ exact custodied action transport
→ lease-fenced terminal persistence
→ action RunTrace + ProductionActionEvaluator
```

Lease de ação **não transfere**. Se ownership se perde, o outcome torna-se `UNCERTAIN`; o produto não inicia uma tentativa substituta. Isso não é claim de exactly-once externo: essa garantia exigiria participação da API TRACTIAN em um protocolo comum de idempotência/fencing.

## Privacidade e segurança

Browser/API/SSE nunca recebem:

- provider credentials/tokens ou auth headers;
- raw identity binding/signing secret;
- evaluator seed/gold/private truth;
- raw provider request/response;
- raw action custody/idempotency material;
- hidden chain-of-thought.

Observabilidade expõe apenas decisões estruturadas, tools, evidência, políticas/reason codes, métricas e projeções sanitizadas.

## Stack

### Backend/runtime

- Python 3.11+
- Pydantic 2.x
- FastAPI / Uvicorn
- PostgreSQL 18 + psycopg
- custom `AgentController` + `HarnessRunner`
- typed `ToolSpec` registry
- pytest
- DuckDB apenas nos extras `dev`/benchmark

### Frontend

- React 19
- TypeScript
- Vite
- TanStack Query
- Apache ECharts
- React Flow (`@xyflow/react`)
- Vitest
- Playwright
- `package-lock.json` + deterministic `npm ci`

## Eval-Driven Development

```text
requirement
→ metric/evaluator
→ baseline
→ hypothesis
→ preregistered candidate
→ repeated/sliced evaluation
→ hard gates + uncertainty
→ PROMOTE / REJECT / INCONCLUSIVE / NO_CHANGE
→ regression
```

Complexidade arquitetural não entra por convenção. RAG/GraphRAG/vector DB, Kubernetes, Kafka, Redis, multi-agent, Temporal, MCP migration ou framework swap continuam fora sem gap medido e challenger vencedor.

## Reprodução

Workflow atual canônico:

`.github/workflows/clean-clone-full-product-reproduction.yml`

Ele executa:

```text
PostgreSQL 18
→ install Python/E2
→ full pytest suite with PostgreSQL enabled
→ PostgreSQL identity/RLS + load + restart regressions
→ distributed runtime handoff/action lease regressions
→ ADR-004 controller regression
→ frozen EV-007 / EV-008 / EV-011
→ historical delivery/evidence validation
→ final handoff audit
→ final freeze bundle validation
→ npm ci from committed lockfile
→ frontend typecheck / tests / production build
→ tracked repository mutation = 0
```

Browser acceptance: `.github/workflows/full-product-playwright.yml`.

O always-on `.github/workflows/final-ci-required.yml` exige clean clone + Chromium + horizontal runtime handoff + action execution lease e expõe um único status: **`required-gate`**.

Para reprodução manual, veja [`docs/FINAL-HANDOFF-RUNBOOK.md`](docs/FINAL-HANDOFF-RUNBOOK.md).

## Claims bloqueados

Não reivindicar:

- provider/model de produção selecionado;
- calibração semântica humana completa sem labels/adjudicação reais;
- Engineer Minutes Saved/business value sem medições humanas;
- benefício de adaptive stopping não promovido;
- capacidade/SLO de produção a partir de load CI;
- RTO/RPO/HA/autoscaling/multi-region/uptime de deployment a partir dos testes de repositório;
- distributed exactly-once de side effects externos;
- enterprise OAuth/OIDC/SSO;
- necessidade/superioridade de LangGraph ou outro framework sem challenger medido;
- branch protection enquanto GitHub reportar `main.protected=false` / `rulesets=[]`;
- reconstrução/substituição do artifact científico C4 ausente.

## Caminho até entrega

```text
P0 distributed product + evidence closure      merged
post-merge required-gate #386                 PASS
canonical-doc rehearsal sync                  current pre-freeze work
hard feature/visual/architecture freeze       end 2026-09-05
final rehearsal/evidence inspection           2026-09-06/07
final delivery                                2026-09-08
```

Após o hard freeze, somente delivery blockers com regressão direcionada podem alterar o candidato.

## Documentação ativa

1. [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md)
2. [`research/p0-hard-freeze-closure-2026-09-05.md`](research/p0-hard-freeze-closure-2026-09-05.md)
3. [`research/results/final-freeze-evidence-bundle-2026-09-04.json`](research/results/final-freeze-evidence-bundle-2026-09-04.json)
4. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
5. [`docs/DELIVERY-PLAN.md`](docs/DELIVERY-PLAN.md)
6. [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md)
7. [`docs/FINAL-HANDOFF-RUNBOOK.md`](docs/FINAL-HANDOFF-RUNBOOK.md)
8. [`docs/BRANCH-PROTECTION.md`](docs/BRANCH-PROTECTION.md)
9. [`docs/RUBRIC-TO-EVIDENCE.md`](docs/RUBRIC-TO-EVIDENCE.md)
10. [`docs/PROJECT-PRINCIPLES.md`](docs/PROJECT-PRINCIPLES.md)

Historical ADRs e frozen experiment artifacts permanecem imutáveis e autoritativos para seus próprios checkpoints.