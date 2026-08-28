# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-28 02:00 BRT  
**Canonical branch after merge:** `main`  
**Canonical main head at this checkpoint:** `903b977928ff19bc63c6ff35acd92f233af813be`  
**Current reconciliation branch:** `docs/reconcile-provider-comparison-executor`  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Historical ledger:** [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)  
**Latest chronological entry:** [`progress/026-provider-comparison-executor-freeze-2026-08-28.md`](progress/026-provider-comparison-executor-freeze-2026-08-28.md)  
**Machine checkpoint:** [`../research/results/project-progress-checkpoint-2026-08-28-0200-brt.json`](../research/results/project-progress-checkpoint-2026-08-28-0200-brt.json)

This document is the **sole canonical human-readable source for current project state and authorization**. Frozen scientific artifacts, ADRs and production authorization packets remain authoritative for their exact semantics. Production authorization does not alter the C4 scientific gate.

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
canonical comparison plan                    32 ATTEMPTS / SHA-256 69691adf…
provider-free fixture                        PASS / NO_SELECTION / NON-PRODUCTION EVIDENCE
production live provider calls consumed      0 / 32
production provider/model selected           NO
production credentials probed                NO
production reliability campaign              NOT YET EXECUTED
global final architecture                    UNFROZEN
production-readiness claim                   NOT AUTHORIZED
```

## Scientific critical path — unchanged

The scientific path remains frozen through LOGO and blocked at `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`.

Exact missing evaluator-side deterministic score-row artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

The original artifact must be recovered/provisioned exactly. Reconstruction, rescoring or substitution remains forbidden. Production provider authorization does **not** authorize C4 generation, rescoring, semantic judging, survivor selection or blind-partition access.

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

Identity, seed, action authorization state and evaluator-private truth remain outside provider control. All five canonical mutating actions remain disabled.

### ADR-008 / ADR-009 — frozen live-comparison envelope

The production comparison remains exactly:

- OpenAI `gpt-5.6-sol` / `openai.responses.v1.standard`;
- Google `gemini-3.7-flash` / `google.interactions.v1beta.stateless`;
- 8 public deterministic DEV probes;
- 2 repetitions per unit/candidate;
- 32 maximum live calls;
- zero warm-up, automatic retry, fallback, parallel provider call or provider seed;
- M1–M10, disqualifying hard gates and deterministic `NO_SELECTION` rule.

Authorization packet:

`research/frozen/provider-model-live-comparison-authorization-v1.json`

It is effective only for a separately governed production-comparison execution task. Calls consumed remain **0**.

### ADR-010 — exact provider comparison executor

Issue #38 / PR #39 froze the executor after provider-free validation.

Canonical executor evidence:

```text
executor source blob                  4357aa101f5a15d5fc8376b17fa38ca51ea72ae3
executor tests blob                   6663177bb96a8fdffd15fa64c9cc7e5a92edf2e3
fixture validator blob                563b47e14dbf6119deef167ae8926261c38ed07a
provider-free fixture blob            7c3972b2e467de4a21c6ef353f5427bf7651b4d9
plan SHA-256                          69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f
freeze artifact                       research/frozen/provider-comparison-executor-freeze-v1.json
ADR                                   docs/adr/010-provider-comparison-executor-2026-08-28.md
PR #39 merge                          903b977928ff19bc63c6ff35acd92f233af813be
```

Final head `dd15ce32362247066edf0a476f8a9e93eb6cdbe8` passed **14/14** triggered workflows, including:

```text
provider-comparison-executor   #3 / success
production-runtime             #31 / success
provider-model-comparison      #6 / success
provider-live-authorization    #3 / success
all research regressions             success
```

The provider-free fixture exercised all 32 potential attempts without network calls and produced `NO_SELECTION` by construction because fixture evidence cannot select a production provider. It validates execution/evidence plumbing, not model quality.

The executor:

- verifies frozen design/population/authorization/client identities;
- materializes canonical attempt indexes `0..31` and parity-balanced candidate order;
- exposes no budget reset and rejects attempt 33;
- converts only public frozen contexts to `ControllerContext`;
- never owns TRACTIAN tool execution;
- adjudicates the eight public rubrics deterministically;
- aggregates M1–M10 without semantic/private judges;
- preserves operational failures in denominators;
- fails closed on custody/provenance violations;
- returns `NO_SELECTION` for fixture/incomplete/unresolved evidence;
- never persists raw provider request/response/credential material.

Preserved failures remain part of evidence:

1. initial #38 head changed the ADR-009-frozen package export blob; production-runtime #27 returned 130 pass / 1 governance failure. The export was restored rather than the validator weakened;
2. first dedicated executor workflow failed before fixture evaluation because the standalone script lacked repo-root import bootstrap. The import bootstrap was fixed without changing protocol/metrics.

Neither failure consumed a provider call.

## Current production execution state

```text
live authorization                    EFFECTIVE / BOUNDED / ADR-009
executor                              FROZEN / ADR-010
maximum live calls                    32
calls consumed                         0
first live attempt executed           NO
credentials/account probed            NO
provider selected                     NO
NO_SELECTION remains valid            YES
production actions enabled            NO
```

The next production step is therefore no longer executor implementation. It is a **separate live-comparison execution task** using the exact ADR-010 executor. The task must not make a credential/capability probe. If required secrets are not explicitly provisioned, it must stop before attempt 0 and record an operational blocker without changing candidates/routes.

## Immediate blockers and priorities

1. **Scientific:** recover the exact original C4 score-row artifact; do not reconstruct/rescore it.
2. **Production:** prepare the separate ADR-009/010 live execution surface, with explicit secret injection outside provider-client code and fail-before-attempt-0 behavior when credentials are absent.
3. Execute the exact 32-attempt comparison only when required secrets are provisioned; every actual invocation consumes the frozen budget and remains in denominators.
4. Freeze the live result and deterministic selection (`candidate_id` or `NO_SELECTION`) without threshold/candidate changes.
5. Keep all production mutating actions disabled.
6. After provider evidence, run reliability/failure/security/observability regressions and integrate the selected provider — or safe `NO_SELECTION` outcome — into final delivery evidence.

## Still forbidden

- reconstructing or rescoring the missing C4 score-row artifact;
- using ADR-009 calls for C4/scientific work;
- survivor/PREFERRED inference before the reporting freeze;
- semantic, FRESH_BLIND or LEGACY_LOCKED_TEST access;
- changing ADR-008 candidates, population, thresholds or selection rules after any live call without prospective amendment;
- hidden provider retries, fallbacks, warm-ups or provider-side conversation state;
- credential/account probing merely to test availability;
- provider-native TRACTIAN tool execution;
- production mutating actions before separate action-enablement evidence/decision;
- claiming a provider/model winner from fixture evidence;
- global architecture or production-readiness claims beyond current evidence.
