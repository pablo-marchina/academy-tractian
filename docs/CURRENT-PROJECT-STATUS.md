# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-28 06:21 BRT  
**Canonical branch after implementation merge:** `main`  
**Canonical implementation merge head:** `b432ca9d5c32ffedcda2b26fc15959f3f4f415bd`  
**Current reconciliation branch:** `docs/reconcile-adr-016-final-delivery`  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Latest chronological entry:** [`progress/032-final-delivery-reproduction-evidence-freeze-2026-08-28.md`](progress/032-final-delivery-reproduction-evidence-freeze-2026-08-28.md)  
**Machine checkpoint:** [`../research/results/project-progress-checkpoint-2026-08-28-0621-brt.json`](../research/results/project-progress-checkpoint-2026-08-28-0621-brt.json)

This document is the **sole canonical human-readable source for current project state and authorization**. Frozen scientific artifacts, ADRs and authorization packets remain authoritative for exact semantics. Production/delivery work does not advance the C4 scientific gate.

## Executive state

```text
Project North Star                           maximize actual TRACTIAN/Inteli delivery under P1-P4
Final delivery target                        2026-09-08

P12-C4 packet                                FROZEN_COMPLETE_C4_PACKET
P12-C4 deterministic scoring                 FROZEN / 144 OF 144 / 0 RECOMPUTATION MISMATCHES
P12-C4 bootstrap 20k                         FROZEN / PASS / INDEPENDENT RECOMPUTATION PASS
P12-C4 LOGO sensitivity                      FROZEN / 7 OF 7 / INDEPENDENT RECOMPUTATION PASS
current authorized scientific gate           REQUIRED_PER_GROUP_AND_SLICE_REPORTING
per-group/slice reporting                    AUTHORIZED / BLOCKED ON EXACT SCORE-ROW ARTIFACT
semantic / FRESH_BLIND / LEGACY_LOCKED_TEST  NOT AUTHORIZED
project-level PREFERRED                      NONE

P0 Agent Controller                          FROZEN / ADR-004
production action safety                     FROZEN / ADR-005
default ProductionRuntime actions            DISABLED
provider-neutral DecisionSource              FROZEN / ADR-006
model-call provenance                        FROZEN / ADR-007
provider comparison design                   FROZEN / ADR-008
OpenAI/Gemini concrete clients               FROZEN / ADR-009
provider comparison executor                 FROZEN / ADR-010
live execution/custody wrapper               FROZEN / ADR-011
controlled action execution/evaluator        FROZEN / ADR-012
EV-007 failure performance                   FROZEN / ADR-013 / 11 OF 11 SAFETY EXPECTATIONS
EV-008 repeated-run stability                FROZEN / ADR-014 / 30 OF 30 RUNS / 66 OF 66 DIMENSIONS
EV-011 customer-safe communication           FROZEN / ADR-015 / 60 OF 60 APPLICABLE CHECKS
final-delivery reproduction/evidence         FROZEN / ADR-016
integrated provider-free demo                5 OF 5 / REPORT 43903731…
evidence index                               31 ENTRIES / 30 OF 30 RESIDENT BLOBS / 0 VIOLATIONS
clean-checkout freeze regression              237 PRODUCTION TESTS + 12 ADR-004 / PASS
next unblocked provider-free P0/P1            FINAL HANDOFF ACCEPTANCE AUDIT + GAP CLOSURE

canonical provider comparison plan           32 ATTEMPTS / SHA-256 69691adf…
production live provider calls consumed      0 / 32
first live attempt executed                  NO
production provider/model selected           NO
credential/account probes                    0
real customer mutations performed            0
blanket real-customer mutations              NOT AUTHORIZED
global final architecture                    UNFROZEN
production-readiness claim                   NOT AUTHORIZED
```

## Scientific critical path — unchanged and parallel

The scientific path remains blocked at `REQUIRED_PER_GROUP_AND_SLICE_REPORTING` on the exact original evaluator-side score-row artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

Only exact artifact recovery/provisioning is authorized. Reconstruction, rescoring or substitution remain forbidden. Production reliability/provider/delivery work does not authorize C4 semantic judging, survivor selection or blind-partition access.

## Production architecture state

The default application-owned path remains:

```text
request
→ AgentController                         ADR-004
→ DecisionSource                         ADR-006
→ governed provider client               ADR-009 only when separately executed
→ ControllerDecision / ToolProposal
→ HarnessRunner.execute_tool()           exclusive tool boundary
→ B1 canonical argument validation
→ ADR-005/B2 action safety
→ RunTrace
→ deterministic ProductionEvaluator
```

Identity, seed, action authorization and evaluator-private truth remain outside provider control. The default `ProductionRuntime` remains read-only for mutating actions.

The controlled supplied/test action path remains ADR-012 only:

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

All five canonical action ToolSpecs have provider-free accepted-action capability evidence. A transport failure after claim remains consumed/uncertain and cannot be automatically replayed. This is not blanket authorization for a real customer environment.

## Provider comparison state — unchanged

The frozen comparison remains exactly:

- OpenAI `gpt-5.6-sol` / `openai.responses.v1.standard`;
- Google `gemini-3.7-flash` / `google.interactions.v1beta.stateless`;
- 8 public deterministic DEV probes × 2 repetitions × 2 candidates = maximum 32 calls;
- zero warm-ups, retries, fallbacks, parallel live calls, provider seeds or provider-side conversation state;
- M1–M10 hard gates and deterministic candidate ID / `NO_SELECTION` outcome.

Canonical plan SHA-256:

`69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f`

Issue #44 is the only live execution task. It may execute only through the frozen governed wrapper with both explicit secrets and one canonical durable custody root. Credential/account probing is forbidden. Calls remain 0/32 and no provider/model is selected.

## Frozen reliability/evaluation foundations

### ADR-013 — EV-007

```text
report SHA-256        7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9
failure cases         11
safety expectations   11 / 11
expected evaluator     8 PASS / 3 FAIL
leaks/calls/mutations  0 / 0 / 0
```

EV007-05, EV007-09 and EV007-11 remain intentional evaluator failures. Safe containment does not erase invalid/incomplete/tampered evidence.

### ADR-014 — EV-008

```text
report SHA-256             1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8
provider-free runs         30 / 30
stable units                6 / 6
stable dimension checks    66 / 66
contract expectations      30 / 30
leaks/retries/replays       0 / 0 / 0
provider calls/mutations    0 / 0
```

### ADR-015 — EV-011

```text
report SHA-256                    cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e
communication cases               10 / 10
applicable predicate checks       60
passed predicate checks           60 / 60
failed predicate checks            0
evaluator classifications          9 PASS / 1 FAIL
expected evaluator FAIL            COMM-07
provider calls/mutations           0 / 0
semantic/private/blind access      0
```

`COMM-07` remains evaluator-invalid by design; safe communication does not convert an uncertain post-claim action into valid execution.

## ADR-016 — provider-free final-delivery reproduction and evidence package

Issue #57 / PR #58 froze the highest-value unblocked final-delivery reproducibility path.

Canonical integrated demo:

```text
campaign version                  provider-free-final-delivery-reproduction-v1
report SHA-256                    43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445
scenarios                         5 / 5
exact traces evaluated            5 / 5
contract expectations             5 / 5
provider calls                    0
credential/account probes         0
real customer mutations           0
semantic/private/blind access     0
```

The fixed scenario order is read/investigate, clarify, abstain, escalate and one ADR-012 controlled supplied/test accepted action. DEMO-05 produces exactly one local action transport and one durable local claim; it does not touch a real customer environment.

Canonical evidence index:

```text
entries                            31
repository-resident entries        30
exact Git blobs resolved           30 / 30
external blocker entries            1
violations                          0
```

The index explicitly distinguishes:

- provider-free reproducible evidence;
- immutable historical ADR evidence;
- the live provider comparison as `UNEXECUTED_GATED`;
- the missing exact C4 artifact as `EXTERNALLY_BLOCKED`.

It does not index itself, avoiding circular blob identity.

Final freeze head `e603a44a817c13bbd9b1784d50edbfb41f095501` passed:

```text
final-delivery-provider-free-reproduction #10   PASS
clean-checkout production tests                 237 passed
ADR-004 controller regression                    12 passed
EV-007 / EV-008 / EV-011                        PASS / exact frozen SHAs
integrated demo                                 PASS / exact 43903731…
evidence index                                  30 / 30 resolved / 0 violations
triggered workflows                             12 / 12 success
freeze self-check                               PASS
```

PR #58 merged to `main` as `b432ca9d5c32ffedcda2b26fc15959f3f4f415bd`.

Two falsifications remain part of the evidence history: inferred ADR filenames in the first cut, and an incorrect checker assumption that every historical freeze used `result.path`. Neither failure changed the preregistered five-scenario geometry or any frozen upstream result.

ADR-016 establishes an auditable provider-free handoff baseline only. It does not authorize or imply live provider execution, provider selection, C4 reconstruction, semantic/private/blind evaluation, global architecture freeze or production readiness.

## Immediate priorities

1. **Final handoff acceptance audit + gap closure:** use `DELIVERY-ACCEPTANCE.md` to produce the final rubric-to-evidence crosswalk, validate setup/run/evaluate instructions, close documentation/runbook/fallback/rollback gaps, and run one final end-to-end provider-free regression before delivery.
2. **Provider execution in parallel:** issue #44 remains blocked until both explicit provider secrets and one canonical durable custody root exist; otherwise remain at attempt 0 / 0 calls.
3. **Scientific recovery in parallel:** recover the exact original C4 score-row artifact only; do not reconstruct/rescore.
4. **If provider result becomes available:** freeze exact candidate ID or `NO_SELECTION`; rerun compatible frozen EV-007/008/011 definitions without post-hoc metric changes.
5. **Final claims:** explicitly label any provider/C4-dependent acceptance row as blocked/unexecuted if its external prerequisite remains absent by handoff.

## Still forbidden

- reconstructing/rescoring/substituting the missing C4 artifact;
- semantic, FRESH_BLIND or LEGACY_LOCKED_TEST access without a separate gate;
- using ADR-009 calls for scientific/C4 work;
- changing frozen provider comparison geometry after live evidence without prospective amendment;
- hidden provider retries/fallbacks/warm-ups or provider-side state;
- credential/account probing;
- provider-native TRACTIAN tool execution or bypass of `HarnessRunner.execute_tool()`;
- weakening ADR-005 or releasing uncertain action claims to permit replay;
- treating ADR-012 as blanket real-customer authorization;
- changing EV-007/008/011 or ADR-016 definitions after observing later evidence;
- claiming provider/model selection from provider-free evidence;
- claiming global architecture freeze or production readiness beyond current evidence.