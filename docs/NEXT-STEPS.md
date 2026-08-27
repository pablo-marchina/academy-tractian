# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE / canonical short-horizon execution plan  
**Planning checkpoint:** 2026-08-27 11:02 BRT  
**Current state source:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Macro plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file answers only: **what should be done next from the current evidence-backed state?** Exact authorization remains governed by `CURRENT-PROJECT-STATUS.md` and the applicable frozen artifacts/results.

## 1. Current execution objective

C4 deterministic scoring, group-cluster bootstrap and leave-one-group-out sensitivity are frozen. The only currently authorized scientific gate is the staged project gate:

```text
REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

This gate covers the still-unexecuted requirements from the frozen C2 preregistration `required_reporting` section:

- all per-group outcomes;
- modality slices: `investigate`, `execute`, `contextualize`;
- safety and failure-family slices;
- operational failure counts and denominators.

The gate must consume the exact frozen deterministic score rows and cannot change the C4 candidates or scores.

Still forbidden:

- provider/model generation;
- score mutation or rescoring;
- candidate regeneration;
- survivor/PREFERRED decision before this reporting gate freezes;
- semantic evaluation;
- FRESH_BLIND;
- LEGACY_LOCKED_TEST;
- final architecture freeze.

## 2. Immediate scientific sequence

### Step 1 — Open a focused reporting task and branch after LOGO integration

Pin:

- LOGO freeze Git blob;
- deterministic score-row SHA-256;
- bootstrap and LOGO result SHA-256 values;
- frozen preregistration blob;
- exact modality labels and reporting requirements;
- the source used to classify modality/failure families;
- explicit denial of survivor/semantic/blind/provider operations.

### Step 2 — Build a reporting-only runner

The runner may compute only the preregistered reporting summaries from already-frozen deterministic rows and public/frozen case metadata. It must not call the deterministic scorer, private oracle, provider or model.

Required fail-closed checks include:

- score-row SHA mismatch;
- LOGO freeze/hash mismatch;
- 144-row / 36×4 geometry mismatch;
- group set mismatch;
- unknown or ambiguous modality classification;
- post-result addition/removal of slice categories;
- missing denominators;
- private-oracle, semantic, blind or provider access.

### Step 3 — Produce required per-group and slice reporting

Required outputs:

1. per-arm outcomes for each of the seven independent `asset_story_group` groups under the frozen aggregation hierarchy;
2. `investigate`, `execute`, `contextualize` modality summaries with explicit denominators;
3. frozen safety/failure-family summaries with explicit denominators;
4. operational failure counts and denominators;
5. no candidate promotion inference inside the reporting runner.

### Step 4 — Independently validate and freeze

Verify exact input hashes, classifications, denominators and aggregate reconstruction. Freeze the reporting result before considering the decision rules.

### Step 5 — Advance only the decision gate explicitly opened by the reporting freeze

A later closure may authorize a **survivor/no-survivor decision** based on the already-frozen deterministic hard gates, bootstrap, LOGO and reporting evidence. It must not automatically authorize semantic evaluation or blind data.

## 3. Parallel P0/P1 work allowed

Only work that cannot contaminate the frozen C4 path may continue in parallel, including delivery-gap inventory, real API/tool-contract conformance, demonstration coverage, production decision questions and reproducibility/documentation preparation.

## 4. Work intentionally deferred

Do not select or implement as final merely because it is available: RAG/vector DB/reranker, multi-agent decomposition, persistent memory, MCP, adaptive routing, rich UI, final provider/model/runtime or final deployment topology.

## 5. Critical path to final delivery

```text
FROZEN_C4_DETERMINISTIC_SCORING
        ↓
FROZEN_C4_BOOTSTRAP_20000
        ↓
FROZEN_C4_LEAVE_ONE_GROUP_OUT_SENSITIVITY
        ↓
REQUIRED_PER_GROUP_AND_SLICE_REPORTING   ← CURRENT
        ↓
C4 survivor / no-survivor decision
        ↓
semantic child gate only if deterministically eligible
        ↓
candidate/evaluator freeze
        ↓
independent validation
        ↓
production-fit decisions
        ↓
architecture freeze
        ↓
integrated Agent + Evaluator implementation
        ↓
P0/P1 regression + real-path demo
        ↓
2026-09-08 final delivery
```

## 6. Deadline protection

The final delivery target remains 2026-09-08. Do not spend the protected integration/documentation window on speculative P2 complexity.

## 7. Update rule

Update this file when the current authorized gate or a material blocker changes. Closed work belongs in `PROJECT-PROGRESS-LOG.md`; durable architecture belongs in `ARCHITECTURE-ROADMAP.md`; final acceptance evidence belongs in `DELIVERY-ACCEPTANCE.md`.
