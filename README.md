# Academy × TRACTIAN

Engenharia e avaliação de agentes industriais sobre a API didática da TRACTIAN, combinando as duas trilhas permitidas pelo TAPI:

- **Trilha A — agente:** agente industrial com tools tipadas, política de parada, evidência, segurança e outcomes `FINAL / CLARIFY / ABSTAIN / ESCALATE`;
- **Trilha B — avaliação:** cenários, métricas, campanhas de falha/estabilidade, experimentos de provider, inspeção de traces e reprodução.

## Estado atual

- runtime/evaluator provider-free: **implementado e reproduzível**;
- integração TRACTIAN: **18 operações tipadas**;
- D01 Cloudflare: **32/32 live attempts**, **USD 0**, `NO_SELECTION`;
- D01: **24/24 `CLIENT_FAILURE` ocorreram exatamente no teto de 512 output tokens**;
- D02: mesmo experimento com **1024 completion tokens** e failure subtype sanitizado; execução live governada ainda pendente;
- arquitetura do agente: **single-agent preservada** até evidência justificar mudança;
- frontend: será construído do zero como **realtime observability control room**;
- observabilidade planejada: safe projection → durable telemetry → FastAPI/SSE → React control room;
- entrega final: **2026-09-08**.

## Comece aqui

A documentação ativa foi consolidada. Leia nesta ordem:

1. [`docs/README.md`](docs/README.md) — índice e política de documentação;
2. [`docs/CURRENT-PROJECT-STATUS.md`](docs/CURRENT-PROJECT-STATUS.md) — única fonte humana de estado/autorizações atuais;
3. [`docs/DELIVERY-PLAN.md`](docs/DELIVERY-PLAN.md) — plano unificado até a entrega;
4. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — arquitetura, stack, técnicas e frameworks;
5. [`docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md`](docs/TAPI-DELIVERY-COVERAGE-2026-09-02.md) — requisito TAPI → técnica/stack/output/evidência;
6. [`docs/DELIVERY-ACCEPTANCE.md`](docs/DELIVERY-ACCEPTANCE.md) — Definition of Done final;
7. [`docs/FINAL-HANDOFF-RUNBOOK.md`](docs/FINAL-HANDOFF-RUNBOOK.md) — setup, reprodução, demo e fallback;
8. [`docs/RUBRIC-TO-EVIDENCE.md`](docs/RUBRIC-TO-EVIDENCE.md) — navegação para evidência acadêmica;
9. [`docs/PROJECT-PRINCIPLES.md`](docs/PROJECT-PRINCIPLES.md) — governança.

ADRs e artefatos congelados continuam históricos e imutáveis; sua existência não implica autorização atual.

## Arquitetura resumida

```text
User request
  → ProductionRuntime
  → DecisionSource / provider
  → AgentController
  → HarnessRunner
  → typed ToolSpec registry
  → B1/B2/B3 safety boundaries
  → TRACTIAN API transport
  → observations
  → terminal outcome
  → RunTrace
  → evaluator
  → safe observability projection
  → telemetry store / FastAPI / SSE
  → React control room
```

O `RunTrace` bruto nunca deve ser servido ao browser. A UI recebe apenas projeções sanitizadas; evaluator-private truth, identidade/seed, credenciais, raw provider material e bodies proibidos permanecem fora da fronteira web.

## Stack principal

### Já implementado

- Python 3.11+
- Pydantic 2.x
- `AgentController` próprio
- `HarnessRunner`
- typed `ToolSpec` registry
- pytest
- hatchling/wheel
- Cloudflare Workers AI clients/experiments governados

### P0 até a entrega

- FastAPI
- DuckDB
- Server-Sent Events
- React + TypeScript + Vite
- TanStack Query
- Apache ECharts
- React Flow
- Vitest + Testing Library + Playwright

LangGraph, LangChain, MCP, RAG, persistent memory e adaptive routing **não fazem parte do caminho crítico** porque não há gap medido que justifique adicioná-los.

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

Essa sequência não requer secrets nem chamadas live de provider.

## Regras de evidência

- USD 0 para serviços externos do projeto; paid spillover proibido.
- Não inventar quota, provider state ou resultado.
- Não reexecutar attempt live `CLAIMED`/`UNCERTAIN`.
- Não modificar artefatos/ADRs congelados para alinhar narrativa posterior.
- `NO_SELECTION` é resultado válido.
- Falha de provider/frontend não autoriza expansão arquitetural automática.

Para desenvolvimento, leia também [`CONTRIBUTING.md`](CONTRIBUTING.md).