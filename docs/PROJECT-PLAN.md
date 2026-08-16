# Academy × TRACTIAN — Project Action Plan

**Status:** E0 + E1 FROZEN; E2 COMPLETE; E3 FROZEN; E4 VALIDATION COMPLETE; E5 EXECUTED; E6 LIVE API PASS; E7 TOPOLOGY ADR RECORDED; E8 GROQ FREE MODEL PASS; E8 OPTIONAL FREE-PROVIDER COMPARATORS REGISTERED; E9 EVALUATOR-SIDE SCORER NEXT  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 14:23 BRT  
**Target final delivery:** 2026-09-08

This is the active execution plan after the real TRACTIAN package was audited. It separates frozen evidence/contracts from experimental architecture decisions, explicitly forbids demo-first development and records that E8 is free-anywhere: any remote API, hosted service or local system is allowed if the total project cost remains USD 0.

## 1. Current state

### Frozen / complete

- `NORMALIZED-CONTRACT-v1` frozen.
- `API-BEHAVIOR-MAP-v1` frozen.
- `ScenarioSchema v1` and gold/evaluator boundary frozen.
- `BENCHMARK-SPLIT-v1` frozen before runtime/model/prompt/architecture selection.
- E2 framework-neutral ToolSpec/Trace/Replay/Evaluator harness complete.
- E4 B0-B3 guarded-boundary DEV+VALIDATION comparison complete.
- E5 evidence acquisition/stopping comparison executed.
- E6 LangGraph + ToolSpec + HarnessRunner + HttpxTransport live path passed.
- E7 topology ADR recorded: native ToolSpec calls internally, MCP-compatible adapter externally.
- E8 Groq `llama-3.1-8b-instant` passed DEV + VALIDATION as a real zero-cost remote model candidate.
- E8 optional comparators registered: OpenRouter free / `:free`, Gemini key-visible models, Hugging Face free credits, Ollama fallback.
- E9 evaluator-side task-quality scorer preregistered.

### Current candidate bundle

- Boundary: B3 guarded boundary.
- Evidence/stopping: evidence-sufficiency policy.
- Evidence planning: adaptive from missing evidence requirements.
- Runtime: LangGraph current candidate.
- Execution boundary: HarnessRunner.
- Transport: HttpxTransport live API path.
- Internal tool surface: native ToolSpec calls.
- External interoperability surface: MCP-compatible adapter.
- Leading free-provider candidate: Groq `llama-3.1-8b-instant`.
- Paid providers: OpenAI/Anthropic disabled under the USD 0 project constraint.

### Still not frozen

- final model/provider choice;
- MCP topology;
- RAG/vector DB;
- multi-agent decomposition;
- persistent memory;
- observability backend;
- UI/demo flow;
- final architecture.

## 2. E8 Groq result

| Metric | DEV | VALIDATION | Aggregate |
|---|---:|---:|---:|
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

## 3. Optional comparator policy

OpenRouter was added as the next optional free comparator through `scripts/research/e8_free_anywhere_model_runner_v3.py`. It only permits `openrouter/free` or specific models ending in `:free` and blocks non-free model ids plus `openrouter/auto` / `openrouter/auto:free`.

Gemini remains optional only after a key-visible `generateContent` model is listed. Hugging Face remains low priority because free-credit exhaustion must not become a paid run. Ollama remains fallback only.

Optional comparators do not block E9.

## 4. E9 next

Build an evaluator-side scorer that consumes fixed model outputs and hashes, then maps them to private DEV/VALIDATION oracles outside the model prompt. The scorer must separate proxy success from real task-quality evidence and measure:

- decision correctness;
- evidence-plan correctness;
- action/escalation correctness;
- unsupported final-claim rate;
- schema validity;
- trace completeness;
- latency;
- cost.

## 5. Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- Optional provider comparators are useful but must not delay E9.
- No final architecture freeze yet.
