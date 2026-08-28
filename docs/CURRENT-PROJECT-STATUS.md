# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-28 04:02 BRT  
**Canonical branch after merge:** `main`  
**Canonical main head at this checkpoint:** `f45c568c24217b54ead8be01c7ac7e0cca2dea7e`  
**Current reconciliation branch:** `docs/reconcile-adr-012-controlled-actions`  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Historical ledger:** [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)  
**Latest chronological entry:** [`progress/028-controlled-action-execution-freeze-2026-08-28.md`](progress/028-controlled-action-execution-freeze-2026-08-28.md)  
**Machine checkpoint:** [`../research/results/project-progress-checkpoint-2026-08-28-0402-brt.json`](../research/results/project-progress-checkpoint-2026-08-28-0402-brt.json)

This document is the **sole canonical human-readable source for current project state and authorization**. Frozen scientific artifacts, ADRs and production authorization packets remain authoritative for their exact semantics. Production work does not alter the C4 scientific gate.

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
controlled action execution profile          FROZEN / ADR-012 / PROVIDER-FREE PASS
controlled action evaluator                  FROZEN / ADR-012 / SAME RunTrace
controlled durable idempotency claim         FROZEN / PRE-TRANSPORT / AT-MOST-ONCE ATTEMPT
blanket real-customer mutations              NOT AUTHORIZED
provider-neutral DecisionSource              FROZEN / ADR-006
model-call trace/provenance                   FROZEN / ADR-007
exact provider comparison design             FROZEN / ADR-008
concrete OpenAI/Gemini HTTP clients          FROZEN / ADR-009
bounded production live comparison           AUTHORIZED_FOR_SEPARATE_TASK / MAX 32 / ADR-009
provider comparison executor                 FROZEN / ADR-010 / PROVIDER-FREE PASS
governed live execution wrapper              FROZEN / ADR-011 / PROVIDER-FREE PASS
authorization-level live custody             FROZEN / SINGLE CANONICAL CUSTODY ROOT REQUIRED
canonical comparison plan                    32 ATTEMPTS / SHA-256 69691adf…
production live provider calls consumed      0 / 32
first live attempt executed                  NO
production provider/model selected           NO
production credentials/account probed        NO
production reliability campaign              NOT YET EXECUTED
global final architecture                    UNFROZEN
production-readiness claim                   NOT AUTHORIZED
```

## Scientific critical path — unchanged and parallel

The scientific path remains frozen through LOGO and blocked at `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`.

Exact missing evaluator-side deterministic score-row artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

The original artifact must be recovered/provisioned exactly. Reconstruction, rescoring or substitution remains forbidden. Production provider authorization does **not** authorize C4 generation, rescoring, semantic judging, survivor selection or blind-partition access.

C4 recovery remains a parallel scientific track and must not block provider-free P0/P1 production work.

## Production architecture state

The default application-owned production path remains:

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
→ deterministic ProductionEvaluator
```

The default `ProductionRuntime` remains read-only for mutating actions. Identity, seed, action authorization state and evaluator-private truth remain outside provider control.

ADR-012 now adds a separate explicit controlled-action profile without changing that default:

```text
trusted exact action grant
+ runtime-owned permission / scope / confirmation / idempotency
→ ControlledActionRuntime
→ AgentController                         same ADR-004 ownership
→ HarnessRunner.execute_tool()            same exclusive tool boundary
→ B1 canonical argument validation
→ ADR-005 ProductionActionSafetyPolicy
→ durable exclusive-create idempotency claim
→ supplied transport
→ RunTrace
→ ControlledActionEvaluator
```

The profile is capability evidence, not blanket authorization to mutate real customer environments.

## ADR-008 through ADR-010 — frozen comparison semantics

The frozen provider comparison remains exactly:

- OpenAI `gpt-5.6-sol` / `openai.responses.v1.standard`;
- Google `gemini-3.7-flash` / `google.interactions.v1beta.stateless`;
- 8 public deterministic DEV probes;
- 2 repetitions per unit/candidate;
- maximum 32 live calls;
- zero warm-up, automatic retry, fallback, parallel provider call or provider seed;
- M1–M10, disqualifying hard gates and deterministic `NO_SELECTION` rule.

ADR-010 freezes the exact comparison executor and canonical plan:

```text
executor source blob                  4357aa101f5a15d5fc8376b17fa38ca51ea72ae3
plan SHA-256                          69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f
PR #39 merge                          903b977928ff19bc63c6ff35acd92f233af813be
```

The executor evaluates provider decisions only; it never executes TRACTIAN tools. Its provider-free fixture remains non-production evidence and cannot select a provider.

## ADR-011 — governed live execution capability

Issue #41 / PR #42 added and froze the operational layer required before a real ADR-009 run.

Frozen implementation:

```text
provider_live_execution.py blob       e2e2f2c7350efc0ab67490027347d76a6da54914
provider_live_task.py blob            6e86f008b5136c88cab574f64564709e1029a945
wrapper freeze                        research/frozen/provider-live-execution-wrapper-freeze-v1.json
ADR                                   docs/adr/011-governed-live-provider-execution-wrapper-2026-08-28.md
PR #42 merge                          7e8cbacf4f704bb1ec6a81b627c18cf7c595d703
```

The governed entrypoint is `GovernedProviderLiveTask`, not direct lower-level wrapper invocation. A future live task must receive both required secrets explicitly, use one canonical durable custody root, persist `CLAIMED` before each network-capable invocation, never replay claimed/uncertain attempts automatically and write only sanitized evidence.

Calls consumed remain 0/32 and no credential/account probe has occurred.

## ADR-012 — controlled action execution capability

Issue #45 / PR #46 froze the provider-free controlled action profile after falsification and full regression validation.

Frozen implementation:

```text
controlled_actions.py blob                 9e5f2d49ebc82303423f81ec8916b02c511f2a1e
controlled_action_evaluation.py blob       ae5f1a7777893941882196c8c2f3810676eba0a4
test_controlled_actions.py blob            357cc503d0b329d025abe004a2c780f6ee5ea2fa
test_controlled_action_evaluation.py blob  4b65fd911539092bb1126cc4e6db5dc985dad76b
freeze                                     research/frozen/controlled-action-execution-profile-freeze-v1.json
ADR                                        docs/adr/012-controlled-action-execution-profile-2026-08-28.md
PR #46 merge                               f45c568c24217b54ead8be01c7ac7e0cca2dea7e
```

Final exact-head validation:

```text
production-runtime #49                success
production tests                      170 passed
ADR-004 controller regression         12 passed
triggered workflows                   11 / 11 success
freeze self-check                     PASS
provider calls                        0
real customer mutations               0
```

All five canonical mutating ToolSpecs were exercised through deterministic supplied/test transport with explicit trusted authorization and `accepted=true` semantics. Unauthorized, unconfirmed, unknown-scope, cross-company and duplicate attempts remain contained before unsafe transport. A transport failure after durable claim remains consumed/uncertain and is not automatically replayed.

The default `ProductionRuntime` remains action-disabled and the default `ProductionEvaluator` remains read-only. `ControlledActionEvaluator` is separate and requires a matching B2 `ALLOWED` event plus `accepted=true` for executed actions.

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
controlled action proof                 5 / 5 CANONICAL ACTIONS / SYNTHETIC TRANSPORT
default runtime real actions            DISABLED
blanket real-customer mutations         NOT AUTHORIZED
```

The two largest provider/action implementation foundations are now complete. The live provider comparison is blocked only on its separately governed execution prerequisites; the next provider-free development priority is reliability/evaluation evidence.

## Immediate blockers and priorities

1. **Provider execution:** issue #44 may proceed only with one canonical durable custody root and both explicitly provisioned secrets; otherwise stop before attempt 0.
2. **Reliability/evaluation P0/P1:** implement EV-007 failure performance first, then EV-008 repeated-run stability and EV-011 customer-safe communication using provider-free/scripted paths.
3. **Integrated action evidence:** reuse ADR-012 for supplied/test action scenarios; do not create another action execution path or globally enable the default runtime.
4. **Scientific in parallel:** recover the exact original C4 score-row artifact only; do not reconstruct or rescore it.
5. **After provider evidence:** freeze candidate ID or `NO_SELECTION`, bind only an authorized selected provider behind ADR-006, then rerun reliability/stability/communication and integrated real Agent + Evaluator scenarios.
6. **Final delivery:** close reproducibility, evidence index, end-to-end demonstration and handoff before speculative P2 architecture work.

## Still forbidden

- reconstructing or rescoring the missing C4 score-row artifact;
- using ADR-009 calls for C4/scientific work;
- survivor/PREFERRED inference before the reporting freeze;
- semantic, FRESH_BLIND or LEGACY_LOCKED_TEST access without a separately opened scientific gate;
- changing ADR-008 candidates, population, thresholds or selection rules after any live call without prospective amendment;
- hidden provider retries, fallbacks, warm-ups or provider-side conversation state;
- credential/account probing merely to test availability;
- restarting through a new custody root after a reserved/consumed live run without prospective governance;
- provider-native TRACTIAN tool execution;
- weakening ADR-005 or bypassing `HarnessRunner.execute_tool()` for actions;
- deleting/releasing a durable action claim after uncertain transport failure to permit replay;
- treating ADR-012 as blanket authorization for real customer mutations;
- claiming a provider/model winner from fixture evidence;
- global architecture or production-readiness claims beyond current evidence.
