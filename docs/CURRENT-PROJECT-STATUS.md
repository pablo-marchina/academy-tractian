# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-28 00:37 BRT  
**Canonical branch after merge:** `main`  
**Canonical main head at this checkpoint:** `bde8ff21d7a6c91c970b397d760d94d3f4ac26c3`  
**Current reconciliation branch:** `docs/reconcile-provider-comparison-design`  
**Final delivery target:** 2026-09-08  
**Audited project source baseline:** [`../research/tractian-source-baseline-2026-08-27.md`](../research/tractian-source-baseline-2026-08-27.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Progress ledger:** [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)  
**Machine-readable checkpoint:** [`../research/results/project-progress-checkpoint-2026-08-28-0037-brt.json`](../research/results/project-progress-checkpoint-2026-08-28-0037-brt.json)

This file is the **sole canonical human-readable current-state and authorization snapshot**. Frozen experiment/result artifacts remain authoritative for exact scientific semantics, while ADRs are authoritative only for their stated architecture/product scopes. Capability never implies authorization.

## Executive state

```text
Project North Star                           maximize actual TRACTIAN/Inteli delivery under P1-P4
Benchmark Integrity Gate                    CLOSED
P12 evaluation protocol                     FROZEN
P12-C1                                      CLOSED / DETERMINISTIC FAIL / NO ARM QUALIFIED
P12-C2                                      CONSUMED_OPERATIONAL_FAILURE / 31 OF 36 / NO SCORING
P12-C3                                      CONSUMED_TERMINAL_OPERATIONAL_FAILURE / 3 OF 36 / NO SCORING
P12-C4 common parents                       PASS / 36 OF 36
P12-C4 local factorial outputs              PASS / 144 OF 144
P12-C4 packet                               FROZEN_COMPLETE_C4_PACKET
P12-C4 deterministic scoring                FROZEN / 144 OF 144 / 0 RECOMPUTATION MISMATCHES
P12-C4 bootstrap 20k                        FROZEN / PASS / INDEPENDENT RECOMPUTATION PASS
P12-C4 LOGO sensitivity                     FROZEN / 7 OF 7 / INDEPENDENT RECOMPUTATION PASS
current authorized scientific gate          REQUIRED_PER_GROUP_AND_SLICE_REPORTING
required reporting                          AUTHORIZED / BLOCKED ON EXACT SCORE-ROW ARTIFACT
survivor/no-survivor                        NOT AUTHORIZED
semantic evaluation                         NOT AUTHORIZED
FRESH_BLIND                                 NOT AUTHORIZED
LEGACY_LOCKED_TEST                          NOT AUTHORIZED
provider/model calls authorized now         0
current project-level PREFERRED             NONE
P0 Agent Controller                         FROZEN_FOR_P0_CONTROLLER_SCOPE / ADR-004
production runtime slice                    MERGED / VALIDATED / PROVIDER_FREE / READ_ONLY
production deterministic evaluator          MERGED / VALIDATED / SAME RunTrace / TRACE_ONLY
production action-safety policy             FROZEN / ADR-005
production mutating actions                 DISABLED / FAIL_CLOSED BEFORE TRANSPORT
provider-neutral DecisionSource             FROZEN / ADR-006
model-call provenance                       FROZEN / ADR-007
provider comparison preregistration         PREREGISTERED_PROVIDER_FREE_ONLY / ADR-007
exact provider/model comparison design      FROZEN_FOR_LIVE_COMPARISON_AUTHORIZATION_DESIGN / ADR-008
exact future live candidate routes          FROZEN AS COMPARISON INPUTS / NOT SELECTED
real production provider clients            NOT IMPLEMENTED
live provider/model comparison              NOT AUTHORIZED / NOT EXECUTED
production provider/model selected          NO
semantic production evaluation              NOT IMPLEMENTED / NOT AUTHORIZED
production reliability campaign             NOT YET EXECUTED
global final architecture                   UNFROZEN
production-readiness claim                  NOT AUTHORIZED
```

## Scientific evidence and blocker

The scientific chain remains frozen through deterministic scoring, 20,000-resample whole-group bootstrap and seven-group LOGO sensitivity. Exact immutable identities remain:

```text
deterministic score rows SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bootstrap result SHA-256           08977c0d419144b885a7d2da6ffb73796ca43d80aa4e330a462d33c058464526
LOGO full result SHA-256           bc62cc45b4e3344861a152825096a8a1b28f41f2d831f86fd81de35964363f8c
```

The **only authorized scientific gate** remains `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`, covering per-`asset_story_group` outcomes, modality slices (`investigate`, `execute`, `contextualize`), safety/failure-family slices and operational-failure denominators.

Execution remains blocked on the exact original evaluator-side deterministic-score artifact:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

That artifact must be recovered/provisioned exactly. Reconstruction, replacement or rescoring is forbidden. Until reporting is independently validated and frozen, survivor/PREFERRED inference remains unauthorized.

## Production architecture state

### ADR-004 — controller/runtime

The P0 controller is the explicit application-owned provider-free `AgentController`. `HarnessRunner.execute_tool()` remains the exclusive real tool-execution boundary. Identity and seed remain outside `DecisionSource` control. This is not a global architecture freeze.

### Production runtime + evaluator

The first distinct `src/academy_tractian/` runtime slice and deterministic production evaluator are merged and validated. The integrated path produces and evaluates the **same `RunTrace`** without private/gold inputs or semantic judges.

The canonical 18-operation ToolSpec remains the stable tool contract. All five mutating actions remain blocked before transport.

### ADR-005 — action safety

The layered action policy is frozen, including permission, known/same-company scope, justification, requester confirmation, exact action fingerprint, runtime-owned idempotency and duplicate protection. Real runtime state still has:

```text
actions_enabled                         false
real action permissions                     0
real resource/company bindings              0
requester confirmations                     0
durable idempotency store               absent
mutating action transport calls              0
```

Policy capability is not action authorization.

### ADR-006 — provider-neutral decision adapter

`ProviderDecisionSource` freezes a provider-neutral strict adapter boundary. It projects only public ToolSpecs and bounded controller context, rejects malformed/duplicate-key/unknown-tool output, and preserves B1 argument-validation and ADR-005/B2 action-authorization ownership.

No provider SDK or provider-owned agent/tool loop is part of this neutral contract.

### ADR-007 — model-call provenance

A future provider client may emit one sanitized self-verifying `provider-model-call-v1` record per client invocation. Raw request/response bodies, exception text, credentials, identity/seed, action authorization state and private evaluator truth are forbidden from that telemetry.

Provider-free evaluator mode still requires zero `model_call` events. Traced-provider mode is structural only and does not itself authorize live inference or semantic evaluation.

### ADR-008 — exact provider/model comparison design

Issue #32 / PR #33 froze the **comparison design**, not a provider selection.

Exact validated design artifacts:

```text
manifest Git blob                9c3d0901414445bd4de557d5ef1d2f68a15c883b
public DEV population Git blob   abd6a7d973a8779f425c3607d963e29f15db09e5
population file SHA-256          561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251
protocol Git blob                c43b11d3c25a209f20e40ee90007a9e1e504ae5d
validator Git blob               4f6bc39b44e8eb27987f7312335dfe35a65b146a
final validated PR head          2eeae416690bcd3383f714a2446687a2d73d8dfc
merge commit                     bde8ff21d7a6c91c970b397d760d94d3f4ac26c3
```

Frozen comparison inputs:

- local scripted/null baseline — zero inference calls and ineligible for production selection;
- OpenAI `gpt-5.6-sol` via `openai.responses.v1.standard` — quality-frontier candidate;
- Google `gemini-3.7-flash` via `google.interactions.v1beta.stateless` — lower-cost hosted candidate.

The population is a new prospective public set of **8 synthetic DecisionSource probes × 2 repetitions**. Historical evaluator-private E9/E10/E14 `real_task_quality` is explicitly not reused as M4 ground truth.

A later separately authorized comparison is bounded to **32 maximum live calls**: 8 units × 2 repetitions × 2 live candidates, with zero warm-up, zero automatic retry, zero provider fallback, no provider seed and no parallel live execution. Operational failures remain in denominators.

M1–M10, hard gates, stopping/amendment rules and the deterministic selection rule are frozen before any live call. Hard-gate violations are disqualifying. The rule explicitly permits `NO_SELECTION`; there is no weighted global score.

Validation history is preserved:

```text
initial head 617ed300...       production-runtime #17 FAIL
cause                           validator relative-vs-absolute path normalization only
corrected head 0dc3753f...     12 / 12 workflows SUCCESS
comparison-design #2           SUCCESS
production-runtime #18         SUCCESS incl. ADR-004 regression
final ADR head 2eeae416...     12 / 12 workflows SUCCESS
comparison-design #4           SUCCESS
production-runtime #20         SUCCESS incl. ADR-004 regression
provider/model calls               0
```

The failed first validation changed no candidate, population, metric, threshold or authorization and remains visible in history.

## Authorization boundary after ADR-008

Authorized now on the **product** track:

- provider-free implementation of concrete provider clients conforming to ADR-006/ADR-007;
- a focused live-comparison authorization packet that pins credentials/account/readiness policy, exact client implementations, frozen design identities and execution custody;
- provider-free tests that prove those clients cannot own the agent/tool loop, retry or fallback silently;
- reliability/security/observability work that does not make a provider/model call or enable actions.

Still **not authorized**:

- API-key/credential probing;
- any real OpenAI/Google/other inference request;
- executing the 32-call comparison;
- ranking/selecting/PREFERRED claims from documentation alone;
- production mutating action execution;
- semantic judge evaluation;
- C4 rescoring/reconstruction;
- survivor/PREFERRED scientific inference before reporting freeze;
- FRESH_BLIND or LEGACY_LOCKED_TEST;
- global final-architecture freeze;
- production-readiness claims.

## Immediate priorities

Two tracks remain intentionally independent:

1. **Scientific:** recover/provision the exact `b1c877...` score-row artifact; run the reporting-only runner; independently validate and freeze the required per-group/slice report; advance only to the next gate explicitly opened by that freeze.
2. **Product:** create the separate live-comparison authorization task and provider-specific client implementations **provider-free first**. Do not probe credentials or call a model until a later explicit authorization exists.

After a governed live comparison can be executed and frozen, the product path may select a provider/model or return `NO_SELECTION`, then proceed to the remaining integrated reliability/security/observability and final-demonstration evidence. Action enablement remains a separate decision.

## Delivery timing

The master plan remains:

```text
2026-08-27 → 2026-08-29   close scientific decision path where artifact custody permits
2026-08-30 → 2026-09-02   freeze remaining material product decisions + implement core
2026-09-03 → 2026-09-05   reliability/security/integrated evaluation
2026-09-06 → 2026-09-07   final documentation + demonstration evidence
2026-09-08                delivery target
```

P2 complexity such as RAG/vector DB, persistent memory, MCP, multi-agent topology or rich UI remains deferred unless a measured P0/P1 requirement justifies it.
