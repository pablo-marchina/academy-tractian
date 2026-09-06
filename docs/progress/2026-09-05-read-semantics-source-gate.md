# Read-semantics source-gate checkpoint — 2026-09-05

## Objective

Close the offline TRACTIAN read-semantics gap without changing the accepted `AgentController`, provider request v1, production runtime/evaluator foundations, or frozen EV-* evidence.

The baseline problem was explicit: raw `tool_result` evidence already contained HTTP status and response body, and the domain already defined `ResponseMode`, but generic controller observation success was still derived from HTTP status. Therefore an HTTP-success response could not, by itself, establish whether the upstream result was `complete`, `partial`, `inconclusive`, `conflict`, or `unavailable`.

## Authoritative contract used

The supplied TRACTIAN contract remains represented by the hash-pinned canonical tool registry rather than a copied OpenAPI artifact. Existing real-API probe code reads the structured response field `body.mode`, and existing E2 fixtures use the same structured field. No prose or natural-language heuristic was introduced.

The deterministic source contract implemented by `read-semantics-v1` is:

```text
non-2xx read                         -> unavailable / source=http_status
2xx + valid structured body.mode     -> preserve exact canonical ResponseMode
2xx + missing/invalid body.mode      -> inconclusive / source=fail_closed + contract issue
2xx + non-object body                -> inconclusive / source=fail_closed + contract issue
trace status/result mismatch         -> inconclusive / source=fail_closed + contract issue
action result                        -> never classified as a read
```

Canonical values are `complete`, `partial`, `inconclusive`, `conflict`, and `unavailable`.

## Implementation

Added:

- `research/e2/read_semantics.py`
  - deterministic response classifier;
  - trace-only evaluator over existing raw `tool_result` evidence;
  - canonical-registry-derived read denominator;
  - explicit provenance and contract issue codes.
- `research/e2/tests/test_read_semantics.py`
  - all five response modes;
  - HTTP/body precedence;
  - missing/invalid mode fail-closed behavior;
  - action exclusion;
  - live/replay equivalence;
  - trace integrity mismatch;
  - provider-facing schema invariance.
- `src/academy_tractian/read_semantics_gate.py`
  - sanitized production source-gate wrapper;
  - no raw TRACTIAN body copied into report or exception;
  - acceptance fails on structural contract issues while safe classification remains `inconclusive`.
- `tests/test_read_semantics_gate.py`
  - production-facing complete/partial/conflict/unavailable cases;
  - malformed-success rejection;
  - secret-marker non-leakage;
  - zero-read terminal trace behavior.

`ProviderDecisionRequest v1` and `ControllerObservation` remain unchanged. The provider already receives the raw structured body, so adding a second provider-facing semantic field would have changed request hashes and the preregistered tournament protocol without authorization.

## Freeze-preservation corrections

Two attempted integration points were deliberately rejected rather than normalized into new evidence.

### Frozen HarnessRunner

The first implementation instrumented `research/e2/runner.py` directly. Historical freeze reproduction rejected the changed foundation. The runner was restored byte-for-byte to its frozen blob instead of repinning EV-007/EV-008/EV-011 or weakening validators.

The final design is post-hoc: it consumes the immutable raw trace and derives semantic state without mutating the trace.

### Provider authorization package export

The new gate was briefly exported through `src/academy_tractian/__init__.py`. Provider live-authorization validation correctly rejected the package hash change. The public export file was restored exactly rather than repinning that authorization packet.

The gate remains available as the additive module `academy_tractian.read_semantics_gate`. An intermediate wheel/image smoke proved the module and `research.e2.read_semantics` dependency were included in the built artifact; the final restored code head then passed the complete required CI surface.

## Validated evidence

Validated implementation head:

```text
6ec5dcd7f5a4b4db81c3951d3592c955e3c64a4e
```

At that exact code head:

```text
production-runtime                         PASS
standalone wheel smoke                     PASS
production image smoke                     PASS
clean-clone full-product reproduction      PASS
frozen EV-007 / EV-008 / EV-011            PASS
ADR-004 controller boundary regression     PASS
frontend provider-free                     PASS
observability provider-free                PASS
horizontal runtime handoff                 PASS
Railway IaC contract                       PASS
full-product Playwright                    PASS
final-ci-required / required-gate          PASS
```

Result: 11/11 workflows green.

## Explicit non-claims

This checkpoint authorizes and proves no live provider call, no real TRACTIAN call, no production action, no remote TRACTIAN reachability, and no hosted observation of all five response modes. Provider state remains `NO_SELECTION`; TRACTIAN remains `UNCONFIGURED` by default or at most `CONFIGURED_UNVERIFIED` when complete server-side configuration is supplied.

## Next gate

Prepare provider-free acceptance for the required agent modes — Contextualize, Investigate, Clarify, Abstain, and Escalate — using additive deterministic trace-level invariants only. Reuse existing communication and escalation-handoff controls where possible. Do not modify the frozen controller/runtime/evaluator foundations or provider-decision-request-v1; do not infer semantic correctness from prose alone.
