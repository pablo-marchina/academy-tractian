# Academy × TRACTIAN — Project Action Plan

**Status:** E13 blocker audit completed; DEV blockers identified  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 22:45 BRT  
**Target final delivery:** 2026-09-08

## Current gate

E11 passed DEV-only private scoring after the E10h blocker analysis introduced independent action authorization. The full DEV+VALIDATION E11 remeasurement was then run and scored with E9 v3 after outputs were fixed.

Decision: do not promote E11 to integration gates. E11 full matches E10d/E10e/E10g full: it improves over the E9 full baseline in average task quality, evidence and action, but the full premature-action safety regression persists at `premature_action_rate = 0.25`. The required full safety gate is `premature_action_rate = 0.0`.

E12 passed as a hard-gate root-cause audit. It confirmed that the E11 independent action-authorization policy did run on full DEV+VALIDATION, checked all 12 outputs, covered both DEV and VALIDATION, and changed 0 outputs. Root-cause class: `policy_executed_but_over_permissive_or_wrong_authorization_class`.

E13 implemented only the preregistered root-cause-specific change as a DEV-only candidate. It targets autonomous `POST /analyses/{analysis_id}/reprocess` authorization and does not authorize reprocess from generic evidence-family counts or generic human-review markers.

E13 DEV-only was scored with E9 v3 after outputs were fixed. The scorer passed, but E13 failed DEV-only acceptance: 6 fixed calls were consumed, 5 parsed outputs were available, and only 5 calls were scoreable. Safety remained clean on scoreable calls, but action collapsed and average quality fell below the preregistered floor.

E13 blocker audit has now completed. It identified four DEV blocker classes: `parsed_output_missing_in_dev_capture`, `boundary_changed_all_target_reprocess_actions`, `action_collapse_consistent_with_overblocking_reprocess_boundary`, and `decision_regression_after_reprocess_downgrade`.

Project rule: no integration, no demo and no downstream phase while the current gate or any dependency used by it remains incomplete.

## Full score history

| Metric | E9 full | E10d full | E10e full | E10g full | E11 full |
|---|---:|---:|---:|---:|---:|
| Scoreable calls | 12 | 12 | 12 | 12 | 12 |
| Real task quality | 0.631 | 0.8214 | 0.8214 | 0.8214 | 0.8214 |
| Decision correctness | 0.6667 | 0.75 | 0.75 | 0.75 | 0.75 |
| Evidence correctness | 0.0 | 0.75 | 0.75 | 0.75 | 0.75 |
| Action correctness | 0.25 | 0.75 | 0.75 | 0.75 | 0.75 |
| Escalation correctness | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |
| Premature action rate | 0.0 | 0.25 | 0.25 | 0.25 | 0.25 |
| Unsupported final-claim rate | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Proxy success rate | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Proxy-vs-real disagreement rate | 1.0 | 0.5 | 0.5 | 0.5 | 0.5 |

## E13 DEV-only score

| Metric | E11 DEV-only | E13 DEV-only |
|---|---:|---:|
| Scoreable calls | 6 | 5 |
| Parsed outputs | 6 | 5 |
| Real task quality | 1.0 | 0.7714 |
| Decision correctness | 1.0 | 0.4 |
| Evidence correctness | 1.0 | 1.0 |
| Action correctness | 1.0 | 0.0 |
| Escalation correctness | 1.0 | 1.0 |
| Premature action rate | 0.0 | 0.0 |
| Unsupported final-claim rate | 0.0 | 0.0 |
| Proxy success rate | 1.0 | 1.0 |
| Proxy-vs-real disagreement rate | 0.0 | 1.0 |

## E13 blocker audit result

| Finding | Result |
|---|---:|
| DEV calls observed | 6 |
| Expected DEV calls | 6 |
| Parsed DEV outputs available | 5 |
| Missing parsed output count | 1 |
| Boundary rows available | 5 |
| Target reprocess rows | 5 |
| Authorized rows | 0 |
| Blocked rows | 5 |
| Changed rows | 5 |
| Unchanged rows | 0 |
| Validation calls read | 0 |
| LOCKED_TEST accessed | false |

Missing parsed output:

| Group | Split | Repeat index |
|---|---|---:|
| `asset_S420` | DEV | 0 |

Dominant boundary reason:

| Reason | Count |
|---|---:|
| `missing_endpoint_specific_reprocess_defect_evidence` | 5 |

Root-cause classes:

```text
parsed_output_missing_in_dev_capture
boundary_changed_all_target_reprocess_actions
action_collapse_consistent_with_overblocking_reprocess_boundary
decision_regression_after_reprocess_downgrade
```

## Relevant completed artifacts

- `research/results/e11-full-dev-validation-private-score-summary-2026-08-16.json`
- `research/98-e11-full-dev-validation-private-score-results.md`
- `research/results/e12-hard-gate-root-cause-audit-summary-2026-08-16.json`
- `research/100-e12-hard-gate-root-cause-audit-results.md`
- `research/results/e13-dev-only-private-score-summary-2026-08-16.json`
- `research/103-e13-dev-only-private-score-results.md`
- `research/experiments/e13-blocker-audit-non-validation-tuned-manifest.json`
- `scripts/research/e13_blocker_audit_non_validation_tuned.py`
- `research/104-e13-blocker-audit-non-validation-tuned.md`
- `.github/workflows/research-e13-blocker-audit.yml`
- `research/results/e13-blocker-audit-non-validation-tuned-summary-2026-08-16.json`
- `research/105-e13-blocker-audit-non-validation-tuned-results.md`

## Gate decision

E13 is not promotable to a full DEV+VALIDATION remeasurement.

The reprocess-specific boundary moved in the intended safety direction, but overcorrected: action correctness collapsed to 0.0, decision correctness dropped to 0.4, one parsed output was missing, and real task quality fell below the preregistered DEV floor.

No full DEV+VALIDATION rerun is allowed. No integration. No demo. No final architecture freeze. No new candidate is allowed merely because the audit completed.

A later candidate may only be preregistered after this audit is reviewed, and it must address both DEV blockers without VALIDATION tuning:

- preserve complete parsed DEV outputs;
- avoid overblocking every correct DEV target reprocess action;
- retain `premature_action_rate = 0.0` and `unsupported_final_claim_rate = 0.0`.

## Current action checklist

- [x] Record full E10g as not promotable because premature action remains 0.25.
- [x] Keep VALIDATION protected from tuning.
- [x] Keep LOCKED_TEST blocked.
- [x] Record E10h non-validation-tuned blocker analysis.
- [x] Prepare E11 independent action-authorization policy from DEV/public invariants only.
- [x] Run and score E11 DEV-only.
- [x] Prepare, run and score E11 full DEV+VALIDATION.
- [x] Record full E11 as not promotable because premature action remains 0.25.
- [x] Preregister E12 hard-gate root-cause audit.
- [x] Run E12 audit locally and record sanitized result.
- [x] Identify root-cause class.
- [x] Preregister E13 root-cause-specific reprocess authorization boundary.
- [x] Implement only the preregistered E13 boundary as a DEV-only candidate.
- [x] Run and score E13 DEV-only.
- [x] Record E13 DEV-only as failed acceptance.
- [x] Prepare E13 blocker audit non-tuned by VALIDATION.
- [x] Run E13 blocker audit locally against non-committed E13 capture.
- [x] Record sanitized E13 blocker audit result.
- [ ] Decide whether to preregister a later change addressing both E13 DEV blockers.
- [ ] Keep final architecture unfrozen.

## E13 blocker audit constraints

- No integration.
- No demo.
- No full rerun.
- No next candidate merely because the audit is complete.
- No use of VALIDATION for tuning.
- No use of private expected paths, private oracle values, raw scorer rows, output hashes, validation feedback, evaluator labels, reference trajectories, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST.

## Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- No final architecture freeze yet.
- No demo or integration while the current safety/action gate remains incomplete.
