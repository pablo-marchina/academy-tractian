# Human semantic calibration pipeline — 2026-09-03

## Decision ID

`SEM-HUMAN-001`

## Status

`IMPLEMENTED CONTRACT / NO HUMAN LABELS COLLECTED / NO JUDGE SELECTED / NO THRESHOLDS SELECTED`

## Purpose

Create the human reference layer required by #128 before any LLM-as-judge can influence EDD promotion. This slice does **not** fabricate labels, does not inspect LOCKED_TEST answers, does not select a judge provider/model, and does not choose acceptance thresholds.

The pipeline is deliberately split into:

```text
sanitized terminal outputs + sanitized evidence context
→ frozen split lookup
→ blind reviewer packet
→ independent pass A + pass B
→ disagreement adjudication by distinct third reviewer
→ resolved HumanSemanticReference records
→ later judge calibration
```

## Why this exists

The semantic evaluator contract in the parent slice can measure judge↔human agreement, but a valid calibration gate requires a human-labelled reference set built without leakage or post-hoc threshold fitting. Human annotation therefore needs its own reproducible data boundary and integrity checks.

A terminal answer cannot be judged independently from the evidence state. In particular, groundedness and operational usefulness can change when the evidence changes even if the final text is byte-for-byte identical. The pipeline therefore binds every review task and every final calibration reference to both the terminal-output hash and the sanitized evidence-context hash.

## Frozen split policy

The existing `research/frozen/benchmark-split-v1.json` remains authoritative.

- `PILOT` may use only `DEV` groups.
- `HELD_OUT_CALIBRATION` may use only `VALIDATION` groups.
- `LOCKED_TEST` is rejected by code before packet construction.
- split/group values are not accepted from the caller; they are derived from the frozen manifest by `scenario_id`.
- at least two distinct asset/story groups are required by default.

This preserves the existing rule that locked test is unavailable for threshold fitting, model selection, runtime selection, architecture ablation or optimizer feedback.

## Reviewer blindness boundary

Two artifacts are produced:

### Reviewer packet
Contains only:

- scenario id;
- hashed terminal-output identity;
- hashed sanitized-context identity;
- response mode;
- rubric dimension and score anchors;
- customer-visible terminal decision/message;
- explicitly sanitized evidence/context digest required to judge the answer.

It does **not** contain:

- DEV/VALIDATION group id;
- frozen split assignment;
- LOCKED_TEST metadata;
- gold/private truth;
- expected score;
- judge score;
- identity/seed;
- prompt or model reasoning;
- credentials.

### Evaluator-only annotation manifest
Contains the deterministic mapping from task id to frozen story group/split and the same immutable output/context identities. This is used for group-aware analysis later and is kept separate from the reviewer packet.

The implementation also rejects obvious forbidden evaluator/runtime material markers in supplied terminal/evidence text. This is a defense-in-depth guard, not a substitute for constructing the source from already-sanitized evaluation material.

## Output and context identity

The output hash is deterministic over the public terminal projection:

```text
output_sha256 = SHA256({terminal_decision, response_mode, terminal_message})
```

The context hash is deterministic over the reviewer-visible sanitized evidence/context:

```text
context_sha256 = SHA256({safe_evidence_context})
```

Each annotation task id binds:

```text
scenario_id
+ output_sha256
+ context_sha256
+ response_mode
+ rubric dimension
```

This is the same calibration identity used by the parent semantic evaluator. Two examples with identical terminal text but different evidence context are intentionally different tasks and cannot share a human or judge score.

## Rubric applicability

Every terminal output receives:

1. groundedness;
2. operational usefulness;
3. customer-safe clarity.

`escalation_quality` is added only when the terminal decision is `ESCALATE_HUMAN`.

The rubric text and SHA-256 come from the frozen semantic rubric in the parent contract; the human pipeline does not redefine it.

## Independent review contract

Each task has exactly two independent reviewer slots, `A` and `B`.

Reviewer artifacts store only a one-way `reviewer_ref_sha256`, not a human name/email. For a given task:

- A and B must have different reviewer references;
- a score below `2` must include at least one structured defect reason;
- score `2` may carry only `NO_MATERIAL_DEFECT`;
- agreeing scores produce `resolution=AGREED`, `annotator_count=2`;
- disagreeing scores produce **no human calibration reference** until adjudicated;
- adjudication is accepted only for a task that already has two complete, disagreeing A/B labels;
- adjudication must come from a third reviewer reference different from both A and B;
- resolved disagreement produces `resolution=ADJUDICATED`, `annotator_count=3`;
- an adjudication attached to an agreeing, incomplete or otherwise non-disputed task is rejected rather than silently ignored.

Missing labels or unresolved disagreement therefore keep `calibration_ready=false`.

## Human-human metrics

Before judge comparison, the resolution report exposes per rubric dimension:

- paired task count;
- exact agreement;
- adjacent agreement;
- quadratic-weighted Cohen's kappa;
- disagreement count.

Human disagreement is evidence about rubric ambiguity and cannot be hidden by later judge agreement.

## No acceptance thresholds in this slice

This pipeline intentionally does not define a minimum human-human kappa, judge↔human kappa, exact agreement threshold, false-pass threshold, or sample-size threshold for production gating.

Those values must be preregistered **after** pilot evidence is collected and before the held-out judge run. The valid sequence remains:

```text
DEV pilot labels
→ inspect rubric ambiguity / label distribution
→ freeze rubric + judge candidate set + acceptance policy
→ one held-out VALIDATION calibration
→ CALIBRATED_GATE | DESCRIPTIVE_ONLY
```

If the pilot shows that the current rubric cannot be labelled consistently, the rubric must be revised and versioned before any held-out calibration. No judge is promoted to compensate for a poor human rubric.

## CLI

Prepare a blind packet:

```bash
python scripts/semantic_human_calibration.py prepare \
  --sources <sanitized-source-array.json> \
  --split-manifest research/frozen/benchmark-split-v1.json \
  --purpose PILOT \
  --reviewer-packet <reviewer-packet.json> \
  --annotation-manifest <annotation-manifest.json>
```

Resolve human passes:

```bash
python scripts/semantic_human_calibration.py resolve \
  --reviewer-packet <reviewer-packet.json> \
  --annotation-manifest <annotation-manifest.json> \
  --labels <two-pass-labels.json> \
  --adjudications <adjudications.json> \
  --human-references <human-reference.json> \
  --resolution-report <human-resolution.json> \
  --require-complete
```

`--require-complete` exits non-zero while any task is unresolved.

## Hard gates

- LOCKED_TEST source accepted before final: `0`;
- task moved across frozen split/group: `0`;
- reviewer packet contains evaluator split/group metadata: `0`;
- same output with different sanitized context reuses a task/calibration identity: `0`;
- duplicate output+context/task identity: `0`;
- same reviewer fills both independent passes for one task: `0`;
- score below `2` without structured defect reason: `0`;
- disagreement silently converted into a calibration reference: `0`;
- adjudication accepted without two disagreeing reviewer scores: `0`;
- reviewer acts as own adjudicator: `0`;
- unresolved packet reported calibration-ready: `0`;
- judge/model/provider invocation in this slice: `0`;
- fabricated project human labels: `0`.

## Next evidence step

After the parent semantic-calibration contract and this pipeline are integrated, create sanitized DEV pilot outputs from real evaluation runs, collect independent human labels, and report the human-human agreement/error distribution. Only that evidence can justify freezing a judge-candidate experiment and acceptance policy for the VALIDATION holdout.
