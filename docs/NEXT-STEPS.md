# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE / canonical short-horizon execution plan  
**Planning checkpoint:** 2026-08-27 10:20 BRT  
**Current state source:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Macro plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file answers only: **what should be done next from the current evidence-backed state?** Exact authorization remains governed by `CURRENT-PROJECT-STATUS.md` and the applicable frozen artifacts/results.

## 1. Current execution objective

C4 deterministic scoring is now frozen as `FROZEN_C4_DETERMINISTIC_SCORING` with 144/144 scoreable outputs and 0 independent recomputation mismatches.

The only newly authorized scientific gate is:

```text
BOOTSTRAP_20000
```

Frozen parameters:

- resamples: **20,000**;
- seed: **20260822**;
- confidence level: **95%**;
- resampling unit: **asset_story_group**;
- input: the exact evaluator-side deterministic row artifact with SHA-256 `b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c`.

Still forbidden:

- new provider/model generation;
- score alteration or recomputation in response to statistical outcomes;
- LOGO;
- modality/failure slices;
- semantic evaluation;
- FRESH_BLIND;
- LEGACY_LOCKED_TEST;
- candidate regeneration;
- final architecture freeze.

## 2. Immediate scientific sequence

### Step 1 — Create a bootstrap-only planning record and focused branch

Treat the statistical gate as a separate Class C task.

The task must pin:

- deterministic-scoring freeze and Git blob;
- exact deterministic row-artifact SHA-256;
- C2 factorial preregistration blob;
- bootstrap count, seed, confidence level and group resampling unit;
- exact aggregation hierarchy;
- primary comparison graph;
- explicit denial of LOGO/slices/semantic/blind/provider work.

### Step 2 — Build/verify a bootstrap-only runner

Do **not** execute the historical monolithic `p12_c2_factorial_score.py` wholesale.

The bootstrap runner may consume the frozen deterministic rows and implement only the preregistered statistical operations needed for the `BOOTSTRAP_20000` gate. It must stop before LOGO and slices.

Required fail-closed checks:

- deterministic input SHA mismatch;
- anything other than 144 scoreable rows;
- incomplete 36 × 4 factorial geometry;
- group/scenario/ticket/repetition aggregation mismatch;
- changed arm semantics;
- changed bootstrap parameters;
- provider/model/private-oracle access during the bootstrap process;
- invocation of LOGO/slice/semantic code.

### Step 3 — Execute exactly the frozen bootstrap

Required outputs are the preregistered paired effects / confidence intervals and any deterministic aggregate quantities strictly necessary to interpret that gate.

Do not add new post-result hypotheses or alternate resampling choices.

### Step 4 — Independently validate and freeze the bootstrap result

Validate at minimum:

- 20,000 resamples actually used;
- seed `20260822`;
- cluster resampling by whole `asset_story_group`;
- aggregation hierarchy unchanged;
- expected comparison graph unchanged;
- deterministic-input SHA unchanged;
- provider/model/private/blind accesses remain 0;
- no LOGO/slices/semantic stage executed.

Freeze the result before opening any later analysis gate.

### Step 5 — Advance only the gate explicitly opened by the bootstrap freeze

Do not assume LOGO, slices or semantic evaluation become authorized automatically.

After closure, update:

- `CURRENT-PROJECT-STATUS.md`;
- machine checkpoint;
- `PROJECT-PROGRESS-LOG.md`;
- this file.

## 3. Parallel P0/P1 work allowed

Work that cannot contaminate the frozen C4 statistical path may continue in parallel:

1. final delivery-gap inventory against `DELIVERY-ACCEPTANCE.md`;
2. real supplied-API/tool contract analysis and conformance preparation;
3. final demonstration coverage design for contextualize / investigate / execute / clarify-or-abstain / escalate / conflict / failure;
4. production decision questions, baselines and metrics for model/provider, runtime/controller, tool contract, evaluator stack, fallback policy, observability and deployment;
5. reproducibility/documentation preparation that does not make unearned claims.

All such work remains subject to P1–P4 and the P0 → P1 → justified-P2 priority rule.

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

Each must earn its place through a requirement/risk mapping and controlled comparison against a simpler baseline.

## 5. Critical path to final delivery

```text
FROZEN_C4_DETERMINISTIC_SCORING
        ↓
BOOTSTRAP_20000                  ← CURRENT
        ↓
newly authorized robustness/reporting gates
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

If a later optional feature cannot be compared, integrated and regression-tested without endangering P0/P1 closure, defer it.

## 7. Update rule

Update this file when the current authorized gate or a material blocker changes. Closed work belongs in `PROJECT-PROGRESS-LOG.md`; durable architecture belongs in `ARCHITECTURE-ROADMAP.md`; final acceptance evidence belongs in `DELIVERY-ACCEPTANCE.md`.
