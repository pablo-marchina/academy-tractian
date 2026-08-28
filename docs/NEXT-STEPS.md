# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE / canonical short-horizon execution plan  
**Planning checkpoint:** 2026-08-27 22:47 BRT  
**Current state source:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Macro plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file answers only: **what should be done next from the current evidence-backed state?** Exact scientific authorization remains governed by `CURRENT-PROJECT-STATUS.md` and the applicable frozen artifacts/results.

## 1. Current execution objective

The project has two deliberately isolated short-horizon tracks:

```text
SCIENTIFIC TRACK                              DELIVERY TRACK
REQUIRED_PER_GROUP_AND_SLICE_REPORTING        runtime + deterministic evaluator integrated
        ↓                                             ↓
reporting freeze                              ADR-005 action-safety policy frozen
        ↓                                             ↓
survivor/no-survivor if authorized            model/provider DecisionSource comparison ← NEXT
        ↓                                             ↓
later child gates only if opened              trusted auth/idempotency + real-path evidence
```

Neither track may silently authorize the other.

The current scientific gate remains:

```text
REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

The production path remains provider-free and all five mutating canonical actions remain fail-closed before transport. ADR-005 freezes the required action-safety protocol but **does not authorize action execution**.

## 2. Immediate scientific sequence — highest scientific priority

### Step S1 — Recover the exact frozen deterministic-score artifact

The prepared reporting path remains blocked until the **original** evaluator-side file is available outside the Git repository with exact identity:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
geometry 36 common parents × 4 arms
```

Do not reconstruct, rescore, regenerate or substitute this artifact.

### Step S2 — Provision and execute the already-prepared reporting-only path

Once the exact artifact is recovered:

1. provision it into evaluator-side storage outside the repo through the fail-closed provisioner in PR #10;
2. run `p12_c4_required_reporting.py` against those exact bytes;
3. run `p12_c4_validate_required_reporting.py` independently;
4. require exact input hashes, geometry, group classifications, denominators and aggregate reconstruction to pass;
5. require zero prohibited provider/private/semantic/blind operations.

### Step S3 — Freeze required per-group and slice reporting

Required outputs remain:

- per-arm outcomes for all seven independent `asset_story_group` groups;
- modality slices: `investigate`, `execute`, `contextualize`, each with explicit denominators;
- safety/failure-family slices with explicit denominators;
- operational failure counts and denominators;
- no candidate-promotion inference inside the reporting runner.

### Step S4 — Advance only the gate explicitly opened by the reporting freeze

A reporting closure may authorize a **survivor/no-survivor decision** using the already-frozen hard gates, bootstrap, LOGO and reporting evidence. It does not automatically authorize semantic evaluation, FRESH_BLIND or LEGACY_LOCKED_TEST.

## 3. Immediate delivery sequence — can run in parallel without C4 contamination

ADR-004, the production runtime, deterministic evaluator and ADR-005 now provide a stable provider-free skeleton. The next P0 decision is the missing production `DecisionSource` adapter/model-provider boundary.

### Step D1 — Production action-safety policy — COMPLETE / FROZEN

ADR-005 freezes a layered runtime-owned action policy covering:

- declared permission;
- global execution switch;
- runtime/model authorization-state isolation;
- canonical argument and justification requirements;
- fail-closed known/same-company resource scope;
- requester confirmation bound to the exact action fingerprint;
- idempotency key bound to that exact fingerprint;
- duplicate-action rejection before transport.

The real runtime still fixes `actions_enabled = false`, grants zero action permissions, provisions no action confirmations/idempotency keys/resource mappings and performs zero action transport calls.

Actual action enablement requires a **separate future governed decision** backed by trusted real authorization/scope/confirmation state, durable idempotency semantics and failure/retry evidence.

### Step D2 — Define and compare the production model/provider `DecisionSource` adapter — NEXT

Start provider-free. Freeze the adapter contract and comparison protocol before any live provider call.

Required baseline invariants:

- implementation plugs into ADR-004 `DecisionSource` and cannot bypass `AgentController` or `HarnessRunner`;
- output is strictly one typed `ControllerDecision` per turn;
- provider/model never receives runtime identity, seed, action authorization, idempotency state or evaluator-private truth;
- tool arguments remain constrained by canonical ToolSpec/B1;
- model failure, malformed output and timeout/error paths fail closed through the existing controller boundary;
- provider-specific code stays behind a replaceable adapter interface;
- provider/model selection is distinct from historical C4 serving-route qualification.

Compare at minimum:

1. a **null/provider-free scripted adapter** for deterministic contract testing;
2. a strong quality-frontier provider/model candidate;
3. a feasible lower-cost/local/open candidate;
4. any additional candidate only if it represents a credible Pareto trade-off.

Before authorizing live calls, preregister measurements for structured-decision adherence, tool-selection/argument validity, task quality on allowed development material, failure behavior, latency, reliability, resource/cost, portability and trace integrity.

**Provider calls remain unauthorized now.** The first implementation step should therefore be adapter interfaces, deterministic fake-provider tests, comparison matrix/protocol and fail-closed conformance checks. Any live comparison needs its own explicit authorization.

### Step D3 — Prepare trusted production action authorization/idempotency integration

This can proceed separately from model/provider comparison, but must not enable actions yet.

Define the production source of truth for:

- user permissions;
- user/company identity binding;
- resource → company ownership;
- requester confirmation lifecycle;
- durable idempotency key reservation/consumption;
- retry, timeout and ambiguous-result handling;
- audit retention.

ADR-005 is the contract these sources must satisfy. Do not weaken the policy to match an easier persistence implementation.

### Step D4 — Extend real-path Agent + Evaluator coverage after D2/D3 evidence

Build toward:

```text
request
→ ProductionRuntime
→ production DecisionSource adapter
→ AgentController
→ HarnessRunner / canonical ToolSpec
→ supplied TRACTIAN API
→ RunTrace
→ ProductionEvaluator
→ customer-safe response + evaluation report
```

Required real-path coverage should include:

- contextualize;
- investigate;
- clarify / abstain;
- escalate with useful handoff;
- execute only after a separate action-enablement decision;
- partial/unavailable tools or data;
- conflicting/inconclusive evidence;
- model/provider failure fallback;
- per-run deterministic evaluation.

### Step D5 — Reliability, security and observability evidence

Once a real DecisionSource/provider path exists, run repeated/fault-injected tests for:

- EV-007 failure performance;
- EV-008 stability/repeated-run reliability;
- authorization/resource-scope/idempotency;
- failure continuity and human fallback;
- latency/resource/cost behavior;
- trace/diagnostic coverage;
- customer-safe boundary regressions where deterministically testable.

Semantic/judge evaluation remains a separate gate and must not be introduced merely to fill a rubric row.

## 4. Work intentionally deferred

Do not implement or freeze merely because available:

- RAG/vector DB/reranking;
- multi-agent decomposition;
- persistent agent memory;
- MCP as an additional agent-facing topology;
- adaptive routing/model selection;
- rich UI;
- final deployment topology.

Each remains P2 unless a P0/P1 bottleneck and controlled evidence justify it.

## 5. Critical path to final delivery

The scientific path remains sequential:

```text
FROZEN_C4_DETERMINISTIC_SCORING
        ↓
FROZEN_C4_BOOTSTRAP_20000
        ↓
FROZEN_C4_LEAVE_ONE_GROUP_OUT_SENSITIVITY
        ↓
REQUIRED_PER_GROUP_AND_SLICE_REPORTING   ← SCIENTIFIC CURRENT
        ↓
C4 survivor / no-survivor decision
        ↓
semantic child gate only if explicitly authorized
        ↓
candidate/evaluator freeze
        ↓
independent validation where authorized
```

The non-contaminating product path now progresses in parallel:

```text
ADR-004 P0 CONTROLLER FROZEN
        ↓
PRODUCTION RUNTIME + DETERMINISTIC EVALUATOR MERGED
        ↓
ADR-005 ACTION-SAFETY POLICY FROZEN / ACTIONS STILL OFF
        ↓
MODEL/PROVIDER DECISIONSOURCE COMPARISON       ← DELIVERY CURRENT
        ↓
TRUSTED AUTH/SCOPE/CONFIRMATION/IDEMPOTENCY INTEGRATION
        ↓
SEPARATE ACTION-ENABLEMENT DECISION IF JUSTIFIED
        ↓
INTEGRATED REAL AGENT + EVALUATOR PATH
        ↓
P0/P1 regression + reliability/security evidence
        ↓
architecture freeze when all material choices are justified
        ↓
real-path demo + reproducible handoff
        ↓
2026-09-08 final delivery
```

## 6. Deadline protection

The final delivery target remains 2026-09-08. The scientific artifact blocker must not idle non-contaminating P0/P1 delivery work. Product progress must not be used to bypass the frozen scientific gate.

Prioritize the provider/model DecisionSource contract and comparison, trusted action-state integration, real-path reliability/security and demonstration evidence before speculative P2 components.

## 7. Update rule

Update this file when the current authorized scientific gate, material delivery blocker or immediate production execution path changes. Closed evidence belongs in `PROJECT-PROGRESS-LOG.md`; durable architecture decisions belong in `docs/adr/` / `ARCHITECTURE-ROADMAP.md`; final acceptance evidence belongs in `DELIVERY-ACCEPTANCE.md`.