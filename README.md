# Academy × TRACTIAN

Produção e avaliação de agentes industriais sobre a API didática da TRACTIAN.

A versão atualizada do TAPI define a entrega como uma solução contendo **duas capacidades integradas**:

- **Agente industrial:** interpreta solicitações, usa tools tipadas sobre a API TRACTIAN e decide entre contextualizar, investigar, perguntar, orientar, abstain/escalar ou propor uma ação governada;
- **Framework de avaliação:** mede qualidade, confiabilidade, trajetória, uso de evidência, segurança, falhas, estabilidade, ações de maior impacto e qualidade do output.

Toda entrega também inclui integração com a API, experimento técnico e documentação dos resultados.

## Estado atual

- runtime provider-neutral + evaluator: **implementados e reproduzíveis**;
- integração TRACTIAN: **18 operações tipadas**;
- `POST /api/runs`: **request → runtime → tools/policy → RunTrace → avaliação** implementado;
- observabilidade realtime: **implementada**, com safe projection, persistência DuckDB, FastAPI REST/SSE e reconnect/catch-up;
- frontend React: **implementado**, com Live Run Cockpit, Run Explorer, Trace/Architecture Graph, Evidence/Lineage, Mission Control, Tools/Policy, Eval Lab, Provider Lab e Dynamic Data Explorer;
- Production Health: **instrumentado quantitativamente** para runtime/API/resource/SSE/adapter/provider signals;
- production actions: **PR #143**, two-phase custody/confirmation/idempotency, com gate completo verde e merge ainda pendente;
- D01 Cloudflare: **32/32 live attempts**, **USD 0**, `NO_SELECTION`;
- D01: **24/24 `CLIENT_FAILURE` no teto exato de 512 output tokens**;
- D02: protocolo equivalente com **1024 completion tokens** + failure subtype sanitizado; live execution ainda pendente;
- entrega final: **2026-09-08**.

## Comece aqui

Leia a documentação ativa nesta ordem:

1. [`docs/README.md`](docs/README.md) — índice e política de documentação;
2. [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md) — única fonte humana do estado atual;
3. [`docs/DELIVERY-PLAN.md`](docs/DELIVERY-PLAN.md) — plano rebaselined até a entrega;
4. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — arquitetura, stack, técnicas e estados de decisão;
5. [`docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md`](docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md) — TAPI → técnica/stack/output/evidência;
6. [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md) — Definition of Done;
7. [`docs/FINAL-HANDOFF-RUNBOOK.md`](docs/FINAL-HANDOFF-RUNBOOK.md) — reprodução/handoff;
8. [`docs/RUBRIC-TO-EVIDENCE.md`](docs/RUBRIC-TO-EVIDENCE.md) — navegação acadêmica;
9. [`docs/PROJECT-PRINCIPLES.md`](docs/PROJECT-PRINCIPLES.md) — governança P1–P4.

ADRs e artefatos congelados permanecem evidência histórica imutável; um freeze histórico não implica que uma escolha ainda seja a decisão final do produto se um novo requisito material surgir.

## Arquitetura atual

```text
React Operator Control Room
        ↑ REST + genuine SSE
FastAPI Product / Observability API
        ↑ safe telemetry / DuckDB
RealtimeProductionRuntime
        ↓
DecisionSource / provider
        ↓
AgentController
        ↓
HarnessRunner
        ↓
18-operation typed ToolSpec registry
        ↓
B1 / B2 / B3 deterministic boundaries
        ↓
TRACTIAN API
        ↓
normalized observations / evidence
        ↓
FINAL | CLARIFY | ABSTAIN | ESCALATE
        ↓
RunTrace
        ↓
ProductionEvaluator
        ↓
safe evaluation + analytics + frontend
```

O `RunTrace` bruto nunca cruza a fronteira web. Credenciais, identity binding, evaluation seed, raw provider material, forbidden raw tool/observation bodies e evaluator-private/gold permanecem fora do browser.

## Stack implementada

### Backend/runtime

- Python 3.11+
- Pydantic 2.x
- FastAPI
- Uvicorn
- DuckDB
- `AgentController` próprio
- `HarnessRunner`
- typed `ToolSpec` registry
- pytest
- hatchling/wheel
- Cloudflare Workers AI clients/experiments governados

### Frontend

- React 19
- TypeScript
- Vite
- TanStack Query
- Apache ECharts
- React Flow (`@xyflow/react`)
- Vitest

Playwright/full-browser E2E e o lockfile transitive freeze ainda fazem parte do gate final de produção/reprodução.

## Princípio de escolha tecnológica

O projeto não otimiza para quantidade de frameworks.

Toda escolha material deve passar por:

```text
decision question
→ TAPI / risk mapping
→ systematic research
→ credible alternatives + simple/NO_CHANGE baseline
→ preregistered metrics/hard gates
→ controlled experiment
→ uncertainty/failure/production-fit analysis
→ Pareto decision
→ ADR + regression
```

Consequências atuais:

- native typed tools permanecem preferidos a MCP sem um gap de interoperabilidade;
- RAG/vector/reranking e persistent memory permanecem fora do produto sem um gap de retrieval/state medido;
- adaptive investigation/stopping/escalation será avaliado sob #129 e só entra se vencer quantitativamente;
- o custom AgentController permanece baseline, mas será revalidado contra um runtime HITL/checkpoint como LangGraph devido ao novo two-phase action flow;
- DuckDB permanece preferido para analytics; mutable operational state será revalidado contra PostgreSQL apenas se a produção reivindicar durabilidade/concurrency além do single-process testado.

## EDD

Mudanças materiais seguem:

```text
requirement
→ metric/evaluator
→ baseline
→ hypothesis
→ candidate
→ repeated/sliced evaluation
→ PROMOTE / REJECT / INCONCLUSIVE
→ regression
```

A avaliação final é deterministic-first. Uma camada semântica só poderá virar gate após calibração contra labels humanos para dimensões como operational conclusion, groundedness, handoff usefulness e customer-safe communication.

## Provider-free reprodução atual

```bash
python -m pip install -e ".[dev]" -e "research/e2[dev]"
python -m pytest -q tests
python -m pytest -q research/e2/tests/test_controller.py
python scripts/validate_ev007_failure_campaign.py
python scripts/validate_ev008_stability_campaign.py
python scripts/validate_ev011_communication_campaign.py
python scripts/validate_delivery_reproduction.py
python scripts/validate_final_handoff_audit.py
```

Essa sequência não requer provider secrets nem live provider calls.

## Próximos gates

1. merge #143;
2. D02 somente após reset + fresh governed authorization;
3. integrate D02 result;
4. semantic-quality evaluator calibration (#128);
5. adaptive investigation/stopping/escalation experiment (#129);
6. runtime/HITL materiality revalidation (#92);
7. operational storage + deployment/restart hardening (#131);
8. Playwright + dependency lock + full integrated E2E (#114/#131);
9. clean checkout reproduction + documentation/evidence freeze;
10. delivery em 2026-09-08.

## Regras de evidência

- USD 0 para serviços externos; paid spillover proibido.
- Não inventar provider/quota/result/production readiness.
- Não reexecutar live attempt `CLAIMED`/`UNCERTAIN`.
- Não modificar frozen historical evidence para alinhar narrativa posterior.
- `NO_SELECTION`, `REJECT` e `NO_CHANGE` são resultados válidos.
- Framework complexity precisa derrotar o baseline quantitativamente antes de entrar no produto.

Para desenvolvimento, leia também [`CONTRIBUTING.md`](CONTRIBUTING.md).
