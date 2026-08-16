# Post-E0/E1 Execution Backlog — E8 Statistical Pilot Prep

Status: **E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 TOPOLOGY ADR RECORDED; E8 STATISTICAL PILOT PREP; E8 PILOT EXECUTION NEXT**

This file supersedes the pre-freeze task statuses in `research/06-research-backlog.md` for active execution. The older file is retained as historical planning evidence.

## Completed gates

- `NORMALIZED-CONTRACT-v1` frozen.
- `API-BEHAVIOR-MAP-v1` frozen.
- `ScenarioSchema v1` semantics frozen.
- 16 scenarios / 17 tickets / 10 leakage groups frozen as grouping constraints.
- E2 integrated framework-neutral harness complete.
- `BENCHMARK-SPLIT-v1` frozen before runtime/model/prompt/architecture selection.
- E4 B0-B3 guarded-boundary DEV+VALIDATION comparison complete.
- E5 evidence acquisition/stopping comparison complete.
- E6 runtime discriminating spike complete.
- E6 minimal LangGraph integration spike complete.
- E6 adaptive real ToolSpec/HarnessRunner LangGraph spike complete.
- E6 live API integration path and CI contract gate complete.
- E6 local live API execution complete with `LIVE_PASS`.
- E7 native tools vs MCP-compatible surface comparison complete with `E7_PASS`.
- E7 topology ADR decision prep recorded.
- E8 statistical pilot/model benchmark prep registered and validated with `E8_PREP_PASS`.

## Current candidate policy/runtime/surface bundle

- B3 guarded boundary.
- Evidence-sufficiency/stopping policy.
- LangGraph as current runtime candidate.
- `HttpxTransport` live API path configured and executed against the supplied TRACTIAN API.
- Native ToolSpec calls as internal default candidate.
- MCP-compatible `tools/list` + `tools/call` adapter as external interoperability candidate.
- MCP not required for final delivery at this gate unless a future delivery/evaluator/partner/deployment/tooling constraint requires an MCP server/client boundary.
- Free-first model benchmark policy; paid model candidates disabled by default.
- B0/free loop/fixed reference retained as baselines or infrastructure anchors.
- Pydantic AI/Graph and OpenAI Agents SDK retained as comparators.

Still not frozen:

- model/provider;
- MCP topology;
- RAG/vector DB;
- multi-agent decomposition;
- persistent memory;
- observability backend;
- UI/demo flow;
- final architecture.

## E7 topology ADR decision prep

Completed work:

- [x] keep native tools as internal default candidate;
- [x] keep MCP-compatible as external interoperability candidate;
- [x] decide MCP is not required for final delivery at this gate;
- [x] document condition under which MCP becomes required later;
- [x] preserve B3 + evidence-sufficiency + adaptive evidence planning;
- [x] preserve `HttpxTransport` live API path;
- [x] keep Pydantic AI/Graph and OpenAI Agents SDK as comparators;
- [x] keep LOCKED_TEST blocked;
- [x] avoid freezing final architecture.

Decision result:

| Decision item | Result |
|---|---|
| Internal default candidate | native ToolSpec calls |
| External interoperability candidate | MCP-compatible adapter |
| MCP required for final delivery at this gate | false |
| MCP requirement condition | require only if future delivery/evaluator/partner/deployment/tooling constraint requires MCP |
| Final architecture frozen | false |

## E8 statistical pilot/model benchmark prep

Completed work:

- [x] preregister statistical pilot/model benchmark prep;
- [x] define model/provider candidate slots without freezing concrete model IDs;
- [x] enforce free-first budget policy;
- [x] require explicit approval before paid reference model runs;
- [x] preserve native ToolSpec internal default and MCP-compatible optional adapter;
- [x] preserve B3 + evidence-sufficiency + adaptive evidence planning;
- [x] preserve LangGraph + `HttpxTransport` live API path;
- [x] separate model stochasticity from deterministic environment modes;
- [x] define DEV + VALIDATION only pilot scope;
- [x] define task-success, escalation/action correctness, trace quality, cost and latency metrics;
- [x] keep Pydantic AI/Graph and OpenAI Agents SDK as comparators;
- [x] keep LOCKED_TEST blocked;
- [x] add CI prep validator that makes no model calls;
- [x] avoid freezing final architecture.

Candidate slots:

| Slot | Purpose | Default |
|---|---|---:|
| `no_model_policy_baseline` | deterministic safety/proposal baseline | enabled |
| `groq_openai_compatible_free_first` | free/low-cost OpenAI-compatible model candidate | disabled until key/config |
| `google_gemini_free_or_low_cost` | alternative free/low-cost candidate | disabled until key/config |
| `openai_reference_optional` | high-quality paid reference candidate | disabled until explicit budget approval |
| `anthropic_reference_optional` | cross-provider paid reference candidate | disabled until explicit budget approval |
| `local_ollama_optional` | local no-token-cost comparator | disabled until latency feasible |

Prep result:

| Check | Result |
|---|---:|
| Status | `E8_PREP_PASS` |
| Candidate slots defined | 6 |
| Default budget mode | `free_first` |
| Paid models enabled by default | false |
| CI model calls | false |
| Representative groups | 5 |
| Splits | DEV + VALIDATION |
| LOCKED_TEST accessed | false |
| Design axes | model stochasticity + environment robustness |
| Primary metrics defined | true |
| Leakage controls defined | true |
| Final architecture frozen | false |

Artifacts:

- `research/60-e8-statistical-pilot-model-benchmark-preregistration.md`
- `research/experiments/e8-statistical-pilot-model-benchmark-manifest.json`
- `research/results/e8-statistical-pilot-prep-summary-2026-08-16.json`
- `scripts/research/e8_statistical_pilot_prep.py`

## Next active task

Execute E8 DEV smoke and then the statistical pilot only after local candidate availability/budget is confirmed.

Required work:

- [ ] decide which free/low-cost candidates are actually available in the local environment;
- [ ] keep paid OpenAI/Anthropic reference candidates disabled unless explicit budget approval is given;
- [ ] run DEV smoke before VALIDATION;
- [ ] capture or replay fixed observation packets separately from model stochasticity;
- [ ] run repeated model calls only for enabled candidates;
- [ ] run deterministic environment robustness checks separately;
- [ ] score task success, action/escalation correctness, evidence coverage, trace completeness, latency and cost;
- [ ] keep native ToolSpec internal default and MCP-compatible optional adapter;
- [ ] preserve B3 + evidence-sufficiency + adaptive evidence planning;
- [ ] preserve LangGraph + `HttpxTransport` live API path;
- [ ] keep LOCKED_TEST blocked;
- [ ] do not freeze final architecture yet.

## Methodological constraint

No item in E2, E3, E4, E5, E6, E7 or E8 prep is a demo. Test doubles, scripted paths and fixtures validate instrumentation, contracts, splits and evaluator behavior only. Architecture and agent-quality claims require controlled experiments against the supplied TRACTIAN environment and cannot use LOCKED_TEST before final evaluation.