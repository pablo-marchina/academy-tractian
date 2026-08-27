# E4 — DEV Scoreable Proposal Run

**Date:** 2026-08-16  
**Status:** EXECUTED / DEV-ONLY / SCOREABLE-PRIVATE-SUMMARY-RECORDED  
**Split:** DEV  
**LOCKED_TEST:** not accessed

This report records the first scoreable DEV proposal run for the E4 B0-B3 guarded-boundary experiment. Unlike the previous boundary-only plan, this run includes tool proposals plus natural-language final answers/handoff text.

The private evaluator-only gold was used only locally. The public repository records aggregate redacted metrics and does not expose per-scenario expected facts, rubrics or gold text.

## Inputs

- Scoreable proposal plan: `research/experiments/e4-dev-scoreable-proposal-plan-gpt-5-5-thinking-2026-08-16.json`
- Boundary adapter: `scripts/research/e4_model_proposal_adapter.py`
- Split manifest: `research/frozen/benchmark-split-v1.json`
- CI run: `31946763543`
- Uploaded artifact: `e4-dev-scoreable-proposal-boundary`
- Artifact id: `9263503605`
- Redacted scoreable summary: `research/results/e4-private-dev-scoreable-evaluator-redacted-summary-2026-08-16.json`

## Safeguards preserved

- `LOCKED_TEST` was not accessed.
- The scoreable plan used only DEV groups.
- The adapter rejected non-DEV/locked-test use by construction.
- Identity and seed remained runner-bound.
- The plan was labeled `proposal_source_class=model_agent`.
- The run included natural-language final answers/handoff text.
- Private evaluator-only gold was not committed.

## Pressure cases included

The run deliberately adds two DEV pressure cases:

1. **B1 pressure:** invalid/too-short action justification in a retraining proposal.
2. **B3 pressure:** specialist-action proposal before required evidence is collected.

These are experimental pressure probes, not a demo path.

## Boundary metrics

| Variant | Proposals | Executed calls | Blocked calls | Invalid arg executions | Premature action executions | Required action executions | Contained unsafe proposals | Uncontained safety failures |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 | 27 | 27 | 0 | 1 | 1 | 7 | 0 | 2 |
| B1 | 27 | 26 | 1 | 0 | 1 | 6 | 1 | 1 |
| B2 | 27 | 26 | 1 | 0 | 1 | 6 | 1 | 1 |
| B3 | 27 | 25 | 2 | 0 | 0 | 5 | 2 | 0 |

## Private DEV scoreable aggregate

| Variant | Scenarios | Scoreable pass | Scoreable partial | Scoreable fail | Decision OK | Action OK | Safety OK | Avg evidence coverage | Avg conclusion marker coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 | 8 | 6 | 0 | 2 | 8 | 6 | 6 | 1.000 | 1.000 |
| B1 | 8 | 7 | 0 | 1 | 8 | 7 | 7 | 1.000 | 1.000 |
| B2 | 8 | 7 | 0 | 1 | 8 | 7 | 7 | 1.000 | 1.000 |
| B3 | 8 | 8 | 0 | 0 | 8 | 8 | 8 | 1.000 | 1.000 |

## Interpretation

1. B1 now shows value by containing the invalid short-justification action proposal that B0 would execute.
2. B3 now shows value by containing the premature action-before-evidence proposal that B0/B1/B2 would execute.
3. B2 has no new effect in this scoreable pressure run because the scoreable plan does not include a cross-company or permission-denied action.
4. B3 is the only variant with zero uncontained safety failures and 8/8 scoreable private DEV passes.
5. This is DEV evidence only. It supports preparing a VALIDATION comparison, but it still cannot freeze runtime, model, prompt, MCP, RAG, multi-agent design or UI.

## Next decision

The next correct step is not architecture freeze. The next step is a VALIDATION-ready E4 package:

```text
E4 VALIDATION preparation
├── carry B1/B2/B3 forward as candidate boundaries
├── keep B0 as baseline
├── generate validation proposal plan on VALIDATION groups only
├── preserve LOCKED_TEST block
├── rerun B0/B1/B2/B3
├── combine with private VALIDATION evaluator
└── promote/reject B1/B2/B3 with evidence
```
