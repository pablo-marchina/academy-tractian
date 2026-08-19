# E14t Full-DEV Bounded Evidence Restoration — Aggregate Result

Date: 2026-08-19

## Decision

**E14t FAILS the preregistered full-DEV evidence gate.**

The transform and public surface audit passed structurally, and the intervention improved evidence metrics while preserving the accepted decision/action/escalation and safety state. However, evidence correctness and mean expected-read recall remain below the frozen thresholds.

No private scorer row, private expected-path row, group/ticket failure identity, semantic-judge row, VALIDATION feedback, or LOCKED_TEST content was inspected or used to reach this decision.

## Deterministic transform aggregate

```text
fixed / parsed:                         10 / 10
E14s base reads:                        59
restoration candidate calls:             7
restoration reads added:                  4
calls with restoration:                   4
final public reads:                      63
max observed reads/call:                  7
non-evidence field changes:               0
route-contract failures:                  0
per-call addition failures:               0
candidate-pool failures:                  0
global-budget failures:                   0
provider calls:                            0
```

## Public surface audit

```text
assessed calls:                          10
complete surface coverage:             true
unsupported identifiers:                  0
unrecognized METHOD+path mentions:        0
unsupported unit numeric mentions:        0
false trace self-check flags:             0
concrete provenance violations:           0
```

The one-sided public surface audit does not establish general free-text groundedness.

## Frozen E9 v4.1 aggregate

```text
fixed / scoreable:                       10 / 10
reference_quality:                       0.8143
decision_correctness:                    0.8000
evidence_correctness:                    0.3000
mean_expected_read_recall:               0.8000
mean_extra_public_read_count:            3.4000
action_correctness:                      0.8000
escalation_correctness:                  0.8000
premature_action_rate:                   0.0000
unsupported_action_or_escalation_rate:   0.0000
locked/gold leakage rate:                0.0000
alignment resolved:                      true
normalization resolved:                  true
complete measurement:                    true
validation authorized:                   false
```

Frozen evidence thresholds:

```text
evidence_correctness                    >= 0.5000
mean_expected_read_recall               >= 0.8333
mean_extra_public_read_count            <= 3.5000
```

E14t therefore fails on `evidence_correctness` and `mean_expected_read_recall`.

## Semantic packet characterization

The post-E14t v4.2 claim packet was built but **no semantic judge was called** because deterministic v4.1 already failed.

```text
calls with visible case:                 10
claim units:                            143
zero-claim calls:                         0
calibration_reason claims:               40
evidence_plan claims:                    63
proposed_next_step claims:               11
risk_notes claims:                       29
complete packet coverage:              true
judge called:                          false
```

The 143-claim packet is characterization-only and cannot authorize VALIDATION.

## Aggregate-only interpretation

Compared with the accepted E14q2 evidence baseline and the rejected E14s candidate:

```text
                    E14q2    E14s    E14t
public reads          63       59      63
evidence correct     .20      .20     .30
mean recall          .7667    .7750   .8000
mean extras          3.50     3.10    3.40
```

Bounded restoration improved both recall and exact-call evidence correctness while remaining under the extra-read ceiling, but it did not close the full-DEV evidence gate.

The frozen evaluator defines `evidence_correct` per call as `evidence_recall == 1.0`. At E14t, `evidence_correctness = 0.3` means only 3/10 calls are complete. With only 0.1 mean extra-read headroom, a pure-addition intervention can add at most one read globally if it wants a worst-case guarantee of remaining at or below 3.5. One additional read can complete at most one additional call, so pure bounded addition cannot reach the required 5/10 evidence-correct calls. The next experiment must therefore change evidence selection/reasoning rather than simply expand the plan.

## Boundary

- E14t must not be rerun or tuned from private rows.
- No Qwen semantic measurement is authorized for E14t.
- VALIDATION remains blocked.
- LOCKED_TEST remains untouched.
- Next candidate design may use only public-contract facts and aggregate E14q2/E14r/E14s/E14t findings.
