# Post-E0/E1 Execution Backlog — E8 Groq Pass, Optional Comparators, E9 Next

Status: **E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 TOPOLOGY ADR RECORDED; E8 GROQ FREE MODEL PASS; E8 OPTIONAL FREE-PROVIDER COMPARATORS REGISTERED; E9 EVALUATOR-SIDE SCORER NEXT**

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
- [x] E8 candidate scope corrected from local-only to free-anywhere.
- [x] E8 real free candidate run manifest and runner added.
- [x] E8 v2 scorer/retry runner added.
- [x] Groq `llama-3.1-8b-instant` passed DEV + VALIDATION as the first real zero-cost remote model candidate.
- [x] Optional free-provider comparator policy registered.
- [x] OpenRouter free comparator support added via v3 runner.
- [x] E9 evaluator-side task-quality scorer preregistered.

## Current candidate policy/runtime/surface bundle

- B3 guarded boundary.
- Evidence-sufficiency/stopping policy.
- Adaptive evidence planning from missing evidence requirements.
- LangGraph as current runtime candidate.
- `HttpxTransport` live API path configured and executed against the supplied TRACTIAN API.
- Native ToolSpec calls as internal default candidate.
- MCP-compatible `tools/list` + `tools/call` adapter as external interoperability candidate.
- Free-only budget policy: OpenAI/Anthropic paid references disabled.
- Leading free-provider candidate: Groq `llama-3.1-8b-instant`.
- Optional free-provider comparators: OpenRouter free / `:free`, Gemini key-visible models, Hugging Face free credits, Ollama fallback.
- Pydantic AI/Graph and OpenAI Agents SDK retained as comparators.

Still not frozen:

- final model/provider choice;
- MCP topology;
- RAG/vector DB;
- multi-agent decomposition;
- persistent memory;
- observability backend;
- UI/demo flow;
- final architecture.

## E8 Groq real free model pass

Result:

| Metric | DEV | VALIDATION | Aggregate |
|---|---:|---:|---:|
| Status | pass | pass | `E8_FREE_ANYWHERE_MODEL_RUN_PASS` |
| Provider | Groq | Groq | Groq |
| Model | `llama-3.1-8b-instant` | `llama-3.1-8b-instant` | `llama-3.1-8b-instant` |
| Total calls | 6 | 6 | 12 |
| Successful calls | 6 | 6 | 12 |
| Task-success proxy | 1.0 | 1.0 | 1.0 |
| Schema-valid rate | 1.0 | 1.0 | 1.0 |
| No LOCKED_TEST claim rate | 1.0 | 1.0 | 1.0 |
| Trace completeness | true | true | true |
| Avg latency ms | 8974.732 | 9766.9 | 9370.816 |
| P95 latency ms | 30724.136 | 50841.424 | 50841.424 |
| Cost USD | 0.0 | 0.0 | 0.0 |

Artifacts:

- `research/65-e8-groq-free-anywhere-model-run-results.md`
- `research/results/e8-groq-free-anywhere-model-run-summary-2026-08-16.json`
- `scripts/research/e8_free_anywhere_model_runner_v2.py`

## E8 optional free-provider comparators

Completed work:

- [x] keep Groq as leading candidate;
- [x] add OpenRouter as optional free comparator;
- [x] require `openrouter/free` or a specific `:free` model for OpenRouter;
- [x] block `openrouter/auto` and `openrouter/auto:free` for E8 zero-cost benchmarking;
- [x] keep Gemini as optional only after `models.list` returns a key-visible `generateContent` model;
- [x] keep Hugging Face low priority due free-credit/billing risk;
- [x] keep Ollama as fallback only, not a locality requirement;
- [x] ensure optional comparators do not block E9.

Artifacts:

- `research/66-e8-optional-free-provider-comparators.md`
- `research/experiments/e8-optional-free-provider-comparators-manifest.json`
- `scripts/research/e8_free_anywhere_model_runner_v3.py`

## E9 active next task

Build evaluator-side scorer that maps fixed model outputs to private DEV/VALIDATION oracles without leaking gold into model prompts.

Required work:

- [ ] consume fixed model outputs and output hashes;
- [ ] read private DEV/VALIDATION oracles only on scorer side;
- [ ] keep model prompts gold-free;
- [ ] measure decision-class correctness;
- [ ] measure evidence-plan correctness;
- [ ] measure action/escalation correctness;
- [ ] measure unsupported final-claim rate;
- [ ] compare proxy success vs real task-quality score;
- [ ] keep LOCKED_TEST blocked;
- [ ] keep OpenAI/Anthropic disabled;
- [ ] do not freeze final architecture yet.

Artifact:

- `research/67-e9-evaluator-side-task-quality-scorer-preregistration.md`

## Methodological constraint

No item in E2, E3, E4, E5, E6, E7 or E8 is a demo. Test doubles, scripted paths and fixtures validate instrumentation, contracts, splits and evaluator behavior only. Architecture and agent-quality claims require controlled experiments against the supplied TRACTIAN environment and cannot use LOCKED_TEST before final evaluation.
