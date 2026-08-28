# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-28 03:25 BRT  
**Canonical branch after merge:** `main`  
**Canonical main head at this checkpoint:** `7e8cbacf4f704bb1ec6a81b627c18cf7c595d703`  
**Current reconciliation branch:** `docs/reconcile-adr-011-live-wrapper`  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Historical ledger:** [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)  
**Latest chronological entry:** [`progress/027-governed-live-provider-wrapper-freeze-2026-08-28.md`](progress/027-governed-live-provider-wrapper-freeze-2026-08-28.md)  
**Machine checkpoint:** [`../research/results/project-progress-checkpoint-2026-08-28-0325-brt.json`](../research/results/project-progress-checkpoint-2026-08-28-0325-brt.json)

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
production mutating actions                  DISABLED
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

The application-owned production path remains:

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

Identity, seed, action authorization state and evaluator-private truth remain outside provider control. All canonical mutating actions remain disabled in the current production runtime.

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

Final provider-free validation before merge:

```text
production-runtime #41                success
production tests                      146 passed
ADR-004 controller regression         12 passed
triggered workflows                   11 / 11 success
real provider calls                   0
credential/account probes             0
```

The governed entrypoint is `GovernedProviderLiveTask`, not direct lower-level wrapper invocation. A future live task must:

1. receive both required secret values explicitly;
2. use one canonical durable custody root;
3. reserve an exclusive sanitized ADR-009 custody marker before run preparation;
4. use only the fixed `<custody_root>/run` path;
5. persist `CLAIMED` before each network-capable executor invocation;
6. never automatically retry/resume a claimed or uncertain attempt;
7. preserve all operational failures in the frozen denominators;
8. write only sanitized custody/ledger/result evidence.

If a secret is absent, preparation fails before custody creation/attempt 0. No account/capability probe is permitted.

If preparation fails after authorization custody is reserved, the custody marker remains and blocks normal restart/reset. Switching to another custody root is not implicitly authorized and would require a new prospective custody decision.

## Current production execution state

```text
live authorization                    EFFECTIVE / BOUNDED / ADR-009
executor                              FROZEN / ADR-010
live operational wrapper              FROZEN / ADR-011
maximum live calls                    32
calls consumed                         0
first live attempt executed           NO
credentials/account probed            NO
provider selected                     NO
NO_SELECTION remains valid            YES
production actions enabled            NO
```

The implementation needed for safe live execution is now complete. The next provider step is a **separate governed live execution task**, not additional wrapper development.

## Immediate blockers and priorities

1. **Provider execution:** create the separate ADR-009/010/011 live task. It may proceed only with one canonical durable custody root and both explicitly provisioned secrets; otherwise stop before attempt 0.
2. **Provider result:** if execution occurs, consume the exact envelope once and freeze the resulting candidate ID or `NO_SELECTION` without changing the frozen design after the fact.
3. **Action P0 in parallel:** develop/validate the controlled action-authorization source/profile provider-free, reusing ADR-005. Do not enable real production mutations yet.
4. **Evaluation P0/P1 in parallel:** implement EV-007 failure performance, EV-008 repeated-run stability and EV-011 customer-safe communication using provider-free/scripted paths first.
5. **Scientific in parallel:** recover the exact original C4 score-row artifact only; do not reconstruct or rescore it.
6. **After provider evidence:** bind the selected provider, or explicitly handle `NO_SELECTION`, then run the integrated real Agent + Evaluator regression/demo path.

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
- production mutating actions before separate action-enablement evidence/decision;
- claiming a provider/model winner from fixture evidence;
- global architecture or production-readiness claims beyond current evidence.
