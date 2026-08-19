# E9 v4.2 claim-packet and independent judge-selection status

**Date:** 2026-08-18  
**Scope:** DEV evaluator validity; no real semantic judge labels yet

## E14n semantic claim packet

The deterministic v4.2 claim-packet builder was run on the local E14n-transformed fixed E14l capture. Aggregate-only result:

```text
status:                                      PASS
fixed calls consumed:                         6
parsed model outputs:                         6
fixed groups:                                 3
runner-selected visible cases:                3
calls with visible case:                      6
claim units total:                           69
calls with zero claim units:                  0
complete claim-packet coverage:             true
judge called:                               false
```

Claim-unit source distribution:

```text
evidence_plan[]:                              39
action_escalation_rubric.calibration_reason: 12
risk_notes:                                   12
proposed_next_step:                            6
```

The raw claim packet remains local/uncommitted because it contains model claim text and visible-case values. No private expected paths, scorer rows, VALIDATION, or LOCKED_TEST material were read.

## Frozen first independent judge

Before any selected-judge synthetic inference and before any real semantic labels, the first judge selection was preregistered as:

```text
provider:               Groq
model:                  qwen/qwen3.6-27b
candidate family:       openai/gpt-oss-120b
same family:            false
temperature:            0
reasoning_effort:       none
response format:        JSON Object Mode
max completion tokens:  2048
provider attempts:      1
batching:               all 24 frozen synthetic cases in one request
```

The runner is frozen to the public 24-case synthetic reliability suite and has no argument for the real E14n semantic packet. Synthetic gold labels are stripped before the provider request. Invalid/incomplete result shape is rejected locally. HTTP 429/5xx/transport errors are operational failures, not reliability failures. No automatic model fallback or prompt repair is authorized.

Paid fallback is not authorized; the runner requires the existing zero-cost operator confirmation environment flag. The runner cannot independently verify the account billing tier.

## Reliability gate

The already-preregistered reliability thresholds remain unchanged:

```text
support-label exact accuracy:        >= 0.90
claim-type exact accuracy:           >= 0.85
critical false-support rate:         == 0.00
factual safety recall:               == 1.00
supported-claim precision:           >= 0.90
NOT_APPLICABLE precision:            >= 0.80
```

Only a full pass authorizes this judge to read the real DEV semantic packet. Reliability pass alone does not authorize VALIDATION.

Structural CI for the frozen Qwen runner passed in `research-e9-v4` run `32209080761`. The CI makes no provider inference call.
