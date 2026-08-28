# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-28 05:36 BRT  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)

This file is the short-horizon execution plan. It does not itself authorize a scientific gate, live provider call, real customer mutation or provider selection.

## 1. Scientific critical path — unchanged and parallel

Current scientific gate: `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`.

Exact missing evaluator-side deterministic score-row artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
```

Immediate scientific work is exact artifact recovery/provisioning only. Reconstruction, rescoring and substitution are forbidden. If recovered, run only the already authorized per-group/slice reporting, independently validate and freeze before any later scientific gate.

## 2. Live provider comparison — implementation complete / execution separately gated

```text
comparison design                   ADR-008 / FROZEN
clients + authorization             ADR-009 / FROZEN
executor                            ADR-010 / FROZEN
live custody wrapper                ADR-011 / FROZEN
plan SHA-256                        69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f
max live calls                      32
calls consumed                       0
provider selected                   NO
```

Issue #44 is the only live execution task. Before attempt 0 it requires both explicit OpenAI/Google secrets and one canonical durable custody root. If either is absent, stay at 0/32 calls; credential/account probing is forbidden.

## 3. Controlled actions — capability complete / ADR-012

The default `ProductionRuntime` remains action-disabled. Supplied/test consequential scenarios must reuse:

```text
trusted exact grant
→ ControlledActionRuntime
→ AgentController
→ HarnessRunner.execute_tool()
→ B1
→ ADR-005
→ durable pre-transport claim
→ supplied transport
→ RunTrace
→ ControlledActionEvaluator
```

Do not add a parallel action path or infer blanket real-customer authorization from ADR-012.

## 4. Reliability and communication foundations complete

### EV-007 / ADR-013

```text
failure cases                        11
safety expectations                  11 / 11
expected evaluator classifications   8 PASS / 3 FAIL
raw leaks                             0
provider calls                        0
real mutations                        0
report SHA-256  7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9
```

### EV-008 / ADR-014

```text
stability units                       6
repetitions / unit                    5
provider-free runs                   30 / 30
stable units                          6 / 6
stable dimension checks              66 / 66
contract expectations                30 / 30
raw leaks / retries / replays         0 / 0 / 0
provider calls / real mutations       0 / 0
report SHA-256  1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8
```

### EV-011 / ADR-015

```text
communication cases                  10 / 10
predicate definitions                12
applicable predicate checks          60
passed predicate checks              60 / 60
failed predicate checks               0
not-applicable checks                60
evaluator classifications             9 PASS / 1 FAIL (COMM-07 expected)
provider calls / real mutations       0 / 0
semantic/private/blind access         0
retries / replays                      0 / 0
report SHA-256  cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e
```

Do not redesign EV-007, EV-008 or EV-011. Their frozen definitions should later be reused against a governed selected provider without post-hoc changes.

## 5. NEXT provider-free P0/P1 — clean reproduction + evidence index + integrated demo

Issue #44 is still blocked on external prerequisites, so the highest-value unblocked work is final-delivery reproducibility rather than more architecture.

Build one provider-free delivery package that proves a fresh checkout can install the accepted production/runtime dependencies, execute representative integrated scenarios, evaluate their exact `RunTrace`s, and resolve every claimed frozen evidence item through a machine-readable index.

### Required reproduction path

Freeze one canonical command sequence that performs, from a clean checkout with no provider secrets:

1. dependency installation for the production package and `research/e2` harness;
2. production/runtime unit regression;
3. accepted ADR-004 controller regression;
4. EV-007 validator;
5. EV-008 validator;
6. EV-011 validator;
7. one integrated provider-free demonstration covering read/investigate, clarify, abstain, escalate and an explicitly controlled supplied/test action;
8. deterministic evaluation of the exact traces created by the demo;
9. evidence-index validation.

No live provider call, credential probe or real customer mutation may be required for this path.

### Machine-readable evidence index

Create one canonical index that records at minimum:

- evidence ID;
- evidence category (`adr`, `freeze`, `result`, `validator`, `workflow`, `demo`, `scientific_blocker`);
- repository path where applicable;
- Git blob SHA-1 where the file is repository-resident;
- canonical report/result SHA-256 where applicable;
- issue / PR / ADR relationship where applicable;
- authorization status / interpretation boundary;
- whether the item is reproducible provider-free, externally blocked or historical immutable evidence.

The index must include at least ADR-004 through ADR-015, EV-007/008/011 freezes/results, the frozen provider-comparison plan, the missing C4 artifact identity/blocker, and the integrated demo evidence produced by this task.

Do not silently omit blocked evidence. The C4 artifact and live provider comparison must appear as explicitly blocked/unexecuted items rather than false PASSes.

### Integrated provider-free demo

Use existing runtime/controller/harness boundaries; do not build a second agent path.

The demo must include deterministic supplied/local scenarios for:

- successful read/investigate;
- clarification;
- safe abstention;
- human escalation;
- one controlled accepted action using ADR-012 supplied/test transport.

For every scenario persist only sanitized deterministic evidence needed for reproduction: scenario ID, terminal decision/reason, ordered tool/policy signatures, evaluator classification, trace hash and result hash. Do not add real secrets, raw customer data or real mutations.

### Required acceptance

```text
clean-checkout command path defined             YES
provider secrets required                       NO
live provider calls                              0
credential/account probes                        0
real customer mutations                          0
representative demo scenarios                    5 / 5
exact demo traces evaluated                      5 / 5
evidence-index entries resolve                   100% for repository-resident items
blocked external evidence labeled explicitly     YES
EV-007 validator                                 PASS
EV-008 validator                                 PASS
EV-011 validator                                 PASS
production/runtime regressions                   PASS
```

Prefer one dedicated validator/workflow for this final-delivery package. Freeze exact scenario population, index schema and command sequence before interpreting results.

## 6. Parallel provider execution

If issue #44 becomes executable, run the exact ADR-009/010/011 envelope once and freeze either an exact candidate ID or `NO_SELECTION`. Do not create a new executor or custody root to evade existing evidence.

After a valid provider result exists, rerun compatible EV-007/008/011 definitions against that governed result without changing metric definitions after seeing the live outcomes.

## 7. Integrated final delivery path

After the provider-free reproduction package exists, and regardless of whether #44 remains externally blocked:

- retain one clean install/run/evaluate handoff;
- retain one machine-readable evidence inventory;
- demonstrate accepted read/clarify/abstain/escalate/action behavior;
- use ADR-012 only for explicitly controlled supplied/test execute scenarios unless real authorization is separately established;
- record exact latency/resource/cost only where actual evidence exists;
- rerun the full regression before delivery;
- document external blockers without converting them into fabricated completeness.

## 8. Deadline sequence

```text
NOW        reconcile ADR-015 / EV-011 freeze
NEXT       clean reproduction + evidence index + integrated provider-free demo
PARALLEL   issue #44: provision canonical custody + both secrets or remain at 0/32 calls
PARALLEL   recover exact C4 score-row artifact only
WHEN READY execute exact live provider envelope once; freeze candidate_id or NO_SELECTION
AFTER      rerun frozen reliability definitions against governed provider result
FINAL      end-to-end regression, demo and handoff before 2026-09-08
```

## 9. Deferred unless measured P0/P1 gap

Continue deferring RAG/vector DB/reranking, persistent memory, MCP, multi-agent orchestration, adaptive routing and rich UI. Avoid a large shared-core refactor before final evidence/reproduction is stable.
