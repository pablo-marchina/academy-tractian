# Sample Size, Repetitions & Compute Budget — Wave 2

Status: **METHOD FROZEN PROVISIONALLY; exact N/k pending API pilot**

Research questions: R12 (reliability), R13 (statistics), R19 (reproducibility), R21 (model benchmark)

## 1. Core principle

Do not choose `N scenarios` and `k repetitions` by convention. Choose them from:

- scenario-family coverage;
- desired uncertainty/precision;
- paired-comparison power/discordance;
- stochastic variability observed in a pilot;
- provider/API quotas;
- project deadline.

The **scenario**, not each repeated run, is the primary generalization unit. Repeated runs are nested observations used to estimate within-scenario stochastic reliability.

## 2. Why repeated runs do not multiply independent sample size

If one scenario is executed five times, those five outcomes share the same task structure, entities, required policy and expected state. Treating them as five unrelated benchmark tasks would understate uncertainty.

Analysis should distinguish:

- variation **between scenarios**;
- variation **within a scenario across stochastic executions**.

Accordingly, confidence intervals/comparisons should use scenario-level aggregation or cluster-aware resampling where appropriate.

## 3. Exact sample sizes remain intentionally open

We cannot validly freeze exact `N` or `k` before knowing:

- number of API endpoint/action families;
- risk/action taxonomy;
- number of controlled perturbation families;
- average model calls per trajectory;
- average tokens per model call;
- API/provider rate limits;
- reset speed;
- pilot failure/discordance rates.

Choosing a number now would create false precision.

## 4. Staged experiment budget

Use four stages so compute is spent where it changes decisions.

### Stage 0 — Harness verification

Purpose: prove evaluator/reset/trace correctness, not compare models.

- tiny hand-inspected scenario set;
- deterministic/fake model/tool tests where possible;
- one or two live smoke executions per path;
- no statistical claims.

### Stage 1 — Screening

Purpose: remove clearly unsuitable model/runtime/config candidates cheaply.

- representative development subset;
- low repeat count;
- hard capability failures trigger elimination;
- avoid expensive optimization.

### Stage 2 — Pilot / variance estimation

Purpose: estimate the quantities needed to choose final `N` and `k`.

Pilot should span the major scenario/risk families and use paired configurations on identical base scenarios/fault profiles.

Estimate:

- overall success range;
- within-scenario instability;
- scenario-to-scenario variance;
- discordant-pair rate between primary configurations;
- severe-event frequency;
- latency/token/tool-call distributions;
- infrastructure failure rate;
- average quota consumption per run.

### Stage 3 — Validation / model and architecture selection

- larger scenario coverage;
- repeated paired runs;
- enough precision to discriminate meaningful architecture/model differences;
- build Pareto set;
- freeze final configuration before test.

### Stage 4 — Locked final test

- full gold test-family coverage;
- pre-selected repeat count;
- no tuning after exposure;
- report all primary outcomes and confidence intervals.

## 5. Proportion confidence intervals

For ordinary binary success proportions, use a binomial interval with good finite-sample behavior such as **Wilson** rather than relying on the simple Wald interval.

For zero observed severe incidents, report `0/N` plus an exact/binomial upper confidence bound (e.g. Clopper–Pearson) or another pre-specified conservative interval. Never state “100% safe.”

Statsmodels provides Wilson, beta/exact and related proportion intervals; implementation should be unit tested against known cases.

## 6. Paired configuration comparisons

Because models/architectures will usually be tested on the same scenarios, use paired analysis.

For binary scenario outcomes:

- exact McNemar test when discordant counts are small;
- asymptotic McNemar only when justified;
- always report the paired effect size / success difference and confidence interval, not just a p-value.

The question is not merely “is there significance?” but “how large and decision-relevant is the improvement?”

## 7. Bootstrap strategy

SciPy's bootstrap tooling supports paired resampling and BCa intervals. For project metrics such as latency differences, tool-count differences and aggregated reliability, use **paired scenario-level/bootstrap resampling**, preserving within-scenario observations as a cluster when repeated runs exist.

Do not independently resample individual repeated runs across scenarios unless the estimand explicitly treats runs as independent, which generally will not be our primary claim.

## 8. Repetition count `k`

Choose `k` after Stage 2.

Trade-off:

- larger `k` estimates within-scenario stochastic stability better;
- larger number of unique scenarios improves coverage/generalization;
- with fixed compute, over-investing in `k` can starve scenario diversity.

A provisional experimental policy is:

1. low `k` in screening;
2. moderate `k` in pilot/validation;
3. final `k` chosen from observed instability and resource budget;
4. increase repeats selectively for high-variance/high-impact families only if that rule is pre-specified.

Do not present `pass^k` without defining exactly whether it means all `k` independent trials succeed, empirical per-scenario stability, or another aggregation.

## 9. Scenario-family coverage before raw sample count

Coverage matrix should include, when API semantics permit:

- contextualize/read-only;
- investigate multi-step;
- authorized mutation;
- high-impact mutation;
- missing information;
- partial result;
- inconclusive result;
- conflicting result;
- temporary failure;
- permission failure;
- ask vs act controlled pair;
- act vs abstain/escalate controlled pair;
- stale evidence;
- tool-output injection/adversarial family;
- retry/idempotency family.

A larger `N` concentrated in one easy family is less useful than a stratified benchmark covering the rubric-relevant behavior space.

## 10. Scenario weighting

Primary results should avoid arbitrary hidden weights.

Recommended reporting:

- macro average across predefined scenario families;
- micro/overall result across all scenarios;
- per-family result;
- high-impact safety results separately.

Run sensitivity analysis if family sizes are unequal enough that micro and macro conclusions differ.

## 11. Multiple comparisons

Avoid unrestricted model/configuration fishing.

Pre-register a small family of primary comparisons, for example:

1. baseline vs structured agent;
2. structured agent vs +deterministic gate;
3. gate vs +mutation verification;
4. final agent vs strongest baseline;
5. finalists in model benchmark.

If multiple hypothesis tests are interpreted jointly, use a pre-specified correction such as Holm for the primary family. Exploratory analyses should be labeled exploratory rather than retroactively declared confirmatory.

## 12. Effect sizes

Report practical differences with uncertainty:

### Binary

- absolute success difference;
- relative difference when meaningful;
- paired discordance counts;
- risk difference for safety events.

### Continuous/count

- paired median/mean difference for latency;
- token difference;
- model/tool-call difference;
- trajectory-length difference;
- bootstrap confidence intervals.

Heavy-tailed latency should not be summarized by mean alone; include median and upper quantiles.

## 13. Infrastructure failures

A provider timeout, test-harness defect or failed environment reset is not automatically an agent failure.

Every run outcome must distinguish:

```text
PASS
AGENT_FAIL
SYSTEM_CONTAINED_AGENT_FAIL
INFRA_FAIL
EVALUATOR_INVALID
```

Primary agent metrics need a pre-specified denominator policy. Also report infrastructure reliability independently so exclusion does not hide operational fragility.

## 14. Sequential resource allocation

To preserve free/local quota:

- eliminate hard capability failures early;
- eliminate clearly Pareto-dominated configurations at validation checkpoints;
- do not optimize prompts for candidates already dominated on safety/quality;
- cache/replay API observations for experiments that are intended to isolate model reasoning;
- reserve live API runs for end-to-end claims;
- reserve locked-test quota before exploratory optimization.

Stopping/elimination decisions must be based on development/validation data only.

## 15. Live vs replay budget

Use different experiment modes:

### Live

Measures full system including API stochasticity and network behavior.

### Replay

Uses recorded observations to compare agent/model/configuration under identical tool evidence. This is valuable for causal isolation and cheaper repeated model analysis.

### Fault injection

Uses controlled error profiles to quantify robustness.

Do not mix these modes into one success rate without labeling them.

## 16. Budget manifest

Before each large experiment produce:

```yaml
experiment_id:
scenarios:
scenario_families:
configs:
repetitions:
max_model_calls_per_run:
estimated_input_tokens_per_run:
estimated_output_tokens_per_run:
estimated_total_requests:
estimated_total_tokens:
provider_limits_snapshot:
api_limits_snapshot:
expected_wall_clock:
reserved_final_test_budget:
```

Then compare estimated vs actual consumption after execution.

## 17. Final N/k selection procedure

After the real API is available:

1. construct initial scenario-family taxonomy;
2. create a pilot set spanning those families;
3. run primary baseline/candidate with paired repetitions;
4. estimate within/between-scenario variability, discordance and cost;
5. choose minimum practically meaningful effect for primary comparison;
6. calculate/simulate candidate `N`/`k` plans under the measured cost and uncertainty;
7. select the plan that satisfies coverage + precision within budget;
8. pre-register it before locked-test execution.

This procedure, rather than a guessed fixed sample size, is the current research recommendation.

## 18. Decision state

The **method for choosing sample/repetition budget is now defined**. Exact `N`, `k` and scenario allocation remain correctly blocked on the API-derived pilot.
