# Benchmark Integrity Gate — B0→B4

**Status:** ACTIVE / BLOCKING  
**Date:** 2026-08-21  
**Governance:** subordinate to [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Scope:** retrospective benchmark-integrity audit, contamination accounting, evaluation-protocol selection and freeze  
**Agent optimization:** paused until B4 closes

## Why this gate exists

The repository-wide principles require systematic comparison, production-first engineering, quantitative/adaptive design and eval-driven development. A retrospective review found that the historical benchmark policy evolved over time: the original E3 definition allowed `VALIDATION` to support candidate selection/tuning, while the later protocol redefined `VALIDATION` as measurement-only. Historical aggregate validation results also informed some subsequent experimental directions.

This does not erase or invalidate the historical experiments. It means their evidential role must be classified precisely before the evaluation stack can be trusted as the basis for further optimization or final claims.

This gate therefore precedes any new agent-optimization work.

## Blocking sequence

```text
B0 — Benchmark Integrity Audit
        ↓
B1 — Exposure / Contamination Ledger
        ↓
B2 — Evaluate Benchmark-Design Alternatives
        ↓
B3 — Select New Evaluation Protocol
        ↓
B4 — Freeze Evaluation Protocol
        ↓
resume agent optimization
```

To avoid confusion with the historical B0–B3 guarded-boundary variants, these stages may be referred to in artifacts as `BIG-B0` through `BIG-B4` (`Benchmark Integrity Gate`).

## Non-negotiable rules during B0–B4

- No new E14v-C or other agent-optimization candidate may be executed.
- No new model, prompt, policy, planner, guard, judge, runtime, retrieval or architecture candidate may be promoted from benchmark performance during this gate.
- No new provider inference call may be justified as agent optimization during this gate.
- Existing consumed attempts remain consumed and must not be rerun or erased.
- Historical failures, measurements and protocol changes remain immutable evidence.
- No benchmark split may be called independent merely because only aggregate rather than row-level feedback was observed.
- `VALIDATION` and `LOCKED_TEST` receive no new semantic/private inspection unless an explicitly preregistered benchmark-integrity diagnostic proves that the inspection is necessary and minimizes information exposure.
- Prefer committed historical records, manifests, workflows, sanitized aggregates and Git history over reopening private benchmark contents.
- Operational/provider diagnostics that consume no benchmark semantics and cannot influence candidate quality may be preserved as archival characterization, but they do not advance the agent-optimization line.
- No split reassignment, new holdout, cross-validation scheme or replacement benchmark is selected before B2 compares credible alternatives.

## B0 — Benchmark Integrity Audit

### Question

What benchmark information has actually been accessed, measured or exposed across the full project history, under which policy, and for what purpose?

### Required audit scope

Inventory every material experiment, diagnostic, scorer, workflow and decision record from benchmark freeze onward and record at least:

- date / experiment ID / artifact;
- policy in force at that time;
- split(s) touched;
- whether a candidate executed on the split;
- whether an evaluator/scorer loaded private oracle material;
- whether exposure was public metadata, structural private metadata, aggregate metric feedback, row-level semantic feedback or raw oracle content;
- whether results were visible before the next hypothesis/decision;
- whether the result could have influenced model/prompt/policy/runtime/evaluator/threshold/architecture development;
- whether the exposure was necessary for evaluator validity rather than candidate optimization;
- whether the information was committed, local-only or operator-observed;
- uncertainty where the historical record is incomplete.

### Required outputs

- chronological benchmark-access inventory;
- historical policy timeline;
- benchmark-exposure map;
- explicit contradictions between historical documentation and actual chronology;
- list of unresolved exposure questions requiring evidence.

### B0 exit gate

B0 passes only when every material benchmark-related experiment is accounted for or explicitly marked `UNKNOWN` with a bounded reason. Absence of evidence may not be silently treated as evidence of no exposure.

## B1 — Exposure / Contamination Ledger

### Question

Which historical exposures preserve independence, which reduce independence, and which decisions were potentially or actually influenced by benchmark feedback?

### Ledger schema

Each exposure record must include:

```text
experiment_id
observed_at
split
candidate_executed
private_oracle_loaded
exposure_scope
information_granularity
aggregate_feedback_observed
row_level_feedback_observed
raw_semantic_oracle_observed
next_decision_or_hypothesis
influence_possible
influence_documented
independence_impact
confidence
source_artifacts
notes
```

### Exposure dimensions

Do not collapse exposure into one simplistic severity score. Track at least these independent dimensions:

1. **Public metadata exposure** — split/group/scenario counts and already-public coverage descriptors.
2. **Structural private exposure** — oracle shape, row counts, alignment or schema without semantic expected values.
3. **Aggregate outcome exposure** — split-level quality/safety/latency/etc. results.
4. **Row-level outcome exposure** — case-specific evaluator labels or failure information.
5. **Semantic oracle exposure** — expected paths, answers, labels, trajectories or equivalent private target content.
6. **Candidate execution exposure** — whether a candidate was actually evaluated on the split.
7. **Adaptive influence** — whether any exposure affected a later hypothesis, candidate, threshold, prompt, guard, evaluator or architecture decision.

### Contamination rule

For a claimed independent holdout, any split-derived information that materially influences later candidate development breaks independence for that later decision, even when the feedback was aggregate-only. The magnitude and scope of contamination must still be measured rather than assumed to invalidate every possible use of the split.

### B1 exit gate

B1 passes only when:

- every B0 exposure has a ledger entry;
- every material historical decision is linked to the benchmark evidence that preceded it;
- the current `DEV`, `VALIDATION` and `LOCKED_TEST` independence status is explicitly classified with uncertainty;
- no stronger independence claim is made than the ledger supports.

## B2 — Evaluate Benchmark-Design Alternatives

### Question

Given the actual exposure history, small number of independent storyline groups, project constraints and production objective, what evaluation design provides the strongest evidence with the lowest adaptive-overfitting and leakage risk?

### Candidate set

The candidate set must be systematically researched and may expand before preregistration. At minimum evaluate materially different strategies such as:

- retain the current split roles as a baseline if defensible;
- reclassify historically exposed `VALIDATION` into the development/selection pool while preserving a final holdout;
- grouped repeated cross-validation over exposed development groups plus a final holdout;
- nested grouped cross-validation for selection/estimation where sample size permits;
- a newly created independent blind validation set;
- externally or partner-held blind evaluation;
- new independently authored/adjudicated cases;
- synthetic/adversarial benchmark expansion as supplementary robustness evidence, not automatically as a replacement for real/domain holdout data;
- hybrids of the above when they solve distinct problems.

No candidate is preferred in advance.

### Comparison criteria

Define hard constraints and measurement methods before selecting a protocol. At minimum compare:

- independence from historical adaptive development;
- leakage/adaptive-overfitting risk;
- effective number of independent groups;
- statistical efficiency / uncertainty / variance;
- scenario-family and risk coverage;
- ability to support fair paired comparisons;
- robustness to small-sample instability;
- final-test preservation;
- production/domain representativeness;
- reproducibility and auditability;
- compatibility with deterministic evaluators and validated LLM judges;
- compute/provider cost and operational feasibility;
- ability to support adaptive optimization without corrupting final measurement;
- feasibility before the final delivery target.

Where feasible, quantify protocol behavior through resampling/simulation using only permitted development information, including expected confidence-interval width, fold instability, coverage imbalance and sensitivity to individual groups.

### Research requirement

B2 must use primary methodological evidence where available and must document the search scope, alternatives rejected before experiment, assumptions and remaining credible alternatives. A protocol cannot win simply because it is conventional.

### B2 exit gate

B2 passes only when the credible candidate space is sufficiently broad, comparison criteria are frozen before outcome-dependent selection, and the evidence is sufficient to identify a Pareto frontier or explain why alternatives are non-dominated.

## B3 — Select New Evaluation Protocol

### Question

Which benchmark/evaluation protocol is best-supported for this project after B2?

### Required selection process

- Apply the preregistered hard constraints and comparison criteria.
- Do not choose by an arbitrary weighted score unless the utility function itself was justified and preregistered.
- Treat benchmark integrity and safety against leakage as hard constraints when appropriate.
- Record uncertainty, trade-offs and sensitivity to assumptions.
- Document rejected alternatives and reversal triggers.
- Explicitly define the roles of development data, selection/CV data, validation/blind data and final test data.
- Define what information may and may not flow from each split back into development.

### Decision state

The selected protocol becomes `PREFERRED`, not yet `FROZEN`.

### B3 exit gate

B3 passes only when one protocol is best-supported or the evidence explicitly shows that a hybrid/non-dominated design is required. If a credible materially different protocol remains unevaluated, B3 cannot close.

## B4 — Freeze Evaluation Protocol

### Question

Can the preferred protocol be made executable, reproducible, auditable and safe enough to govern all remaining optimization and final evaluation?

### Required freeze artifacts

B4 must version and freeze at least:

- benchmark/split or fold manifest;
- exact allowed and forbidden uses of each data partition;
- candidate-selection and optimization boundary;
- evaluator versions and validity requirements;
- semantic-judge role and judge-selection/validation requirements;
- repeated-run protocol;
- pairing/randomness/seed policy;
- primary outcomes and hard safety constraints;
- uncertainty/confidence-interval method;
- missing run / provider failure / infrastructure failure treatment;
- multiple-comparison policy where applicable;
- regression-evaluation policy;
- production robustness/fault-evaluation relationship;
- final-test authorization rule;
- breach/contamination response procedure;
- artifact/provenance requirements.

### Pre-resume verification

Before agent optimization resumes, execute provider-free structural/self-check tests proving that:

- forbidden split reads are blocked by default;
- allowed split usage matches the frozen protocol;
- no candidate path can silently read private oracle material;
- benchmark manifests are versioned and internally consistent;
- evaluator and judge gates fail closed when prerequisites are missing;
- LOCKED_TEST/final-test access requires the explicitly frozen final authorization path.

### B4 exit gate

B4 closes only when the protocol is executable and regression-protected, not merely documented.

After B4, agent optimization may resume under the new protocol. Existing candidates (including E14v) must be reinterpreted using the decision-state model and may be continued only if still justified by the newly frozen evaluation design.

## Relationship to historical work

Historical experiments remain valid evidence about what was executed under their contemporaneous rules. This gate does not retroactively relabel a past experiment as fraudulent or delete inconvenient results.

Instead it separates three questions:

1. **What did the experiment show under its original protocol?**
2. **How much independent evidence does that result provide under the current stricter governance?**
3. **What, if anything, must be re-evaluated before a component can become `PREFERRED` or `FROZEN`?**

The default retrospective rule is conservative: historical results may support `RESEARCHED` or `QUALIFIED` status, but they cannot by themselves prove final optimality when comparison completeness, benchmark independence, uncertainty or production fitness is unresolved.

## Immediate project state

Until B4 closes:

```text
benchmark integrity / protocol validity   ACTIVE BLOCKER
agent optimization                        PAUSED
E14v scientific line                      PRESERVED, NOT ADVANCED
VALIDATION candidate feedback             BLOCKED
LOCKED_TEST candidate evaluation          BLOCKED
final architecture                        UNFROZEN
production-readiness claim                NOT AUTHORIZED
```
