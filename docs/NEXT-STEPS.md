# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-28 01:16 BRT  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)

This file is the short-horizon execution plan. It does not itself authorize a scientific gate, provider call, action execution or provider selection.

## 1. Scientific critical path — continue in parallel

Current scientific gate remains:

`REQUIRED_PER_GROUP_AND_SLICE_REPORTING`

The reporting runner stays blocked on the exact original evaluator-side deterministic score rows:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
```

Immediate scientific action remains artifact recovery/provisioning only. Do not reconstruct, rescore or replace it.

If recovered exactly:

1. provision through the existing fail-closed path;
2. execute required per-group/slice reporting only;
3. independently validate;
4. freeze the reporting output;
5. advance only to the next explicitly opened scientific decision gate.

Scientific provider/model calls remain 0.

## 2. Production P0 — implement the ADR-009 comparison executor provider-free

ADR-009 now provides an effective **bounded authorization for a separate execution task**, but no live call has been consumed.

The next Class C task should implement an execution surface that can reproduce the exact ADR-008/009 comparison without changing its design.

Required provider-free implementation:

1. load and verify exact authorization/design/population blobs before execution;
2. construct the provider-free baseline and the exact OpenAI/Gemini clients from ADR-009;
3. keep credential retrieval outside `provider_clients.py`; execution code receives explicit secret values and never serializes them;
4. enforce deterministic order P01→P08, repeats 0→1, alternating live candidate order by parity;
5. enforce a hard global call budget of 32 with zero warm-up/retry/fallback/parallel calls;
6. convert each public probe into the exact `ControllerContext` expected by `ProviderDecisionSource`;
7. capture one sanitized attempt record per authorized invocation, including candidate/unit/repeat/order, request SHA, call ID/outcome, latency and separate provider usage;
8. preserve failures in denominators and stop on route/model/custody/provenance mismatch;
9. implement deterministic public-probe M4 adjudication from the frozen unit rubrics;
10. aggregate ADR-008 M1–M10 without semantic/private judges;
11. apply the exact frozen hard gates and selection rule, including `NO_SELECTION`;
12. write only sanitized result/attempt/usage artifacts — never raw provider request/response/credentials;
13. support a full provider-free fixture/dry execution that proves geometry, ordering, budget, failure handling and selection logic before any network call.

Provider-free executor validation must run before real credentials are provisioned.

## 3. Authorized live execution — only after executor validation

Once the executor has a frozen provider-free PASS, the existing ADR-009 envelope permits a separate governed execution with at most:

```text
candidates                     2
units                          8
repeats / unit / candidate     2
maximum live calls            32
warm-ups                       0
retries                        0
fallbacks                      0
parallel calls                 0
provider seed                  none
production actions             disabled
```

Do not probe credentials merely to determine availability. If the required execution secrets are not provisioned, close that run as an operational blocker rather than changing candidates or silently substituting routes.

A live run must stop without ranking if it cannot preserve the frozen route/model/schema, ADR-007 provenance, privacy boundary or complete packet. Incomplete evidence yields `NO_SELECTION`.

## 4. After provider comparison

Only after the frozen comparison result exists:

- if one candidate is selected, bind it behind the existing provider-neutral `DecisionSource` without changing ADR-004/005/006/007 ownership;
- if result is `NO_SELECTION`, retain the provider-free safe baseline and open a prospective amendment only if additional provider evidence is justified;
- run provider/model failure-injection and repeated-run stability evidence;
- close remaining EV-007 failure-performance, EV-008 stability and EV-011 customer-safe-communication gaps;
- measure latency/reliability/resource behavior for the final interaction mode;
- integrate the real Agent + Evaluator path for final demo/regression evidence.

## 5. Consequential actions remain a separate track

ADR-005 is a policy freeze, not execution authorization. Keep all production mutating actions disabled until trusted real sources exist for:

- permissions;
- resource/company scope;
- exact requester confirmation;
- durable idempotency/duplicate protection;
- retry/failure semantics and audit evidence.

Do not let action enablement block provider-free comparison-executor work.

## 6. Complexity gate

Continue deferring RAG/vector DB/reranking, persistent memory, MCP, multi-agent orchestration, adaptive routing and rich UI unless a measured P0/P1 gap requires them. The current highest-value path is executor → bounded provider evidence → reliability/security/evaluator closure → integrated demo.

## 7. Deadline sequence

```text
NOW        reconcile ADR-009 + build provider-free comparison executor
NEXT       validate/freeze executor geometry, metrics and sanitized artifacts
THEN       consume bounded live authorization only if credentials are provisioned
AFTER      freeze provider result or NO_SELECTION
PARALLEL   recover exact C4 reporting artifact
THEN       reliability / security / observability / evaluator gaps
FINAL      integrated real-path demo + documentation + reproducible handoff
```
