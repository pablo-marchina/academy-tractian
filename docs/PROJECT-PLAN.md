# Academy × TRACTIAN — Project Action Plan

**Status:** E13 DEV-only reprocess authorization boundary ready  
**Planning date:** 2026-08-16  
**Progress checkpoint:** 2026-08-16 22:16 BRT  
**Target final delivery:** 2026-09-08

## Current gate

E11 passed DEV-only private scoring after the E10h blocker analysis introduced independent action authorization. The full DEV+VALIDATION E11 remeasurement was then run and scored with E9 v3 after outputs were fixed.

Decision: do not promote E11 to integration gates. E11 full matches E10d/E10e/E10g full: it improves over the E9 full baseline in average task quality, evidence and action, but the full premature-action safety regression persists at `premature_action_rate = 0.25`. The required full safety gate is `premature_action_rate = 0.0`.

The full scorer run was valid: 12 fixed calls, 12 parsed model outputs, 5 private oracles loaded, 12 matching oracle calls and 12 scoreable calls. VALIDATION was measurement-only, not tuning. LOCKED_TEST remains blocked and final architecture remains unfrozen.

Project rule: no integration, no demo and no downstream phase while the current gate or any dependency used by it remains incomplete.

E12 passed as a hard-gate root-cause audit. It confirmed that the E11 independent action-authorization policy did run on full DEV+VALIDATION, checked all 12 outputs, covered both DEV and VALIDATION, and changed 0 outputs. Root-cause class: `policy_executed_but_over_permissive_or_wrong_authorization_class`.

E13 has now implemented only the preregistered root-cause-specific change as a DEV-only candidate. It targets autonomous `POST /analyses/{analysis_id}/reprocess` authorization and does not authorize reprocess from generic evidence-family counts or generic human-review markers.

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

## E13 implemented boundary

E13 implements one root-cause-specific change:

```text
reprocess_specific_authorization_boundary
```

Target endpoint:

```text
POST /analyses/{analysis_id}/reprocess
```

Target failure mode:

```text
over_permissive_authorization_of_autonomous_reprocess_actions
```

Rule implemented: do not authorize autonomous reprocess from generic evidence-family counts or generic human-review markers. Authorize `POST /analyses/{analysis_id}/reprocess` only when endpoint-specific visible evidence shows that the existing analysis itself is invalid, failed, stale, incomplete, blocked by data-quality failure, or otherwise unsafe to rely on without recomputation.

If endpoint-specific reprocess-defect evidence is missing, E13 downgrades immediate reprocess to investigation or human handoff without executing reprocess.

The E13 dry-run CI passed without external model calls.

## Relevant completed artifacts

- `research/results/e11-full-dev-validation-private-score-summary-2026-08-16.json`
- `research/98-e11-full-dev-validation-private-score-results.md`
- `research/experiments/e12-hard-gate-root-cause-audit-manifest.json`
- `scripts/research/e12_hard_gate_root_cause_audit.py`
- `research/99-e12-hard-gate-root-cause-audit.md`
- `.github/workflows/research-e12.yml`
- `research/results/e12-hard-gate-root-cause-audit-summary-2026-08-16.json`
- `research/100-e12-hard-gate-root-cause-audit-results.md`
- `research/experiments/e13-preregistered-reprocess-authorization-boundary-manifest.json`
- `research/101-e13-preregistered-reprocess-authorization-boundary.md`
- `research/experiments/e13-dev-only-reprocess-authorization-boundary-manifest.json`
- `scripts/research/e13_dev_only_reprocess_authorization_boundary.py`
- `research/102-e13-dev-only-reprocess-authorization-boundary.md`
- `.github/workflows/research-e13.yml`

## Gate decision

E11 remains not promotable to integration.

E13 is ready for DEV-only local capture and private scoring. It does not authorize integration, demo, a full rerun or final architecture freeze.

No full DEV+VALIDATION rerun is allowed unless E13 passes DEV-only first.

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
- [ ] Run E13 DEV-only capture.
- [ ] Score E13 DEV-only after outputs are fixed.
- [ ] Keep final architecture unfrozen.

## E13 next-step constraints

- No integration.
- No demo.
- No full rerun before DEV-only acceptance.
- No new candidate unrelated to over-permissive reprocess authorization.
- No use of VALIDATION for tuning.
- No use of private expected paths, private oracle values, raw scorer rows, output hashes, validation feedback, evaluator labels, reference trajectories, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST.

## Methodological constraints

- The model must not see expected answers, private oracles, reference trajectories, scorer-only labels, `eval/expected-paths.json`, `docs/test-scenarios.md`, `data/cases.parquet`, or LOCKED_TEST material.
- LOCKED_TEST remains blocked until final evaluation.
- VALIDATION must not be used for tuning loops.
- No final architecture freeze yet.
- No demo or integration while the current safety gate remains incomplete.
