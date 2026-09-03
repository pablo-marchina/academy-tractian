# Operational conclusion + engineer-effort evaluation — decision record

**Decision ID:** `OV-001`  
**Date:** 2026-09-03  
**Issue:** #156  
**Status:** `IMPLEMENTED CONTRACT / NO PROJECT HUMAN-EFFORT MEASUREMENTS COLLECTED / NO VALUE CLAIM AUTHORIZED`

## 1. Decision target

TRACTIAN's kickoff target is operational rather than textual: reach the same useful conclusion a competent engineer would reach, investigate with evidence, escalate when necessary with useful context, and reduce engineer time spent resolving tickets.

The project therefore needs a first-class evaluator-side layer for:

- operational conclusion correctness;
- evidence correctness when evaluator labels exist;
- escalation correctness;
- unsafe/premature action behavior;
- usefulness of human handoff; and
- measured human effort.

This layer complements, rather than replaces, the deterministic trace evaluator and calibrated semantic-response evaluator.

## 2. Hard constraints

For this slice:

- provider/model calls: `0`;
- runtime/agent behavior changes: `0`;
- authoritative `LOCKED_TEST` scenarios accepted: `0`;
- fabricated or imputed engineer time: `0`;
- raw private truth / gold answer text / chain-of-thought in the value artifact: `0`;
- reviewer personal identity in report artifacts: `0`;
- safety failures compensated by a weighted efficiency score: `0`.

No semantic judge, business-value threshold or production promotion threshold is selected here.

## 3. Alternatives considered

### A. Aggregate task-quality score only

**Rejected.** A mean can hide weak escalation or action behavior and cannot quantify engineer effort.

### B. Compare unpaired grand means for manual vs assisted tickets

**Rejected as the primary design.** Ticket difficulty becomes a major confounder; different ticket mixes can manufacture an apparent benefit.

### C. Same engineer solves the exact same ticket manually and immediately repeats it with assistance

**Rejected as an uncontrolled design.** Learning/memory contaminates the second attempt.

### D. Case-paired measurement under a preregistered design

**Selected.** Effort measurements must be paired at case/comparison level under one explicit design:

- `INDEPENDENT_MATCHED`: independent operators/arms measure manual and assisted handling on the same or prospectively matched case; or
- `COUNTERBALANCED_CROSSOVER`: assignment/order is prospectively balanced so learning/order effects are not silently attributed to the agent.

Every measured pair carries an `effort_protocol_id`. Missing effort remains missing.

## 4. Research basis

The experiment has a comparative objective: quantify the effect of agent assistance while controlling other sources of variation. NIST's Engineering Statistics Handbook recommends choosing an experimental design from the experiment's objective and treats estimation of an a-priori factor effect as a comparative-design problem.

Source: NIST/SEMATECH e-Handbook of Statistical Methods — “How do you select an experimental design?”  
https://www.itl.nist.gov/div898/handbook/pri/section3/pri33.htm

Crossover designs can be efficient because the same participant can contribute to both conditions, but order/carryover can bias treatment comparisons. ICH E9 explicitly identifies carryover as a principal crossover-design risk. The application here is not clinical; the transferable methodological point is that repeated-task comparisons must control order/learning effects.

Source: ICH E9 Statistical Principles for Clinical Trials, section 3.1.2, hosted by FDA.  
https://www.fda.gov/media/71336/download

The implementation therefore does not interpret “paired” as permission to let someone repeat the same ticket immediately without experimental control.

## 5. Atomic observation

One record represents one evaluator-side ticket/case outcome:

```text
scenario_id
+ group_id
+ case_id
+ declared split
+ response_mode
+ operational outcome labels
+ optional measured effort pair + protocol/design
+ optional agent runtime duration
```

The record does not contain expected-answer text.

## 6. Frozen split integrity

Caller-provided `split` and `group_id` are not trusted.

Every report/bundle build requires the frozen benchmark split manifest and reconstructs:

```text
scenario_id
→ authoritative group_id
→ authoritative split
```

The build fails if:

- the manifest is not `benchmark-split-v1` and `FROZEN`;
- DEV / VALIDATION / LOCKED_TEST sections are incomplete;
- a scenario appears more than once;
- an observation's scenario is absent;
- caller group disagrees with the manifest;
- caller split disagrees with the manifest; or
- the authoritative split is `LOCKED_TEST`.

This blocks a caller from disguising a locked scenario as `DEV`.

The report stores both:

- `dataset_sha256`; and
- `split_manifest_sha256`.

Bundle record order is canonicalized, and caller metadata cannot overwrite canonical evidence metadata or hashes.

## 7. Operational metrics

The report exposes:

- `operational_conclusion_accuracy`;
- `evidence_correctness_rate` when labelled;
- `escalation_correctness_rate`;
- `escalation_precision`;
- `escalation_recall`;
- `escalation_f1`;
- `premature_action_rate`;
- `unsupported_conclusion_rate`;
- `useful_auto_resolution_rate`;
- `ready_to_continue_escalation_rate`;
- `restart_from_zero_escalation_rate`.

The conceptual primary target is operational conclusion correctness, not textual similarity to a reference answer.

## 8. Human-effort metrics

When a valid measured pair exists:

```text
engineer_minutes_saved =
    manual_baseline_seconds / 60
    - assisted_human_seconds / 60
```

The report exposes:

- paired effort sample count;
- effort coverage rate;
- protocol/design identities;
- manual baseline minutes/ticket;
- assisted human-review minutes/ticket;
- engineer minutes saved/ticket;
- engineer minutes saved total;
- tickets per engineer-hour when finite.

Negative savings are preserved as regressions rather than clipped to zero. Agent wall-clock runtime remains a separate quantity because machine elapsed time and human attention are not interchangeable.

## 9. Hard failure semantics

The EDD adapter independently records:

- `PREMATURE_ACTION`;
- `UNSUPPORTED_OPERATIONAL_CONCLUSION`;
- `MISSED_REQUIRED_ESCALATION`;
- `INCORRECT_AUTO_RESOLUTION`.

A candidate cannot offset one of these failures merely by saving human time.

No absolute production threshold is selected in this slice. Thresholds must be preregistered from DEV/pilot evidence before a held-out VALIDATION promotion decision.

## 10. Measurement protocol before any value claim

Before claiming “saves X minutes per ticket”:

1. freeze one `effort_protocol_id` for the experiment;
2. define eligibility/exclusion before timing;
3. select `INDEPENDENT_MATCHED` or `COUNTERBALANCED_CROSSOVER` prospectively;
4. assign cases/operators prospectively;
5. use identical start/stop definitions for both arms;
6. predefine interruption/invalid-trial handling;
7. preserve missing measurements as missing;
8. balance ticket class/complexity across arms;
9. report sample count and coverage beside time metrics;
10. analyze paired case-level differences, not only grand means;
11. keep correctness/safety gates active during value comparison;
12. keep reviewer identity/evaluator truth outside runtime and frontend.

For crossover measurement, the protocol must additionally define order assignment and carryover/learning handling. If that cannot be defended, use independent matched measurement.

## 11. EDD integration

`operational_value_metric_bundle()` reuses the existing `EvalMetricBundle` / comparison stack, including:

- group-aware pairing;
- response-mode slices;
- deterministic comparison identity;
- paired bootstrap confidence intervals;
- independent hard-gate rejection; and
- `PROMOTE | REJECT | INCONCLUSIVE` semantics.

A second comparison framework was intentionally not introduced.

## 12. Implemented outputs

- `src/academy_tractian/operational_value.py` — typed contract, frozen-split verification, report and EDD adapter;
- `scripts/operational_value_report.py` — provider-free CLI requiring the frozen split manifest;
- `tests/test_operational_value.py` — KPI, measurement, leakage and split-binding tests;
- `tests/test_operational_value_integrity.py` — canonical ordering, metadata integrity and manifest validation tests;
- `.github/workflows/eval-driven-development-provider-free.yml` — CI gate integration.

## 13. Validation state

On PR #157 head `f509734996edcdf96d5972b008549b256900c395`, the relevant project gates passed, including:

- eval-driven development;
- benchmark split audit;
- E9 scorer audits;
- frontend provider-free;
- observability provider-free;
- production runtime;
- final delivery provider-free reproduction; and
- final handoff acceptance audit.

The decision record describes capability, not measured business benefit.

## 14. Current non-claims

Until real measurements are collected, do not claim:

- that the current agent saves engineer time;
- a specific minutes/ticket improvement;
- a productivity multiplier;
- production-scale useful auto-resolution;
- a calibrated operational-value threshold; or
- a final production policy selected from VALIDATION.

## 15. Next evidence step

Produce a DEV pilot packet from real project cases under a frozen effort protocol, collect operational labels and measured manual/assisted durations, inspect measurement quality/missingness, then preregister candidate-vs-baseline metric rules before VALIDATION.
