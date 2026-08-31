# Architecture Decision Records

This directory contains material decision records governed by [`../PROJECT-PRINCIPLES.md`](../PROJECT-PRINCIPLES.md) and organized against the material decision register in [`../ARCHITECTURE-ROADMAP.md`](../ARCHITECTURE-ROADMAP.md).

An ADR records the evidence and decision **for its stated scope at that time**. Later evidence may supersede a route without erasing the original record.

## Index

| ADR | Scope | Interpretation |
|---|---|---|
| [`000-template.md`](000-template.md) | template | use for future material decisions |
| [`001-provider-capacity-serving-path-2026-08-24.md`](001-provider-capacity-serving-path-2026-08-24.md) | Cerebras P12-C4 qualification path | historical/consumed route; not a production-provider selection |
| [`002-openrouter-no-card-serving-amendment-2026-08-26.md`](002-openrouter-no-card-serving-amendment-2026-08-26.md) | OpenRouter/OpenInference P12-C4 amendment | historical/consumed route after live qualification failure; not production selection |
| [`003-nvidia-nim-no-card-serving-amendment-2026-08-26.md`](003-nvidia-nim-no-card-serving-amendment-2026-08-26.md) | NVIDIA NIM P12-C4 qualification amendment | enabled the successful C4 serving path; remains qualification-only and does not freeze NVIDIA for production |
| [`004-agent-controller-runtime-2026-08-27.md`](004-agent-controller-runtime-2026-08-27.md) | P0 single-agent controller/runtime boundary | explicit provider-free controller frozen for the P0 scope; `HarnessRunner` remains the exclusive tool-execution boundary; LangGraph retained as the first qualified durable-orchestration upgrade path |
| [`005-production-action-safety-policy-2026-08-27.md`](005-production-action-safety-policy-2026-08-27.md) | P0 production consequential-action safety boundary | layered runtime-owned action authorization policy frozen; all production actions remain globally disabled and actual action enablement requires a separate governed decision |
| [`006-provider-neutral-decision-source-2026-08-27.md`](006-provider-neutral-decision-source-2026-08-27.md) | P0 production provider-integration adapter boundary | provider-neutral strict `DecisionSource` adapter frozen; provider SDK/model selection/live calls remain separately governed and unauthorized |
| [`007-model-call-trace-provenance-2026-08-27.md`](007-model-call-trace-provenance-2026-08-27.md) | P0 model-call provenance and future provider-comparison evidence boundary | sanitized self-verifying `model_call` trace contract and provider-comparison preregistration frozen; live provider/model calls and selection remain separately governed and unauthorized |
| [`008-provider-model-comparison-design-2026-08-28.md`](008-provider-model-comparison-design-2026-08-28.md) | historical P0 production provider/model comparison design | historical OpenAI/Gemini candidate design; current USD-0 execution scope superseded prospectively by ADR-018; old live packet consumed 0 calls |
| [`009-provider-http-clients-live-comparison-authorization-2026-08-28.md`](009-provider-http-clients-live-comparison-authorization-2026-08-28.md) | historical concrete OpenAI/Gemini clients | implementation evidence retained historically; old execution route must not be used as-is under current USD-0 scope |
| [`010-provider-comparison-executor-2026-08-28.md`](010-provider-comparison-executor-2026-08-28.md) | historical provider/model comparison executor | provider-neutral execution/aggregation concepts remain reusable; old candidate execution remains unauthorized |
| [`018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md`](018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md) | minimum current USD-0 Cloudflare provider/model comparison | freezes exact GLM 4.7 Flash × Nemotron 3 120B A12B preregistration, 32-attempt ceiling, M1–M10 mapping, 7,937.522688-neuron packet cap and `NO_SELECTION`; authorizes 0 implementation/inference calls |
| [`019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md`](019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md) | provider-free Cloudflare client implementation | freezes exact client/test/CI bytes implementing ADR-018 with explicit credentials, injected fakeable transport, strict response containment and zero live calls; live execution remains unauthorized |

Exact consumed/pass outcomes are recorded by the corresponding canonical result artifacts and `PROJECT-PROGRESS-LOG.md`. Current project state/authorization is owned only by `CURRENT-PROJECT-STATUS.md`.

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
