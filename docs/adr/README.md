# Architecture Decision Records

This directory contains material decision records governed by [`../PROJECT-PRINCIPLES.md`](../PROJECT-PRINCIPLES.md).

An ADR records the evidence and decision **for its stated scope at that time**. Later evidence may supersede a route without erasing the original record.

## Current index

| ADR | Scope | Current interpretation |
|---|---|---|
| [`000-template.md`](000-template.md) | template | use for future material decisions |
| [`001-provider-capacity-serving-path-2026-08-24.md`](001-provider-capacity-serving-path-2026-08-24.md) | Cerebras P12-C4 qualification path | historical/consumed route; not a production-provider selection |
| [`002-openrouter-no-card-serving-amendment-2026-08-26.md`](002-openrouter-no-card-serving-amendment-2026-08-26.md) | OpenRouter/OpenInference P12-C4 amendment | historical/consumed route after live qualification failure; not production selection |
| [`003-nvidia-nim-no-card-serving-amendment-2026-08-26.md`](003-nvidia-nim-no-card-serving-amendment-2026-08-26.md) | NVIDIA NIM P12-C4 qualification amendment | enabled the successful C4 serving path; remains qualification-only and does not freeze NVIDIA for production |

Exact consumed/pass outcomes are recorded by the corresponding canonical result artifacts and `PROJECT-PROGRESS-LOG.md`.

## Rule for future ADRs

Before accepting a material architecture choice, the ADR should contain or link to:

1. decision question and scope;
2. requirements and hard constraints;
3. systematic research and primary sources;
4. credible materially different alternatives, including a simple/null baseline;
5. preregistered comparison criteria;
6. quantitative controlled results and uncertainty;
7. robustness/failure-mode evidence;
8. production-fit evidence;
9. trade-offs/Pareto interpretation;
10. rejected options;
11. decision state (`RESEARCHED`, `QUALIFIED`, `PREFERRED`, `FROZEN`, `SUPERSEDED`);
12. reversal triggers;
13. regression obligations.

Do not rewrite an old ADR to make history look consistent with later evidence. Add a new ADR that explicitly supersedes or narrows it.
