# E8 Statistical Pilot + Model Benchmark Prep

**Status:** PREREGISTERED / prep gate only / no model freeze  
**Date:** 2026-08-16  
**Scope:** DEV + VALIDATION only  
**LOCKED_TEST accessed:** false

## Purpose

Prepare the statistical pilot and model benchmark without leaking evaluator-only gold, without touching LOCKED_TEST, and without freezing the final architecture.

E8 is designed to answer two separate questions:

1. **Model stochasticity at fixed observations:** when the same case evidence is fixed, how much do model/provider outputs vary across repeated calls?
2. **Environment robustness under deterministic modes/seeds:** when model/proposal behavior is held constant, how stable is the agent path across runner-bound environment modes/seeds?

This separation prevents a weak model from being confused with an unstable tool/runtime environment, and prevents a stable model from hiding environment brittleness.

## Constants carried from E6/E7

These are held constant for E8 prep:

- Runtime candidate: LangGraph.
- Execution boundary: `HarnessRunner`.
- Tool contract: canonical `research.e2.tool_registry.TOOLS`.
- Boundary: B3 guarded boundary.
- Evidence/stopping: evidence-sufficiency policy.
- Evidence planning: adaptive from missing evidence requirements.
- Transport: `HttpxTransport` live API path.
- Internal tool surface: native ToolSpec calls.
- External interoperability surface: MCP-compatible adapter.
- Comparators retained: Pydantic AI/Graph and OpenAI Agents SDK.

Still not frozen:

- model/provider;
- final MCP topology;
- RAG/vector DB;
- multi-agent decomposition;
- persistent memory;
- observability backend;
- UI/demo flow;
- final architecture.

## Candidate model/provider slots

E8 prep defines candidate slots, not final model IDs. Concrete model IDs must be resolved at run time from current provider availability and local credentials.

| Slot | Role | Cost policy | Notes |
|---|---|---|---|
| `no_model_policy_baseline` | deterministic safety/proposal baseline | free | Existing safe proposal baseline; not agent-quality proof. |
| `groq_openai_compatible_free_first` | low-cost/free OpenAI-compatible candidate | free/low-cost first | Preferred first external model candidate if API key/rate limits allow. |
| `google_gemini_free_or_low_cost` | alternative low-cost candidate | free/low-cost first | Include only if credentials are available. |
| `openai_reference_optional` | high-quality reference candidate | paid only with explicit budget | Optional reference; not required for free-first execution. |
| `anthropic_reference_optional` | high-quality cross-provider reference | paid only with explicit budget | Optional reference; not required for free-first execution. |
| `local_ollama_optional` | local/no-token-cost comparator | local compute only | Include only if runtime latency is tolerable. |

No paid model is enabled by default. Paid candidates require explicit budget approval and environment configuration.

## Split policy

Allowed:

- DEV
- VALIDATION

Forbidden:

- LOCKED_TEST
- evaluator-only gold paths
- reference final answers as model input
- hardcoded expected actions/conclusions as prompts

Representative pilot groups:

- DEV: `asset_G501`, `asset_C710`, `asset_S420`
- VALIDATION: `asset_B204`, `asset_M102`

E8 prep does not inspect or use LOCKED_TEST cases.

## Pilot design

### Axis A — model stochasticity at fixed observations

1. Use the current LangGraph + HarnessRunner + ToolSpec path to obtain or replay fixed evidence observations for each allowed case.
2. Freeze the observation packet shown to the model/proposal layer.
3. Run each enabled model candidate multiple times at controlled decoding settings.
4. Score output variation independently from tool/environment variation.

Planned default repeats:

- DEV smoke: 3 repeats per candidate/case.
- VALIDATION pilot: 5 repeats per candidate/case after DEV smoke passes.

### Axis B — environment robustness under deterministic modes/seeds

1. Keep the model/proposal candidate fixed.
2. Vary only runner-bound deterministic environment modes/seeds where supported.
3. Measure whether the same policy bundle preserves evidence, action/escalation safety and trace integrity.

Planned default modes:

- `complete`
- `partial`
- `inconclusive`
- `conflict`
- `unavailable`

Only runner-bound seeds are allowed; the model may not choose identity or seed.

## Metrics

Primary:

- task success;
- action/escalation correctness;
- premature action rate;
- premature stop rate;
- unsupported final-claim rate;
- evidence coverage;
- B3 guard fidelity;
- evidence-sufficiency compliance;
- RunTrace completeness;
- LOCKED_TEST access flag.

Secondary:

- request count;
- unnecessary calls;
- 4xx/5xx rate;
- policy block count and type;
- latency average and p95;
- token/cost estimate where provider telemetry is available;
- output variance across repeats;
- disagreement patterns across providers.

## Leakage controls

The model/proposal layer may see only:

- agent-visible case inputs;
- ToolSpec/native or MCP-compatible schema information;
- live or replayed tool observations from allowed DEV/VALIDATION cases;
- non-gold system instructions.

The model/proposal layer must not see:

- `eval/expected-paths.json`;
- `eval/test-scenarios.md`;
- `docs/test-scenarios.md`;
- `data/cases.parquet`;
- LOCKED_TEST groups;
- scorer-only oracles;
- final expected answers.

## Budget policy

Default budget mode is `free_first`.

- `no_model_policy_baseline`, Groq/free-tier, Gemini/free-tier and local candidates may be prepared first.
- OpenAI/Anthropic reference runs are optional and require explicit budget approval.
- The pilot runner must be able to execute a contract/prep mode without API keys.
- No secrets are committed.

## Success criteria for E8 prep

E8 prep passes when:

- candidate slots are defined;
- budget policy is explicit;
- split policy blocks LOCKED_TEST;
- two-axis statistical design is defined;
- metrics are defined;
- leakage controls are explicit;
- constants from E6/E7 are preserved;
- a CI prep runner validates the manifest without making model calls;
- final architecture remains unfrozen.

## Non-goals

- No model/provider freeze.
- No final prompt freeze.
- No final architecture freeze.
- No LOCKED_TEST run.
- No demo-first claim.
- No paid model execution without explicit budget approval.

## Next after prep

Run the E8 pilot only after selecting which candidate slots are actually available in the local environment and after confirming budget constraints.