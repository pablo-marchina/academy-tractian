# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE / canonical short-horizon execution plan  
**Current state source:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Macro plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file answers only one question: **what should be done next from the current evidence-backed project state?**

It does not define experiment truth. Exact authorization and experiment semantics remain governed by `CURRENT-PROJECT-STATUS.md` and the applicable frozen artifacts/results.

## 1. Current execution objective

While `CURRENT-PROJECT-STATUS.md` reports `DETERMINISTIC_SCORING` as the current authorized gate, the only scientific gate that may advance is deterministic private scoring over the already frozen C4 packet.

No additional provider generation is authorized for this C4 packet. Bootstrap, LOGO, slices, semantic evaluation, FRESH_BLIND and LEGACY_LOCKED_TEST remain later gates and must not be executed opportunistically.

## 2. Immediate sequence

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

### Step 2 — Use a scoring-only C4 runner

The C4 deterministic-scoring runner must:

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

1. freeze the scorer source pins and exact input hashes;
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

## 3. Parallel work allowed now

Architecture and production-fit research may proceed in parallel provided it does not:

- expose hidden evaluator/blind outcomes;
- change the frozen C4 candidate outputs;
- claim a final architecture before the applicable comparison/validation gates close;
- silently translate a research implementation into a production standard.

Parallel work should focus on decision questions, hard requirements, alternatives, baselines, measurable production criteria and ADR-ready evidence described in `ARCHITECTURE-ROADMAP.md`.

## 4. Work intentionally deferred

The following should **not** be started merely for repository aesthetics or premature production-readiness signaling:

- final production package/runtime structure;
- final provider/model selection;
- final orchestration/runtime selection;
- final RAG/vector/memory/multi-agent architecture;
- production deployment topology;
- FRESH_BLIND outcome access;
- LEGACY_LOCKED_TEST access.

When a production architecture becomes evidence-backed and eligible to freeze, create the production code boundary explicitly instead of promoting `scripts/research/` into production code.

## 5. Update rule

Update this file whenever either condition occurs:

1. the current authorized gate changes; or
2. a material blocker changes the short-horizon execution path.

Do not use this document as a historical ledger. Closed steps belong in `PROJECT-PROGRESS-LOG.md`; durable architecture direction belongs in `ARCHITECTURE-ROADMAP.md`.
