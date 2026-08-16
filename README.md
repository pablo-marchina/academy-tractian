# Academy × TRACTIAN — Industrial Agent Engineering & Evaluation

Repository central do TAPI individual **Engenharia e Avaliação de Agentes Industriais** (Inteli × TRACTIAN).

## Status

**Phase 1 — Post-Artifact Research & Experimental Architecture Selection**

O projeto já recebeu o TAPI atualizado, o kickoff e o pacote real da TRACTIAN (`inteli-tractian-project.zip`). A fase deixou de ser pesquisa genérica: agora as hipóteses são testadas contra a API, os casos e o gold fornecidos pelo parceiro.

A arquitetura de produção ainda **não está congelada**. Runtime, MCP, modelo, RAG, multi-agent, observability backend, routing e optimization só serão escolhidos se requisitos ou experimentos do próprio projeto justificarem a escolha.

Plano de execução atual: [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md)  
Hub de pesquisa e evidências: [`research/README.md`](research/README.md)  
Research Gate: [Issue #1](https://github.com/pablo-marchina/academy-tractian/issues/1)

## Project goal

O TAPI atualizado exige uma solução contendo **os dois componentes**:

1. **Industrial Agent Engineering** — agente capaz de contextualizar, investigar, executar e escalar de forma confiável sobre a API industrial fornecida pela TRACTIAN.
2. **Agent Evaluation & Reliability** — framework quantitativo para medir seleção de ferramentas, argumentos, trajetória, evidências, conclusão/resposta, segurança, robustez, estabilidade e comportamento em ações.

A arquitetura é deliberadamente integrada: o framework de avaliação mede e orienta o desenvolvimento do próprio agente.

## Evidence-first rule

> **“Best” means best supported by evidence for this problem — not newest, most popular or most complex.**

Fluxo obrigatório para decisões relevantes:

`requisito → pesquisa → alternativas → hipótese → experimento TRACTIAN → evidência → ADR → decisão`

Não adicionamos complexidade sem requisito, hipótese ou critério de avaliação correspondente.

## What the TRACTIAN package established

A auditoria da Wave 4 já substituiu várias hipóteses por fatos executáveis:

- 17 casos de entrada para o agente e 16 cenários narrativos de avaliação;
- apenas 10 grupos principais de ativo/storyline, portanto split aleatório por ticket geraria leakage;
- separação explícita entre material visível ao agente e gold exclusivo do evaluator;
- 18 operações HTTP em 17 path templates;
- trajetórias de engenheiro são referência, não scripts obrigatórios;
- ações retornam eventos `accepted=true`, mas não persistem alterações no estado fornecido;
- `x-user-id` e `seed` precisam ser vinculados pelo runner, fora do controle do modelo;
- modos de resposta podem ser controlados de forma determinística por seed;
- o OpenAPI bruto possui chave YAML duplicada para `/assets/{assetId}`, exigindo normalização antes de codegen/tools;
- handlers de ação fazem validação semântica limitada e o backend não impõe isolamento company/resource além de permissões grosseiras;
- o corpus de conhecimento tem 5 documentos e já possui endpoints de search/document retrieval;
- `expected-paths.json` é menos completo que os cenários narrativos, então exact trajectory match não pode ser o gold principal.

Detalhes e evidências estão em `research/26`–`30`.

## Central experiment

A principal hipótese pós-artefato é testar se uma **guarded contract-aware tool boundary** melhora correção e segurança sem reduzir materialmente o task success.

Variantes pré-registradas:

- **B0:** wrapper mínimo válido para benchmark;
- **B1:** B0 + validação tipada estrita;
- **B2:** B1 + guardas determinísticos de permissão/company/resource;
- **B3:** B2 + política explícita de evidência para agir/escalar;
- **B4:** confirmação explícita como extensão de safety separada, enquanto não houver requisito oficial que a torne canônica.

Depois desse núcleo, runtime, MCP e modelos serão comparados mantendo ToolSpec, cenários e evaluators constantes.

## Research Gate

`FROZEN-v1` só pode acontecer depois de:

- contrato OpenAPI normalizado e testado contra o runtime;
- ScenarioSchema v1/gold human-reviewed;
- split dev/validation/locked-test congelado sem leakage conhecido;
- experimento B0–B3 concluído;
- experimento de evidence/stopping concluído;
- ADRs de runtime e MCP apoiados por experimentos equivalentes;
- pilot estatístico usado para definir `k` e protocolo confirmatório;
- modelo selecionado com benchmark nativo do projeto;
- técnicas opcionais aceitas/rejeitadas com evidência;
- inconsistências materiais do pacote documentadas;
- dependências externas restantes explicitamente registradas.

## Repository map

```text
.
├── README.md
├── docs/
│   ├── PROJECT-PLAN.md          # plano de ação e critical path
│   └── adr/                     # architecture decision records
└── research/
    ├── README.md                # research/evidence hub
    ├── 00-25...                 # Waves 1–3 + TAPI/kickoff
    ├── 26-30...                 # Wave 4: pacote real/API/gold/experimentos
    └── schemas/                 # ScenarioSchema/TraceSchema research contracts
```

## Current critical path

`OpenAPI normalization → ScenarioSchema v1 → Canonical ToolSpec/evaluators/TraceSchema v1 → leakage-aware split → B0–B3 → evidence/stopping → runtime/MCP → pilot/model benchmark → ADRs → FROZEN-v1 → final implementation/evaluation/demo`

O calendário detalhado até 08/09 está em [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md).

## Important dates

- TRACTIAN onboarding/kickoff: **2026-08-13**
- TRACTIAN package received/audited: **2026-08-15**
- Target `FROZEN-v1`: **2026-08-27** (project target, not partner requirement)
- Final presentation and delivery: **2026-09-08**

## Development rule

Nenhum componente permanece apenas por aparência de sofisticação. Se RAG, multi-agent, routing, persistent memory, prompt optimization ou qualquer outra técnica não produzir benefício mensurável, reduzir risco ou satisfazer requisito explícito, ela deve ser rejeitada ou removível por ADR/ablation.