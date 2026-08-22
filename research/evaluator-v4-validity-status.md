# Evaluator v4 validity status

Date: 2026-08-18

## Why v4 exists

Frozen E9 v3 remains useful for historical comparability, but oracle-free synthetic tests demonstrated that its lexical heuristics can mis-handle negation, conditionals, root-question wording, evidence outside `evidence_plan`, and semantic unsupported claims.

## Private oracle shape learned without values

Aggregate-only diagnostics established:

- 17 expected-path rows;
- 57 expected-path steps;
- every step is an object with `step:string` and `note:string`;
- 57/57 steps contain an HTTP method and a path recognized by the 18-entry public tool registry;
- strict method + public-tool signature coverage is 1.0;
- all 17 rows have every expected step recognizable as a public tool signature;
- `root_question` and `mode` were excluded from action/escalation label inference.

This supports a deterministic public-tool-signature evaluator rather than additional lexical heuristics.

## Frozen v4 semantics

`research/experiments/evaluator-v4-deterministic-tool-signature-amendment.json` freezes the implementation direction before any candidate can be scored by v4:

- supervision comes from normalized `expected_path.step` only;
- tool method/path normalize against `research/e2/tool_registry.py`;
- evidence credit comes only from `evidence_plan`;
- action expectation is derived from expected action-tool signatures;
- explicit human escalation is derived only from the public request-specialist and case-escalate signatures;
- generic words such as “human”, “specialist”, or “action” do not create labels;
- root-question wording cannot define expected action/escalation;
- general free-text groundedness is reported as unmeasured rather than approximated by absence of gold/leakage phrases.

## Current implementation status

`scripts/research/e9_evaluator_side_scorer_v4.py` is implemented as **measurement-only**. It cannot authorize VALIDATION yet.

Oracle-free synthetic checks cover:

- root-question confound blocking;
- evidence-plan isolation;
- deterministic action endpoint matching;
- explicit escalation endpoint semantics;
- unsupported action detection;
- aggregate-only output privacy.

The first CI run failed before tests because a clean runner lacked the existing registry dependency `pydantic`; the workflow was corrected without changing evaluator semantics. The subsequent synthetic test step passed.

## Remaining validity blocker

The historical E9 adapter scores at asset/story-group level and may aggregate more than one private expected-path row into one group. Before v4 can become a gate, `scripts/research/e9_private_oracle_group_ambiguity_diagnostic.py` must establish whether group-level aggregation merges multiple distinct action targets.

If it does, v4 stays measurement-only until the scoring unit is fixed without candidate-specific feedback. If it does not, v4 can advance to the preregistered validity gate.

LOCKED_TEST remains untouched and VALIDATION remains blocked.
