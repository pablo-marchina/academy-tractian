# E10c DEV-only Private Score Results

**Status:** E10C_DEV_ONLY_NO_ESCALATION_IMPROVEMENT_E10D_NEXT  
**Date:** 2026-08-16  
**Run scored by:** `scripts/research/e9_evaluator_side_scorer_v3.py`  
**Capture source:** `scripts/research/e10c_dev_only_escalation_capture.py`  
**Tuning split:** DEV only  
**VALIDATION used for tuning:** false  
**VALIDATION ran:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## What happened

E10c successfully ran the DEV-only escalation-calibration path and produced fixed outputs that could be scored by the private evaluator-side scorer.

The E10c score consumed:

| Input | Value |
|---|---:|
| Fixed calls consumed | 6 |
| Parsed model outputs available | 6 |
| Private oracles loaded | 3 |
| Calls with matching private oracle | 6 |
| Scoreable calls | 6 |

No raw private oracle rows, fixed parsed model outputs, expected answers, trajectories or evaluator-only labels are committed.

## DEV-only comparison

| Metric | E9 DEV-only baseline | E10 DEV-only | E10b DEV-only | E10c DEV-only |
|---|---:|---:|---:|---:|
| Real task quality | 0.4762 | 0.619 | 0.8571 | 0.8571 |
| Decision correctness | 0.3333 | 0.3333 | 1.0 | 1.0 |
| Evidence correctness | 0.0 | 1.0 | 1.0 | 1.0 |
| Action correctness | 0.0 | 0.0 | 1.0 | 1.0 |
| Escalation correctness | 0.0 | 0.0 | 0.0 | 0.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy success rate | 1.0 | 1.0 | 1.0 | 1.0 |
| Proxy-vs-real disagreement rate | 1.0 | 1.0 | 1.0 | 1.0 |

## Interpretation

E10c preserved E10b's decision, evidence and action gains and did not regress safety/leakage controls.

However, E10c did not improve the remaining blocker:

- escalation correctness remains 0.0;
- real task quality remains 0.8571;
- proxy-vs-real disagreement remains 1.0.

The correct decision is not to promote E10c to full DEV+VALIDATION. It should become a negative DEV-only finding: prompt-only escalation clarification did not move the scorer signal.

## Boundary preserved

E10c kept the intended benchmark boundary:

- DEV-only tuning;
- no VALIDATION tuning;
- no LOCKED_TEST access;
- private expected paths used only by the scorer after outputs were fixed;
- raw expected values not printed or committed;
- no model/provider/final architecture freeze.

## Next gate

E10d should not be another vague prompt-only escalation instruction. The next candidate should add a visible-output consistency guard based only on the model's own `decision_class`, `action_escalation_rubric`, `action_endpoint`, `proposed_next_step`, and `risk_notes`.

E10d must not use private oracle text. It may only enforce internal consistency such as:

- if the model selects `escalation_candidate`, then `requires_human_escalation=true`;
- if the model's own rubric says `needs_human_escalation=true`, then `requires_human_escalation=true`;
- if the model names `request-specialist` or `escalate` as the concrete endpoint, then `requires_human_escalation=true`;
- if the model names visible safety/severity/permission/specialist-review/high-impact rationale, then `requires_human_escalation=true`.

E10d should be promoted only if escalation correctness improves above 0.0 while preserving evidence/action gains and keeping premature action, unsupported final claims and leakage risk at 0.0.
