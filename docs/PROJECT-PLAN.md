# Academy × TRACTIAN — Project Action Plan

**Status:** full-DEV safety/authorization gate closed; evidence-completeness gate still open; E14v-B synthetic qualification failed before route-quality could be established  
**Planning date:** 2026-08-19  
**Progress checkpoint:** 2026-08-20 23:03 BRT  
**Target final delivery:** 2026-09-08

## Executive status

The project remains in the DEV-only research loop. VALIDATION is measurement-only and blocked; LOCKED_TEST remains untouched/final-only; final architecture is not frozen.

Stable foundations:

- E9 v4.1 deterministic evaluator frozen and structurally valid.
- E9 v4.2 semantic-groundedness protocol frozen.
- Independent semantic judge `qwen/qwen3.6-27b` qualified on the frozen synthetic suite.
- Full DEV coverage complete: 5/5 groups, 8/8 scenarios, 10 fixed calls, 2 repeats/group, contextualize included.
- E14n v1.1 identifier-provenance guard retained.
- E14p deterministic epistemic serializer retained; its previously accepted full-DEV semantic run passed groundedness.
- E14q/E14q2 deterministic safety/action authorization guards retained.
- The E14u full-DEV stack remained safety-clean at decision/action/escalation `0.8/0.8/0.8`, premature `0`, unsupported `0`, leakage `0`.

The unresolved blocker remains **evidence completeness/selection**. No candidate has yet satisfied the frozen full-DEV evidence gate, and the isolated E14v planner has not yet completed a valid public synthetic qualification because all three authorized synthetic attempts have failed before route-quality could be established.

## Frozen evidence gate

```text
evidence_correctness                    >= 0.5000
mean_expected_read_recall               >= 0.8333
mean_extra_public_read_count            <= 3.5000
```

## Evidence-gate history

### E14q2 baseline

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

Directionally useful but below the frozen evidence gate. Its semantic packet was characterization-only; no semantic judge was called.

### E14t — FAIL, strongest deterministic evidence result so far

Bounded restoration added four public reads to the E14s selection while preserving all non-evidence fields:

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

E9 v4.1 defines `evidence_correct` per call as full expected-read recall. Therefore E14t at `0.3` means 3/10 calls are complete. With only 0.1 mean extra-read headroom, pure expansion cannot guarantee 5/10 complete calls. This established that the next intervention had to improve **evidence selection/reasoning**, not simply add reads.

### E14u — FAIL

E14u moved the intervention upstream into a public evidence-decomposition system prompt. The authorized generation completed 10/10 full-DEV calls, followed by the unchanged deterministic post-stack:

```text
E14u raw generation
→ E14n v1.1
→ E14p
→ E14q
→ E14q2
→ public surface audit
→ E9 v4.1 once
→ v4.2 claim packet
```

The deterministic safety surface remained clean, but the evidence blocker worsened:

```text
evidence_correctness                    0.1000
mean_expected_read_recall               0.7417
mean_extra_public_read_count            4.0000
decision_correctness                    0.8000
action_correctness                      0.8000
escalation_correctness                  0.8000
premature_action_rate                   0.0000
unsupported_action_or_escalation_rate   0.0000
leakage                                 0.0000
```

The E14u v4.2 packet contained 214 claims, including 134 evidence-plan claim units. Because frozen v4.1 failed, that packet is characterization-only and **no Qwen semantic measurement was run**.

Conclusion: whole-response prompt decomposition increased evidence-plan surface area without improving route selection. E14u is rejected.

## Active research line — E14v isolated public evidence-route planner

E14v separates evidence-route selection from whole-response generation. The planner outputs only canonical public GET routes and is qualified on a frozen public synthetic suite before any real DEV planner call is allowed.

Frozen scientific candidate:

```text
provider                    Groq free
model                       openai/gpt-oss-120b
reasoning effort            medium
temperature                 0
max completion tokens       1024
synthetic cases             14
max distinct reads          7
VALIDATION                   forbidden
LOCKED_TEST                  forbidden
```

The planner is forbidden from using private expected paths, private scorer rows, semantic judge labels, VALIDATION feedback, LOCKED_TEST, coverage tags, ticket-specific rules, or parent evidence-plan selections.

### E14v synthetic attempt #1 — operationally invalid

Structural CI passed before the attempt. The single authorized public synthetic run produced:

```text
synthetic rows                      14
rows with provider error            14
rows with valid route contract       0
provider error category       HTTPError
```

No route-quality conclusion was drawn and the attempt lock remains consumed.

### E14v-A synthetic attempt #2 — operationally invalid, HTTP 403

E14v-A was preregistered as a transport-contract-only amendment:

```text
response format        strict json_schema
include_reasoning      false
reasoning_format       not sent
```

Model, prompt, fixture, thresholds, route catalog, reasoning effort, temperature, retry policy and pacing remained unchanged.

Sanitized aggregate diagnostic:

```text
synthetic rows                      14
HTTP 403                            14
rows with provider error            14
rows with valid route contract       0
transport attempts / row             3
```

This was classified as **external provider permission/access denial**, not planner-quality failure. The E14v-A output and lock remain consumed and preserved.

### E14v-B synthetic attempt #3 — FAIL, transport diagnosis pending

After manual confirmation that `openai/gpt-oss-120b` was permitted at the relevant Groq organization/project layers, E14v-B was preregistered as a provider-permission-remediation-only continuation.

The wrapper reuses the E14v-A provider transport rather than reimplementing it. Final structural CI passed:

```text
workflow   research-e14v-b-provider-permission-remediation
run_id     32373474815
job_id     96439178694
conclusion success
```

The single authorized E14v-B synthetic attempt was then consumed and returned:

```text
status                              FAIL
synthetic cases                       14
valid_output_rate                 0.0000
route_recall                      0.0000
action_dependency_recall          0.0000
exact_set_match_rate              0.0000
mean_extra_reads                   0.0000
unknown_route_count                     0
duplicate_route_count                   0
read_cap_violations                     0
```

This aggregate alone does **not** establish planner-quality failure because no valid output reached route evaluation. The current required step is a local, provider-free sanitized transport diagnostic over the fixed E14v-B artifact, exposing only aggregate error category, HTTP status, transport-attempt distribution and route-contract validity.

No E14v-C or real DEV attempt is authorized yet.

## Current action checklist

### Foundations and evaluator

- [x] Freeze E9 v4.1 evaluator semantics.
- [x] Freeze E9 v4.2 semantic protocol.
- [x] Qualify independent Qwen semantic judge on frozen public synthetic suite.
- [x] Complete 5/5 full-DEV coverage.
- [x] Retain E14n v1.1 provenance guard.
- [x] Validate E14p serializer behavior.
- [x] Close deterministic safety/action guard stack with E14q/E14q2.

### Evidence-selection experiments

- [x] Reject E14r from aggregate-only evidence.
- [x] Reject E14s from aggregate-only evidence.
- [x] Reject E14t from aggregate-only evidence.
- [x] Record the upper-bound argument showing pure-addition cannot satisfy the evidence-correctness target under the extras budget.
- [x] Preregister and structurally qualify E14u.
- [x] Run the single authorized E14u 10-call full-DEV generation.
- [x] Apply unchanged E14n → E14p → E14q → E14q2 stack to E14u.
- [x] Run E14u public surface audit and E9 v4.1 once.
- [x] Build E14u v4.2 claim packet.
- [x] Reject E14u from aggregate-only v4.1 evidence; do not run Qwen.

### E14v isolated route planner

- [x] Preregister isolated public evidence-route planner.
- [x] Freeze 14-case public synthetic qualification suite and thresholds.
- [x] Pass E14v structural CI.
- [x] Consume E14v synthetic attempt #1; classify as operationally invalid.
- [x] Preregister E14v-A transport-only amendment.
- [x] Pass E14v-A structural CI.
- [x] Consume E14v-A synthetic attempt #2.
- [x] Diagnose E14v-A as 14/14 HTTP 403 provider-access denial.
- [x] Confirm Groq model permission remediation externally.
- [x] Preregister E14v-B provider-permission-remediation-only continuation.
- [x] Pass final E14v-B structural CI (`32373474815`).
- [x] Consume the single E14v-B synthetic attempt #3.
- [ ] Run the provider-free sanitized E14v-B transport diagnostic.
- [ ] Classify E14v-B as provider/transport failure versus valid-response contract/planner failure using aggregate-only diagnostics.
- [ ] If another operational amendment is justified, preregister it before any provider call; never silently rerun a consumed attempt.
- [ ] Authorize real E14v DEV only after a frozen public synthetic qualification passes.

### Gates after a valid E14v synthetic PASS

- [ ] Run exactly one real E14v DEV planner attempt over the fixed E14p parent.
- [ ] Reapply unchanged E14q → E14q2.
- [ ] Run public surface audit.
- [ ] Run frozen E9 v4.1 exactly once on the new fixed candidate.
- [ ] Build the new v4.2 claim packet.
- [ ] If deterministic full DEV passes, preregister the exact semantic packet shape before one qualified semantic measurement.
- [ ] If deterministic + semantic full DEV pass, authorize VALIDATION measurement-only.
- [ ] Keep final architecture unfrozen until the full-DEV gate closes.
- [ ] Keep LOCKED_TEST untouched until final evaluation.

## Decision tree from the current checkpoint

```text
E14v-B fixed synthetic artifact
            │
            ▼
provider-free sanitized transport diagnostic
            │
     ┌──────┴───────────────────────────────┐
     │                                      │
provider/transport error             valid provider responses
     │                                      │
     ▼                                      ▼
classify exact aggregate cause       assess output-contract/planner failure
     │                                      │
     ▼                                      ▼
explicit amendment only              reject/amend scientifically
(no silent rerun)                    without DEV/private-row inspection
     │                                      │
     └──────────────────┬───────────────────┘
                        │
                        ▼
             frozen synthetic PASS required
                        │
                        ▼
                one real DEV planner attempt
                        │
                        ▼
              E14q → E14q2 → surface
                        │
                        ▼
                    E9 v4.1
                        │
                ┌───────┴───────┐
                │               │
              FAIL             PASS
                │               │
          stay in DEV     build/preregister
                           semantic packet
                                │
                                ▼
                         one semantic measure
                                │
                         ┌──────┴──────┐
                         │             │
                       FAIL           PASS
                         │             │
                    stay in DEV   VALIDATION
                                  measurement-only
```

## Non-negotiable boundaries

- No tuning on VALIDATION.
- No LOCKED_TEST access before final evaluation.
- No private expected paths or private scorer rows in model prompts or candidate logic.
- No per-row private-label inspection to design E14u/E14v follow-ups.
- No semantic-judge labels used as candidate-tuning data.
- All consumed real-provider attempts retain their attempt locks; locks must never be deleted or bypassed.
- E14u full-DEV generation must never be rerun.
- E14v, E14v-A and E14v-B synthetic attempts must never be rerun under their consumed locks.
- Any new provider/model/transport/prompt/fixture/threshold change requires an explicit preregistration or amendment before provider execution.
- No real E14v DEV run before public synthetic qualification passes.
- No integration/demo/final architecture freeze until deterministic + semantic full-DEV gates close.
