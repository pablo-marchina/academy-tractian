# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE / canonical short-horizon execution plan  
**Planning checkpoint:** 2026-08-27 10:41 BRT  
**Current state source:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Macro plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file answers only: **what should be done next from the current evidence-backed state?** Exact authorization remains governed by `CURRENT-PROJECT-STATUS.md` and the applicable frozen artifacts/results.

## 1. Current execution objective

C4 deterministic scoring and the preregistered 20,000-resample group-cluster bootstrap are frozen. The only currently authorized scientific gate is:

```text
LEAVE_ONE_GROUP_OUT_SENSITIVITY
```

The LOGO gate must consume the same frozen deterministic score-row artifact:

`b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c`

and the frozen bootstrap result:

`08977c0d419144b885a7d2da6ffb73796ca43d80aa4e330a462d33c058464526`

The omission unit is the preregistered independent `asset_story_group`. There are exactly seven independent groups.

Still forbidden:

- new provider/model generation;
- deterministic score alteration or regeneration in response to outcomes;
- modality/failure-family slices;
- semantic evaluation;
- FRESH_BLIND;
- LEGACY_LOCKED_TEST;
- candidate regeneration;
- survivor/PREFERRED decision before required robustness/reporting gates close;
- final architecture freeze.

## 2. Immediate scientific sequence

### Step 1 — Open a focused LOGO planning record and branch

Treat LOGO as a separate Class C statistical gate. Pin:

- bootstrap freeze Git blob;
- deterministic score-row SHA-256;
- bootstrap-result SHA-256;
- frozen C2 statistical scorer blob;
- exact `logo_effects(...)` semantics;
- seven-group geometry;
- explicit denial of slices/semantic/blind/provider work.

### Step 2 — Build a LOGO-only runner

Do **not** execute the historical monolithic `p12_c2_factorial_score.py` wholesale.

The runner may perform only the frozen leave-one-group-out calculations required by the preregistration. It must fail closed if:

- deterministic input SHA changes;
- bootstrap freeze/result hashes do not match;
- row count differs from 144;
- geometry differs from 36 parents × 4 arms × 7 groups;
- primary comparison graph changes;
- any score is recomputed or changed;
- provider/model/private-oracle access occurs;
- LOGO code crosses into slices, semantic or blind evaluation.

### Step 3 — Execute the seven leave-one-group-out estimates

For each preregistered primary comparison and metric, omit exactly one `asset_story_group` at a time and average the paired group effects over the six retained groups, reproducing the frozen historical C2 `logo_effects(...)` semantics exactly.

No new metric, comparison, threshold or post-result hypothesis may be added.

### Step 4 — Independently validate and freeze LOGO

Validate at minimum:

- seven unique omitted groups;
- six retained groups per omission;
- exact primary comparison graph;
- exact equality to independent recomputation using frozen historical helper semantics;
- deterministic-input SHA unchanged;
- bootstrap-result SHA unchanged;
- provider/model/private/blind accesses remain zero;
- slices/semantic remain unexecuted.

Freeze LOGO before opening any later reporting gate.

### Step 5 — Advance only the gate explicitly opened by the LOGO freeze

Do not assume slices, survivor selection or semantic evaluation become authorized automatically.

After closure update:

- `CURRENT-PROJECT-STATUS.md`;
- machine-readable checkpoint;
- `PROJECT-PROGRESS-LOG.md`;
- this file.

## 3. Parallel P0/P1 work allowed

Only work that cannot contaminate the frozen C4 path may continue in parallel, including delivery-gap inventory, real API/tool-contract conformance, demonstration coverage, production decision questions, and reproducibility/documentation preparation.

All parallel work remains subject to P1–P4 and the P0 → P1 → justified-P2 priority rule.

## 4. Work intentionally deferred

Do not select or implement as final merely because it is available:

- RAG/vector DB/reranker;
- multi-agent decomposition;
- persistent memory;
- MCP or another protocol layer;
- adaptive routing;
- rich UI;
- final provider/model/runtime;
- final production packaging/deployment topology.

## 5. Critical path to final delivery

```text
FROZEN_C4_DETERMINISTIC_SCORING
        ↓
FROZEN_C4_BOOTSTRAP_20000
        ↓
LEAVE_ONE_GROUP_OUT_SENSITIVITY   ← CURRENT
        ↓
newly authorized reporting/robustness gate(s)
        ↓
C4 survivor / no-survivor decision
        ↓
semantic child gate if eligible
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
