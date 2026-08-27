# Statistical Analysis Plan — Wave 1

Status: **PROVISIONAL — final sample sizes and inferential choices depend on scenario count and compute budget**

## 1. Experimental unit

The main unit of generalization should normally be the **scenario**, not an individual stochastic run.

Reason: repeated executions of the same scenario share instructions, expected state, tools and difficulty. Treating every run as an independent scenario would artificially inflate sample size and understate uncertainty.

Data hierarchy:

`scenario → configuration → repeated run`

with metadata slices such as family, risk class, mutation/read-only and fault profile.

## 2. Primary reporting philosophy

For every important comparison report:

- point estimate;
- effect size/difference between configurations;
- 95% confidence interval;
- number of scenarios;
- repetitions per scenario;
- raw counts for safety-critical events;
- scenario-family/risk slices;
- experiment/configuration hash.

P-values, when used, are secondary to effect size + uncertainty + safety constraints.

## 3. Binary task success

### Descriptive single-proportion intervals

For a simple binomial proportion under appropriate independence, use a Wilson interval by default rather than the naive normal/Wald interval. `statsmodels.stats.proportion.proportion_confint` supports Wilson, Clopper–Pearson (`beta`), Jeffreys and other methods.

However, pooled repeated runs are **not automatically independent** because runs are clustered by scenario. Therefore Wilson intervals on all run rows should not be presented as the main uncertainty estimate when repeated trials are used.

Source: https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html

### Primary repeated-run aggregate

Candidate primary method:

1. compute each scenario’s success proportion across its `k` runs;
2. aggregate equally across scenarios so scenarios, not repeated rows, define the sampling unit;
3. bootstrap **scenario indices** to obtain an interval for mean scenario success/reliability;
4. preserve within-scenario runs when a scenario is resampled.

This is a cluster/scenario bootstrap implemented explicitly in project code so the resampling unit is unambiguous.

## 4. Paired configuration comparison

Configurations should be evaluated on the **same scenario set**.

Primary candidate effect:

`Δ = mean_scenario_success(A) - mean_scenario_success(B)`

Use a paired bootstrap over scenario IDs so each resample contains the same sampled scenarios for A and B. SciPy’s bootstrap API supports paired resampling for corresponding observations; for our nested repeated-run design we will likely implement a small explicit scenario-cluster resampler and test it against simple paired cases.

Source: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html

### McNemar as a special-case check

McNemar’s test is appropriate for paired binary outcomes represented by a 2×2 paired contingency table; statsmodels supports an exact binomial version. It is a useful check when each scenario contributes one well-defined paired binary outcome (for example, a deterministic replay comparison or an agreed scenario-level binary summary).

It should **not** be blindly applied to every repeated run as if those runs were independent paired scenarios.

Source: https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html

## 5. More than two paired configurations

Statsmodels provides Cochran’s Q as an extension for identical binomial proportions across `k` paired treatments/configurations. This may be useful for a small set of binary paired baseline comparisons when the data meet its structure.

For the full repeated-run/nested experiment, scenario-level bootstrap comparisons and an explicit multiple-comparison policy are likely easier to interpret.

Source: https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.cochrans_q.html

## 6. Reliability metrics

We need to report more than average success.

Candidate outputs per configuration:

- mean per-scenario success rate;
- distribution of scenario success rates across repeated runs;
- fraction of scenarios with 100% success across `k` runs (`pass^k`-style strict reliability, matching the benchmark concept once formula is frozen);
- fraction of scenarios with zero safety violations across `k` runs;
- worst/low-quantile scenario reliability;
- conditional reliability by fault family and mutation risk.

`k` must be stated in every report because strict all-runs reliability decreases as `k` increases.

Reference concept: τ-bench — https://arxiv.org/abs/2406.12045

## 7. Safety events and “zero observed failures”

A report of `0 / N` unsafe actions is not evidence that true risk is zero.

For critical event proportions:

- always publish numerator and denominator;
- include a one-sided or two-sided binomial confidence bound using an exact/appropriate method;
- keep safety as a hard feasibility criterion for architecture selection rather than compensating it with latency/accuracy points.

Clopper–Pearson (`beta`) is conservative and supported by statsmodels; Wilson may be used for general proportions. The exact final reporting convention will be frozen after sample size is known.

Source: https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html

## 8. Continuous/count efficiency metrics

Examples:

- latency;
- model calls;
- tool calls;
- investigation steps;
- input/output tokens where provider exposes them;
- retry count.

These distributions may be skewed. Report robust descriptive summaries (median, quantiles) alongside mean when useful.

For paired configuration differences, use scenario-level paired bootstrap intervals for the chosen statistic. Do not rely only on an unpaired mean comparison when both systems ran the same cases.

## 9. Fault robustness

For each controlled fault profile `f`:

`RobustnessDrop_f = Success_clean - Success_f`

Evaluate paired on the same base scenarios when possible. Report:

- absolute percentage-point change;
- confidence interval on paired scenario-level difference;
- safety-event change;
- recovery behavior/failure taxonomy distribution.

Fault profiles specified directly by TAPI (complete, partial, inconclusive, conflict, temporary unavailability) should receive separate results rather than one merged “robustness” number.

## 10. Act / Ask / Investigate / Abstain / Escalate

For first-class policy decisions:

- confusion matrix;
- class-specific recall/precision where meaningful;
- safety-critical confusion counts (especially incorrect `ACT`);
- paired accuracy for controlled scenario pairs such as should-act vs should-abstain;
- scenario-level bootstrap CI for aggregate paired correctness.

Accuracy alone can hide dangerous class asymmetry.

## 11. Multiple comparisons

Likely sources of multiplicity:

- many models;
- many architecture variants;
- many fault families;
- many metrics.

Research rule:

1. preregister a **small set of primary outcomes** and primary architecture comparisons;
2. mark secondary/exploratory analyses as such;
3. if formal hypothesis tests are run across many related comparisons, apply an appropriate family/FDR correction chosen before inspecting final test results;
4. do not select the winning configuration by cherry-picking one of many metrics.

The exact correction method is not frozen yet because the final comparison graph is unknown.

## 12. Development / validation / locked test

To avoid adaptive overfitting:

- `development`: prompts, code, failure debugging;
- `validation`: framework/model/threshold/optimizer selection;
- `test_locked`: final reported performance.

Variants/paraphrases of the same underlying scenario stay in one split.

The final test is not used by GEPA/DSPy, Optuna, manual prompt tuning or architecture selection.

## 13. Randomness and pairing

Record separately:

- model randomness/configuration;
- API/environment stochasticity;
- fault-injection seed;
- scenario generation seed;
- runtime/framework version.

When possible, use recorded/replayed API observations for direct agent/model comparisons so both configurations receive the same evidence. When live API randomness cannot be controlled, treat it as part of end-to-end variance and run more repeated trials rather than pretending the comparison is perfectly paired.

## 14. Missing and infrastructure-failed runs

Before final experiment, define categories:

- agent failure;
- expected tool/API fault from scenario;
- provider/rate-limit failure;
- evaluator failure;
- infrastructure crash.

Do not silently drop failed runs. Report counts and specify which categories enter task-success denominators. Sensitivity analysis may be needed when external provider failures are material.

## 15. Sample-size / compute-budget research still required

The final plan must choose:

- number of gold scenarios per family;
- repetitions `k`;
- number of configurations allowed in validation;
- final test configurations;
- acceptable CI width for primary task/reliability outcomes;
- safety-event exposure/opportunity count.

This will be solved after API scenario taxonomy and model access constraints are known.

## 16. Implementation candidates

- `numpy`, `pandas` — run-level/scenario-level data;
- `scipy.stats.bootstrap` — validated simple bootstrap building block;
- `statsmodels` — proportion intervals, paired categorical tests;
- custom small, tested scenario-cluster bootstrap — repeated-run hierarchy.

All statistical helper functions should have unit tests against known/simple cases.
