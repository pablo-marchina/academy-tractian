# Academy × TRACTIAN — Industrial Agent Engineering & Evaluation

Repository central do TAPI individual **Engenharia e Avaliação de Agentes Industriais** (Inteli × TRACTIAN).

## Status

**Phase 0 — Systematic Research / Research Gate**

Nenhuma arquitetura, framework, modelo, estratégia de retrieval, protocolo de agentes ou stack de avaliação é considerado definitivo nesta fase. As escolhas serão congeladas somente depois de uma revisão sistemática das alternativas relevantes, do contrato da API da TRACTIAN e de experimentos comparativos mínimos.

## Project goal

Construir uma solução integrada que cubra, em profundidade:

1. **Industrial Agent Engineering** — agente capaz de contextualizar, investigar, executar e escalar de forma confiável sobre a API industrial fornecida pela TRACTIAN.
2. **Agent Evaluation & Reliability** — framework quantitativo para medir seleção de ferramentas, argumentos, trajetória, evidências, resposta, segurança, robustez, estabilidade e ações de maior impacto.

A trilha formal a ser declarada no TAPI será confirmada com o parceiro; até lá, o projeto é desenhado para cobrir ambas de forma coesa, com avaliação sendo parte do ciclo de desenvolvimento do agente.

## Guiding principle

> “Best” means **best supported by evidence for this problem**, not newest, most popular, or most complex.

Arquitetura e técnicas serão selecionadas com base em requisitos, literatura primária, especificações/documentação oficial e resultados no benchmark do próprio projeto.

## Research Gate

A implementação principal só será congelada após termos:

- requirement matrix completa;
- mapa explícito das lacunas que dependem da TRACTIAN;
- revisão de arquitetura de agentes e tool use;
- decisão sobre MCP;
- estratégia de state/memory;
- threat model e safety policy;
- taxonomia de avaliação e failure taxonomy;
- protocolo de reliability, robustness e adversarial testing;
- estratégia de observabilidade e tracing;
- metodologia estatística e de reprodutibilidade;
- benchmark/model-selection protocol;
- decisões sobre retrieval/RAG e optimization;
- Architecture Decision Records (ADRs) com alternativas e evidências;
- zero dúvidas pesquisáveis relevantes em aberto.

## Repository structure

A estrutura de pesquisa e implementação será criada incrementalmente neste repositório. Durante a fase atual, a fonte de verdade estará em `research/` e `docs/adr/`.

## Important dates

- TRACTIAN onboarding: **2026-08-13**
- Final presentation and delivery: **2026-09-08**

## Development rule

Não adicionar complexidade sem hipótese ou critério de avaliação correspondente. Qualquer componente que não produza benefício mensurável, reduza risco ou seja requisito explícito deve poder ser removido por ablation/ADR.
