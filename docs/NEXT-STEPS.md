# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE / canonical short-horizon execution plan  
**Current state source:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Macro plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file answers only one question: **what should be done next from the current evidence-backed project state?**

It does not define experiment truth. Exact authorization and experiment semantics remain governed by `CURRENT-PROJECT-STATUS.md` and the applicable frozen artifacts/results.

## 1. Current execution objective

While `CURRENT-PROJECT-STATUS.md` reports `DETERMINISTIC_SCORING` as the current authorized gate, the only scientific gate that may advance is deterministic private scoring over the already frozen C4 packet.

No additional provider generation is authorized for this C4 packet. Bootstrap, LOGO, slices, semantic evaluation, FRESH_BLIND and LEGACY_LOCKED_TEST remain later gates and must not be executed opportunistically.

At the project level, work should follow the priority order in `DELIVERY-ACCEPTANCE.md`:

```text
P0 requested capabilities + trustworthy evaluation
        ↓
P1 production/security/reliability required to operate P0
        ↓
P2 optional complexity only with measured need/benefit
```

## 2. Immediate scientific sequence

### Step 1 — Close deterministic-scoring provenance

Verify and record before any private scoring execution:

- the immutable C4 freeze artifact and its Git blob;
- the exact 144-output artifact source, artifact ID/digest and file SHA-256;
- exact parent/arm cardinality and output hashes;
- evaluator v4.1 and its required source/dependency blobs;
- the exact evaluator-side private oracle source and custody mechanism;
- absence of provider credentials from the scoring environment;
- continued denial of FRESH_BLIND and LEGACY_LOCKED_TEST access.

Do not infer or reconstruct the private oracle from public fixtures.

### Step 2 — Use the prepared scoring-only C4 runner

Prepared runner: `scripts/research/p12_c4_deterministic_private_scoring.py`.

Its presence in the repository is **not execution authorization**. The private-oracle custody/handoff still has to be explicitly resolved and frozen before this runner may be used.

The runner is required to:

- consume exactly the frozen 144 outputs;
- use the frozen deterministic evaluator semantics only;
- emit one score row per fixed output;
- preserve parent/output identity and provenance;
- serialize no private expected-path text or private endpoint lists;
- perform zero provider/model/network calls;
- perform zero bootstrap resamples;
- perform zero LOGO analysis;
- perform zero modality/failure slices beyond per-row deterministic scoring;
- access neither FRESH_BLIND nor LEGACY_LOCKED_TEST.

Historical monolithic scorers may be used as frozen semantic references, but must not be executed wholesale when they cross later gates.

### Step 3 — Freeze the evaluator-side execution handoff

Only after the private-oracle provenance/custody route is explicit:

1. verify/freeze the prepared scorer source blob and exact input hashes;
2. freeze the evaluator-side execution/authorization contract;
3. ensure provider credentials are absent;
4. ensure the private oracle remains evaluator-side;
5. define fail-closed behavior for any missing, duplicate, unscoreable or mismatched output;
6. define the sanitized evidence artifact that may be retained.

Do not create an execution route that guesses how private material should be provisioned.

### Step 4 — Execute deterministic scoring exactly within the frozen authorization

The execution is complete only if:

- all 144 outputs are present and immutable;
- all 144 outputs are scoreable under the frozen evaluator;
- no input/output hash changes;
- no provider/model call occurs;
- no later statistical/semantic gate executes;
- no unauthorized partition is accessed;
- the sanitized result is complete and independently verifiable.

Any fail-closed result must remain evidence rather than being silently repaired or reinterpreted.

### Step 5 — Freeze deterministic result and stop

After successful deterministic scoring:

- independently verify row count, hashes, scorer provenance and access counters;
- freeze the deterministic result;
- append the transition to `PROJECT-PROGRESS-LOG.md`;
- update `CURRENT-PROJECT-STATUS.md` and the latest machine checkpoint;
- replace this file's immediate sequence with the next newly authorized gate.

Do **not** assume that bootstrap becomes authorized merely because deterministic scoring ran. The deterministic-result freeze must explicitly open the next gate.

## 3. Parallel work allowed now — delivery-focused only

Architecture and production-fit research may proceed in parallel provided it does not:

- expose hidden evaluator/blind outcomes;
- change the frozen C4 candidate outputs;
- claim a final architecture before the applicable comparison/validation gates close;
- silently translate a research implementation into a production standard.

Parallel work should prioritize **P0/P1 questions that can block final delivery**, especially:

1. final real API/tool integration contract and traceability;
2. coverage of contextualize / investigate / execute / clarify-or-abstain / escalate behaviors;
3. incomplete/conflicting/unavailable-data failure behavior;
4. integrated per-run evaluation without gold leakage;
5. safe authorization/action/idempotency semantics;
6. production observability and reproducible environment;
7. provider/runtime choices only to the extent required to deliver the above reliably.

For each material decision, start with the simplest viable baseline and follow `PROJECT-PRINCIPLES.md` before selecting a more complex option.

## 4. Work intentionally deferred

The following should **not** be started merely for repository aesthetics, novelty or premature production-readiness signaling:

- final production package/runtime structure before sufficient architecture evidence;
- final provider/model selection without comparison;
- final orchestration/runtime selection without comparison;
- RAG/vector/reranking without a demonstrated retrieval requirement/bottleneck;
- persistent memory without required multi-turn benefit;
- multi-agent decomposition without measured advantage over single-agent baseline;
- protocol/adaptor complexity without portability/integration benefit;
- FRESH_BLIND outcome access;
- LEGACY_LOCKED_TEST access.

When a production architecture becomes evidence-backed and eligible to freeze, create the production code boundary explicitly instead of promoting `scripts/research/` into production code.

## 5. Deadline protection rule

The final delivery target is 2026-09-08. Preserve the final project window for:

- P0 acceptance closure;
- integrated agent + evaluator implementation;
- real API/e2e regression;
- robustness/failure scenarios;
- documentation/reproducibility;
- release/demo/runbook evidence.

Do not consume that window with P2 enhancements unless P0/P1 coverage is already secure and quantitative evidence shows the enhancement materially improves the final solution.

## 6. Update rule

Update this file whenever either condition occurs:

1. the current authorized gate changes; or
2. a material blocker changes the short-horizon execution path.

Also re-check `DELIVERY-ACCEPTANCE.md` whenever a planned feature, architecture decision or scope change could create or close a final-delivery gap.

Do not use this document as a historical ledger. Closed steps belong in `PROJECT-PROGRESS-LOG.md`; durable architecture direction belongs in `ARCHITECTURE-ROADMAP.md`.
