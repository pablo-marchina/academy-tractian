# Post-Freeze Execution Backlog — Active Research Gate

Status: **E0/E1 frozen; E2–E8 infrastructure/runtime research complete enough for the active agent-quality loop; E9 v4.1/v4.2 evaluator stack frozen; full DEV 5/5 coverage active; E14q2 safety PASS; E14r evidence replacement FAIL; E14s evidence consensus READY**

Checkpoint: **2026-08-19 16:34 BRT**

This file is the active execution backlog. Older research files remain historical evidence and must not be interpreted as the current gate when they conflict with this checkpoint.

## Non-negotiable experiment boundaries

- [x] DEV is the only development/tuning split.
- [x] VALIDATION is measurement-only.
- [x] LOCKED_TEST is final-only.
- [x] Private expected paths remain evaluator-side only.
- [x] Raw fixed outputs, scorer rows, semantic rows, private paths and output hashes are not committed.
- [x] Real semantic-judge labels are not candidate-tuning data.
- [x] Attempt locks / no-rerun rules remain binding.
- [x] Final architecture remains unfrozen.

## Stable evaluated stack components

The current candidate lineage uses:

- model candidate: `openai/gpt-oss-120b`;
- reasoning: medium;
- strict JSON output;
- fixed full-DEV coverage: 5 groups, 10 calls, 2 repeats/group;
- E14n v1.1 public identifier-provenance guard;
- E14p deterministic epistemic serializer;
- E14q + E14q2 deterministic action/escalation authorization consistency;
- E9 v4.1 deterministic quality/safety evaluator;
- E9 v4.2 semantic-groundedness protocol;
- independent judge: `qwen/qwen3.6-27b`, already qualified on the frozen public synthetic suite.

The next evidence intervention may replace only `evidence_plan`; all other accepted fields must remain fixed.

## Evaluator status

### E9 v4.1 — frozen measurement-only

Current semantics:

- exact runner-selected visible-ticket alignment;
- no group-union fallback;
- exact canonical METHOD+path normalization;
- evidence credit from `evidence_plan` only;
- action/decision/escalation scored separately;
- leakage scan over string values only;
- PASS requires every fixed call to be parsed, aligned, normalized and scoreable.

### E9 v4.2 — frozen semantic protocol

Current semantics:

- claim sources: `evidence_plan[]`, `proposed_next_step`, `risk_notes`, `calibration_reason`;
- every factual assertion must be supported by the visible packet or public static contract;
- non-factual procedural/uncertainty/metadata claims must be `NOT_APPLICABLE`;
- the candidate model is not its own semantic judge;
- semantic PASS cannot rescue deterministic quality/safety FAIL.

Independent judge reliability is already PASS and remains frozen.

## Full-DEV coverage status

- [x] 5 / 5 DEV groups covered.
- [x] 8 / 8 DEV scenarios represented.
- [x] contextualize modality included.
- [x] 10 / 10 fixed calls captured.
- [x] 2 repeats per group.
- [x] VALIDATION not used during this full-DEV development loop.
- [x] LOCKED_TEST not accessed.

Coverage is no longer the blocker.

## Candidate history relevant to the active gate

### E14o — rejected

Prompt-only public factual-grounding discipline failed the semantic target on representative DEV:

```text
factual assertions:        4
supported:                 2
not supported:             2
factual groundedness:    0.5
semantic gate:          FAIL
```

### E14p — semantic layer PASS, full candidate rejected

Representative semantic measurement:

```text
126 / 126 claims
0 factual assertions
semantic groundedness 1.0
PASS
```

Full-DEV semantic measurement:

```text
206 / 206 claims
0 factual assertions
semantic groundedness 1.0
PASS
```

But full-DEV v4.1 rejected the candidate because:

```text
evidence_correctness                    0.2000
mean_expected_read_recall               0.7667
premature_action_rate                   0.1000
unsupported_action_or_escalation_rate   0.1000
```

E14p remains useful as a deterministic serialization layer, not as evidence that model reasoning improved.

### E14q — partial safety pass

```text
decision_correctness                    0.7000
action_correctness                      0.8000
escalation_correctness                  0.7000
premature_action_rate                   0.0000
unsupported_action_or_escalation_rate   0.1000
```

### E14q2 — current accepted safety/action base

```text
reference_quality                       0.8000
decision_correctness                    0.8000
evidence_correctness                    0.2000
mean_expected_read_recall               0.7667
mean_extra_public_read_count            3.5000
action_correctness                      0.8000
escalation_correctness                  0.8000
premature_action_rate                   0.0000
unsupported_action_or_escalation_rate   0.0000
leakage                                 0.0000
```

- [x] safety/action target PASS.
- [x] evidence unchanged by design.
- [x] semantic packet/judge not rerun because v4.2 claim-source fields were unchanged.

E14q2 is the fixed parent for the active evidence-selection experiments.

### E14r — rejected evidence replacement

E14r replaced the broad evidence plan with public visible-case cue routing.

Aggregate transform:

```text
reads before   63
reads after    34
added          13
removed        42
```

Aggregate v4.1:

```text
evidence_correctness          0.0000
mean_expected_read_recall     0.4000
mean_extra_public_read_count  2.0000
```

Decision/action/escalation stayed `0.8 / 0.8 / 0.8`; safety stayed `0 / 0`.

- [x] E14r rejected from aggregate-only result.
- [x] no private row inspection.
- [x] no group/ticket failure inference.
- [x] 114-claim packet built for characterization only.
- [x] semantic judge not run on E14r.

Interpretation: sparse public cue replacement over-pruned useful evidence.

## Active experiment — E14s

Experiment:

```text
E14s-full-DEV-public-evidence-candidate-pool-consensus
```

Status:

```text
preregistered before transform: true
structural CI: PASS
CI run: 32285078034
real transform consumed: false
```

### Intervention

Single intervention class: deterministic evidence selection only.

Inputs allowed:

- fixed E14q2 evidence plan;
- exact runner-selected visible case;
- public tool registry;
- public action state;
- E14r deterministic selector as an independent public candidate source.

Forbidden:

- private expected paths;
- private scorer rows;
- per-row evaluator labels;
- semantic judge rows;
- VALIDATION feedback;
- LOCKED_TEST;
- group/ticket-specific evidence rules;
- split `coverage_tags` as route-selection features.

### Frozen E14s selection policy

Candidate pool = union of:

1. canonical reads already proposed by fixed E14q2;
2. reads proposed by the deterministic E14r public selector.

Priority:

1. active action authorization / target-dependency reads;
2. consensus reads appearing in both sources;
3. remaining E14r deterministic reads;
4. remaining original E14q2 reads in original order.

Cap:

```text
6 reads per call
```

No read outside the public candidate pool may be synthesized.

### Frozen E14s gate

```text
fixed calls                              = 10
scoreable calls                          = 10
evidence_correctness                    >= 0.5000
mean_expected_read_recall               >= 0.8333
mean_extra_public_read_count            <= 3.5000
decision_correctness                    = 0.8000
action_correctness                      = 0.8000
escalation_correctness                  = 0.8000
premature_action_rate                   = 0.0000
unsupported_action_or_escalation_rate   = 0.0000
locked_test_or_gold_leakage_rate        = 0.0000
```

## Immediate execution backlog

### E14s deterministic phase

- [ ] Apply E14s once to the same fixed E14q2 full-DEV outputs.
- [ ] Require 10 / 10 parsed outputs.
- [ ] Require zero non-evidence-field changes.
- [ ] Require zero route-contract failures.
- [ ] Require selected-read cap compliance on all calls.
- [ ] Run public surface audit.
- [ ] Require zero concrete provenance violations.
- [ ] Run frozen E9 v4.1 once.
- [ ] Compare only the aggregate to the preregistered E14s gate.
- [ ] Do not inspect private rows.
- [ ] Build a fresh E9 v4.2 packet because `evidence_plan` changes.
- [ ] Record only aggregate packet shape.
- [ ] Stop before semantic judge.

### If E14s deterministic gate fails

- [ ] Record sanitized aggregate failure.
- [ ] Mark E14s rejected.
- [ ] Do not use private rows, groups or ticket identities to redesign the candidate.
- [ ] Do not run semantic judge for candidate promotion.
- [ ] Do not use VALIDATION.
- [ ] Preregister the next DEV-only evidence intervention from public invariants + aggregates only.

### If E14s deterministic gate passes

- [ ] Freeze exact new v4.2 packet shape before semantic labels.
- [ ] Reuse the same qualified Qwen judge and frozen system prompt/settings.
- [ ] Create a dedicated attempt lock.
- [ ] Run exactly one full-DEV semantic judge attempt.
- [ ] Require full claim coverage.
- [ ] Require semantic groundedness PASS.
- [ ] Keep VALIDATION blocked until semantic aggregation completes.

## Promotion plan after full DEV

### Full DEV deterministic + semantic PASS

- [ ] Freeze candidate stack for VALIDATION.
- [ ] Preregister VALIDATION measurement-only transport and thresholds.
- [ ] Measure the two frozen VALIDATION groups / three scenarios.
- [ ] Do not tune from validation feedback.
- [ ] Apply the same deterministic quality/safety/leakage gates.
- [ ] Apply the same semantic-groundedness protocol.

### VALIDATION PASS

- [ ] Freeze candidate policy/post-processing stack.
- [ ] Integrate into production-shaped runtime without changing evaluated semantics.
- [ ] Verify live API, transport, retry, trace, error handling and observability paths.
- [ ] If integration changes evaluated semantics, return to DEV before final evaluation.
- [ ] Freeze final architecture.
- [ ] Freeze final evaluation artifact.

### Final evaluation

- [ ] Preregister LOCKED_TEST final measurement.
- [ ] Execute LOCKED_TEST once.
- [ ] Do not rerun or repair based on LOCKED_TEST results.
- [ ] Record final metrics, limitations and failures.
- [ ] Finalize README and system architecture documentation.
- [ ] Finalize experiment report.
- [ ] Prepare demo/presentation from the frozen evaluated system.

## Gate sequence

```text
E14s deterministic full-DEV gate
          ↓
full-DEV semantic gate
          ↓
VALIDATION measurement-only
          ↓
candidate + architecture freeze
          ↓
LOCKED_TEST final-only
          ↓
final docs / demo / presentation
```

## Current decision

**Do not run VALIDATION. Do not run LOCKED_TEST. Do not freeze final architecture.**

The only authorized next quality action is the preregistered E14s full-DEV deterministic evidence-selection measurement over the same fixed E14q2 outputs.
