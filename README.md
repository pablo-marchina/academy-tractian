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
- clean-clone current-product reproduction: **verde e gated**;
- final CI: **`required-gate` verde no merged `main` `b86b15ef…`**;
- branch protection: **CI pronta, enforcement externo ainda pendente**;
- human semantic-review collector + source generation: **implementados**, mas labels humanos reais/calibração ainda não podem ser fabricados;
- operational-value collector + frozen paired analysis: **implementados**, mas não há business-value claim sem medições humanas reais;
- adaptive stopping: **evaluator-only diagnostic**; nenhuma política adaptativa foi promovida ao runtime;
- load/concurrency: **campanha provider-free medida**, interpretação descritiva, sem claim de capacidade de produção;
- restart/recovery: **campanha PostgreSQL integrada verificada**, sem replay/retry automático e sem claim de RTO/RPO/availability;
- D01/D02 provider experiments: **USD 0 / `NO_SELECTION`**;
- final evidence state: **`READY_FOR_HARD_FREEZE` candidate**;
- hard feature/visual/architecture freeze: **programado para o fim de 2026-09-05**, ainda não tratado como efetivo;
- entrega final: **2026-09-08**.

A fonte humana canônica do estado atual é [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md). A decisão de freeze candidata está em [`research/final-freeze-decision-2026-09-04.md`](research/final-freeze-decision-2026-09-04.md), com manifesto verificável em [`research/results/final-freeze-evidence-bundle-2026-09-04.json`](research/results/final-freeze-evidence-bundle-2026-09-04.json).

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

## Reprodução e CI final

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
→ historical delivery/evidence validation
→ final handoff audit
→ final freeze bundle validation
→ npm ci from committed lockfile
→ frontend typecheck / tests / production build
→ git diff cleanliness check
```

O full-browser acceptance permanece separado em `.github/workflows/full-product-playwright.yml`. O always-on `.github/workflows/final-ci-required.yml` chama os dois contratos e expõe um único status estável: **`required-gate`**.

Para reprodução manual, veja [`docs/FINAL-HANDOFF-RUNBOOK.md`](docs/FINAL-HANDOFF-RUNBOOK.md).

## Claims que permanecem bloqueados

- nenhum provider de produção foi selecionado;
- nenhuma economia de minutos de engenharia é reivindicada sem dados humanos reais;
- nenhuma calibração semântica é reivindicada antes dos labels humanos/adjudicação;
- nenhum ganho de stopping adaptativo é reivindicado antes de challenger oracle-free;
- nenhum número do CI de load é capacidade de produção;
- recovery em CI não prova RTO/RPO, HA, multi-region ou uptime de deployment;
- branch protection não é reivindicada antes de o GitHub reportar enforcement ativo;
- LangGraph ou qualquer framework alternativo não é necessário/superior sem comparação medida;
- o artifact científico C4 ausente não é reconstruído, substituído ou reavaliado.

## Critical path

1. validar/mergear o **final freeze evidence bundle** (#114);
2. 2026-09-05: apenas integrated test/fix da candidata;
3. fim de 2026-09-05: hard feature/visual/architecture freeze;
4. aplicar e verificar branch protection no GitHub Settings quando disponível;
5. 2026-09-06/07: reprodução/rehearsal/buffer;
6. 2026-09-08: entrega.

Evidência humana real pode ser coletada quando revisores/operadores estiverem disponíveis. Sem esses dados, o estado correto continua `NOT READY`, não uma claim fabricada.

## Documentação ativa

1. [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md)
2. [`research/final-freeze-decision-2026-09-04.md`](research/final-freeze-decision-2026-09-04.md)
3. [`research/results/final-freeze-evidence-bundle-2026-09-04.json`](research/results/final-freeze-evidence-bundle-2026-09-04.json)
4. [`docs/BRANCH-PROTECTION.md`](docs/BRANCH-PROTECTION.md)
5. [`docs/DELIVERY-PLAN.md`](docs/DELIVERY-PLAN.md)
6. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
7. [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md)
8. [`docs/FINAL-HANDOFF-RUNBOOK.md`](docs/FINAL-HANDOFF-RUNBOOK.md)
9. [`docs/RUBRIC-TO-EVIDENCE.md`](docs/RUBRIC-TO-EVIDENCE.md)
10. [`docs/PROJECT-PRINCIPLES.md`](docs/PROJECT-PRINCIPLES.md)

Frozen experiment artifacts permanecem imutáveis e autoritativos para seus próprios escopos históricos.
