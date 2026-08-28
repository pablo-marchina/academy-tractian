# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-28 03:25 BRT  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)

This file is the short-horizon execution plan. It does not itself authorize a scientific gate, provider call, production mutation or provider selection.

## 1. Scientific critical path — unchanged and parallel

Current scientific gate:

`REQUIRED_PER_GROUP_AND_SLICE_REPORTING`

The reporting runner remains blocked on the exact original evaluator-side deterministic score rows:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
```

Immediate scientific work is artifact recovery/provisioning only. Do not reconstruct, rescore or replace it.

If recovered exactly:

1. provision through the existing fail-closed path;
2. run required per-group/slice reporting only;
3. independently validate;
4. freeze the reporting artifact;
5. advance only to the next explicitly opened scientific gate.

Do not let this external artifact blocker stop provider-free P0/P1 production work.

## 2. Production P0 — live provider execution is now operationally ready

ADR-010 freezes the exact provider comparison executor. ADR-011 now freezes the governed live execution/custody layer around it.

Canonical identity:

```text
executor freeze                     ADR-010
live execution/custody freeze       ADR-011
plan SHA-256                        69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f
units                               8
repeats                             2
live candidates                     2
max calls                           32
calls consumed                      0
```

Do **not** build another executor or wrapper.

The next Class C provider task is the actual separately governed invocation surface. Before attempt 0 it must:

1. start from the exact merged ADR-011 implementation/freeze;
2. designate one canonical durable execution custody root and preserve it as evidence;
3. receive OpenAI and Google secrets explicitly from the execution environment;
4. check secret presence only — no account/capability request;
5. enter only through `GovernedProviderLiveTask`;
6. verify production actions remain disabled;
7. if either secret is absent, stop before custody reservation/attempt 0 with a sanitized operational blocker;
8. if the canonical custody root already contains ADR-009 custody evidence, refuse a second run;
9. never switch to another custody root after a reserved/consumed run without prospective governance.

## 3. Execute ADR-009 exactly once only when the preconditions are met

If both secrets are explicitly provisioned, the governed live task may consume at most:

```text
OpenAI attempts                   16
Google attempts                   16
total attempts                    32
warm-up calls                      0
automatic retries                  0
fallbacks                          0
parallel provider calls            0
provider seed                      none
provider-side conversation state   none
production actions                 disabled
```

Every attempted provider invocation is consumed evidence, including operational failures.

The execution must stop on:

- frozen input/blob mismatch;
- route/model drift;
- raw/custody/provenance violation;
- hidden retry/fallback behavior;
- attempt-order/budget mismatch;
- authorization-custody mismatch;
- unauthorized action/tool transport behavior.

A `CLAIMED`/`uncertain` attempt is never automatically replayed. Do not replace a failed candidate/route in place. Any material amendment must be prospective and preserve already-consumed evidence.

## 4. Freeze the live comparison result

After a live task ends, preserve the ADR-011 custody marker, attempt ledger and sanitized result. Freeze one result containing:

- exact frozen design/executor/wrapper identities;
- canonical custody identity;
- attempted/unattempted indexes;
- candidate/unit/repeat mapping;
- sanitized ADR-007 provenance;
- M1–M10 with exact preregistered denominators;
- hard-gate status;
- operational failure families;
- exact provider usage where reported;
- latency distribution;
- normalized cost only where exact accounting inputs exist;
- deterministic final outcome: candidate ID or `NO_SELECTION`.

Incomplete or custody-compromised evidence cannot become a winner.

If a candidate is selected, bind it behind ADR-006 only after the result is frozen and status is reconciled.

If the result is `NO_SELECTION`, treat this as a P0 blocker to diagnose immediately. Do not select a provider by intuition or historical C4 evidence. Any repair/candidate change requires prospective design/governance.

## 5. P0 action-enablement work — start provider-free in parallel

The final acceptance requires justified execution requests, while current production actions remain disabled. Start a separate Class C action-enablement track without waiting for provider selection.

Reuse ADR-005 rather than redesigning action safety. The provider-free task should establish trusted runtime-owned sources for:

- permissions;
- user/company identity and resource/company scope;
- exact action/requester confirmation policy;
- action fingerprint binding;
- durable idempotency keys and consumed-key state;
- accepted-action semantics against the supplied synthetic TRACTIAN API;
- retry/failure/audit behavior.

First prove the enabled path using scripted/deterministic `DecisionSource` inputs. Do not enable arbitrary production mutations and do not couple action enablement to provider-comparison calls.

## 6. EV-007 / EV-008 / EV-011 — start provider-free in parallel

Implement the remaining high-value evaluation/reliability gaps before waiting for the live provider result.

### EV-007 — failure performance

Add deterministic fault-injection coverage for provider/client failure, malformed provider output, tool/transport failure and partial/unavailable evidence. Measure whether the controller produces a safe fallback, clarification, abstention or escalation rather than crashing or acting unsafely.

### EV-008 — repeated-run stability

Add a repeated-run runner/report over controlled request/context inputs. Report explicit denominators and stability for decision kind, tool choice, action choice where applicable and final conclusion signature.

### EV-011 — customer-safe communication

Add deterministic checks for unnecessary provider/backend/service disclosure, credentials/raw exception detail and other forbidden internal material. Use semantic/human assessment only for communication qualities that cannot be evaluated reliably with deterministic rules.

These paths should be provider-neutral first, then rerun against the selected live provider.

## 7. Integrated final path after provider evidence

Once a provider result exists and the action/evaluation foundations above are ready:

- bind selected provider behind ADR-006, or explicitly preserve the safe baseline if a governed follow-up is required after `NO_SELECTION`;
- integrate contextualize/investigate/clarify/abstain/escalate behavior through real supplied API reads;
- integrate the controlled action-enabled profile for the required `execute` scenario only after its own evidence/decision;
- run EV-007 failure injection and EV-008 repeated stability using the selected provider;
- verify EV-011 customer-safe terminal communication;
- evaluate the same production `RunTrace` through the integrated evaluator;
- measure end-to-end latency/reliability/resource/cost behavior;
- preserve real-path traces and reproducible run manifests.

## 8. Final-delivery protection

Continue deferring RAG/vector DB/reranking, persistent memory, MCP, multi-agent orchestration, adaptive routing and rich UI unless a measured P0/P1 gap requires them.

Do not perform a large `research/e2` shared-core refactor before the final evidence path is stable. Close reproducibility through a documented clean install/run/evaluate path first.

## 9. Deadline sequence

```text
NOW        reconcile ADR-011 wrapper/custody freeze
NEXT       open actual live-execution task; provision canonical custody + secrets or stop at attempt 0
PARALLEL   controlled action-enablement task using scripted DecisionSource
PARALLEL   EV-007 failure + EV-008 stability + EV-011 communication evaluators
PARALLEL   recover exact C4 score-row artifact only
THEN       execute exact ADR-009 envelope once when prerequisites are satisfied
THEN       freeze candidate_id or NO_SELECTION and reconcile status
THEN       integrate selected provider + controlled action path + real Agent/Evaluator scenarios
AFTER      full reliability/security/observability/performance regressions
FINAL      clean reproduction + README/evidence index + real-path demo
```
