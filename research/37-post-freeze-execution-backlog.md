# Post-E0/E1 Execution Backlog — E8 Free Pilot Smoke

Status: **E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 TOPOLOGY ADR RECORDED; E8 FREE PILOT SMOKE; E8 FREE/LOCAL CANDIDATE RUN NEXT**

This file supersedes the pre-freeze task statuses in `research/06-research-backlog.md` for active execution. The older file is retained as historical planning evidence.

## Completed gates

- [x] `NORMALIZED-CONTRACT-v1` frozen.
- [x] `API-BEHAVIOR-MAP-v1` frozen.
- [x] ScenarioSchema v1 and gold/evaluator boundary frozen.
- [x] E2 integrated framework-neutral harness complete.
- [x] `BENCHMARK-SPLIT-v1` frozen before runtime/model/prompt/architecture selection.
- [x] E4 B0-B3 guarded-boundary DEV+VALIDATION comparison complete.
- [x] E5 evidence acquisition/stopping comparison complete.
- [x] E6 runtime discriminating spike complete.
- [x] E6 adaptive real ToolSpec/HarnessRunner LangGraph spike complete.
- [x] E6 local live API execution complete with `LIVE_PASS`.
- [x] E7 native tools vs MCP-compatible surface comparison complete with `E7_PASS`.
- [x] E7 topology ADR recorded.
- [x] E8 statistical pilot/model benchmark prep registered and validated.
- [x] E8 free-only pilot execution smoke passed.

## Current candidate policy/runtime/surface bundle

- B3 guarded boundary.
- Evidence-sufficiency/stopping policy.
- Adaptive evidence planning from missing evidence requirements.
- LangGraph as current runtime candidate.
- `HttpxTransport` live API path configured and executed against the supplied TRACTIAN API.
- Native ToolSpec calls as internal default candidate.
- MCP-compatible `tools/list` + `tools/call` adapter as external interoperability candidate.
- Free-only budget policy: OpenAI/Anthropic paid references disabled.
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

## E8 free pilot execution smoke

Completed work:

- [x] enforce fully free mode with project cost limit USD 0;
- [x] keep OpenAI/Anthropic paid reference candidates disabled;
- [x] detect available free/local candidate slots through environment only;
- [x] execute no-model policy baseline as the always-free candidate;
- [x] run DEV smoke before VALIDATION;
- [x] use fixed observation packet hashes;
- [x] execute repeated outputs for the stochastic-repeat harness;
- [x] measure task-success proxy, action/escalation correctness proxy, evidence coverage proxy, RunTrace completeness, latency and cost;
- [x] preserve native ToolSpec + optional MCP-compatible adapter;
- [x] keep LOCKED_TEST blocked;
- [x] avoid claiming external model-quality evidence from the no-model baseline.

Result:

| Metric | Result |
|---|---:|
| Status | `E8_FREE_PILOT_SMOKE_PASS` |
| Free-only mode | true |
| Project cost limit USD | 0 |
| Paid models enabled | false |
| External model calls in CI | false |
| Executed candidate slot | `no_model_policy_baseline` |
| DEV groups | `asset_G501`, `asset_C710`, `asset_S420` |
| VALIDATION groups | `asset_B204`, `asset_M102` |
| DEV smoke before VALIDATION | true |
| DEV repeats per group | 3 |
| VALIDATION repeats per group | 5 |
| Task success proxy | 1.0 |
| Action/escalation correctness proxy | 1.0 |
| Evidence coverage proxy | 1.0 |
| RunTrace completeness | true |
| Cost USD | 0.0 |
| LOCKED_TEST accessed | false |

Artifacts:

- `research/60-e8-statistical-pilot-model-benchmark-preregistration.md`
- `research/61-e8-free-pilot-execution-results.md`
- `research/experiments/e8-statistical-pilot-model-benchmark-manifest.json`
- `research/experiments/e8-free-pilot-execution-manifest.json`
- `research/results/e8-statistical-pilot-prep-summary-2026-08-16.json`
- `research/results/e8-free-pilot-execution-summary-2026-08-16.json`
- `scripts/research/e8_statistical_pilot_prep.py`
- `scripts/research/e8_free_pilot_runner.py`

## Next active task

Run E8 with any actually available free/local model candidate in the user's local environment, still with cost USD 0.

Required work:

- [ ] confirm whether `GROQ_API_KEY` + `E8_ENABLE_GROQ=1` is available and free;
- [ ] confirm whether `GEMINI_API_KEY` or `GOOGLE_API_KEY` + `E8_ENABLE_GEMINI=1` is available and free;
- [ ] confirm whether local Ollama has tolerable latency with `OLLAMA_HOST` + `E8_ENABLE_OLLAMA=1`;
- [ ] keep OpenAI/Anthropic disabled;
- [ ] run DEV smoke before VALIDATION;
- [ ] preserve fixed observation packets and repeated outputs;
- [ ] measure task success, action/escalation correctness, evidence coverage, trace completeness, latency and cost;
- [ ] keep LOCKED_TEST blocked;
- [ ] do not freeze final architecture yet.

## Methodological constraint

No item in E2, E3, E4, E5, E6, E7 or E8 is a demo. Test doubles, scripted paths and fixtures validate instrumentation, contracts, splits and evaluator behavior only. Architecture and agent-quality claims require controlled experiments against the supplied TRACTIAN environment and cannot use LOCKED_TEST before final evaluation.
