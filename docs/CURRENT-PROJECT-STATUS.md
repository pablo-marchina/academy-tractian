# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-28 04:20 BRT  
**Canonical branch after merge:** `main`  
**Canonical main head at this checkpoint:** `403316bf615a463de70741d41cbed32fea5dc34c`  
**Current reconciliation branch:** `docs/reconcile-adr-013-ev007`  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Historical ledger:** [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)  
**Latest chronological entry:** [`progress/029-ev007-failure-performance-freeze-2026-08-28.md`](progress/029-ev007-failure-performance-freeze-2026-08-28.md)  
**Machine checkpoint:** [`../research/results/project-progress-checkpoint-2026-08-28-0420-brt.json`](../research/results/project-progress-checkpoint-2026-08-28-0420-brt.json)

This document is the **sole canonical human-readable source for current project state and authorization**. Frozen ADRs, scientific artifacts and authorization packets remain authoritative for their exact semantics. Production work does not alter the C4 scientific gate.

## Executive state

```text
Project North Star                           maximize actual TRACTIAN/Inteli delivery under P1-P4
Final delivery target                        2026-09-08

P12-C4 packet                                FROZEN_COMPLETE_C4_PACKET
P12-C4 deterministic scoring                 FROZEN / 144 OF 144 / 0 RECOMPUTATION MISMATCHES
P12-C4 bootstrap 20k                         FROZEN / PASS / INDEPENDENT RECOMPUTATION PASS
P12-C4 LOGO sensitivity                      FROZEN / 7 OF 7 / INDEPENDENT RECOMPUTATION PASS
current authorized scientific gate           REQUIRED_PER_GROUP_AND_SLICE_REPORTING
scientific provider/model calls authorized   0
per-group/slice reporting                    AUTHORIZED / BLOCKED ON EXACT SCORE-ROW ARTIFACT
survivor/no-survivor decision                NOT AUTHORIZED
semantic evaluation                          NOT AUTHORIZED
FRESH_BLIND                                  NOT AUTHORIZED
LEGACY_LOCKED_TEST                           NOT AUTHORIZED
project-level PREFERRED                      NONE

P0 Agent Controller                          FROZEN_FOR_P0_CONTROLLER_SCOPE / ADR-004
production runtime slice                     MERGED / VALIDATED / PROVIDER_FREE BASELINE
production deterministic evaluator           MERGED / VALIDATED / SAME RunTrace
production action-safety policy              FROZEN / ADR-005
default production mutating actions          DISABLED
provider-neutral DecisionSource              FROZEN / ADR-006
model-call trace/provenance                   FROZEN / ADR-007
exact provider comparison design             FROZEN / ADR-008
concrete OpenAI/Gemini HTTP clients          FROZEN / ADR-009
provider comparison executor                 FROZEN / ADR-010 / PROVIDER-FREE PASS
governed live execution wrapper              FROZEN / ADR-011 / PROVIDER-FREE PASS
controlled action execution profile          FROZEN / ADR-012 / PROVIDER-FREE PASS
controlled durable idempotency claim         FROZEN / PRE-TRANSPORT / AT-MOST-ONCE ATTEMPT
EV-007 failure performance                   FROZEN / ADR-013 / 11 OF 11 SAFETY EXPECTATIONS
EV-007 expected evaluator classifications    8 PASS / 3 FAIL / EXACTLY AS PREREGISTERED
EV-007 raw sensitive leaks                   0
EV-007 automatic retries                     0
EV-008 repeated-run stability                NEXT / NOT YET FROZEN
EV-011 customer-safe communication           PLANNED AFTER EV-008

canonical comparison plan                    32 ATTEMPTS / SHA-256 69691adf…
production live provider calls consumed      0 / 32
first live attempt executed                  NO
production provider/model selected           NO
production credentials/account probed        NO
blanket real-customer mutations              NOT AUTHORIZED
real customer mutations performed            0
global final architecture                    UNFROZEN
production-readiness claim                   NOT AUTHORIZED
```

## Scientific critical path — unchanged and parallel

The scientific path remains blocked at `REQUIRED_PER_GROUP_AND_SLICE_REPORTING` on the exact original evaluator-side deterministic score-row artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

The artifact must be recovered/provisioned exactly. Reconstruction, rescoring or substitution remain forbidden. Production provider/reliability work does not authorize C4 generation, semantic judging, survivor selection or blind-partition access.

C4 recovery remains a parallel external-artifact track and must not block provider-free P0/P1 production development.

## Production architecture state

The application-owned default path remains:

```text
request
→ AgentController                         ADR-004
→ ProviderDecisionSource                  ADR-006
→ concrete provider client                ADR-009 when separately executed
→ ControllerDecision / ToolProposal
→ HarnessRunner.execute_tool()            exclusive real TRACTIAN tool boundary
→ B1 canonical argument validation
→ ADR-005/B2 action safety
→ normalized RunTrace
→ ProductionEvaluator
```

Identity, seed, action authorization state and evaluator-private truth remain outside provider control. The default `ProductionRuntime` remains read-only for mutating actions.

### Controlled consequential actions — ADR-012

A separate explicit provider-free capability exists for supplied/controlled action scenarios:

```text
trusted exact action grant
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

All five canonical action ToolSpecs have provider-free accepted-action proof. Unauthorized, unknown-scope, cross-company, unconfirmed and duplicate attempts remain contained. A transport failure after claim remains consumed/uncertain and cannot be automatically replayed.

ADR-012 is capability evidence, not blanket authorization for real customer mutation.

## Provider comparison state — ADR-008 through ADR-011

The frozen comparison remains exactly:

- OpenAI `gpt-5.6-sol` / `openai.responses.v1.standard`;
- Google `gemini-3.7-flash` / `google.interactions.v1beta.stateless`;
- 8 public deterministic DEV probes;
- 2 repetitions per unit/candidate;
- 32 maximum live calls;
- zero warm-up, automatic retry, fallback, parallel provider call or provider seed;
- M1–M10, disqualifying hard gates and deterministic `NO_SELECTION`.

Canonical plan SHA-256:

`69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f`

ADR-010 freezes the exact executor. ADR-011 freezes the operational live wrapper/custody. The governed entrypoint for a future live comparison is `GovernedProviderLiveTask`, using one canonical durable custody root and both explicitly provisioned secrets.

Issue #44 is the only current live execution task. Credential/account probing is forbidden. Calls remain 0/32.

## ADR-013 — EV-007 provider-free failure performance

Issue #48 / PR #49 froze the first integrated production failure campaign.

Canonical evidence:

```text
failure_campaign.py blob             ad34dd0fa238738f2fa332cb6c60340aa020e80f
validator blob                        3361ed0252cab59f2d53a82ce0a53e172dfa4ec2
result blob                           c81c32c3477058e85b3325683b4670116370b730
result report SHA-256                 7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9
freeze                                research/frozen/ev007-provider-free-failure-performance-freeze-v1.json
ADR                                   docs/adr/013-provider-free-failure-performance-campaign-2026-08-28.md
PR #49 merge                          403316bf615a463de70741d41cbed32fea5dc34c
```

Frozen result:

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

The three evaluator FAIL cases are intentional evidence, not unresolved campaign failures:

- EV007-05: invalid canonical arguments are safely blocked by B1 but remain an invalid proposal;
- EV007-09: post-claim action transport failure safely abstains and cannot replay, but the incomplete action execution chain remains evaluator-invalid;
- EV007-11: tampered model-call provenance is rejected.

This preserves the principle that safety containment does not erase agent/evidence defects.

### Preserved falsification

Initial EV-007 head `63ec4cb0…` produced `171 passed / 8 failed` because case hashes were computed before Pydantic defaults were materialized. No campaign case executed on that head. The hash canonicalization was corrected without changing case semantics.

Final PR head `d6c5ff450649ac0d365b1a5a3d01b6f322399aed` passed:

```text
ev007-failure-performance #5    PASS
production-runtime #58          182 passed
ADR-004 regression              12 passed
triggered workflows             12 / 12 success
freeze self-check               PASS
```

## Current production execution state

```text
live provider authorization             EFFECTIVE / BOUNDED / ADR-009
provider executor                       FROZEN / ADR-010
live operational wrapper                FROZEN / ADR-011
maximum live provider calls             32
provider calls consumed                  0
first live provider attempt             NO
credentials/account probed              NO
provider selected                       NO
controlled action capability            FROZEN / ADR-012
EV-007 failure performance              FROZEN / ADR-013
EV-008 repeated-run stability           NEXT
EV-011 communication safety             AFTER EV-008
default runtime real actions            DISABLED
blanket real-customer mutations         NOT AUTHORIZED
```

The implementation foundations for provider selection, controlled actions and deterministic failure handling are now complete. The highest-value unblocked provider-free task is EV-008 repeated-run stability.

## Immediate blockers and priorities

1. **EV-008 stability:** freeze an exact provider-free repeated-run population and independent stability dimensions without changing ADR-013.
2. **Provider execution:** issue #44 may proceed only with one canonical durable custody root plus both explicit secrets; otherwise remain at attempt 0 / 0 calls.
3. **EV-011 communication safety:** implement after EV-008 using deterministic leakage/failure-message checks first.
4. **Scientific in parallel:** recover the exact original C4 score-row artifact only; do not reconstruct or rescore it.
5. **After provider evidence:** freeze candidate ID or `NO_SELECTION`, bind only a governed selected provider behind ADR-006 and rerun compatible EV-007/008/011 dimensions.
6. **Final delivery:** close reproducibility, clean install/run/evaluate, evidence index, integrated demonstration and handoff before speculative P2 work.

## Still forbidden

- reconstructing or rescoring the missing C4 score-row artifact;
- using ADR-009 calls for C4/scientific work;
- semantic, FRESH_BLIND or LEGACY_LOCKED_TEST access without a separate scientific gate;
- changing ADR-008 candidates/population/thresholds after live calls without prospective amendment;
- provider warm-ups, hidden retries/fallbacks or provider-side conversation state;
- credential/account probing merely to test availability;
- restarting live execution through a new custody root after a reserved/consumed run without prospective governance;
- provider-native TRACTIAN tool execution;
- bypassing `HarnessRunner.execute_tool()` or weakening ADR-005 for actions;
- releasing a durable action claim after uncertain transport failure to permit replay;
- treating ADR-012 as blanket real-customer mutation authorization;
- weakening evaluator rules merely to convert EV-007 expected failures into passes;
- claiming a provider/model winner from provider-free evidence;
- global architecture or production-readiness claims beyond current evidence.
