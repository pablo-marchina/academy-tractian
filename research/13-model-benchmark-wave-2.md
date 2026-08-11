# Model Benchmark & Adaptive Routing — Wave 2

Status: **BENCHMARK METHOD PROVISIONAL — no model selected**

Research questions: R11, R12, R13 and R21.

## Research conclusion

Public leaderboards can filter candidates but cannot select the production model for the TRACTIAN project. Final selection must use the actual project tool contract, scenario distribution, evidence patterns, fault profiles and decision policy.

The unit compared is a **model + provider + configuration + agent policy**, with all candidates receiving equivalent canonical tools and evaluation conditions.

## Required capabilities

The model must be evaluated on more than single-turn JSON function selection. Relevant capabilities include:

- understanding requests and missing information;
- choosing among `ASK`, `INVESTIGATE`, `ACT`, `ABSTAIN` and `ESCALATE`;
- correct tool selection and typed arguments;
- sequential/multi-step tool dependencies;
- use of partial, inconclusive and conflicting evidence;
- appropriate stopping;
- evidence-grounded response generation;
- stability across repeated runs;
- recovery after tool/API failures.

## Role of external benchmarks

The Berkeley Function-Calling Leaderboard (BFCL) is useful for candidate filtering because its current benchmark family includes function calling plus multi-turn/multi-step and agentic tasks. It is not evidence of TRACTIAN performance by itself because our tools, policies, states, risks and failure distribution are different.

Official provider documentation is used to verify hard capabilities such as tool calling, structured output, context limits, model identifiers, free-access limits and provider-specific constraints.

## Initial candidate pool — not frozen

Wave 2 keeps a heterogeneous screening pool based on currently documented accessible tool-capable models. Candidate names must be re-verified immediately before experiments because hosted catalogs change.

Potential Groq-hosted candidates include:

- `openai/gpt-oss-120b`;
- `openai/gpt-oss-20b`;
- `qwen/qwen3.6-27b`;
- one Llama-family reference if still available and useful as a latency/resource baseline.

Gemini models with current function-calling support and free-tier access should also enter the screening pool. Exact Gemini candidate(s) are intentionally not frozen yet.

A local/open-weight candidate is eligible only if available hardware can serve enough repeated trials within the project deadline. Local execution is not automatically better if throughput prevents valid evaluation.

## Fair-comparison contract

All candidates must receive:

- same canonical tool definitions and descriptions;
- same deterministic policy layer;
- same scenario/dataset version;
- same environment reset and fault profile;
- semantically equivalent system policy;
- same maximum step/retry budgets;
- same context/evidence projection;
- same evaluator;
- equivalent randomness settings where supported.

Provider-specific tool-call envelopes are adapters, not intentional behavioral differences.

## Benchmark stages

### A — Capability screening

Use a small development subset to eliminate clearly unsuitable candidates. Include read tools, semantically similar tools, typed arguments, sequential dependencies, a mutation proposal, missing information, a case requiring abstention/escalation and partial/conflicting observations.

Use few repetitions here to conserve quota; do not make final reliability claims.

### B — Development benchmark

Run surviving models across broader scenario families. Diagnose the failure taxonomy and tune only development-safe configuration/prompt variants.

### C — Validation comparison

Run paired repeated evaluation on the same validation scenarios and fault profiles. Build a Pareto set.

### D — Locked final test

Only final architecture/configuration candidates touch the locked test set. Any later model/prompt/routing change requires a new versioned experiment and explicit acknowledgement of test reuse.

## Metric vector

Do not create an arbitrary weighted score.

Hard or near-hard constraints include severe incorrect high-impact action behavior, policy-boundary failures, cross-resource failures and invalid executed actions.

Quality/reliability objectives include:

- final task/state success;
- repeated-run reliability;
- correct decision class (`ASK/INVESTIGATE/ACT/ABSTAIN/ESCALATE`);
- tool precision/recall;
- argument semantic accuracy;
- evidence coverage/grounding;
- robust success under fault profiles.

Efficiency objectives include:

- end-to-end/model latency;
- input/output tokens where available;
- model-call and tool-call count;
- trajectory length;
- provider quota/resource consumption.

Use Pareto analysis to identify dominated configurations.

## Tool-calling decomposition

Measure separately:

- function/tool selection;
- argument schema validity;
- argument semantic correctness;
- required-tool omission;
- unnecessary/forbidden tool proposal;
- tool sequence/dependency correctness;
- action proposal correctness;
- stopping correctness.

This prevents a single final success bit from hiding the reason a model succeeded or failed.

## Repeated-run design

Hosted models are stochastic and a seed does not imply full determinism. Therefore:

- choose repetition count from the statistical/compute pilot;
- pair configuration comparisons on the same scenarios/fault setup where possible;
- keep scenario as the principal generalization unit;
- report both capability and stability;
- record every generation parameter.

## Quotas are part of the experiment budget

Official Groq documentation publishes free-plan rate/token limits, and Gemini offers documented free-tier access for current model families. These constraints should be metered explicitly rather than discovered after the benchmark is designed.

The runner should track requests, tokens, retries, model-specific quota usage and wall-clock time. Use staged elimination instead of spending large repeat budgets on clearly dominated candidates.

## Adaptive routing gate

Do **not** implement routing by default.

Routing is justified only if validation results reveal complementary strengths, such as a fast model matching the strongest candidate on low-risk read scenarios while a stronger model materially improves conflict/high-impact cases.

Then compare:

1. best single global model;
2. static routing from observable risk/task features;
3. learned/calibrated routing only if development data is sufficient.

Potential routing features include request class, read/mutation class, number/similarity of tools, evidence completeness/conflict, risk class, prior tool error and trajectory length. Gold/evaluator labels unavailable at runtime are forbidden as routing features.

## Calibration gate

Self-reported model confidence is not treated as a calibrated probability. If a learned risk/failure predictor is introduced, compare it against a simple rule-based baseline and evaluate with reliability curves, Brier/log score and selective-risk behavior. Thresholds must be tuned outside the locked test set.

## Model-version drift

For every run store provider, requested model ID, returned model/version metadata when available, provider/API version, timestamp and configuration. If an alias changes during the project, pre/post-change runs may represent different configurations and must not be silently pooled.

## Decision rule

A configuration enters `FROZEN-v1` only if it:

1. supports the required tool/action semantics;
2. satisfies the project's safety constraints;
3. is non-dominated or is deliberately selected from the Pareto set;
4. has sufficient repeated evidence for the reliability claim;
5. is accessible enough to reproduce the final experiment/demo;
6. has exact provider/model/configuration recorded.

## Open dependencies

The real API is needed to finalize tool overlap, trajectory depth, action-schema complexity, context size, usefulness of parallel calls, scenario families and final compute/quota requirements.

**No model is selected in Wave 2.**
