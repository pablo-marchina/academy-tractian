# Progress 032 — ADR-016 provider-free final-delivery reproduction/evidence freeze

**Date:** 2026-08-28  
**Implementation PR:** #58  
**Issue:** #57  
**Implementation merge:** `b432ca9d5c32ffedcda2b26fc15959f3f4f415bd`

## What changed

The previously preregistered final-delivery provider-free work is complete and frozen under ADR-016.

The package now contains:

- one exact five-scenario integrated provider-free demo over the accepted production/controller/evaluator path;
- one immutable compact demo result manifest;
- one machine-readable evidence index that resolves repository-resident evidence by canonical path and Git blob;
- one clean-checkout workflow that reproduces production tests, ADR-004, EV-007, EV-008, EV-011 and the integrated demo;
- one deterministic delivery validator that cross-checks rerun results against the static manifest and evidence index;
- one machine-readable ADR-016 freeze and independent self-check.

## Frozen integrated result

```text
report SHA-256                       43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445
DEMO-01..05                          5 / 5
exact traces                         5 / 5
contract expectations                5 / 5
provider calls                       0
credential/account probes            0
real customer mutations              0
semantic/private/blind access        0
retries / replays                     0 / 0
```

DEMO-05 is only a controlled supplied/test action: exactly one local action transport plus one fresh durable local claim. It does not establish real-customer mutation authorization.

## Evidence index

```text
entries                              31
repository-resident entries          30
resolved exact Git blobs             30 / 30
external blockers                     1
violations                            0
```

The external item is the exact C4 score-row artifact, still unavailable and explicitly `EXTERNALLY_BLOCKED`. The provider comparison remains `UNEXECUTED_GATED` at 0/32 calls and no provider/model is selected.

## Preserved falsifications

Two implementation failures remain documented as evidence rather than being erased:

1. inferred ADR filenames caused the first evidence-index tests to fail while the demo itself already passed;
2. run `33158501340` failed `231 passed / 1 failed` because the checker incorrectly assumed every historical EV freeze used `result.path`; EV-008/011 instead bind the result file through `direct_blobs`.

Both fixes corrected evidence-resolution assumptions only. The five-scenario preregistration and frozen upstream result identities were unchanged.

## Final freeze validation

Final implementation head:

`e603a44a817c13bbd9b1784d50edbfb41f095501`

```text
final-delivery-provider-free-reproduction #10 / 33158898906  PASS
clean-checkout production tests                               237 passed
ADR-004 controller regression                                  12 passed
EV-007                                                          PASS
EV-008                                                          PASS
EV-011                                                          PASS
integrated final-delivery validator                            PASS
evidence index                                              30/30 / 0 violations
freeze self-check                                               PASS
all triggered workflows                                      12 / 12 success
```

The final demo report SHA reproduced exactly and every upstream report identity remained unchanged.

## Authorization state after freeze

Unchanged:

- scientific gate: `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`;
- exact C4 recovery only; reconstruction/rescoring/substitution forbidden;
- live provider calls: 0/32;
- provider/model selected: no;
- credential/account probes: 0;
- real customer mutations: 0;
- default `ProductionRuntime` actions: disabled;
- semantic/FRESH_BLIND/LEGACY_LOCKED_TEST: not authorized;
- global architecture: unfrozen;
- production-readiness claim: not authorized.

## Next

The highest-value unblocked P0/P1 work is now a final handoff acceptance audit and gap closure driven by `docs/DELIVERY-ACCEPTANCE.md`: classify every material requirement against exact evidence, close remaining unblocked README/setup/runbook/fallback/rollback/documentation gaps, produce a reviewer-friendly rubric-to-evidence crosswalk and run a final provider-free end-to-end regression before delivery.

Issue #44 and exact C4 recovery remain parallel external-prerequisite tracks.