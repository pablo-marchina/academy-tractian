# Academy × TRACTIAN

Produção e avaliação de agentes industriais sobre a API didática da TRACTIAN.

A entrega é uma solução única com duas capacidades integradas:

- **Agente industrial:** interpreta solicitações, consulta tools tipadas da TRACTIAN, reúne evidência e decide entre orientar, esclarecer, abstain/escalar ou propor uma ação governada;
- **Framework de avaliação:** mede conclusão operacional, evidência, trajetória, segurança, falhas, estabilidade, ações e valor operacional sem expor material privado do avaliador.

## Estado atual

- runtime provider-neutral + deterministic evaluator: **implementados**;
- integração TRACTIAN: **18 operações tipadas**;
- produto multiusuário `POST /api/runs` + REST/SSE: **implementado**;
- observabilidade segura: **DuckDB read model + realtime telemetry**;
- frontend React operator control room: **implementado**;
- production actions: **custody → confirmação → idempotency → execução**, sem blind retry;
- identidade promovida: **bearer assinado HMAC-SHA256**, tenant/user/identity server-trusted; não é OAuth/OIDC/JWT;
- estado operacional mutável: **PostgreSQL** com RLS tenant-scoped; DuckDB permanece analytics/read model;
- Playwright full-product E2E + frontend lockfile: **implementados e gated**;
- human semantic-review collector + source generation: **implementados**, mas labels humanos reais/calibração ainda não podem ser fabricados;
- operational-value collector + frozen paired analysis: **implementados**, mas não há business-value claim sem medições humanas reais;
- adaptive stopping: **evaluator-only diagnostic**; nenhuma política adaptativa foi promovida ao runtime;
- load/concurrency: **campanha provider-free medida**, interpretação descritiva, sem claim de capacidade de produção;
- restart/recovery: **campanha PostgreSQL integrada verificada**, sem replay/retry automático e sem claim de RTO/RPO/availability;
- D01/D02 provider experiments: **USD 0 / `NO_SELECTION`**;
- entrega final: **2026-09-08**.

A fonte humana canônica do estado atual é [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md).

## Arquitetura promovida

```text
React Operator Control Room
        ↑ REST + genuine SSE
FastAPI Product / Observability API
        ↑ trusted signed runtime identity
PostgreSQL mutable operational state + tenant RLS
        ↑
RealtimeProductionRuntime.prepare()/execute()
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
safe projection → DuckDB analytics/read model
        ↓
REST/SSE/frontend
```

Ação consequencial:

```text
proposal
→ deterministic validation
→ private persistent custody
→ PENDING_CONFIRMATION
→ authenticated operator confirms opaque action_id
→ authorization + kill switch revalidated
→ atomic idempotency claim
→ exact custodied action executes
→ action RunTrace + evaluator
```

Falha ambígua após claim vira `UNCERTAIN`; restart nunca concede permissão para retry/replay.

## Fronteira de privacidade

O browser nunca recebe raw `RunTrace`, credenciais, identity binding, evaluator seed/private truth, raw provider material, raw action arguments/idempotency material ou chain-of-thought. Observabilidade e artifacts de CI usam projeções sanitizadas/agregadas.

## Stack

### Backend/runtime

- Python 3.11+
- Pydantic 2.x
- FastAPI / Uvicorn
- PostgreSQL + psycopg para estado operacional mutável
- DuckDB para telemetry/analytics/read model
- custom `AgentController` + `HarnessRunner`
- typed `ToolSpec` registry
- pytest

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

## EDD

Mudanças materiais seguem:

```text
requirement
→ metric/evaluator
→ baseline
→ hypothesis
→ candidate
→ repeated/sliced evaluation
→ hard gates + uncertainty
→ PROMOTE / REJECT / INCONCLUSIVE / NO_CHANGE
→ regression
```

Complexidade arquitetural não entra por convenção. RAG/GraphRAG/vector DB, Kubernetes, Kafka, Redis, multi-agent, Temporal, MCP migration ou framework swap continuam fora sem gap medido e challenger vencedor.

## Reprodução provider-free

Há duas superfícies deliberadamente distintas:

- `.github/workflows/final-delivery-provider-free-reproduction.yml` — **workflow histórico congelado**, preservado byte-for-byte porque seu blob faz parte do freeze de evidência;
- `.github/workflows/clean-clone-full-product-reproduction.yml` — **reprodução canônica do produto atual** a partir de checkout limpo.

O workflow atual executa, sem provider secrets:

```text
PostgreSQL 18
→ install Python/E2
→ full pytest suite with PostgreSQL enabled
→ explicit identity/RLS + load + restart P0 checks
→ ADR-004 controller regression
→ frozen EV-007 / EV-008 / EV-011
→ final delivery demo/evidence validation
→ final handoff audit
→ npm ci from committed lockfile
→ frontend typecheck / tests / production build
→ git diff cleanliness check
```

O full-browser acceptance permanece separado e obrigatório em `.github/workflows/full-product-playwright.yml`.

Para reprodução manual, veja [`docs/FINAL-HANDOFF-RUNBOOK.md`](docs/FINAL-HANDOFF-RUNBOOK.md).

## Claims que permanecem bloqueados

- nenhum provider de produção foi selecionado;
- nenhuma economia de minutos de engenharia é reivindicada sem dados humanos reais;
- nenhuma calibração semântica é reivindicada antes dos labels humanos/adjudicação;
- nenhum ganho de stopping adaptativo é reivindicado antes de challenger oracle-free;
- nenhum número do CI de load é capacidade de produção;
- recovery em CI não prova RTO/RPO, HA, multi-region ou uptime de deployment;
- LangGraph ou qualquer framework alternativo não é necessário/superior sem comparação medida.

## Próximos gates

1. fechar **clean-clone full reproduction** (#174);
2. branch protection + final CI P0;
3. final freeze + benchmark/evidence bundle P0;
4. coletar/calibrar evidência humana real quando os revisores estiverem disponíveis;
5. P1 somente com tempo/evidência: runtime LangGraph comparison, final provider/model benchmark, adaptive model routing, OpenTelemetry standardization e frontend consolidation.

## Documentação ativa

1. [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md)
2. [`docs/DELIVERY-PLAN.md`](docs/DELIVERY-PLAN.md)
3. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
4. [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md)
5. [`docs/FINAL-HANDOFF-RUNBOOK.md`](docs/FINAL-HANDOFF-RUNBOOK.md)
6. [`docs/RUBRIC-TO-EVIDENCE.md`](docs/RUBRIC-TO-EVIDENCE.md)
7. [`docs/PROJECT-PRINCIPLES.md`](docs/PROJECT-PRINCIPLES.md)

Frozen experiment artifacts permanecem imutáveis e autoritativos para seus próprios escopos históricos.