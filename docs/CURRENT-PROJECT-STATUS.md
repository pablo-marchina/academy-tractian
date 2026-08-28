# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-27 22:29 BRT  
**Canonical branch after merge:** `main`  
**Canonical main head at this checkpoint:** `fb1b959d7c2c0b185c9764d23f36746e3885dd7d`  
**Current reconciliation branch:** `docs/reconcile-production-evaluator-status`  
**Final delivery target:** 2026-09-08  
**Audited project source baseline:** [`../research/tractian-source-baseline-2026-08-27.md`](../research/tractian-source-baseline-2026-08-27.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Progress ledger:** [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)  
**Repository guide:** [`REPOSITORY-GUIDE.md`](REPOSITORY-GUIDE.md)  
**Machine-readable checkpoint:** [`../research/results/project-progress-checkpoint-2026-08-27-2229-brt.json`](../research/results/project-progress-checkpoint-2026-08-27-2229-brt.json)

This document is the **sole canonical human-readable source for current project state and authorization**. Frozen experiment artifacts remain authoritative for exact scientific semantics. Architecture/product progress recorded here does not itself authorize a scientific gate.

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
P12-C4 LOGO sensitivity                     FROZEN / 7 OF 7 OMISSIONS / INDEPENDENT RECOMPUTATION PASS
current authorized scientific gate          REQUIRED_PER_GROUP_AND_SLICE_REPORTING
per-group reporting                         AUTHORIZED / NOT EXECUTED
modality slices                             AUTHORIZED ONLY IN CURRENT REPORTING GATE / NOT EXECUTED
safety/failure-family slices                AUTHORIZED ONLY IN CURRENT REPORTING GATE / NOT EXECUTED
semantic evaluation                         NOT AUTHORIZED
FRESH_BLIND                                 NOT AUTHORIZED
LEGACY_LOCKED_TEST                          NOT AUTHORIZED
provider calls authorized now               0
current project-level PREFERRED             NONE
survivor/no-survivor decision               NOT AUTHORIZED YET
P0 Agent Controller runtime                 FROZEN_FOR_P0_CONTROLLER_SCOPE / ADR-004
first production runtime slice              MERGED / VALIDATED / PROVIDER_FREE / READ_ONLY
production deterministic evaluator          MERGED / VALIDATED / TRACE_ONLY / PROVIDER_FREE
runtime + deterministic evaluator           INTEGRATED ON THE SAME RunTrace
production mutating actions                 DISABLED / FAIL_CLOSED BEFORE TRANSPORT
production model/provider adapter           NOT SELECTED / NOT IMPLEMENTED
semantic production evaluation              NOT IMPLEMENTED / NOT AUTHORIZED
production reliability campaign             NOT YET EXECUTED
global final architecture                   UNFROZEN
production-readiness claim                  NOT AUTHORIZED
```

## Current scientific evidence

The C4 statistical chain remains frozen through LOGO:

1. `research/results/p12-c4-deterministic-scoring-freeze-2026-08-27.json` — 144/144 deterministic score rows, 0 independent score mismatches;
2. `research/results/p12-c4-bootstrap-20000-freeze-2026-08-27.json` — exact 20,000-resample whole-group percentile bootstrap;
3. `research/results/p12-c4-logo-sensitivity-freeze-2026-08-27.json` — exact seven leave-one-`asset_story_group`-out estimates per primary comparison.

Exact immutable statistical inputs remain:

```text
deterministic score rows SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bootstrap result SHA-256           08977c0d419144b885a7d2da6ffb73796ca43d80aa4e330a462d33c058464526
LOGO full result SHA-256           bc62cc45b4e3344861a152825096a8a1b28f41f2d831f86fd81de35964363f8c
```

LOGO independent validation reproduced the frozen historical C2 `logo_effects(...)` semantics exactly with 0 mismatch sections, 7 omitted groups and 6 retained groups per estimate.

Observed robustness evidence, without candidate-selection inference:

- E1 expected-read recall effect remains negative under every group omission;
- E1 extra-public-read effect remains negative under every group omission;
- E1 evidence-correctness effect is not sign-robust: it becomes positive when `asset_M102` is omitted;
- E1 task/reference-quality effect is not sign-robust for the same omission;
- S1 remains exactly measurement-identical to S0 on every preregistered primary safety contrast under all seven omissions;
- A11 reproduces the E1 LOGO pattern on evidence metrics and remains zero on decision/action/escalation/safety contrast metrics.

All four arm aggregates still contain nonzero confirmed hard-safety violations. Under the frozen preregistration, hard safety is an exact gate rather than a statistical tradeoff, but the formal survivor/no-survivor decision remains deferred until the remaining required reporting gate is frozen.

## Current scientific authorization boundary

The only current scientific gate remains:

### `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`

Authorized now:

- all per-`asset_story_group` outcomes required for reporting;
- modality slices: `investigate`, `execute`, `contextualize`;
- safety and failure-family slices;
- operational failure counts and denominators;
- validation and freeze of those reporting outputs.

The prepared reporting path remains blocked on the exact original evaluator-side deterministic-score artifact whose immutable identity is:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

That artifact must be recovered/provisioned exactly. Reconstruction, rescoring or replacement is forbidden.

Still forbidden:

- provider/model generation;
- score recomputation or mutation;
- candidate regeneration;
- survivor/PREFERRED decision before the reporting freeze closes;
- semantic evaluation;
- FRESH_BLIND;
- LEGACY_LOCKED_TEST;
- global final architecture freeze;
- production-readiness claims.

## Current architecture and production evidence

### P0 Agent Controller — frozen for scoped use

ADR-004 (`docs/adr/004-agent-controller-runtime-2026-08-27.md`) records the accepted P0 controller decision:

- explicit provider-free `AgentController`;
- `HarnessRunner.execute_tool()` remains the exclusive real tool-execution boundary;
- runner-owned identity/seed stay outside `DecisionSource` context;
- LangGraph remains a reversal/upgrade candidate only if durable cross-process state/checkpoint/HITL becomes a demonstrated requirement.

This is a scoped runtime decision, not a global architecture freeze and not a model/provider selection.

### First production runtime vertical slice — merged and validated

Issue #17 / PR #18 created the first distinct production surface under `src/academy_tractian/` and merged it to `main` as:

`b68dcabe3d2c2474c18e68aec082e77f1e74f3c8`

Validated PR head:

`5c566075b83c27de7a81eb724c0d37acdf8a1023`

Validation evidence:

- dedicated `production-runtime` Actions run `33132279628`: `completed / success`;
- production runtime tests: success;
- ADR-004 controller regression: success;
- all 12 workflows triggered against the final PR head: `completed / success`.

The slice exposes `ProductionRuntime`, preserves the canonical 18-operation ToolSpec registry, routes read tools through `HarnessRunner`, keeps all five mutating actions fail-closed at B2 before transport, and produces normalized `RunTrace` without importing model/provider/orchestration SDKs.

### Deterministic production evaluator — merged and integrated

Issue #20 / PR #21 added a production evaluation surface that consumes only the exact `RunTrace`, public canonical ToolSpec and explicit read-only/provider-free evaluation policy.

Merged production/evaluator commit:

`fb1b959d7c2c0b185c9764d23f36746e3885dd7d`

Validated PR head:

`53e4767bffe49162cbc13847ac69164275897275`

Validation evidence:

- `production-runtime` Actions run `33132937896` (#3): `completed / success`;
- all production runtime/evaluator tests: success;
- ADR-004 controller regression: success;
- all 11 workflows triggered against the final PR head: `completed / success`.

The production evaluator now deterministically checks, without evaluator-private truth:

- trace lifecycle/sequence integrity;
- production trace identity/config provenance;
- canonical ToolSpec proposal argument validity;
- identity/seed absence from model-controlled proposal/call fields;
- executed proposal → call → result → observation structure;
- policy-denial containment;
- zero executed mutating actions under the read-only production policy;
- provider-free trace behavior;
- terminal and safe-failure consistency;
- stable canonical trace hashing.

`IntegratedProductionRunner` executes `ProductionRuntime` once and evaluates that exact captured trace. Evaluation reports preserve independent checks and do not copy observation/tool-result bodies. They do not import `Scenario`, expected paths, research semantic evaluator stacks, model clients or provider clients.

This closes the deterministic structural integration portion of `REQ-017`; it does **not** establish semantic task correctness or full product acceptance.

## Current non-claims

The project does **not** currently claim that:

- any C4 arm is a final survivor, `PREFERRED` or final `FROZEN` candidate;
- required per-group/modality/failure reporting is complete;
- any arm is eligible for semantic evaluation;
- independent generalization has been measured;
- a production model/provider has been selected;
- production mutating actions are authorized or enabled;
- the production evaluator proves semantic conclusion correctness, expected-path correctness or evidence-oracle completeness;
- repeated-run production reliability has been established;
- RAG, memory, MCP, multi-agent or deployment topology is final;
- the global architecture is frozen;
- the system is production-ready.

## Delivery coverage state

The requested final product remains an integrated **industrial agent + trustworthy evaluation framework**. A provider-free read-only production runtime and deterministic trace evaluator are now integrated on the same run, materially advancing both planes. The remaining major delivery gaps include production action safety, model/provider decision and adapter, scenario/semantic coverage where separately authorized, reliability/security evidence, real-path demonstration and final architecture/handoff.

Priority remains:

```text
P0 requested capability + trustworthy evaluation
        ↓
P1 production/security/reliability/partner quality
        ↓
P2 optional complexity only with measured benefit
```

Two tracks may proceed in parallel only while their boundaries remain isolated:

1. **Scientific:** recover the exact frozen score artifact → execute/validate/freeze required reporting → advance only the gate explicitly opened by that freeze.
2. **Delivery:** govern consequential-action safety, compare/implement a production model/provider adapter under separate authorization, then extend real-path Agent + Evaluator reliability/security coverage without touching frozen C4 evidence.

## Planning pointers

- **What happens next:** [`NEXT-STEPS.md`](NEXT-STEPS.md)
- **What final delivery must prove:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)
- **General architecture:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)
- **Macro plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)
- **Historical ledger:** [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)

When the required reporting gate closes, freeze it first, then update status/checkpoint/ledger/next steps before considering any survivor/no-survivor decision.