# E13 Blocker Audit — Non-Validation-Tuned Results

**Status:** E13_BLOCKER_AUDIT_PASS  
**Date:** 2026-08-16  
**Scope:** DEV-only blocker audit  
**Demo:** false  
**Integration:** false  
**New product:** false  
**New guard:** false  
**Next candidate:** false  
**VALIDATION used for tuning:** false  
**VALIDATION calls read:** 0  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Summary

E13 was audited after the DEV-only private score failed acceptance. The audit was diagnostic only: it did not create a new candidate, did not use VALIDATION for tuning, did not inspect LOCKED_TEST, and did not authorize integration, demo, full rerun, or architecture freeze.

The audit confirms that the E13 DEV-only failure has two blocker families:

1. one DEV call had no parsed output;
2. the reprocess-specific authorization boundary changed every detected target `POST /analyses/{analysis_id}/reprocess` action, which is consistent with action collapse.

The root-cause classes are:

```text
parsed_output_missing_in_dev_capture
boundary_changed_all_target_reprocess_actions
action_collapse_consistent_with_overblocking_reprocess_boundary
decision_regression_after_reprocess_downgrade
```

## Capture audit

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

## Missing parsed output

| Group | Split | Repeat index |
|---|---|---:|
| `asset_S420` | DEV | 0 |

The trace-event summary indicates that six prompts were built, but only five model calls and five parsed outputs were observed. One model call failed.

## Boundary behavior

| Boundary reason | Count |
|---|---:|
| `missing_endpoint_specific_reprocess_defect_evidence` | 5 |

| Endpoint | Count |
|---|---:|
| `post /analyses/{analysis_id}/reprocess` | 5 |

| Group | Boundary applied count |
|---|---:|
| `asset_G501` | 2 |
| `asset_C710` | 2 |
| `asset_S420` | 1 |

The boundary changed every parsed target reprocess action and authorized none. The audit found no endpoint-specific defect categories in the parsed target rows.

## Trace event counts

| Event | Count |
|---|---:|
| `prompt_built` | 6 |
| `model_called` | 5 |
| `output_parsed` | 5 |
| `output_scored` | 6 |
| `visible_escalation_consistency_guard_applied` | 5 |
| `visible_premature_action_safety_guard_checked` | 5 |
| `visible_balanced_safety_action_guard_checked` | 5 |
| `independent_action_authorization_checked` | 5 |
| `reprocess_specific_authorization_boundary_blocked` | 5 |
| `model_call_failed` | 1 |

## Sanitized score context

| Metric | E13 DEV-only |
|---|---:|
| Scoreable calls | 5 |
| Real task quality | 0.7714 |
| Decision correctness | 0.4 |
| Evidence correctness | 1.0 |
| Action correctness | 0.0 |
| Escalation correctness | 1.0 |
| Premature action rate | 0.0 |
| Unsupported final-claim rate | 0.0 |
| Proxy-vs-real disagreement rate | 1.0 |

## Root-cause decision

The E13 blocker is not a full-measurement issue. E13 failed before full DEV+VALIDATION eligibility because DEV completeness and DEV action/decision quality failed.

The most specific supported diagnosis is:

```text
E13 overblocked the DEV reprocess action surface: every parsed target reprocess action was downgraded for missing endpoint-specific reprocess-defect evidence, which preserved safety but collapsed action correctness to 0.0 and decision correctness to 0.4. In parallel, one DEV call lacked a parsed output after a model-call failure.
```

## Gate decision

Do not prepare full DEV+VALIDATION E13.  
Do not integrate.  
Do not demo.  
Do not freeze final architecture.  
Do not create a next candidate from this audit alone.

A later candidate may only be preregistered after this audit is reviewed, and it must address both DEV blockers without VALIDATION tuning:

- preserve complete parsed DEV outputs;
- avoid overblocking every correct DEV target reprocess action;
- retain `premature_action_rate = 0.0` and `unsupported_final_claim_rate = 0.0`.

## Boundary

This record is sanitized. It does not include raw fixed parsed outputs, raw score rows, output hashes, private expected paths, oracle values, local private paths, API keys, validation feedback, reference trajectories, evaluator-only labels, or LOCKED_TEST material.
