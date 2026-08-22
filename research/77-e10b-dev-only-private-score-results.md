# E10b DEV-only Private Score Results

**Status:** E10B_DEV_ONLY_PRIVATE_SCORE_STRONG_IMPROVEMENT_ESCALATION_GAP  
**Date:** 2026-08-16  
**Run scored by:** `scripts/research/e9_evaluator_side_scorer_v3.py`  
**Capture source:** `scripts/research/e10b_dev_only_action_escalation_capture.py`  
**Tuning split:** DEV only  
**VALIDATION used for tuning:** false  
**VALIDATION ran:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## What happened

E10b successfully ran the DEV-only action/escalation calibration path and produced fixed outputs that could be scored by the private evaluator-side scorer.

The E10b score consumed:

| Input | Value |
|---|---:|
| Capture total calls | 6 |
| Fixed calls consumed | 6 |
| Parsed model outputs available | 6 |
| Private oracles loaded | 3 |
| Calls with matching private oracle | 6 |
| Scoreable calls | 6 |

No raw private oracle rows, fixed parsed model outputs, expected answers, trajectories or evaluator-only labels are committed.

## DEV-only comparison

| Metric | E9 DEV baseline | E10 DEV | E10b DEV | Delta E10b vs E10 |
|---|---:|---:|---:|---:|
| Real task quality | 0.4762 | 0.619 | 0.8571 | +0.2381 |
| Decision correctness | 0.3333 | 0.3333 | 1.0 | +0.6667 |
| Evidence correctness | 0.0 | 1.0 | 1.0 | 0.0 |
| Action correctness | 0.0 | 0.0 | 1.0 | +1.0 |
| Escalation correctness | 0.0 | 0.0 | 0.0 | 0.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy success rate | 1.0 | 1.0 | 1.0 | 0.0 |
| Proxy-vs-real disagreement rate | 1.0 | 1.0 | 1.0 | 0.0 |

## Interpretation

E10b produced a strong DEV-only improvement:

- real task quality improved from 0.619 to 0.8571 versus E10;
- decision correctness improved from 0.3333 to 1.0;
- evidence correctness stayed at 1.0;
- action correctness improved from 0.0 to 1.0;
- premature action stayed at 0.0;
- unsupported final claims stayed at 0.0;
- LOCKED_TEST stayed inaccessible.

However, the preregistered acceptance target required escalation correctness to improve above 0.0. E10b did not satisfy that part of the target.

Therefore, E10b should not be promoted to full DEV+VALIDATION yet. The next iteration should be a narrower DEV-only E10c focused specifically on escalation calibration.

## Boundary preserved

E10b kept the intended benchmark boundary:

- DEV-only tuning;
- no VALIDATION tuning;
- no LOCKED_TEST access;
- private expected paths used only by the scorer after outputs were fixed;
- raw expected values not printed or committed;
- no model/provider/final architecture freeze.

## Acceptance target result

| Target | E10b result | Pass? |
|---|---:|---:|
| Evidence correctness above E9 DEV baseline | 1.0 > 0.0 | yes |
| Action correctness above 0.0 | 1.0 | yes |
| Escalation correctness above 0.0 | 0.0 | no |
| Premature action rate equals 0.0 | 0.0 | yes |
| Unsupported final-claim rate equals 0.0 | 0.0 | yes |
| LOCKED_TEST inaccessible | false accessed | yes |
| No private oracles/fixed parsed outputs committed | preserved | yes |

## Next gate

E10c should preserve the E10b gains but add escalation-specific calibration on DEV only. It should not be promoted unless escalation correctness improves above 0.0 while maintaining decision, evidence and action gains and without increasing premature action, unsupported final claims or leakage risk.
