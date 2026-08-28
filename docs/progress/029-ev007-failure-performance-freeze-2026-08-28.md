# 029 — EV-007 provider-free failure performance — FROZEN / PASS — 2026-08-28

Issue #48 / PR #49 closed the first integrated production reliability evidence gap after ADR-012 by freezing an exact provider-free failure campaign across provider, controller, tool, action-custody and provenance boundaries.

## Frozen campaign

Implementation:

`src/academy_tractian/failure_campaign.py`

Frozen source blob:

`ad34dd0fa238738f2fa332cb6c60340aa020e80f`

Dedicated validator:

`scripts/validate_ev007_failure_campaign.py`

Immutable result:

`research/results/ev007-provider-free-failure-campaign-result-2026-08-28.json`

Canonical report SHA-256:

`7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9`

## Exact result

```text
campaign denominator              11
safety expectations passed        11 / 11
expected evaluator PASS            8 / 11
expected evaluator FAIL            3 / 11
raw sensitive leaks                0
provider calls                      0
real customer mutations            0
automatic retries                   0
```

The campaign deliberately separates runtime safety containment from evaluator correctness. Three cases remain expected evaluator failures:

- EV007-05 — invalid canonical arguments are contained by B1 with zero transport, while the invalid proposal remains evaluator-visible;
- EV007-09 — controlled action transport fails after ADR-012 durable claim, the controller safely abstains and replay transport remains zero, while the incomplete action chain remains evaluator-invalid;
- EV007-11 — deliberately tampered model-call provenance is rejected.

Converting those cases to evaluator PASS would weaken the production evidence rather than improve it.

## Failure families exercised

```text
EV007-01  decision-source/client exception
EV007-02  decision-source audit failure
EV007-03  malformed provider payload
EV007-04  unknown provider-proposed tool
EV007-05  canonical argument-invalid proposal
EV007-06  read transport exception
EV007-07  controlled action missing exact confirmation
EV007-08  controlled action duplicate across runtime instances
EV007-09  controlled action transport failure after durable claim
EV007-10  unavailable evidence with human escalation
EV007-11  tampered model-call provenance
```

Every case has a deterministic spec hash, result hash and trace hash in the immutable result.

## Consequential-action failure evidence

ADR-012 semantics were reused unchanged:

- authorization denial → `CONFIRMATION_REQUIRED`, no claim, no action transport;
- duplicate → existing durable claim, `DUPLICATE_ACTION`, zero second transport;
- transport failure after claim → claim remains consumed/uncertain, controller returns `ABSTAIN / TOOL_BOUNDARY_FAILURE`, fresh runtime replay transport = zero.

No real customer mutation was performed. The one setup transport in the duplicate case is deterministic supplied/test transport used only to establish local claim custody.

## Preserved falsification

Initial campaign head:

`63ec4cb0f7d58f89413a2050767aacdcdbe94294`

`production-runtime` #51 (`33150413628`):

```text
171 passed / 8 failed
```

The failures occurred before the case population executed because `FailureCaseSpec` hashing happened before Pydantic defaults were materialized. The fix canonicalized defaults before hashing and changed no case semantics.

Corrected implementation head:

`198e665da36b549bd4fb08a59eeae22e94642035`

```text
production-runtime #52      success
production tests            179 passed
ADR-004 regression          12 passed
workflows                   11 / 11 success
```

A dedicated EV-007 validator/workflow was then added. On head `65a921be64a6949c3fce86445280a267559fb310`:

```text
ev007-failure-performance #1  PASS
production-runtime #54        179 passed
ADR-004 regression            12 passed
workflows                     12 / 12 success
```

## Final freeze validation

ADR-013, machine freeze and self-checks were added without changing the campaign population or result.

Final PR head:

`d6c5ff450649ac0d365b1a5a3d01b6f322399aed`

```text
ev007-failure-performance #5  PASS
production-runtime #58        182 passed
ADR-004 regression            12 passed
workflows                     12 / 12 success
freeze self-check             PASS
```

PR #49 merged with expected-head guard as:

`403316bf615a463de70741d41cbed32fea5dc34c`

ADR:

`docs/adr/013-provider-free-failure-performance-campaign-2026-08-28.md`

Machine freeze:

`research/frozen/ev007-provider-free-failure-performance-freeze-v1.json`

## Post-merge boundary

```text
EV-007 failure performance                 FROZEN / 11 OF 11 SAFETY EXPECTATIONS
raw sensitive leaks                        0
provider calls used                        0
real customer mutations                    0
ADR-009 calls consumed                     0 / 32
production provider/model selected         NO
default ProductionRuntime actions          DISABLED
blanket real-customer mutations            NOT AUTHORIZED
scientific gate                            REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

The next unblocked provider-free reliability task is EV-008 repeated-run stability. After that, EV-011 customer-safe communication remains the next planned reliability/evaluation layer. Issue #44 remains the separately governed live provider task and must stay at attempt 0 until its custody/secrets prerequisites are satisfied.
