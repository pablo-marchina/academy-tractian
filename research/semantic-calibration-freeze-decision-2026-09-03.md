# Semantic calibration freeze decision — 2026-09-03

## Decision

Promote a v2 semantic-calibration gate that can authorize evaluator use only when its acceptance thresholds were frozen before held-out outcomes and are cryptographically bound to one complete human-reviewed `VALIDATION` packet.

The existing `semantic-calibration-policy-v1` remains available for historical/descriptive comparison, but the official CLI forcibly treats that path as `DESCRIPTIVE_ONLY`. Promotion authorization requires `semantic-calibration-protocol-v2` plus `semantic-calibration-evidence-v2`.

## Current evidence state

The semantic rubric, blinded two-reviewer workflow, third-party adjudication, inter-rater metrics and judge-vs-human calibration metrics already exist. This slice closes the remaining post-hoc-policy integrity gap.

**No real human semantic labels are introduced by this change. No judge is calibrated by this change. No acceptance thresholds are selected by this change.** Threshold values in tests are synthetic fixtures used only to verify gate behavior.

## Why v1 was insufficient for promotion

`semantic-calibration-policy-v1` stored threshold values and a policy ID, but it did not prove that:

- the policy was frozen before outcomes were inspected;
- the exact threshold set had not changed while keeping the same policy ID;
- the human references came from the intended held-out `VALIDATION` split;
- the references were bound to the exact frozen benchmark manifest and reviewer packet.

That means a policy object could theoretically be supplied after observing results and still produce `CALIBRATED_GATE`. The v1 metric implementation remains useful for descriptive analysis, but it is not sufficient evidence for promotion.

## Frozen v2 protocol

`SemanticCalibrationProtocol` requires, with no threshold defaults:

- `status = FROZEN`;
- a protocol ID;
- `purpose = HELD_OUT_CALIBRATION`;
- `source_split = VALIDATION`;
- the frozen semantic rubric SHA-256;
- the frozen benchmark split SHA-256;
- minimum pairs per semantic dimension;
- minimum exact agreement;
- minimum quadratic weighted kappa;
- maximum mean absolute error;
- maximum false-pass rate;
- maximum invalid-judge rate.

The canonical SHA-256 of the entire protocol is recorded in the v2 result. Changing any threshold changes the protocol hash even if the human-readable protocol ID is reused.

## Held-out evidence binding

A complete human resolution of a `HELD_OUT_CALIBRATION` packet can be converted into `semantic-calibration-evidence-v2` only when:

- the reviewer packet and evaluator-private manifest have the same packet ID;
- the manifest source split is `VALIDATION`;
- the packet rubric is the frozen rubric;
- all reviewer tasks are fully resolved by two independent reviewers or distinct third-party adjudication;
- the reviewer task bindings match the evaluator-private manifest;
- the complete resolved human-reference key set exactly matches the task set.

The evidence manifest binds task ID, scenario, output hash, sanitized-context hash, response mode and semantic dimension, plus the frozen split and rubric hashes. It contains no reviewer identity, raw prompt, raw provider response, private truth or chain of thought.

## Promotion rule

The only promotion-authorizing path is:

`frozen v2 protocol + hash-bound held-out VALIDATION evidence + adjudicated human references + matching judge observations -> frozen v2 calibration report`

A gate can be authorized only when:

1. protocol rubric hash matches the current frozen rubric;
2. evidence rubric hash matches the protocol;
3. evidence frozen-split hash matches the protocol;
4. the complete human-reference key set matches the evidence manifest exactly;
5. the underlying calibration dataset has no structural integrity failure;
6. every preregistered acceptance threshold passes.

Any binding mismatch fails closed and cannot authorize promotion.

## Legacy policy boundary

`scripts/semantic_eval_calibrate.py --policy ...` may still evaluate a v1 policy for comparison, but its output is forcibly demoted to `DESCRIPTIVE_ONLY` with `LEGACY_V1_POLICY_NOT_GATE_AUTHORIZED`.

For an actual gate, the CLI requires both:

- `--protocol <semantic-calibration-protocol-v2.json>`
- `--evidence-manifest <semantic-calibration-evidence-v2.json>`

`--require-calibrated-gate` exits nonzero unless that frozen v2 path authorizes the gate.

## LOCKED_TEST boundary

`LOCKED_TEST` remains unavailable to the human-calibration packet builder before final evaluation. The v2 protocol and evidence schemas additionally constrain the promotion path to `HELD_OUT_CALIBRATION` on `VALIDATION`. `LOCKED_TEST` must not be used to tune rubrics, thresholds, judge prompts, judge models, architecture or evaluator policy.

## What remains human work

After this slice is promoted, the next blocking evidence is real human annotation:

1. prepare the held-out `VALIDATION` reviewer packet;
2. collect two independent labels for every task;
3. adjudicate disagreements with a distinct third reviewer;
4. inspect inter-rater reliability;
5. freeze the acceptance protocol before judge outcomes used for gating are inspected;
6. run the candidate judge on the exact bound evidence;
7. evaluate the frozen gate.

Until those measurements exist, semantic evaluator status remains unproven and no quality or business-value claim should be made.
