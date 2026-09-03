# Operational conclusion + engineer-effort evaluation — decision record

**Decision ID:** `OV-001`  
**Date:** 2026-09-03  
**Issue:** #156  
**Status:** `IMPLEMENTED CONTRACT / NO PROJECT HUMAN-EFFORT MEASUREMENTS COLLECTED / NO VALUE CLAIM AUTHORIZED`

## 1. Problem

The project already measures structural/safety properties, task-quality signals and semantic-response dimensions, but TRACTIAN's kickoff target is more operational:

1. reach the same operational conclusion a competent engineer would reach;
2. escalate when evidence is insufficient or contradictory;
3. make escalation useful by carrying forward the investigation context; and
4. reduce engineer time spent investigating/responding to tickets.

A single aggregate task-quality score cannot establish those properties. Historical project evidence has already shown why: an apparently strong aggregate score can coexist with materially weaker escalation behavior.

This decision therefore creates a separate evaluator-side contract for **operational correctness + measured human effort** and connects it to the existing group-aware Eval-Driven Development comparison layer.

## 2. Constraints

Hard constraints for this slice:

- provider/model calls: `0`;
- runtime/agent behavior changes: `0`;
- `LOCKED_TEST` accepted by the development measurement contract: `0`;
- fabricated or imputed engineer time: `0`;
- raw private truth / gold answer text / chain-of-thought in this contract: `0`;
- personal reviewer identity in report artifacts: `0`;
- safety failures compensated by a weighted business-value score: `0`.

Human semantic calibration remains a separate layer. This slice does not select a semantic judge or acceptance threshold.

## 3. Alternatives considered

### A — Keep aggregate task quality only

**Rejected.** It cannot directly answer whether the operational conclusion is correct, whether escalation is appropriate, or whether engineer effort falls. It can also hide critical failure classes behind a mean.

### B — Compare unpaired average manual time with average assisted time

**Rejected as the primary design.** Ticket difficulty is a major confounder. Different ticket mixes can create an apparent time improvement even when assistance has no causal operational value.

### C — Have the same engineer solve the exact same ticket manually and then with assistance

**Rejected as an uncontrolled design.** The second attempt is contaminated by learning/memory from the first attempt. A crossover can be useful only when order/case assignment is explicitly balanced and carryover is treated as a design risk.

### D — Case-paired measurement under an explicit preregistered design

**Selected.** Each effort observation must contain a manual and assisted measurement for the same/matched case under one of two explicit designs:

- `INDEPENDENT_MATCHED`: independent operators/arms measure manual and assisted handling on the same or prospectively matched case; or
- `COUNTERBALANCED_CROSSOVER`: assignments/order are prospectively balanced so order/learning effects are not silently attributed to the agent.

Every paired effort record must also carry an `effort_protocol_id`. Missing effort remains missing; the reporting layer never imputes it.

## 4. Research basis for the design choice

This is a comparative experiment: the a-priori factor of interest is assistance by the agent. NIST's Engineering Statistics Handbook recommends selecting experimental design from the experimental objective and treats this as a comparative-design problem when the goal is to estimate the effect of an important factor in the presence of other factors.

Source: NIST/SEMATECH e-Handbook of Statistical Methods, “How do you select an experimental design?”  
https://www.itl.nist.gov/div898/handbook/pri/section3/pri33.htm

Crossover designs can improve efficiency because each subject can act as their own control, but they introduce carryover/order risks. ICH E9 explicitly notes carryover as a principal problem that can bias direct treatment comparisons when unequal across sequences. The application here is not clinical; the methodological implication is the relevant one: a repeated-task crossover must control order/learning rather than treating the second attempt as an independent observation.

Source: ICH E9 Statistical Principles for Clinical Trials, section 3.1.2 (hosted by FDA).  
https://www.fda.gov/media/71336/download

The project therefore does **not** assume that “paired” means “same person repeats the same ticket immediately.” Pairing is at the case/comparison level under a declared design.

## 5. Measurement unit

The atomic unit is one evaluator-side ticket/case observation:

```text
scenario_id
+ group_id
+ case_id
+ split
+ response_mode
+ operational outcome labels
+ optional measured effort pair under protocol
+ optional agent runtime duration
```

No expected-answer text is serialized in the operational-value artifact.

## 6. Operational metrics

Per-ticket outcomes feed the following aggregate metrics:

- `operational_conclusion_accuracy`;
- `evidence_correctness_rate` when evidence labels exist;
- `escalation_correctness_rate`;
- `escalation_precision`;
- `escalation_recall`;
- `escalation_f1`;
- `premature_action_rate`;
- `unsupported_conclusion_rate`;
- `useful_auto_resolution_rate`;
- `ready_to_continue_escalation_rate`;
- `restart_from_zero_escalation_rate`.

The primary conceptual target is operational conclusion correctness, not textual similarity to a reference response.

## 7. Human-effort metrics

When a valid paired effort measurement exists:

```text
engineer_minutes_saved =
    manual_baseline_seconds / 60
    - assisted_human_seconds / 60
```

The report exposes:

- paired effort sample count;
- effort coverage rate;
- manual baseline minutes/ticket;
- assisted human-review minutes/ticket;
- engineer minutes saved/ticket;
- engineer minutes saved total;
- tickets per engineer-hour when assisted human time is non-zero.

A negative value is preserved as a real regression. It is never clipped to zero.

Agent wall-clock runtime is reported separately because machine time and human attention are not interchangeable.

## 8. Hard failure semantics

The EDD adapter marks these per-case hard failures independently from efficiency metrics:

- `PREMATURE_ACTION`;
- `UNSUPPORTED_OPERATIONAL_CONCLUSION`;
- `MISSED_REQUIRED_ESCALATION`;
- `INCORRECT_AUTO_RESOLUTION`.

A configuration with a hard operational failure cannot earn promotion merely by saving engineer minutes.

Absolute production thresholds are intentionally **not** selected in this implementation slice. Choosing thresholds after inspecting results would be post-hoc fitting. Thresholds must be preregistered from DEV/pilot evidence before the held-out VALIDATION decision.

## 9. Split policy

The typed development contract accepts only:

- `DEV`;
- `VALIDATION`.

`LOCKED_TEST` is absent from the type and rejected during validation. It remains unavailable for protocol tuning, threshold selection, model/runtime selection or optimizer feedback.

Recommended sequence:

```text
DEV pilot
→ inspect measurement quality / difficulty balance / missingness
→ freeze effort protocol + metric rules + acceptance thresholds
→ VALIDATION comparison
→ PROMOTE | REJECT | INCONCLUSIVE
```

## 10. Data-collection protocol before any value claim

Before recording a project claim such as “saves X minutes per ticket”:

1. freeze an `effort_protocol_id`;
2. define eligibility/exclusion rules before timing starts;
3. define whether the design is `INDEPENDENT_MATCHED` or `COUNTERBALANCED_CROSSOVER`;
4. assign cases/operators prospectively rather than selecting successful examples afterward;
5. use the same start/stop definition for manual and assisted arms;
6. record interruptions and invalid trials under a predefined rule;
7. preserve missing measurements as missing;
8. balance ticket classes/complexity across arms;
9. report sample count and coverage next to every time metric;
10. analyze paired case-level differences rather than comparing only two grand means;
11. keep operational correctness/safety gates active during the value comparison;
12. do not expose reviewer identity or evaluator-only truth to runtime/frontend.

For a counterbalanced crossover, the protocol must additionally define assignment order and how learning/carryover is assessed. If this cannot be done credibly, use the independent matched design instead.

## 11. EDD integration

`operational_value_metric_bundle()` maps the observations to the project's existing `EvalMetricBundle` so candidate-vs-baseline comparisons reuse:

- group-aware pairing;
- response-mode slices;
- deterministic comparison identity;
- paired bootstrap confidence intervals;
- hard-gate rejection;
- `PROMOTE | REJECT | INCONCLUSIVE` semantics.

This slice deliberately does not create a second comparison framework.

## 12. Outputs implemented

- `src/academy_tractian/operational_value.py` — typed contract, aggregate report and EDD adapter;
- `scripts/operational_value_report.py` — provider-free report/bundle CLI;
- `tests/test_operational_value.py` — contract, leakage, edge-case and KPI tests;
- `.github/workflows/eval-driven-development-provider-free.yml` — CI gate integration.

## 13. Current non-claims

Until real measurements are collected, do **not** claim:

- that the current agent saves engineer time;
- a specific minutes/ticket improvement;
- a productivity multiplier;
- that auto-resolution is operationally useful at production scale;
- that any operational-value threshold has been calibrated;
- that VALIDATION evidence authorizes a final production policy.

The implemented state is a measurement/evaluation capability, not a fabricated positive result.

## 14. Next evidence step

The next value slice is to produce a DEV pilot packet from real project cases under a frozen `effort_protocol_id`, collect operational labels and measured manual/assisted durations, then use the resulting distribution to preregister the candidate-vs-baseline metric rules before VALIDATION.
