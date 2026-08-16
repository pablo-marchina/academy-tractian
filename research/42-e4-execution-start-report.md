# E4 — Execution Start Report

**Date:** 2026-08-16  
**Status:** STARTED / PREREGISTRATION-CHECKED  
**Scope:** DEV + VALIDATION only

E4 has started with a preregistered B0-B3 manifest and CI-level validation. This report records the transition from E3 split freeze to E4 execution.

## What was executed

Created:

- `research/41-e4-guarded-boundary-experiment-preregistration.md`
- `research/experiments/e4-b0-b3-experiment-manifest.json`
- `scripts/research/e4_validate_experiment_manifest.py`

Updated:

- `.github/workflows/research-e2.yml`

The workflow now validates:

1. E2 unit suite;
2. E3 frozen split;
3. E4 experiment manifest.

## E4 scope

The experiment compares:

| Variant | Meaning |
|---|---|
| B0 | minimal benchmark-valid wrapper |
| B1 | B0 + strict typed validation |
| B2 | B1 + deterministic permission/resource guard |
| B3 | B2 + evidence-aware action/escalation gate |

B4 confirmation remains outside the main experiment.

## Locked-test protection

`LOCKED_TEST` remains unavailable for:

- prompt tuning;
- model selection;
- runtime selection;
- agent policy debugging;
- architecture ablation;
- threshold fitting;
- optimizer feedback.

Allowed E4 splits are only:

- DEV for debugging;
- VALIDATION for selection.

## Non-demo protection

The manifest explicitly rejects demo-first development:

- scripted reference paths are not agent-quality evidence;
- test doubles are not agent-quality evidence;
- quality claims require a non-demo proposal source;
- hard safety is reported separately from quality metrics;
- contained unsafe proposals are not treated as executed safety failures, but remain visible as agent-layer failures.

## Next executable step

After the CI validation is green, the next E4 task is to implement the first DEV-only run harness:

```text
E4 DEV runner
├── load BENCHMARK-SPLIT-v1
├── restrict to DEV groups
├── run B0/B1/B2/B3 variants through HarnessRunner
├── require an explicit proposal_source_class
├── reject LOCKED_TEST by construction
├── export per-variant metric tables
└── keep scripted/reference proposal sources labeled as infrastructure-only
```

No model/runtime/prompt/architecture decision is allowed until non-demo DEV and VALIDATION evidence exists.
