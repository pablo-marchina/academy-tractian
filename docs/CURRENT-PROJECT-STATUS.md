# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-28 01:16 BRT  
**Canonical branch after merge:** `main`  
**Canonical main head at this checkpoint:** `c3d7ecbaf02a20276f84e4f6ff756c0bdf3779d9`  
**Current reconciliation branch:** `docs/reconcile-provider-live-authorization`  
**Final delivery target:** 2026-09-08  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Progress ledger:** [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)  
**Machine-readable checkpoint:** [`../research/results/project-progress-checkpoint-2026-08-28-0116-brt.json`](../research/results/project-progress-checkpoint-2026-08-28-0116-brt.json)

This document is the **sole canonical human-readable source for current project state and authorization**. Frozen scientific artifacts, ADRs and frozen production authorization packets remain authoritative for their exact semantics. Production authorization does not alter the scientific C4 gate.

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
survivor/no-survivor decision                NOT AUTHORIZED YET
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
concrete OpenAI/Gemini HTTP clients          MERGED / VALIDATED / ADR-009
bounded production live comparison           AUTHORIZED_FOR_SEPARATE_TASK / MAX 32 / ADR-009
production live provider calls executed      0
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

The original artifact must be recovered/provisioned exactly. Reconstruction, rescoring or substitution remains forbidden.

Authorized scientific work remains limited to the frozen reporting gate: per-group outcomes, `investigate` / `execute` / `contextualize` modality slices, safety/failure-family slices and operational failure counts/denominators. The production provider authorization below does **not** authorize C4 generation, rescoring, survivor selection, semantic judging or blind-partition access.

## Production architecture state

### ADR-004 through ADR-007 — existing frozen boundaries

The accepted runtime remains application-owned:

```text
request
→ AgentController
→ provider-neutral DecisionSource
→ ControllerDecision / ToolProposal
→ HarnessRunner.execute_tool()
→ B1 canonical argument validation
→ ADR-005/B2 action-safety boundary
→ TRACTIAN API transport when permitted
→ normalized RunTrace
→ deterministic production evaluator
```

Identity, seed, action authorization state and evaluator-private truth remain outside provider control. All five canonical mutating actions remain disabled in the real production runtime.

### ADR-008 — exact provider comparison design

The frozen comparison design contains:

- local provider-free scripted/null baseline;
- OpenAI `gpt-5.6-sol` / `openai.responses.v1.standard`;
- Google `gemini-3.7-flash` / `google.interactions.v1beta.stateless`;
- 8 public deterministic DEV probes;
- 2 repetitions per probe/candidate;
- maximum 32 future live calls;
- zero warm-up/retry/fallback/provider seed;
- M1–M10 + hard gates + deterministic Pareto/`NO_SELECTION` rule.

The population contains no private oracle, FRESH_BLIND or LEGACY_LOCKED_TEST material.

### ADR-009 — concrete provider clients + bounded authorization

Issue #35 / PR #36 added the concrete SDK-free HTTP clients and froze the bounded execution envelope.

Validated client implementation:

```text
corrected implementation head       3b823c498811a138de60acd65b280cef5dfd2bb1
provider_clients.py git blob         e78807bdfd4fd0ca9840fa2d9e6c62474237ee45
production-runtime #23               success
triggered workflows                  11 / 11 success
```

The first implementation attempt is preserved. Head `b0a5bc8c2dbea0041ac0324e6471b09b9e68b644` produced `105 passed / 2 failed` in production-runtime #22 because privacy tests rejected unnecessary internal `idempotency` vocabulary in the provider prompt. The fix hardened the prompt; no live call occurred in either attempt.

Frozen authorization packet:

`research/frozen/provider-model-live-comparison-authorization-v1.json`

```text
git blob                            5690414564ccddb07184c333fdf79f4ee2fb7788
provider-free packet head           ad1c427a00a518424fa058c008ffc661df980c60
provider-live-authorization #1      success
production-runtime #24              success
packet-head workflows               12 / 12 success
final ADR head                      a9b3b3221e132c08a2806685ac60c7d8db0d375f
provider-live-authorization #2      success
production-runtime #25              success
provider-comparison-design #5       success
final-head workflows                13 / 13 success
PR #36 merge                        c3d7ecbaf02a20276f84e4f6ff756c0bdf3779d9
```

ADR-009 therefore makes the packet effective **only for a separate governed production-comparison execution task**. It authorizes at most the frozen 32-call envelope. It does not itself execute calls or select a winner.

Current execution state:

```text
live comparison authorization       EFFECTIVE / BOUNDED / SEPARATE TASK ONLY
maximum authorized production calls 32
live calls consumed                  0
credentials/account probed           0
provider selected                    NO
OpenAI selected                      NO
Google selected                      NO
NO_SELECTION still valid             YES
production actions enabled           NO
```

Any route/model/schema change, hidden retry/fallback, need for adapter repair, custody/provenance failure or call-budget issue requires the frozen stop/amendment behavior. Operational failures remain in denominators.

## Immediate blockers and priorities

1. **Scientific:** recover the exact original C4 score-row artifact and close required reporting without reconstruction/rescoring.
2. **Production:** implement the separate ADR-009 comparison execution harness provider-free first: exact population/order loading, credential injection boundary, sanitized attempt/usage ledger, M1–M10 aggregation and deterministic selection.
3. Only after that execution harness passes provider-free may the authorized live packet be consumed; live execution still requires actual credentials to be provisioned to that separate execution task.
4. Keep production actions disabled while trusted permission/scope/confirmation + durable idempotency sources remain absent.
5. After provider evidence, run reliability/failure/security/observability regressions and integrate the chosen result — or `NO_SELECTION` — into the final delivery.

## Still forbidden

- reconstructing or rescoring the missing C4 score-row artifact;
- C4 provider/model generation under ADR-009;
- survivor/PREFERRED inference before the reporting freeze;
- semantic, FRESH_BLIND or LEGACY_LOCKED_TEST access;
- changing ADR-008 candidates/thresholds after the first live comparison call without prospective amendment;
- hidden provider retries, fallbacks or warm-ups;
- provider-native TRACTIAN tool execution;
- production mutating actions before a separate action-enablement decision;
- claiming a provider/model winner before the frozen comparison completes;
- global architecture or production-readiness claims beyond current evidence.
