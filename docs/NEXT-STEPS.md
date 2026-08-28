# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE / canonical short-horizon execution plan  
**Planning checkpoint:** 2026-08-27 22:29 BRT  
**Current state source:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Macro plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file answers only: **what should be done next from the current evidence-backed state?** Exact scientific authorization remains governed by `CURRENT-PROJECT-STATUS.md` and the applicable frozen artifacts/results.

## 1. Current execution objective

The project now has two deliberately isolated short-horizon tracks:

```text
SCIENTIFIC TRACK                              DELIVERY TRACK
REQUIRED_PER_GROUP_AND_SLICE_REPORTING        runtime + deterministic evaluator integrated
        ↓                                             ↓
reporting freeze                              production action-safety decision
        ↓                                             ↓
survivor/no-survivor if authorized            model/provider production-fit decision
        ↓                                             ↓
later child gates only if opened              real-path reliability/security integration
```

Neither track may silently authorize the other.

The current scientific gate remains:

```text
REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

The production runtime/evaluator path is provider-free and read-only. All five mutating canonical actions remain fail-closed before transport, and the integrated evaluator establishes deterministic trace/safety properties only — not semantic task correctness.

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

ADR-004, PR #18 and PR #21 now provide a provider-free read-only Agent Runtime Plane plus deterministic trace evaluation on the exact same run. The next P0/P1 work must address consequential actions and the missing model/provider decision rather than optional orchestration complexity.

### Step D1 — Govern production action safety before enabling any mutating tool — NEXT

Current production config intentionally fixes `actions_enabled = false` and grants zero action permissions.

Open a focused material decision comparing the simplest safe production-action policy against credible alternatives. Freeze at minimum:

- explicit permission mapping per canonical action;
- resource/company scope validation;
- requester-confirmation policy for consequential actions, explicitly separated from benchmark accepted-action semantics;
- idempotency / duplicate-action protection;
- justification requirements and audit evidence;
- human fallback/escalation when authorization/evidence is insufficient;
- retry/failure semantics that cannot duplicate or ambiguously execute actions;
- trace/evaluator obligations proving allowed, denied and repeated action behavior.

The null baseline remains **all actions disabled**. No action may reach production transport until controlled evidence justifies a change from that baseline.

### Step D2 — Define and compare the production model/provider adapter

The controller protocol is frozen; the model/provider is not.

The model/provider decision must compare:

- a strong quality-frontier candidate/configuration;
- a feasible lower-cost/local/open baseline;
- any additional credible Pareto candidate.

Measure task quality, structured-decision adherence, robustness, latency, reliability, resource/cost, portability and failure behavior. Historical C4 serving-route qualification is not production-provider evidence by itself.

Provider calls remain unauthorized until a separately governed execution explicitly opens them.

### Step D3 — Extend real-path Agent + Evaluator coverage

After the applicable action/model decisions are frozen, build toward:

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
- execute only after action safety is authorized;
- partial/unavailable tools or data;
- conflicting/inconclusive evidence;
- model/provider failure fallback;
- per-run deterministic evaluation.

### Step D4 — Reliability, security and observability evidence

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
- persistent memory;
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
FIRST PRODUCTION RUNTIME SLICE MERGED
        ↓
DETERMINISTIC PRODUCTION EVALUATOR MERGED   ← DELIVERY CURRENT
        ↓
ACTION-SAFETY + MODEL/PROVIDER DECISIONS
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

Prioritize action safety, production model/provider fit, real-path reliability/security and demonstration evidence before any speculative P2 component.

## 7. Update rule

Update this file when the current authorized scientific gate, material delivery blocker or immediate production execution path changes. Closed evidence belongs in `PROJECT-PROGRESS-LOG.md`; durable architecture decisions belong in `docs/adr/` / `ARCHITECTURE-ROADMAP.md`; final acceptance evidence belongs in `DELIVERY-ACCEPTANCE.md`.