# Evaluator v4 visible-case / oracle alignment result

Date: 2026-08-18

## Status

The preregistered private aggregate-only visible-case alignment diagnostic passed its activation criterion for every runner-selected frozen group.

Sanitized aggregate result supplied by the operator:

```text
agent case records found:                         17
frozen groups with agent case records:            10
frozen groups with multiple agent case records:   5
runner-selected visible cases:                    10
selected visible cases without ticket_id:          0
selected tickets with exactly one oracle row:     10 / 10
exact-single-row alignment fraction:               1.0
groups where group-union adds other oracle rows:   4
oracle rows without frozen-group mapping:           1
```

Split-level alignment was exact for every runner-selected visible case:

```text
DEV:         5 / 5 exact single-row matches
VALIDATION:  2 / 2 exact single-row matches
LOCKED_TEST: 3 / 3 exact single-row matches
```

The split-level counts are an aggregate structural alignment diagnostic only. They are not candidate feedback and do not authorize VALIDATION or LOCKED_TEST execution.

## Methodological conclusion

The public runner's first-case-per-asset selection rule can be replayed deterministically and the selected case's `ticket_id` identifies exactly one private expected-path row for every frozen group selected by that runner.

This confirms that historical group-level oracle union was over-broad for evidence supervision: four frozen groups contain additional oracle rows beyond the selected visible ticket. Therefore evaluator v4 must not union expected paths by asset/group.

The preregistered activation rule is adopted:

1. replay the runner's first-case-per-asset selection using the same `agent-input/cases.json`;
2. align private supervision by exact `group/asset + ticket_id`;
3. require exactly one matching expected-path row;
4. score only signatures from that single row;
5. zero or multiple matches are unscoreable;
6. never fall back to group-level union;
7. never use root question, mode, candidate output or scorer feedback to resolve alignment.

## Evaluator implementation consequence

`scripts/research/e9_evaluator_side_scorer_v4.py` now implements the selected-ticket alignment rule and requires `--agent-input-cases`. Evidence extraction also recognizes every public read signature present in each `evidence_plan` string instead of crediting only the first signature in a multi-tool string.

Evaluator v4 remains **measurement-only**. Exact ticket alignment resolves the supervision-unit ambiguity, but it does not itself authorize VALIDATION. A future candidate must still pass the full DEV coverage gate across all five frozen DEV groups, and general free-text groundedness remains explicitly unmeasured unless a separately validated metric is added.

## Privacy

No expected-path text, ticket IDs, group IDs, endpoint names, per-row results, hashes, raw model outputs or private paths are committed in this result.