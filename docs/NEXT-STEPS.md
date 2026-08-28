# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-28 04:20 BRT  
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

If recovered exactly, provision it through the existing fail-closed path, run only the authorized per-group/slice reporting, independently validate, freeze that report and advance only through a separately opened scientific gate.

Do not let this external artifact blocker stop provider-free P0/P1 production work.

## 2. Live provider comparison — implementation complete, execution blocked on prerequisites

Provider work is frozen through ADR-011:

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

Before attempt 0 it requires one canonical durable custody root, both OpenAI and Google secrets explicitly provisioned, exact ADR-009/010/011 identity validation and no existing consumed custody marker. Credential/account probing is forbidden.

If either secret is absent, remain at 0/32 calls.

## 3. Controlled consequential actions — capability complete / ADR-012

```text
controlled runtime                    ADR-012 / FROZEN
controlled evaluator                  ADR-012 / FROZEN
default ProductionRuntime actions     DISABLED
canonical actions proven              5 / 5
provider calls                        0
real customer mutations               0
```

For supplied/test action scenarios reuse exactly:

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

Do not create another action execution path or treat ADR-012 as blanket real-customer mutation authorization.

## 4. EV-007 failure performance — COMPLETE / ADR-013

The provider-free reliability campaign is frozen:

```text
campaign denominator              11
safety expectations passed        11 / 11
expected evaluator PASS            8 / 11
expected evaluator FAIL            3 / 11
raw sensitive leaks                0
provider calls                      0
real customer mutations            0
automatic retries                   0
report SHA-256  7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9
```

Keep EV007-05, EV007-09 and EV007-11 as expected evaluator failures. They prove that safe containment does not erase invalid proposal, incomplete post-claim action evidence or tampered provenance.

Do not redesign EV-007 while implementing the next stability layer.

## 5. NEXT provider-free P0/P1 — EV-008 repeated-run stability

Build one exact provider-free stability campaign over deterministic production inputs, reusing accepted ADR-004/006/012/013 boundaries.

### Minimum population

Include representative stable paths rather than only happy-path final responses:

1. read/investigate tool flow;
2. clarification terminal path;
3. abstention terminal path;
4. escalation terminal path;
5. controlled authorized action on isolated fresh claim custody per repetition;
6. one deterministic safe failure family from EV-007 that is repeatable without shared consumed state.

Freeze the exact input set, repetition count and ordering before interpreting results.

### Required stability dimensions

For each unit and across the full denominator report independently:

- terminal decision-kind/signature stability;
- ordered tool-selection stability;
- canonical tool-argument stability;
- action fingerprint stability where applicable;
- policy outcome stability;
- evaluator classification stability;
- failure-family/reason-code stability;
- trace structural-pass rate;
- sanitized conclusion signature stability.

Do not collapse these into one arbitrary weighted score.

### Determinism / custody rules

- scripted/provider-free sources only for the first EV-008 freeze;
- zero live provider calls;
- zero real customer mutations;
- each controlled-action repetition receives isolated fresh local claim custody so idempotency state from one repetition cannot convert a stability test into a duplicate test;
- no hidden retries;
- no provider/private/semantic evaluator;
- deterministic request IDs/custody paths must not introduce false instability into the comparison signatures.

### Interpretation boundary

Provider-free scripted stability proves harness/runtime/evaluator reproducibility, **not live-model behavioral stability**.

Design the report so the same stability dimensions can later be rerun against a governed selected provider after #44, without changing metric definitions post hoc.

## 6. THEN — EV-011 customer-safe communication

After EV-008 is frozen, add deterministic communication/leakage checks over terminal responses and traces:

- no credentials/tokens/authorization headers;
- no raw backend/provider exceptions;
- no unnecessary internal service/provider disclosure;
- no private evaluator/gold material;
- safe language for unavailable/partial/failure states;
- useful clarification/escalation handoff;
- no unsupported claim that an action succeeded when only incomplete/uncertain evidence exists.

Use semantic/human review only where deterministic checks cannot establish the property and only under an explicitly authorized evaluation gate.

## 7. When issue #44 can execute

Run the exact ADR-009 envelope once through `GovernedProviderLiveTask`. Preserve the single custody root, write-ahead claims, frozen denominators and zero retry/fallback rules.

Freeze the result as either an exact candidate ID or `NO_SELECTION`. Incomplete/custody-compromised evidence cannot become a winner.

After selection evidence exists, rerun compatible EV-007/EV-008/EV-011 dimensions against that provider without retrospectively changing their definitions.

## 8. Integrated final delivery path

Once provider evidence and the provider-free reliability foundations exist:

- bind only a governed selected provider behind ADR-006, or preserve the safe baseline after `NO_SELECTION`;
- demonstrate contextualize / investigate / clarify / abstain / escalate against the supplied API path;
- use ADR-012 only for explicitly controlled execute scenarios;
- evaluate the exact production `RunTrace` from each integrated run;
- record reliability, latency and exact resource/cost evidence where available;
- produce one reproducible clean install/run/evaluate handoff and a final evidence index.

## 9. Final-delivery protection

Continue deferring RAG/vector DB/reranking, persistent memory, MCP, multi-agent orchestration, adaptive routing and rich UI unless a measured P0/P1 acceptance gap requires them.

Do not perform a large shared-core refactor before the final evidence path is stable.

## 10. Deadline sequence

```text
NOW        reconcile ADR-013 / EV-007 freeze
NEXT       implement EV-008 provider-free repeated-run stability
THEN       implement EV-011 customer-safe communication
PARALLEL   issue #44: provision canonical custody + both secrets or remain at 0/32 calls
PARALLEL   recover exact C4 score-row artifact only
WHEN READY execute exact ADR-009 envelope once and freeze candidate_id or NO_SELECTION
AFTER      rerun reliability layers against governed provider + integrate ADR-012 execute path
FINAL      full regression + clean reproduction + evidence index + real-path demo
```
