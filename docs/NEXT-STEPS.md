# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE / canonical short-horizon execution plan  
**Planning checkpoint:** 2026-08-27 23:14 BRT  
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
REQUIRED_PER_GROUP_AND_SLICE_REPORTING        ADR-006 provider-neutral adapter frozen
        ↓                                             ↓
reporting freeze                              model-call provenance + live-comparison prereg ← NEXT
        ↓                                             ↓
survivor/no-survivor if authorized            explicit live-provider authorization only later
        ↓                                             ↓
later child gates only if opened              trusted auth/idempotency + real-path evidence
```

Neither track may silently authorize the other.

The current scientific gate remains:

```text
REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

Provider/model calls authorized now remain **0**. ADR-006 freezes the neutral `DecisionSource` adapter contract but does not select a model/provider or authorize a live client. The production path remains provider-free, and all five mutating canonical actions remain fail-closed before transport under ADR-005.

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

ADR-004, the production runtime, deterministic evaluator, ADR-005 and ADR-006 now provide a stable provider-free skeleton through the model/provider decision seam. The next P0 task is to freeze the **real-provider call provenance and prospective comparison protocol** without making a live call.

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

### Step D2 — Provider-neutral production `DecisionSource` adapter — COMPLETE / FROZEN

ADR-006 freezes the provider-neutral contract:

```text
ControllerContext
+ public deterministic ToolSpec projection
→ ProviderDecisionRequest + canonical SHA-256
→ ProviderDecisionClient.complete(request)
→ strict JSON object / duplicate-key rejection
→ ProviderDecisionPayload
→ ControllerDecision / ToolProposal
→ AgentController
→ HarnessRunner / B1 / B2
```

Validated final head `cdd592f5bae53d0fafecabe68832a31f8605907d` passed:

- `67/67` production tests;
- `12/12` ADR-004 controller regressions;
- `11/11` triggered workflows;
- provider/model calls: `0`.

The adapter does not expose runtime identity, seed, action authorization/idempotency/scope or evaluator-private truth. Known-tool argument semantics remain B1-owned; consequential actions remain B2/ADR-005-owned. No production provider/model is selected.

### Step D3 — Freeze provider-call trace/provenance and live-comparison preregistration — NEXT / PROVIDER-FREE

Before the first live provider request, define exactly how a future `ProviderDecisionClient` records a model call without weakening ADR-004/ADR-006 or leaking sensitive payloads.

Required decisions/evidence:

- immutable model-call record schema and ownership;
- exact provider, model and serving-route identifiers;
- request SHA-256 linkage to `ProviderDecisionRequest` without copying sensitive request bodies into evaluation reports;
- response/decision provenance linkage sufficient to audit which provider call produced which controller decision;
- latency, status/failure, token/resource/cost metadata where available;
- explicit no-hidden-retry/no-hidden-fallback baseline;
- redaction rules for credentials, provider error text and customer/tool-result content;
- deterministic behavior when telemetry recording itself fails;
- compatibility with the existing `RunTrace`/production evaluator without exposing private/gold/oracle material;
- prospective live comparison candidate set and metrics.

The live comparison preregistration must include at minimum:

1. provider-free scripted/null baseline;
2. one strong quality-frontier provider/model candidate;
3. one feasible lower-cost/local/open candidate;
4. additional candidates only when they represent a distinct credible Pareto trade-off.

Before any live call, freeze measurement rules for structured-decision adherence, valid known-tool selection, canonical argument validity/B1 containment, allowed-development task quality, failure behavior, latency, reliability, resource/cost, portability and trace integrity.

**This step itself must make zero provider/model calls.** A subsequent live experiment requires a separate explicit authorization after these rules are frozen and current provider/model facts are refreshed from official sources.

### Step D4 — Prepare trusted production action authorization/idempotency integration — PARALLEL / NO ACTION ENABLEMENT

Define the production source of truth for:

- user permissions;
- user/company identity binding;
- resource → company ownership;
- requester confirmation lifecycle;
- durable idempotency key reservation/consumption;
- retry, timeout and ambiguous-result handling;
- audit retention.

ADR-005 is the contract these sources must satisfy. Do not weaken the policy to match an easier persistence implementation, and do not switch `actions_enabled` on in this preparation step.

### Step D5 — Execute live provider/model comparison only after separate authorization

Once D3 is frozen and a new governed task explicitly authorizes live calls:

- refresh exact candidate/model/route availability from primary provider sources;
- execute only against allowed development material;
- preserve one-call provenance and all failures;
- do not infer production selection from historical C4 serving-route qualification;
- compare against the preregistered metrics and null baseline;
- record Pareto trade-offs rather than forcing a winner when evidence is insufficient.

Any provider/model selection requires its own evidence-backed decision/ADR.

### Step D6 — Extend real-path Agent + Evaluator coverage after D3/D4/D5 evidence

Build toward:

```text
request
→ ProductionRuntime
→ provider-neutral DecisionSource
→ separately selected/authorized ProviderDecisionClient
→ AgentController
→ HarnessRunner / canonical ToolSpec
→ supplied TRACTIAN API
→ RunTrace + model-call provenance
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
- model/provider failure fallback under the prospectively frozen policy;
- per-run deterministic evaluation.

### Step D7 — Reliability, security and observability evidence

Once a real DecisionSource/provider path exists, run repeated/fault-injected tests for:

- EV-007 failure performance;
- EV-008 stability/repeated-run reliability;
- authorization/resource-scope/idempotency;
- failure continuity and human fallback;
- latency/resource/cost behavior;
- model/tool trace and diagnostic coverage;
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
ADR-006 PROVIDER-NEUTRAL DECISIONSOURCE CONTRACT FROZEN
        ↓
MODEL-CALL TRACE/PROVENANCE + LIVE-COMPARISON PREREG   ← DELIVERY CURRENT
        ↓
SEPARATE LIVE PROVIDER/MODEL AUTHORIZATION + COMPARISON
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

Prioritize provider-call provenance/comparison preregistration, trusted action-state integration, separately authorized provider evidence, real-path reliability/security and demonstration evidence before speculative P2 components.

## 7. Update rule

Update this file when the current authorized scientific gate, material delivery blocker or immediate production execution path changes. Closed evidence belongs in `PROJECT-PROGRESS-LOG.md`; durable architecture decisions belong in `docs/adr/` / `ARCHITECTURE-ROADMAP.md`; final acceptance evidence belongs in `DELIVERY-ACCEPTANCE.md`.