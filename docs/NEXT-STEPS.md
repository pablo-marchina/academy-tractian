# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE / canonical short-horizon execution plan  
**Planning checkpoint:** 2026-08-27 22:18 BRT  
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
REQUIRED_PER_GROUP_AND_SLICE_REPORTING        production runtime v1 merged/read-only
        ↓                                             ↓
reporting freeze                              integrated production evaluator
        ↓                                             ↓
survivor/no-survivor if authorized            production action-safety decision
        ↓                                             ↓
later child gates only if opened              model/provider production-fit decision
```

Neither track may silently authorize the other.

The current scientific gate remains:

```text
REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

The first production runtime slice is already merged and validated, but it is intentionally provider-free and read-only. All five mutating canonical actions remain fail-closed before transport.

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

ADR-004 and PR #18 removed the missing-controller/production-surface blocker. The next delivery work should prioritize the complete `REQ-017` Agent + Evaluator requirement rather than adding optional orchestration complexity.

### Step D1 — Integrate a provider-free production evaluator over `RunTrace`

Create a focused P0 task that evaluates the exact trace produced by `ProductionRuntime` without changing runtime behavior and without exposing evaluator-only references to `DecisionSource`.

First target deterministic capabilities already supported by runtime evidence:

- trace validity and lifecycle completeness;
- tool/proposal/call/result separation;
- schema/argument correctness;
- contained policy denials;
- identity/seed isolation;
- terminal decision/fallback classification;
- tool/transport failure containment;
- per-run report surface suitable for later semantic evaluators.

Do not add semantic/judge calls merely to complete the interface; deterministic truth remains the baseline.

### Step D2 — Govern production action safety before enabling any mutating tool

Current production config intentionally fixes `actions_enabled = false` and grants zero action permissions.

Before changing that boundary, compare and freeze a production policy covering at minimum:

- explicit permissions and resource/company scope;
- requester confirmation policy for consequential actions, kept separate from benchmark accepted-action semantics;
- idempotency / duplicate-action protection;
- justification requirements;
- human fallback/escalation;
- failure and retry behavior that cannot duplicate actions;
- audit/trace evidence.

No production action should reach transport until this decision and its regression tests are complete.

### Step D3 — Define and compare the production model/provider adapter

The controller protocol is frozen; the model/provider is not.

The next model/provider decision must compare a strong quality-frontier candidate with feasible lower-cost/local/open alternatives against measured task quality, robustness, latency, reliability, resource/cost, portability and failure behavior. Do not infer a production provider from historical C4 serving-route qualification.

Provider calls remain unauthorized until a separately governed execution explicitly opens them.

### Step D4 — Extend the real production path after D1–D3 evidence

Then build toward:

```text
request
→ ProductionRuntime
→ model/provider DecisionSource adapter
→ AgentController
→ HarnessRunner / canonical ToolSpec
→ supplied TRACTIAN API
→ RunTrace
→ integrated evaluator
→ customer-safe response + evaluation result
```

Add end-to-end scenario coverage for contextualize, investigate, clarify/abstain, escalation, execute once authorized, conflicting/inconclusive evidence and provider/tool failure.

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
FIRST PRODUCTION RUNTIME SLICE MERGED     ← DELIVERY CURRENT
        ↓
INTEGRATED PRODUCTION EVALUATOR
        ↓
ACTION-SAFETY + MODEL/PROVIDER DECISIONS
        ↓
INTEGRATED AGENT + EVALUATOR REAL PATH
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

The final delivery target remains 2026-09-08. The scientific artifact blocker must not idle non-contaminating P0/P1 delivery work. At the same time, product progress must not be used to bypass the frozen scientific gate.

Prioritize integrated evaluation, action safety, model/provider production fit, reliability/security and real-path demonstration before any speculative P2 component.

## 7. Update rule

Update this file when the current authorized scientific gate, material delivery blocker or immediate production execution path changes. Closed evidence belongs in `PROJECT-PROGRESS-LOG.md`; durable architecture decisions belong in `docs/adr/` / `ARCHITECTURE-ROADMAP.md`; final acceptance evidence belongs in `DELIVERY-ACCEPTANCE.md`.