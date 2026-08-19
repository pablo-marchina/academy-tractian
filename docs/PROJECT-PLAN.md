# Academy × TRACTIAN — Project Action Plan

**Status:** full-DEV safety/authorization gate closed; evidence-reasoning gate active at E14u  
**Planning date:** 2026-08-19  
**Progress checkpoint:** 2026-08-19 17:45 BRT  
**Target final delivery:** 2026-09-08

## Executive status

The project remains in the DEV-only research loop. VALIDATION is still measurement-only and blocked; LOCKED_TEST remains untouched/final-only; final architecture is not frozen.

Stable foundations:

- E9 v4.1 deterministic evaluator frozen and structurally valid.
- E9 v4.2 semantic-groundedness protocol frozen.
- Independent semantic judge `qwen/qwen3.6-27b` qualified on the frozen synthetic suite.
- Full DEV coverage complete: 5/5 groups, 8/8 scenarios, 10 fixed calls, 2 repeats/group, contextualize included.
- E14n v1.1 identifier-provenance guard retained.
- E14p deterministic epistemic serializer retained; full-DEV semantic groundedness passed on 206/206 claims with zero factual assertions.
- E14q2 closed deterministic safety/action authorization on full DEV: decision/action/escalation `0.8/0.8/0.8`, premature `0`, unsupported `0`, leakage `0`.

The only unresolved DEV blocker is **evidence completeness/selection**.

## Evidence-gate history

Frozen target:

```text
evidence_correctness                    >= 0.5000
mean_expected_read_recall               >= 0.8333
mean_extra_public_read_count            <= 3.5000
```

Accepted E14q2 baseline:

```text
evidence_correctness                    0.2000
mean_expected_read_recall               0.7667
mean_extra_public_read_count            3.5000
```

### E14r — FAIL

Visible-case replacement over-pruned evidence:

```text
public reads                            34
evidence_correctness                    0.0000
mean_expected_read_recall               0.4000
mean_extra_public_read_count            2.0000
```

### E14s — FAIL

Candidate-pool consensus with cap 6:

```text
public reads                            59
evidence_correctness                    0.2000
mean_expected_read_recall               0.7750
mean_extra_public_read_count            3.1000
```

Directionally useful but below the frozen evidence gate. Its 139-claim semantic packet is characterization-only; no semantic judge was called.

### E14t — FAIL, strongest deterministic evidence result so far

Bounded restoration added exactly four public reads to the E14s selection while preserving all non-evidence fields:

```text
public reads                            63
evidence_correctness                    0.3000
mean_expected_read_recall               0.8000
mean_extra_public_read_count            3.4000
reference_quality                       0.8143
decision_correctness                    0.8000
action_correctness                      0.8000
escalation_correctness                  0.8000
premature_action_rate                   0.0000
unsupported_action_or_escalation_rate   0.0000
leakage                                 0.0000
```

The E14t v4.2 packet has 143 claims and is characterization-only; no semantic judge was called because deterministic v4.1 failed.

E9 v4.1 defines `evidence_correct` per call as `evidence_recall == 1.0`. Therefore E14t at `0.3` means 3/10 calls are complete. With only 0.1 mean extra-read headroom, a pure-addition strategy can add at most one read globally if it wants a worst-case guarantee of staying under 3.5. One read can complete at most one additional call, so pure expansion cannot reach 5/10. The project must improve **evidence reasoning/selection**, not volume.

## Active experiment — E14u

E14u is a new prompt-only evidence-decomposition intervention over the exact frozen E14o full-DEV generation stack.

Structural CI: **PASS** (`32300192016`).

Frozen generation configuration:

```text
model                       openai/gpt-oss-120b
reasoning                   medium
temperature                 0
strict JSON                 true
max completion tokens       4096
DEV groups                  5
repeats/group               2
fixed calls                 10
VALIDATION                   forbidden
LOCKED_TEST                  forbidden
```

Single intervention class:

```text
public_evidence_decomposition_system_prompt_only
```

Prompt goals:

- decompose the visible task into concrete unknowns before selecting reads;
- choose the smallest complete public GET set rather than a generic checklist;
- emit exactly one canonical GET per evidence item;
- include `GET /models/{modelId}` when model state/drift/performance/retraining is materially implicated;
- select baseline/data-quality/RMS/spectrum/knowledge/users reads only when their public dependency is material;
- preserve existing decision/action/escalation calibration rules;
- prefer 4–6 distinct reads, allow a seventh only for a distinct dependency, never exceed 7;
- never use private expected paths, scorer labels, VALIDATION feedback or LOCKED_TEST.

The existing E10b public evidence hint list omitted `GET /models/{modelId}` despite the public tool registry and action policy supporting model retraining; E14u fixes that public-contract inconsistency without using private evaluation rows.

## Fixed post-generation stack

If the single E14u generation capture completes, apply unchanged:

1. E14n v1.1 identifier-provenance guard.
2. E14p epistemic serializer.
3. E14q action-authorization consistency guard.
4. E14q2 route-role-purpose consistency guard.
5. Public surface audit.
6. Frozen E9 v4.1 once.
7. Build v4.2 claim packet.
8. Only if deterministic full-DEV passes: preregister exact packet shape, then one semantic measurement.
9. Only if deterministic + semantic full-DEV pass: VALIDATION measurement-only.
10. LOCKED_TEST final-only.

## Current action checklist

- [x] Freeze E9 v4.1 evaluator semantics.
- [x] Freeze E9 v4.2 semantic protocol and qualify independent judge.
- [x] Complete 5/5 full-DEV coverage.
- [x] Validate E14p semantic serializer on full DEV.
- [x] Close safety/action blocker with E14q2.
- [x] Reject E14r from aggregate-only evidence.
- [x] Reject E14s from aggregate-only evidence.
- [x] Reject E14t from aggregate-only evidence.
- [x] Record mathematical upper bound showing pure-addition cannot satisfy evidence correctness target.
- [x] Preregister E14u prompt-only evidence decomposition.
- [x] Implement E14u runner and public self-check.
- [x] Pass E14u structural CI.
- [ ] Run the single authorized E14u full-DEV generation capture.
- [ ] Apply unchanged E14n → E14p → E14q → E14q2 stack.
- [ ] Run full-DEV surface + E9 v4.1.
- [ ] Build new semantic packet.
- [ ] Keep VALIDATION blocked until deterministic + semantic full-DEV pass.
- [ ] Keep final architecture unfrozen.
- [ ] Keep LOCKED_TEST untouched until final evaluation.

## Non-negotiable boundaries

- No tuning on VALIDATION.
- No LOCKED_TEST access before final evaluation.
- No private expected paths or scorer rows in model prompts or candidate logic.
- No per-row private-label inspection for E14u design or follow-up.
- No semantic-judge labels used as candidate-tuning data.
- One real E14u generation runner invocation only; attempt lock is consumed before provider execution and rerun requires an explicit amendment.
- No provider/model substitution without explicit preregistration amendment.
- No integration/demo/final architecture freeze until the current full-DEV gate closes.
