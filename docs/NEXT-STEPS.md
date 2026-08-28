# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-28 04:02 BRT  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)

This file is the short-horizon execution plan. It does not itself authorize a scientific gate, provider call, real customer mutation or provider selection.

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

## 2. Production P0 — execute the frozen live provider comparison only when prerequisites exist

Provider implementation is complete through ADR-011:

```text
comparison design                   ADR-008 / FROZEN
live clients + authorization        ADR-009 / FROZEN
executor                            ADR-010 / FROZEN
live execution/custody wrapper      ADR-011 / FROZEN
plan SHA-256                        69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f
max calls                           32
calls consumed                      0
provider selected                   NO
```

Issue #44 is the actual execution task. Do not build another executor/wrapper.

Before attempt 0, #44 must have:

1. canonical `main` with ADR-011 merged;
2. one canonical durable custody root;
3. both OpenAI and Google secret values explicitly provisioned;
4. no existing ADR-009 custody marker for a prior reserved/consumed run;
5. exact ADR-009/010/011 identity validation;
6. no credential/account capability probe;
7. default production mutating actions disabled.

If either secret is absent, stop before attempt 0. Do not consume a provider call merely to test availability.

If execution occurs, preserve exact frozen geometry: 16 OpenAI + 16 Google attempts maximum, zero warm-ups/retries/fallbacks/parallel provider calls/provider seed, and no replay of claimed/uncertain attempts.

## 3. Controlled consequential actions — capability complete / ADR-012

The provider-free controlled action execution track is now frozen:

```text
controlled runtime                    ADR-012 / FROZEN
controlled evaluator                  ADR-012 / FROZEN
default ProductionRuntime actions     DISABLED
canonical actions proven              5 / 5
provider calls                        0
real customer mutations               0
```

Do not create another action execution path.

For controlled supplied/test scenarios, use exactly:

```text
trusted exact grant
→ ControlledActionRuntime
→ AgentController
→ HarnessRunner.execute_tool()
→ B1
→ ADR-005
→ durable exclusive-create idempotency claim
→ supplied transport
→ RunTrace
→ ControlledActionEvaluator
```

ADR-012 does not authorize blanket real-customer mutation. A later real environment still needs trusted identity/permissions, resource/company scope, exact requester confirmation, durable idempotency custody and explicit target transport/environment authorization.

## 4. NEXT provider-free P0/P1 — EV-007 failure performance

This is now the highest-value implementation task that is not blocked on secrets or the missing C4 artifact.

Build one deterministic provider-neutral failure campaign over the production path. It should exercise at minimum:

- decision-source/client exception;
- malformed/invalid provider decision payload through the ADR-006 path;
- invalid/unknown tool proposal containment;
- tool transport exception after a valid read call;
- controlled action authorization denial;
- controlled action transport failure after durable claim;
- unavailable/partial evidence leading to clarification, abstention or escalation;
- model-call provenance failure where applicable.

For each case record explicit expected safety properties rather than a weighted score:

- process does not crash out of the controller boundary;
- unsafe transport count;
- safe terminal decision/reason code;
- denied-policy containment;
- raw exception/provider material leakage = zero;
- duplicate/replay behavior where consequential actions are involved;
- trace lifecycle/evaluator pass for the expected failure mode.

Use scripted/provider-free sources first. No ADR-009 calls are required for this task.

## 5. THEN — EV-008 repeated-run stability

After EV-007 is frozen, add a repeated-run report over controlled deterministic request/context inputs.

Provider-free baseline should report explicit denominators for:

- terminal decision-kind stability;
- tool-selection stability;
- canonical argument/fingerprint stability;
- controlled action choice stability where applicable;
- final conclusion signature stability;
- trace/evaluation structural-pass rate;
- failure-family consistency.

Do not interpret deterministic scripted stability as live-model quality. The same runner should later be reusable against the selected provider.

## 6. THEN — EV-011 customer-safe communication

Add deterministic leakage/safety checks over terminal responses and traces:

- no credentials/tokens/authorization headers;
- no raw backend/provider exceptions;
- no unnecessary provider/model/internal service disclosure;
- no private evaluator/gold material;
- safe language for unavailable/partial/failure states;
- useful clarification/escalation handoff where applicable.

Use human/semantic review only for communication qualities that cannot be reliably established deterministically, and only under a separately authorized evaluation gate if private/semantic access would be required.

## 7. Freeze provider result when #44 runs

After the live comparison ends, freeze one sanitized result containing:

- exact ADR-008/009/010/011 identities;
- canonical custody identity;
- attempted/unattempted indexes;
- candidate/unit/repeat mapping;
- sanitized ADR-007 provenance;
- M1–M10 with frozen denominators;
- hard-gate status;
- operational failure families;
- latency/usage/cost evidence where exact;
- deterministic final candidate ID or `NO_SELECTION`.

Incomplete/custody-compromised evidence cannot become a winner.

If `NO_SELECTION`, diagnose prospectively; do not choose a provider by intuition or historical C4 evidence.

## 8. Integrated final path after provider evidence

Once provider evidence exists and EV-007/008/011 foundations are ready:

- bind only a governed selected provider behind ADR-006, or preserve the safe baseline after `NO_SELECTION`;
- run contextualize/investigate/clarify/abstain/escalate against the supplied API path;
- use ADR-012 only for explicitly controlled execute scenarios;
- rerun failure/stability/communication evidence with the selected provider;
- evaluate the exact production `RunTrace` from the integrated run;
- record end-to-end latency/reliability/resource/cost behavior;
- preserve reproducible manifests and sanitized traces.

## 9. Final-delivery protection

Continue deferring RAG/vector DB/reranking, persistent memory, MCP, multi-agent orchestration, adaptive routing and rich UI unless a measured P0/P1 gap requires them.

Do not perform a large shared-core refactor before the final evidence path is stable. Close reproducibility through a documented clean install/run/evaluate path first.

## 10. Deadline sequence

```text
NOW        reconcile ADR-012 controlled action freeze
NEXT       implement EV-007 provider-free failure-performance campaign
THEN       implement EV-008 repeated-run stability
THEN       implement EV-011 customer-safe communication checks
PARALLEL   issue #44: provision canonical custody + both secrets or remain at 0/32 calls
PARALLEL   recover exact C4 score-row artifact only
WHEN READY execute exact ADR-009 envelope once and freeze candidate_id or NO_SELECTION
AFTER      integrate selected provider + ADR-012 controlled execute path
FINAL      full regression + clean reproduction + evidence index + real-path demo
```
