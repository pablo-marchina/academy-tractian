# E14l historical rescore under E9 v4.1

**Date:** 2026-08-18  
**Scope:** historical fixed DEV capture only  
**Candidate generation:** unchanged; no new model/provider call  
**Evaluator:** E9 v4.1 measurement-only  
**Status:** structurally complete historical rescore

## Structural validity

The fixed E14l capture was the original complete real capture:

```text
capture status:                    E14L_DEV_ONLY_120B_MEDIUM_REASONING_STRICT_4096_CAPTURE_PASS
fixed calls consumed:              6
parsed model outputs:              6
fixed groups:                      3
runner-selected visible cases:     3
private ticket-aligned oracles:    3
calls with matching oracle:        6
scoreable calls:                   6
normalization resolved:            true
complete fixed measurement:        true
validation gate authorized:        false
```

This is the first E14l v4-family rescore that is structurally eligible for interpretation. The earlier v4 rescore (4/6 scoreable, normalization unresolved, false leakage rate 1.0) is retained only as an evaluator-bug diagnostic and is not quality evidence.

## Aggregate-only v4.1 measurement

```text
reference_quality:                         0.7381
decision_correctness:                      0.6667
evidence_correctness:                      0.1667
mean_expected_read_recall:                 0.7222
mean_extra_public_read_count:              3.8333
action_correctness:                        0.6667
escalation_correctness:                    0.6667
premature_action_rate:                     0.0000
unsupported_action_or_escalation_rate:     0.0000
locked_test_or_gold_leakage_rate:           0.0000
general_free_text_groundedness:            UNMEASURED
```

No private rows, expected-path text, ticket/group labels, endpoint identities, hashes or raw model outputs are recorded here.

## Comparison with historical E9 v3

The same fixed E14l model outputs previously received under E9 v3:

```text
real_task_quality:             0.6190
decision_correctness:          0.3333
evidence_correctness:          1.0000
action_correctness:            0.0000
escalation_correctness:        0.0000
premature_action_rate:         0.0000
unsupported_final_claim_rate:  0.0000
```

The v4.1 remeasurement shows that v3 distorted different dimensions in opposite directions:

- action/escalation were materially under-credited by the lexical v3 semantics;
- evidence was materially over-credited by v3's broader text/asset-union behavior;
- the v4.1 composite reference score is higher, but it is **not** a final real-task gate because free-text groundedness remains explicitly unmeasured.

This is an evaluator correction, not a model improvement. The candidate and fixed outputs did not change.

## Evidence-planning interpretation

Two aggregate observations can be made without inferring any private per-call labels:

1. mean expected-read recall is `0.7222`, so the outputs often cover a substantial fraction of the ticket-aligned expected read set;
2. exact evidence correctness is only `0.1667`, while mean extra public reads are `3.8333` per call.

Therefore the historical E14l evidence behavior is not well described as simply "too little evidence." It is better described as **broad but insufficiently targeted evidence planning**: many public reads are proposed, yet complete coverage of the ticket-aligned required set is uncommon.

This aggregate interpretation must not be converted into hidden group/ticket-specific tuning.

## Gate consequence

- E14l does **not** pass a final task-quality gate.
- E9 v4.1 remains measurement-only.
- General free-text groundedness remains unresolved.
- Historical representative DEV covers only 3/5 DEV groups.
- VALIDATION remains blocked.
- LOCKED_TEST remains untouched/final-only.

Any next candidate must be motivated from public output behavior and aggregate methodology only, not private scorer rows or inferred hidden failures.
