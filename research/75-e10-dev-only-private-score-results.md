# E10 DEV-only Private Score Results

**Status:** E10_DEV_ONLY_PRIVATE_SCORE_PARTIAL_IMPROVEMENT_ACTION_ESCALATION_GAP  
**Date:** 2026-08-16  
**Run scored by:** `scripts/research/e9_evaluator_side_scorer_v3.py`  
**Capture source:** `scripts/research/e10_dev_only_groq_quality_capture_v2.py`  
**Tuning split:** DEV only  
**VALIDATION used for tuning:** false  
**VALIDATION ran:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## What happened

E10 successfully ran the DEV-only improvement path and produced fixed outputs that could be scored by the private evaluator-side scorer.

The E10 score consumed:

| Input | Value |
|---|---:|
| Fixed calls consumed | 6 |
| Parsed model outputs available | 6 |
| Private oracles loaded | 3 |
| Calls with matching private oracle | 6 |
| Scoreable calls | 6 |

No raw private oracle rows, fixed parsed model outputs, expected answers, trajectories or evaluator-only labels are committed.

## DEV-only comparison

The comparable E9 DEV-only baseline is computed from the DEV rows in the prior E9 private scoring run, not from the full DEV+VALIDATION aggregate.

| Metric | E9 DEV-only baseline | E10 DEV-only | Delta |
|---|---:|---:|---:|
| Real task quality | 0.4762 | 0.619 | +0.1428 |
| Decision correctness | 0.3333 | 0.3333 | 0.0 |
| Evidence correctness | 0.0 | 1.0 | +1.0 |
| Action correctness | 0.0 | 0.0 | 0.0 |
| Escalation correctness | 0.0 | 0.0 | 0.0 |
| Premature action rate | 0.0 | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 |
| Proxy success rate | 1.0 | 1.0 | 0.0 |
| Proxy-vs-real disagreement rate | 1.0 | 1.0 | 0.0 |

## Interpretation

E10 improved the intended first bottleneck: evidence grounding. Evidence correctness moved from 0.0 to 1.0 on the DEV-only scorer view.

However, the candidate is not ready for full DEV+VALIDATION measurement because action and escalation calibration are still not improving:

- action correctness remains 0.0;
- escalation correctness remains 0.0;
- decision correctness remains 0.3333;
- proxy-vs-real disagreement remains 1.0.

The correct decision is therefore not to promote this E10 candidate to full validation yet. It should become an intermediate DEV-only finding and feed a narrower E10b iteration focused on action/escalation calibration.

## Boundary preserved

E10 kept the intended benchmark boundary:

- DEV-only tuning;
- no VALIDATION tuning;
- no LOCKED_TEST access;
- private expected paths used only by the scorer after outputs were fixed;
- raw expected values not printed or committed;
- no model/provider/final architecture freeze.

## Next gate

E10b should keep the evidence-first improvement but add an explicit action/escalation decision rubric on DEV only. The next candidate should not be promoted unless DEV-only action/escalation correctness improves without increasing premature action, unsupported final claims or leakage risk.

## E10b minimum acceptance target before full remeasurement

E10b should not be promoted to full DEV+VALIDATION unless a DEV-only private scorer run shows all of the following:

- evidence correctness remains materially above the E9 DEV baseline;
- action correctness improves above 0.0;
- escalation correctness improves above 0.0;
- premature action rate remains 0.0;
- unsupported final-claim rate remains 0.0;
- LOCKED_TEST remains inaccessible;
- no raw private oracles or fixed parsed outputs are committed.
