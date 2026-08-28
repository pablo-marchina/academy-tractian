# Progress 030 — EV-008 repeated-run stability freeze

**Date:** 2026-08-28 05:07 BRT  
**Status:** COMPLETE / MERGED / RECONCILED BY THIS FOLLOW-UP  
**Issue:** #51  
**Implementation PR:** #52  
**Merge:** `d8c08ae532b11a5b7cecd4be08f8740c66905657`  
**ADR:** `docs/adr/014-provider-free-repeated-run-stability-2026-08-28.md`

## Outcome

EV-008 is frozen as deterministic provider-free repeated-run reproducibility evidence over the accepted production/controller/action/evaluator boundaries.

Exact result:

```text
campaign version                     ev008-provider-free-stability-campaign-v1
report SHA-256                        1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8
stability units                       6
repetitions per unit                  5
provider-free runs                   30 / 30
stable units                          6 / 6
stable dimension checks              66 / 66
contract expectations                30 / 30
raw sensitive leaks                   0
automatic retries                     0
replays                               0
provider calls                        0
real customer mutations               0
```

The six frozen units cover read/investigate, clarify, abstain, escalate, controlled accepted action, and deterministic safe read-transport failure. STAB-05 uses a fresh claim root for each repetition while preserving equivalent action fingerprint/authorization/idempotency semantics.

## Stability dimensions

Each unit freezes independent checks for:

1. terminal signature;
2. tool selection;
3. canonical arguments;
4. action fingerprint;
5. policy outcomes;
6. evaluator classification;
7. reason code;
8. normalized behavioral trace;
9. final response;
10. sensitive leak count;
11. retry/replay count.

Only per-execution top-level run/scenario identity is normalized away. Behavioral fields remain in the signatures, and deliberate tamper tests prove instability detection.

## Falsification preserved

The first dedicated-validator attempt on head `a404cd9efca635c8d4740a5a7479ca610e4bf24c` failed before campaign execution because direct script execution lacked the checkout root on `sys.path`. The validator bootstrap was corrected without changing population, metrics, repetition count, normalization or expected semantics.

Corrected head `a88b98e53e2767a5f85290082896f3c9b4d93cd4` produced the canonical report SHA. Final freeze head `4e586e657ca789ac29de4e4e3e271667038e603e` then reproduced it exactly.

Final validation:

```text
ev008-repeated-run-stability #6      PASS
production-runtime #67                199 passed
ADR-004 controller regression          12 passed
triggered workflows                   12 / 12 success
freeze self-check                     PASS
exact 30-run reproduction             PASS
```

## Boundary retained

```text
ADR-009 live calls consumed           0 / 32
credential/account probes             0
provider selected                     NO
real customer mutations               0
default ProductionRuntime actions     DISABLED
scientific gate                       REQUIRED_PER_GROUP_AND_SLICE_REPORTING
semantic/private/blind access         NO
production-readiness claim            NOT AUTHORIZED
```

EV-008 establishes provider-free runtime/harness/evaluator reproducibility only. It does not establish live-model stability or provider quality.

## Next

The next unblocked provider-free P0/P1 task is **EV-011 customer-safe communication**. Freeze deterministic leakage, unsupported-success, uncertainty and handoff checks before interpretation. Issue #44 remains the parallel live provider task and must remain at 0 calls until both explicit secrets and one canonical durable custody root are provisioned. C4 remains parallel exact-artifact recovery only.
