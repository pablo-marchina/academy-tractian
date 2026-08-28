# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-28 05:36 BRT  
**Canonical branch after merge:** `main`  
**Canonical main head at this checkpoint:** `8c710c11e43376d89c6af60e54de598b691a4eff`  
**Current reconciliation branch:** `docs/reconcile-adr-015-ev011`  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Latest chronological entry:** [`progress/031-ev011-customer-safe-communication-freeze-2026-08-28.md`](progress/031-ev011-customer-safe-communication-freeze-2026-08-28.md)  
**Machine checkpoint:** [`../research/results/project-progress-checkpoint-2026-08-28-0536-brt.json`](../research/results/project-progress-checkpoint-2026-08-28-0536-brt.json)

This document is the **sole canonical human-readable source for current project state and authorization**. Frozen scientific artifacts, ADRs and authorization packets remain authoritative for exact semantics. Production work does not advance the C4 scientific gate.

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
EV-008 repeated-run stability                FROZEN / ADR-014 / 30 OF 30 RUNS
EV-008 stable units                          6 OF 6
EV-008 stable dimension checks               66 OF 66
EV-011 customer-safe communication           FROZEN / ADR-015 / 10 OF 10 CASES
EV-011 applicable communication checks       60 OF 60 PASS
EV-011 expected evaluator classifications    9 PASS / 1 FAIL (COMM-07)
next unblocked provider-free P0/P1            CLEAN REPRODUCTION + EVIDENCE INDEX + INTEGRATED DEMO

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

Only exact artifact recovery/provisioning is authorized. Reconstruction, rescoring or substitution remain forbidden. Production reliability/provider work does not authorize C4 semantic judging, survivor selection or blind-partition access.

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

A separate controlled action profile exists under ADR-012:

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

All five canonical action ToolSpecs have provider-free accepted-action evidence. A transport failure after claim remains consumed/uncertain and cannot be automatically replayed. ADR-012 is capability evidence, not blanket authorization for a real customer environment.

## Provider comparison state — ADR-008 through ADR-011

The frozen comparison remains exactly:

- OpenAI `gpt-5.6-sol` / `openai.responses.v1.standard`;
- Google `gemini-3.7-flash` / `google.interactions.v1beta.stateless`;
- 8 public deterministic DEV probes × 2 repetitions × 2 candidates = maximum 32 calls;
- zero warm-ups, retries, fallbacks, parallel live calls, provider seeds or provider-side conversation state;
- M1–M10 hard gates and deterministic candidate ID / `NO_SELECTION` outcome.

Canonical plan SHA-256:

`69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f`

Issue #44 is the only live execution task. It may execute only through `GovernedProviderLiveTask` with both explicit secrets and one canonical durable custody root. Credential/account probing is forbidden. Calls remain 0/32.

## ADR-013 — EV-007 failure performance

Canonical report SHA-256:

`7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9`

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

EV007-05, EV007-09 and EV007-11 remain intentionally expected evaluator failures: safe containment does not erase invalid proposals, incomplete post-claim action evidence or tampered provenance.

## ADR-014 — EV-008 provider-free repeated-run stability

Canonical report SHA-256:

`1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8`

```text
stability units                       6
repetitions per unit                  5
provider-free runs                   30 / 30
stable units                          6 / 6
stable dimension checks              66 / 66
contract expectations                30 / 30
raw sensitive leaks                   0
automatic retries / replays           0 / 0
provider calls / real mutations       0 / 0
```

ADR-014 establishes provider-free runtime/harness/evaluator reproducibility only. It does not establish live-model stability or provider quality.

## ADR-015 — EV-011 provider-free customer-safe communication

Issue #54 / PR #55 froze deterministic objective communication/leakage safety over accepted production traces.

Canonical evidence:

```text
campaign version                     ev011-provider-free-communication-campaign-v1
report SHA-256                        cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e
communication cases                 10 / 10
predicate definitions               12
case × predicate slots             120
applicable predicate checks         60
passed predicate checks             60 / 60
failed predicate checks              0
not-applicable checks               60
contract expectations               10 / 10
evaluator classifications            9 PASS / 1 FAIL
expected evaluator FAIL              COMM-07
provider calls                        0
real customer mutations               0
semantic/private/blind access         0
automatic retries / replays           0 / 0
PR #55 merge                          8c710c11e43376d89c6af60e54de598b691a4eff
```

The campaign covers clarification, abstention, escalation, read transport failure, malformed local provider decision, authorization denial, uncertain post-claim action failure, accepted controlled action, partial/unavailable evidence and successful read/orientation.

The twelve predicates independently check synthetic credential leakage, raw exception leakage, private evaluator leakage, customer-facing internal disclosure, trace support for success claims, failure overclaim, uncertain-action success/replay language, clarification request, escalation handoff, fabrication and accepted-action wording.

`NOT_APPLICABLE` is explicit and never counted as PASS. The test suite deliberately injects communication defects and requires them to become predicate failures.

`COMM-07` remains evaluator-invalid by design because post-claim action transport uncertainty leaves incomplete action evidence. Its communication checks pass because the response does not claim success, leak raw failure material, fabricate completion or advise replay. Safe communication does not erase evaluator-invalid execution evidence.

Freeze-validation head `7a4fdb38753086ff628463f0cadece20066e39ad` passed:

```text
ev011-customer-safe-communication #5   PASS
report SHA-256                          cfa811da… reproduced exactly
production-runtime #75                  218 passed
ADR-004 regression                       12 passed
triggered workflows                     12 / 12 success
freeze self-check                       PASS
exact ten-case reproduction             PASS
```

Final PR head `e915809a8d93de88bc29f010f1a780042390b188` then closed 12/12 workflows successfully before merge.

ADR-015 establishes objective deterministic provider-free communication safety only. It does not establish subjective/live-model writing quality, provider selection or production readiness.

## Immediate priorities

1. **Final-delivery provider-free path:** build and freeze a clean install/run/evaluate reproduction, a machine-readable evidence index and an integrated supplied-API/provider-free demonstration over accepted runtime/tool/evaluator boundaries.
2. **Provider execution in parallel:** issue #44 remains blocked until both explicit secrets and one canonical durable custody root exist; otherwise remain at attempt 0 / 0 calls.
3. **Scientific recovery in parallel:** recover the exact original C4 score-row artifact only; do not reconstruct/rescore.
4. **After provider result:** freeze exact candidate ID or `NO_SELECTION`; rerun compatible EV-007/008/011 definitions without post-hoc metric changes.
5. **Final handoff:** complete end-to-end regression, evidence inventory, reproducible commands and demonstration before 2026-09-08.

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
- changing EV-007/008/011 definitions after observing live provider results;
- claiming provider/model selection from provider-free evidence;
- global architecture or production-readiness claims beyond current evidence.
