# E12 Hard-gate Root-cause Audit

**Status:** E12_HARD_GATE_ROOT_CAUSE_AUDIT_READY  
**Date:** 2026-08-16  
**Is demo:** false  
**Is integration:** false  
**Is new product:** false  
**Is new guard:** false  
**VALIDATION used for tuning:** false  
**LOCKED_TEST accessed:** false  
**Final architecture frozen:** false

## Why this exists

E11 passed DEV-only, but full DEV+VALIDATION preserved the same safety failure as E10d/E10e/E10g: `premature_action_rate = 0.25`.

The project is now in hard phase-gate mode. No integration, demo, UI/final architecture or next product phase may proceed until the current safety gate and its dependencies are fully concluded.

E12 is therefore a root-cause audit, not another guard iteration.

## What E12 audits

E12 checks the E11 full capture metadata to answer:

- Did the independent action-authorization policy actually run on full DEV+VALIDATION?
- How many outputs did it check?
- How many outputs did it change?
- Did it cover both DEV and VALIDATION?
- Did it authorize validation outputs instead of blocking them?
- Is the failure class more consistent with policy non-application, partial coverage, over-permissive authorization or wrong action-class/endpoint classification?

## Boundary

E12 may use:

- local non-committed E11 full fixed-capture metadata;
- sanitized E11 full aggregate score summary;
- DEV/public project invariants;
- public tool endpoint/action-class invariants.

E12 must not use:

- VALIDATION for tuning;
- private expected-path values;
- private oracle values;
- raw scorer rows as committed artifacts;
- output hashes as committed artifacts;
- evaluator labels;
- reference trajectories;
- validation feedback as rule-design input;
- `eval/expected-paths.json`;
- `docs/test-scenarios.md`;
- `data/cases.parquet`;
- LOCKED_TEST material.

## Local command

Use the already-created local full E11 capture file. Do not commit that file.

```powershell
$E12_AUDIT = "$env:TEMP\e12-hard-gate-root-cause-audit.json"

python scripts/research/e12_hard_gate_root_cause_audit.py `
  --manifest research/experiments/e12-hard-gate-root-cause-audit-manifest.json `
  --fixed-output-file $E11_FULL_CAPTURE `
  --sanitized-score-summary research/results/e11-full-dev-validation-private-score-summary-2026-08-16.json `
  --out $E12_AUDIT

Get-Content $E12_AUDIT
```

If the sanitized score summary is unavailable locally, the audit can still run against the capture metadata only:

```powershell
python scripts/research/e12_hard_gate_root_cause_audit.py `
  --manifest research/experiments/e12-hard-gate-root-cause-audit-manifest.json `
  --fixed-output-file $E11_FULL_CAPTURE `
  --out $E12_AUDIT
```

## Expected audit output

The audit output is sanitized and may be committed only after inspection.

It reports:

- policy coverage counts;
- checked/changed counts by split;
- authorization reason counts by split;
- action-class and endpoint counts by split;
- root-cause class;
- whether a next candidate is allowed now.

It must not include raw fixed outputs, score rows, output hashes, local private paths, private oracle values or LOCKED_TEST material.

## Gate rule

No next candidate may be designed until E12 identifies the root-cause class.

No full rerun may happen until a later change is preregistered from that root-cause class without VALIDATION tuning.

No integration or demo is allowed while `premature_action_rate > 0.0` on the full gate.
