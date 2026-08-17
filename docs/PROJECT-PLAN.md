# Academy × TRACTIAN — Project Action Plan

**Status:** E12 hard-gate root-cause audit passed; over-permissive/wrong authorization class identified  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 22:04 BRT  
**Target final delivery:** 2026-09-08

## Current gate

E11 passed DEV-only private scoring after the E10h blocker analysis introduced independent action authorization. The full DEV+VALIDATION E11 remeasurement was then run and scored with E9 v3 after outputs were fixed.

Decision: do not promote E11 to integration gates. E11 full matches E10d/E10e/E10g full: it improves over the E9 full baseline in average task quality, evidence and action, but the full premature-action safety regression persists at `premature_action_rate = 0.25`. The required full safety gate is `premature_action_rate = 0.0`.

The full scorer run was valid: 12 fixed calls, 12 parsed model outputs, 5 private oracles loaded, 12 matching oracle calls and 12 scoreable calls. VALIDATION was measurement-only, not tuning. LOCKED_TEST remains blocked and final architecture remains unfrozen.

Project rule: no integration, no demo and no downstream phase while the current gate or any dependency used by it remains incomplete.

E12 has now passed as a hard-gate root-cause audit. It confirms that the E11 independent action-authorization policy did run on full DEV+VALIDATION, checked all 12 outputs, covered both DEV and VALIDATION, and changed 0 outputs. Root-cause class: `policy_executed_but_over_permissive_or_wrong_authorization_class`.

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

## E12 audit findings

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

## E12 split score context

| Split | Calls | Real quality | Decision | Evidence | Action | Escalation | Premature action | Unsupported claim |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DEV | 6 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| VALIDATION | 6 | 0.6429 | 0.5 | 0.5 | 0.5 | 0.0 | 0.5 | 0.0 |

## Root-cause class

```text
policy_executed_but_over_permissive_or_wrong_authorization_class
```

The failure was not policy non-application and not partial coverage. E12 shows the policy was present, enabled, and covered all 12 full outputs.

The failure persisted because E11 authorized all 12 outputs, including all 6 VALIDATION outputs, as:

```text
authorized_state_change_with_independent_evidence_and_human_review
```

All audited outputs were classified as:

```text
autonomous_state_change via POST /analyses/{analysis_id}/reprocess
```

All audited outputs had 7 detected evidence families, which means the current evidence-family count threshold is too weak to discriminate the failing full behavior.

## Relevant completed artifacts

- `research/results/e11-full-dev-validation-private-score-summary-2026-08-16.json`
- `research/98-e11-full-dev-validation-private-score-results.md`
- `research/experiments/e12-hard-gate-root-cause-audit-manifest.json`
- `scripts/research/e12_hard_gate_root_cause_audit.py`
- `research/99-e12-hard-gate-root-cause-audit.md`
- `.github/workflows/research-e12.yml`
- `research/results/e12-hard-gate-root-cause-audit-summary-2026-08-16.json`
- `research/100-e12-hard-gate-root-cause-audit-results.md`

## Gate decision

E11 remains not promotable to integration.

E12 is complete as an audit gate, but it does not itself authorize a new candidate. A new candidate may only be preregistered after this root-cause class is addressed directly without VALIDATION tuning.

No integration. No demo. No UI/final architecture progression. No full rerun. No new candidate without preregistration grounded in the E12 root-cause class.

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
- [x] Add E12 audit script.
- [x] Add E12 dry-run CI guard.
- [x] Run E12 audit locally against non-committed E11 full capture.
- [x] Record sanitized E12 audit result.
- [ ] Decide whether to preregister a root-cause-specific change.
- [ ] Keep final architecture unfrozen.

## Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- No final architecture freeze yet.
- No demo or integration while the current safety gate remains incomplete.
