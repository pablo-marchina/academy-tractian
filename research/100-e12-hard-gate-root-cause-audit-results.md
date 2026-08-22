# E12 Hard-Gate Root-Cause Audit Results

**Status:** E12_HARD_GATE_ROOT_CAUSE_AUDIT_PASS  
**Date:** 2026-08-16  
**Scope:** DEV + VALIDATION instrumentation audit  
**Demo:** false  
**Integration:** false  
**New product:** false  
**New guard:** false  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Summary

E12 audited the E11 full DEV+VALIDATION capture instrumentation after E11 full failed the safety gate.

The audit proves that the independent action-authorization policy did run on the full capture: 12 outputs were checked, including 6 DEV and 6 VALIDATION outputs. The policy changed 0 outputs.

The root-cause class is:

```text
policy_executed_but_over_permissive_or_wrong_authorization_class
```

This means the failure was not policy non-application and not partial coverage. The policy was present, enabled, and covered both splits, but it authorized every output as an autonomous state-changing action with independent evidence and human review.

## Instrumentation findings

| Finding | Result |
|---|---:|
| Top-level policy present | true |
| Top-level policy enabled | true |
| Total outputs checked | 12 |
| Total outputs changed | 0 |
| DEV outputs checked | 6 |
| VALIDATION outputs checked | 6 |
| DEV outputs authorized | 6 |
| VALIDATION outputs authorized | 6 |
| DEV outputs changed | 0 |
| VALIDATION outputs changed | 0 |
| Validation used for tuning | false |
| LOCKED_TEST accessed | false |

## Authorization pattern

| Split | Authorized reason | Count |
|---|---|---:|
| DEV | `authorized_state_change_with_independent_evidence_and_human_review` | 6 |
| VALIDATION | `authorized_state_change_with_independent_evidence_and_human_review` | 6 |

| Split | Action class | Count |
|---|---|---:|
| DEV | `autonomous_state_change` | 6 |
| VALIDATION | `autonomous_state_change` | 6 |

| Split | Endpoint | Count |
|---|---|---:|
| DEV | `POST /analyses/{analysis_id}/reprocess` | 6 |
| VALIDATION | `POST /analyses/{analysis_id}/reprocess` | 6 |

All 12 audited outputs had 7 detected evidence families, so the current independent-evidence-family threshold is not discriminating the failing full behavior.

## Sanitized score context

| Metric | Full E11 |
|---|---:|
| Scoreable calls | 12 |
| Real task quality | 0.8214 |
| Decision correctness | 0.75 |
| Evidence correctness | 0.75 |
| Action correctness | 0.75 |
| Escalation correctness | 0.5 |
| Premature action rate | 0.25 |
| Unsupported final-claim rate | 0.0 |
| Proxy-vs-real disagreement rate | 0.5 |

## Split summary

| Split | Calls | Real quality | Decision | Evidence | Action | Escalation | Premature action | Unsupported claim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DEV | 6 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| VALIDATION | 6 | 0.6429 | 0.5 | 0.5 | 0.5 | 0.0 | 0.5 | 0.0 |

## Root-cause decision

The E11 policy did execute. It covered DEV and VALIDATION. It did not use private oracle values, validation feedback or LOCKED_TEST. It changed 0 outputs.

Therefore, the full safety failure persisted because the independent action-authorization policy was too permissive for the failing class, or because it classified the failing behavior into the wrong action-authorization class.

The most specific supported finding is:

```text
The policy authorized every full output as autonomous_state_change via POST /analyses/{analysis_id}/reprocess, including all VALIDATION outputs, while VALIDATION premature_action_rate remained 0.5.
```

## Gate decision

Do not integrate.  
Do not demo.  
Do not freeze final architecture.  
Do not design the next candidate blindly.

A next candidate is not allowed merely because E12 finished. A next candidate is allowed only after a preregistered change directly addresses this root-cause class without using VALIDATION tuning.

## Boundary

This record is sanitized. It does not include raw fixed parsed outputs, score rows, output hashes, private expected paths, oracle values, local private paths, API keys, validation feedback, reference trajectories, evaluator-only labels or LOCKED_TEST material.

## Next gate condition

A valid next preregistered change must address at least one of these root-cause mechanisms without relying on VALIDATION feedback:

- autonomous `POST /analyses/{analysis_id}/reprocess` is being treated as safe too often;
- evidence-family count alone is too weak as independent evidence sufficiency;
- generic human-review markers are too weak to authorize autonomous state-changing action;
- the policy needs a stricter action-class boundary for reprocess actions;
- the policy must require endpoint-specific evidence sufficiency beyond visible family presence.
