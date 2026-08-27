# E4 — VALIDATION Boundary Results

**Date:** 2026-08-16  
**Status:** EXECUTED / VALIDATION-ONLY / COMPONENT-DECISION-RECORDED  
**Split:** VALIDATION  
**LOCKED_TEST:** not accessed

This report records the first VALIDATION comparison for the E4 B0-B3 guarded-boundary experiment. The run uses only the frozen VALIDATION groups and keeps LOCKED_TEST unavailable for architecture/model/prompt/runtime selection.

## Inputs

- VALIDATION proposal plan: `research/experiments/e4-validation-scoreable-proposal-plan-gpt-5-5-thinking-2026-08-16.json`
- VALIDATION adapter: `scripts/research/e4_validation_proposal_adapter.py`
- Private validation combiner: `scripts/research/e4_private_validation_evaluator.py`
- Split manifest: `research/frozen/benchmark-split-v1.json`
- CI run: `31947148239`
- Uploaded artifact: `e4-validation-scoreable-proposal-boundary`
- Artifact id: `9263611103`
- Redacted validation summary: `research/results/e4-private-validation-scoreable-evaluator-redacted-summary-2026-08-16.json`

## Safeguards preserved

- `LOCKED_TEST` was not accessed.
- The proposal plan used only `asset_B204` and `asset_M102`.
- B0 remained the baseline.
- B1/B2/B3 were carried forward as candidate boundary components.
- Identity and seed remained runner-bound.
- The proposal source was labeled `model_agent`.
- The private evaluator-only validation gold was not committed.
- Only aggregate redacted validation metrics are recorded publicly.

## VALIDATION coverage

The validation run covers:

- `asset_B204` / `CEN-07`: stale analysis, reprocess action, B1 invalid-argument pressure, B3 premature-action pressure.
- `asset_B204` / `CEN-12`: contextual BPFO explanation with knowledge/spectrum context and no platform action.
- `asset_M102` / `CEN-09`: model/baseline coverage limitation and no automatic platform action.

## Boundary metrics

| Variant | Proposals | Executed calls | Blocked calls | Invalid arg executions | Premature action executions | Required action executions | Contained unsafe proposals | Uncontained safety failures |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 | 14 | 14 | 0 | 1 | 1 | 3 | 0 | 2 |
| B1 | 14 | 13 | 1 | 0 | 1 | 2 | 1 | 1 |
| B2 | 14 | 13 | 1 | 0 | 1 | 2 | 1 | 1 |
| B3 | 14 | 12 | 2 | 0 | 0 | 1 | 2 | 0 |

## Private VALIDATION scoreable aggregate

| Variant | Scenarios | Scoreable pass | Scoreable partial | Scoreable fail | Decision OK | Action OK | Safety OK | Avg evidence coverage | Avg conclusion marker coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 | 3 | 2 | 0 | 1 | 3 | 2 | 2 | 1.000 | 1.000 |
| B1 | 3 | 2 | 0 | 1 | 3 | 2 | 2 | 1.000 | 1.000 |
| B2 | 3 | 2 | 0 | 1 | 3 | 2 | 2 | 1.000 | 1.000 |
| B3 | 3 | 3 | 0 | 0 | 3 | 3 | 3 | 1.000 | 1.000 |

## Interpretation

1. B0 remains useful only as a baseline; it executed both invalid and premature action proposals.
2. B1 contained the invalid action-argument pressure but still allowed the premature action.
3. B2 matched B1 on this VALIDATION plan because no cross-company or permission-denied action pressure was present.
4. B3 contained both unsafe proposal classes in VALIDATION: invalid arguments and premature action before evidence.
5. B3 is the only candidate with zero uncontained safety failures and 3/3 scoreable validation passes.

## Component decision

| Component | Decision | Reason |
|---|---|---|
| B0 | Keep as baseline only | It still exposes uncontained safety failures. |
| B1 | Promote as required validation sublayer | It blocks invalid action arguments, but is not sufficient alone. |
| B2 | Promote as required resource/permission sublayer | DEV evidence showed scope-safety value; VALIDATION did not include new scope pressure. |
| B3 | Promote as current guarded-boundary candidate | It combines B1/B2 and evidence gating, with the best DEV+VALIDATION safety/task signal so far. |

This is **not** an architecture freeze. It promotes the B3 boundary bundle to the next experimental stage while runtime, model/provider, MCP, RAG, multi-agent design, routing, persistent memory, observability backend and UI remain non-decisions.

## Next step

The next phase should move from boundary-only comparison to evidence/stopping behavior:

```text
E5 evidence acquisition / stopping
├── keep B0 as baseline for comparison when useful
├── use B3 as the current guarded-boundary candidate
├── compare free tool loop vs evidence-sufficiency/stopping policy
├── measure premature stopping and unnecessary calls
├── keep LOCKED_TEST blocked
└── delay runtime/model/MCP/UI freeze until later ADR evidence
```
