# Academy × TRACTIAN — Project Action Plan

**Status:** E13 DEV-only failed acceptance; full rerun blocked  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 22:33 BRT  
**Target final delivery:** 2026-09-08

## Current gate

E11 passed DEV-only private scoring after the E10h blocker analysis introduced independent action authorization. The full DEV+VALIDATION E11 remeasurement was then run and scored with E9 v3 after outputs were fixed.

Decision: do not promote E11 to integration gates. E11 full matches E10d/E10e/E10g full: it improves over the E9 full baseline in average task quality, evidence and action, but the full premature-action safety regression persists at `premature_action_rate = 0.25`. The required full safety gate is `premature_action_rate = 0.0`.

E12 passed as a hard-gate root-cause audit. It confirmed that the E11 independent action-authorization policy did run on full DEV+VALIDATION, checked all 12 outputs, covered both DEV and VALIDATION, and changed 0 outputs. Root-cause class: `policy_executed_but_over_permissive_or_wrong_authorization_class`.

E13 implemented only the preregistered root-cause-specific change as a DEV-only candidate. It targets autonomous `POST /analyses/{analysis_id}/reprocess` authorization and does not authorize reprocess from generic evidence-family counts or generic human-review markers.

E13 DEV-only was scored with E9 v3 after outputs were fixed. The scorer passed, but E13 failed DEV-only acceptance: 6 fixed calls were consumed, 5 parsed outputs were available, and only 5 calls were scoreable. Safety remained clean on scoreable calls, but action collapsed and average quality fell below the preregistered floor.

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

## E13 acceptance decision

E13 does not pass DEV-only acceptance.

Failures:

- parsed outputs: expected 6, observed 5;
- scoreable calls: expected 6, observed 5;
- real task quality: required at least 0.8571, observed 0.7714;
- decision correctness: required at least 0.75, observed 0.4;
- action correctness: required at least 0.75, observed 0.0;
- proxy-vs-real disagreement returned to 1.0.

Passes:

- evidence correctness stayed 1.0;
- escalation correctness stayed 1.0;
- premature action stayed 0.0 on scoreable calls;
- unsupported final-claim rate stayed 0.0;
- LOCKED_TEST remained blocked.

## Relevant completed artifacts

- `research/results/e11-full-dev-validation-private-score-summary-2026-08-16.json`
- `research/98-e11-full-dev-validation-private-score-results.md`
- `research/results/e12-hard-gate-root-cause-audit-summary-2026-08-16.json`
- `research/100-e12-hard-gate-root-cause-audit-results.md`
- `research/experiments/e13-preregistered-reprocess-authorization-boundary-manifest.json`
- `research/101-e13-preregistered-reprocess-authorization-boundary.md`
- `research/experiments/e13-dev-only-reprocess-authorization-boundary-manifest.json`
- `scripts/research/e13_dev_only_reprocess_authorization_boundary.py`
- `research/102-e13-dev-only-reprocess-authorization-boundary.md`
- `.github/workflows/research-e13.yml`
- `research/results/e13-dev-only-private-score-summary-2026-08-16.json`
- `research/103-e13-dev-only-private-score-results.md`

## Gate decision

E13 is not promotable to a full DEV+VALIDATION remeasurement.

The reprocess-specific boundary moved in the intended safety direction, but overcorrected: action correctness collapsed to 0.0, decision correctness dropped to 0.4, one parsed output was missing, and real task quality fell below the preregistered DEV floor.

No full DEV+VALIDATION rerun is allowed. No integration. No demo. No final architecture freeze.

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
- [x] Add E13 dry-run CI guard.
- [x] Run E13 DEV-only capture.
- [x] Score E13 DEV-only after outputs are fixed.
- [x] Record E13 DEV-only as failed acceptance.
- [ ] Decide next non-validation-tuned E13 blocker audit before any further candidate.
- [ ] Keep final architecture unfrozen.

## E13 next-step constraints

- No integration.
- No demo.
- No full rerun before DEV-only acceptance.
- No new candidate unrelated to E13 DEV action collapse and parse missing.
- No use of VALIDATION for tuning.
- No use of private expected paths, private oracle values, raw scorer rows, output hashes, validation feedback, evaluator labels, reference trajectories, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST.

## Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- No final architecture freeze yet.
- No demo or integration while the current safety gate remains incomplete.
