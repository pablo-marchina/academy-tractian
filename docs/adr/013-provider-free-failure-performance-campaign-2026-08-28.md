# ADR-013 — Provider-free failure-performance campaign

**Status:** ACCEPTED  
**Decision state:** `FROZEN_FOR_PROVIDER_FREE_FAILURE_PERFORMANCE_CAMPAIGN`  
**Date:** 2026-08-28  
**Issue:** #48  
**PR:** #49  
**Scientific state changed:** NO  
**Production provider/model selected:** NO  
**ADR-009 live provider calls consumed by this decision:** 0  
**Real customer mutations performed by this decision:** 0

## Decision question

Can the integrated production Agent + Evaluator path demonstrate deterministic, inspectable and fail-closed behavior across representative provider, controller, tool-boundary, action-custody and provenance failures without consuming a live provider call or mutating a real customer environment?

## Context

ADR-004 through ADR-012 froze the controller, action safety, provider-neutral decision source, model-call provenance, live comparison design/executor/custody and controlled consequential-action profile. Those decisions prove individual boundaries, but the delivery still needs cross-boundary failure evidence.

A failure campaign must not merely assert that exceptions are caught. It must preserve the distinction between:

- a failure that is safely contained by the runtime; and
- a trace that the evaluator should accept as structurally/correctly behaved.

Those are not equivalent. In particular, a malformed proposal may be safely blocked while still being evidence of an invalid agent proposal, and a transport failure after a durable action claim may be safely abstained while still leaving an incomplete action execution chain that the controlled evaluator should reject.

EV-007 therefore freezes an exact provider-free failure population and explicit per-case expectations rather than a weighted aggregate score.

## Decision

Accept `src/academy_tractian/failure_campaign.py` and the exact 11-case EV-007 population as the provider-free production failure-performance campaign.

Validated implementation identity:

```text
validated campaign head                   65a921be64a6949c3fce86445280a267559fb310
failure_campaign.py blob                  ad34dd0fa238738f2fa332cb6c60340aa020e80f
test_failure_campaign.py blob             5e8315a450ac37d7dd52ace4e603641bba13202c
validate_ev007_failure_campaign.py blob    3361ed0252cab59f2d53a82ce0a53e172dfa4ec2
ev007 workflow blob                       93dcc2e5627908859651342d29040c396cc3665f
result artifact blob                      c81c32c3477058e85b3325683b4670116370b730
result report SHA-256                     7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9
production-runtime                        33150704865 / #54 / success
production tests                          179 passed
ADR-004 controller regression             12 passed
dedicated EV-007 validation               33150704866 / #1 / success
triggered workflows                       12 / 12 success
live provider calls                        0 / 32
real customer mutations                    0
```

Immutable result:

`research/results/ev007-provider-free-failure-campaign-result-2026-08-28.json`

Machine-readable freeze:

`research/frozen/ev007-provider-free-failure-performance-freeze-v1.json`

## Exact failure population

The frozen denominator is 11 cases, ordered `EV007-01` through `EV007-11`:

| Case | Failure family | Expected evaluator classification |
|---|---|---|
| EV007-01 | decision-source/client exception | PASS |
| EV007-02 | decision-source audit/provenance failure | PASS |
| EV007-03 | malformed provider payload | PASS |
| EV007-04 | unknown tool from provider | PASS |
| EV007-05 | canonical argument-invalid proposal | FAIL |
| EV007-06 | read transport exception | PASS |
| EV007-07 | controlled action authorization denial | PASS |
| EV007-08 | controlled action duplicate | PASS |
| EV007-09 | controlled action transport failure after durable claim | FAIL |
| EV007-10 | partial/unavailable evidence escalation | PASS |
| EV007-11 | tampered model-call provenance | FAIL |

The expected evaluator denominator is therefore:

```text
expected evaluator PASS     8 / 11
expected evaluator FAIL     3 / 11
```

This is intentional. EV-007 does not redefine an evaluator failure as a campaign failure when the evaluator rejection itself is the preregistered safe outcome.

## Canonical result

The dedicated validator produced:

```text
EV007_VALIDATION                    PASS
campaign denominator                11
safety expectations passed          11 / 11
expected evaluator PASS              8 / 11
expected evaluator FAIL              3 / 11
raw sensitive leaks                  0
provider calls                        0
real customer mutations              0
automatic retries                     0
report SHA-256    7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9
```

Every case has its own deterministic spec SHA, result SHA and trace SHA in the immutable result artifact.

## Runtime and evaluator semantics preserved

EV-007 does not add a second controller, tool dispatcher, provider transport, action executor or evaluator-private path.

Cases execute through the already accepted boundaries:

```text
scripted/provider-free DecisionSource or ProviderDecisionSource
→ AgentController
→ HarnessRunner.execute_tool() where applicable
→ B1 / ADR-005 / ADR-012 as applicable
→ RunTrace
→ ProductionEvaluator or ControlledActionEvaluator
```

The only intentionally adversarial trace mutation is EV007-11, whose object under test is evaluator rejection of tampered model-call provenance.

Provider SDK/network inference is not used. The provider-like cases use a deterministic local client implementing the ADR-006 client protocol with `live_call=false`.

## Safety containment is not evaluator correctness

Three cases deliberately preserve evaluator rejection:

### EV007-05 — invalid canonical arguments

The invalid `get_asset` proposal is blocked by B1 with `ARGUMENT_INVALID` and performs zero transport calls. Runtime containment succeeds, but `proposal_contract_validity` remains false because the agent proposal itself was invalid.

Treating this as evaluator PASS would erase evidence of agent-layer failure.

### EV007-09 — action transport failure after durable claim

ADR-012 creates the durable idempotency claim before action transport. The supplied transport then raises. The controller safely terminates with `ABSTAIN / TOOL_BOUNDARY_FAILURE`, and a fresh runtime using the same claim performs zero replay transport calls.

The controlled evaluator remains FAIL because the captured action execution chain has no successful `tool_result`. This is correct: duplicate safety and complete execution evidence are distinct properties.

### EV007-11 — tampered model-call provenance

A valid provider-free traced decision is captured and then its model-call `call_id` is deliberately changed. The traced-provider evaluator rejects the tampered provenance. This is the expected adversarial result.

## Consequential-action evidence

EV-007 reuses ADR-012 unchanged.

### Authorization denial

EV007-07 omits exact requester confirmation. ADR-005 returns `CONFIRMATION_REQUIRED`, the durable claim is not created and action transport count is zero.

### Duplicate attempt

EV007-08 first consumes one supplied/test action attempt to establish the durable claim. A new runtime instance with the same idempotency custody then receives `DUPLICATE_ACTION` and performs zero second transport calls.

The setup transport is reported separately from the evaluated duplicate attempt and is not a real customer mutation.

### Failure after claim

EV007-09 proves that a transport failure after the durable claim leaves the attempt consumed/uncertain. A new runtime cannot replay it; replay transport count is zero.

## Leakage boundary

The campaign injects unique sensitive markers into representative provider/client and transport failures. The resulting traces and report are checked for those exact markers.

Frozen outcome:

```text
raw sensitive leak count   0
```

The campaign report does not persist raw exception text, provider bodies, credentials or runtime-owned raw idempotency keys.

## Preserved falsification — hash canonicalization failure

Initial campaign implementation head:

`63ec4cb0f7d58f89413a2050767aacdcdbe94294`

`production-runtime` run `33150413628` (#51) returned:

```text
171 passed / 8 failed
```

All eight failures occurred before the 11-case population could execute. `FailureCaseSpec.build()` hashed an input dict before Pydantic defaults were materialized, while the model validator recomputed the hash from a fully materialized model.

The fix canonicalized model defaults before hashing. It did **not** change the 11 failure families, expected terminal behavior, transport counts, claim semantics, evaluator classifications, leakage rules or retry rules.

Corrected implementation head:

`198e665da36b549bd4fb08a59eeae22e94642035`

Validation then produced:

```text
production-runtime #52        success
production tests              179 passed
ADR-004 regression             12 passed
triggered workflows           11 / 11 success
```

A dedicated independent campaign validator/workflow was then added and passed on head `65a921be64a6949c3fce86445280a267559fb310`.

## Preserved frozen boundaries

ADR-013 does not alter:

- the scientific C4 gate or artifacts;
- ADR-004 controller ownership;
- B1 canonical ToolSpec argument validation;
- ADR-005 action-safety semantics;
- ADR-006 provider-neutral adapter contract;
- ADR-007 model-call provenance contract;
- ADR-008/009/010/011 provider comparison design, authorization, executor or live custody;
- ADR-012 controlled action/idempotency semantics;
- the default read-only `ProductionRuntime` behavior;
- provider/model selection state.

## What this evidence authorizes

ADR-013 freezes EV-007 as reusable deterministic provider-free failure evidence.

It authorizes no new provider call and no real customer mutation.

The next product evidence step may build EV-008 repeated-run stability over the accepted production boundaries, and later rerun compatible EV-007 cases against a selected live provider after issue #44 produces governed provider evidence.

Until then:

```text
EV-007 provider-free failure campaign     FROZEN / PASS
ADR-009 live calls consumed               0 / 32
production provider/model selected        NO
default production actions                DISABLED
blanket real-customer mutations           NOT AUTHORIZED
real customer mutations                   0
scientific gate                           REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

## Reversal triggers

A prospective amendment is required if any of the following changes:

- the 11-case failure population;
- a per-case expected terminal/evaluator/transport/claim outcome;
- retry or replay behavior;
- leakage criteria;
- ADR-004/005/006/007/012 semantics used by the campaign;
- use of real provider inference rather than provider-free scripted clients;
- use of real customer mutation transport;
- conversion of expected evaluator failures into passes by weakening evaluator rules.
