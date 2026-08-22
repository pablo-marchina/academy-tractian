# E13 Blocker Audit — Non-VALIDATION-Tuned

**Status:** E13_BLOCKER_AUDIT_READY  
**Date:** 2026-08-16  
**Scope:** DEV-only diagnostic audit  
**Demo:** false  
**Integration:** false  
**New product:** false  
**New guard:** false  
**Next candidate:** false  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Purpose

E13 implemented the preregistered reprocess-specific authorization boundary and failed DEV-only acceptance.

This audit is the only allowed next movement. It does not implement another candidate and does not tune on VALIDATION. Its purpose is to identify why E13 caused DEV action collapse and why one parsed output was missing.

## E13 failure being audited

Sanitized E13 DEV-only private score context:

| Metric | E13 DEV-only |
|---|---:|
| Fixed calls consumed | 6 |
| Parsed model outputs available | 5 |
| Scoreable calls | 5 |
| Real task quality | 0.7714 |
| Decision correctness | 0.4 |
| Evidence correctness | 1.0 |
| Action correctness | 0.0 |
| Escalation correctness | 1.0 |
| Premature action rate | 0.0 |
| Unsupported final-claim rate | 0.0 |
| Proxy-vs-real disagreement rate | 1.0 |

E13 is not promotable to full DEV+VALIDATION.

## Audit questions

E13 blocker audit checks:

1. whether the E13 reprocess-specific boundary ran on the DEV capture;
2. how many DEV outputs were parsed;
3. which sanitized DEV call identifiers lacked parsed output;
4. how many parsed outputs had boundary metadata;
5. how many target `POST /analyses/{analysis_id}/reprocess` rows were detected;
6. how many rows were changed by the boundary;
7. whether the boundary downgraded every target reprocess action;
8. which public/sanitized boundary reasons dominated;
9. whether the action collapse is consistent with overblocking;
10. whether a later preregistered change is required before any new candidate.

## Boundary

Allowed inputs:

- local non-committed E13 DEV-only fixed capture metadata;
- sanitized E13 aggregate score summary;
- DEV/public invariants already documented in repo.

Forbidden inputs:

- VALIDATION tuning;
- private expected paths;
- private oracle values;
- raw scorer rows;
- output hashes in committed artifacts;
- raw fixed parsed outputs in committed artifacts;
- validation feedback;
- evaluator labels;
- reference trajectories;
- `eval/expected-paths.json` in model/policy/audit output;
- `docs/test-scenarios.md`;
- `data/cases.parquet`;
- LOCKED_TEST.

## Files

- `research/experiments/e13-blocker-audit-non-validation-tuned-manifest.json`
- `scripts/research/e13_blocker_audit_non_validation_tuned.py`
- `research/104-e13-blocker-audit-non-validation-tuned.md`
- `.github/workflows/research-e13-blocker-audit.yml`

## Local run

```powershell
git pull
$env:PYTHONPATH = "."

$E13_AUDIT = "$env:TEMP\e13-blocker-audit-non-validation-tuned.json"

python scripts/research/e13_blocker_audit_non_validation_tuned.py `
  --manifest research/experiments/e13-blocker-audit-non-validation-tuned-manifest.json `
  --fixed-output-file $E13_CAPTURE `
  --sanitized-score-summary research/results/e13-dev-only-private-score-summary-2026-08-16.json `
  --out $E13_AUDIT

Get-Content $E13_AUDIT
```

If the sanitized score summary is not available locally after `git pull`, run without it:

```powershell
python scripts/research/e13_blocker_audit_non_validation_tuned.py `
  --manifest research/experiments/e13-blocker-audit-non-validation-tuned-manifest.json `
  --fixed-output-file $E13_CAPTURE `
  --out $E13_AUDIT
```

## Dry-run CI

The workflow validates the audit script shape with a synthetic DEV-only capture. It does not call an external model.

## Gate decision

No integration.  
No demo.  
No full rerun.  
No final architecture freeze.  
No next candidate merely because this audit is prepared.

A later candidate is allowed only after the audit result identifies a DEV-only blocker class and a new change is preregistered without VALIDATION tuning.
