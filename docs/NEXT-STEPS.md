# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE / canonical short-horizon execution plan  
**Planning checkpoint:** 2026-08-27 08:46 BRT  
**Current state source:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Macro plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Source baseline:** [`../research/tractian-source-baseline-2026-08-27.md`](../research/tractian-source-baseline-2026-08-27.md)

This file answers only one question: **what should be done next from the current evidence-backed project state to maximize the final TRACTIAN delivery?**

It does not define experiment truth. Exact authorization and experiment semantics remain governed by `CURRENT-PROJECT-STATUS.md` and the applicable frozen artifacts/results.

## 1. Current execution objective

While `CURRENT-PROJECT-STATUS.md` reports `DETERMINISTIC_SCORING` as the current authorized scientific gate, the only scientific gate that may advance is deterministic private scoring over the already frozen C4 packet.

No additional provider generation is authorized for this C4 packet. Bootstrap, LOGO, slices, semantic evaluation, FRESH_BLIND and LEGACY_LOCKED_TEST remain later gates and must not be executed opportunistically.

The source/requirements reconciliation against the updated TAPI, delivered project package and kickoff is complete at the planning layer. It did **not** advance the scientific gate.

At the project level, use this priority:

```text
P0 requested capabilities + trustworthy evaluation
        ↓
P1 production/partner-quality fitness needed to operate P0
        ↓
P2 optional complexity only with measured benefit
```

## 2. Scientific critical path — execute in order

### Step 1 — Close deterministic-scoring provenance

Verify and record before any private scoring execution:

- immutable C4 freeze artifact and Git blob;
- exact 144-output artifact source, artifact ID/digest and file SHA-256;
- exact parent/arm cardinality and output hashes;
- evaluator v4.1 and required source/dependency blobs;
- exact evaluator-side private-oracle source and custody mechanism;
- absence of provider credentials from the scoring environment;
- continued denial of FRESH_BLIND and LEGACY_LOCKED_TEST access.

Do not infer/reconstruct private truth from public fixtures or from the delivered `eval/` package.

### Step 2 — Freeze evaluator-side handoff

Only after oracle provenance/custody is explicit:

1. verify/freeze the prepared scorer source blob and exact input hashes;
2. freeze evaluator-side execution/authorization contract;
3. ensure provider credentials are absent;
4. keep private oracle evaluator-side only;
5. define fail-closed behavior for missing, duplicate, unscoreable or mismatched outputs;
6. define the sanitized evidence artifact that may be retained.

### Step 3 — Execute deterministic scoring only

Prepared runner: `scripts/research/p12_c4_deterministic_private_scoring.py`.

Its presence is **not execution authorization**.

Execution is valid only if:

- exactly 144 frozen outputs are consumed;
- all are scoreable under the frozen deterministic evaluator;
- input/output hashes remain unchanged;
- provider/model/network calls = 0;
- bootstrap = 0;
- LOGO = 0;
- post-score slices = 0;
- semantic evaluation = 0;
- FRESH_BLIND/LEGACY_LOCKED_TEST access = 0.

Any fail-closed outcome remains evidence and is not silently repaired.

### Step 4 — Independently validate and freeze deterministic result

Verify:

- 144 score rows and exact bindings;
- scorer/oracle/input provenance;
- deterministic recomputation where feasible;
- no missing/duplicate cells;
- access/provider counters;
- sanitized artifact integrity.

Freeze the deterministic result and stop.

### Step 5 — Advance only if the new freeze explicitly opens the next gate

After deterministic closure:

- append result to `PROJECT-PROGRESS-LOG.md`;
- update `CURRENT-PROJECT-STATUS.md` and machine checkpoint;
- replace this plan with the newly authorized statistical/semantic sequence;
- do **not** assume bootstrap/LOGO/slices are automatically authorized.

## 3. Parallel delivery-quality work allowed now

The following may proceed because it does not require private outcomes or modification of the frozen C4 packet.

### Track A — P0/P1 delivery gap inventory

Use `DELIVERY-ACCEPTANCE.md` and the audited partner package to classify each final acceptance row as:

```text
PROVEN
FOUNDATION_EXISTS_BUT_FINAL_PROOF_PENDING
NOT_YET_IMPLEMENTED
BLOCKED_BY_CURRENT_GATE
OPTIONAL / NOT REQUIRED
```

Prioritize gaps that can threaten the final deadline:

- real supplied-API production-path integration;
- contextualize/investigate/execute/clarify-or-abstain/escalate behavior;
- degraded/conflicting/unavailable evidence handling;
- stable typed tool contract;
- normalized trace capture/inspection;
- integrated evaluator over the same trace;
- human fallback and escalation handoff;
- action/permission safety;
- customer-safe communication;
- clean reproducible setup.

Do not use private/fresh/locked outcomes to populate this inventory.

### Track B — Material architecture decision preparation

For each decision in `ARCHITECTURE-ROADMAP.md`:

1. state the formal requirement/rubric criterion/P1 risk it serves;
2. define the simple baseline;
3. identify credible alternatives;
4. predefine quality/robustness/production metrics;
5. identify what evidence already exists vs what still requires experiment;
6. stop short of `PREFERRED/FROZEN` until comparison evidence is adequate.

Highest-priority decisions after candidate evidence closes:

1. final behavior/candidate;
2. model/provider strategy — include a strong quality frontier and feasible lower-cost/local baseline;
3. explicit controller/runtime;
4. stable Tool Contract + TRACTIAN API adapter;
5. single-agent baseline vs any justified decomposition;
6. evaluator stack;
7. failure/human-fallback policy;
8. action/confirmation policy for interactive production without altering benchmark semantics;
9. observability/trace inspection;
10. deployment/interface sufficient for the real final demo.

RAG/vector/reranking/persistent memory/MCP/multi-agent/richer UI are not priority by default.

### Track C — Final demonstration/evidence design

Prepare the final evidence matrix without fabricating results:

- contextualization;
- investigation;
- justified action;
- clarification/abstention;
- escalation with useful handoff;
- conflict/inconclusive handling;
- data/tool/model/provider failure path;
- customer-safe response;
- per-run evaluation;
- aggregate reliability view.

For each item, specify the eventual trace/evaluator evidence needed. Do not hard-code a happy-path script as the proof itself.

### Track D — Delivered-package contract coverage

Use the actual delivered package, not narrative assumptions:

- 17 agent-visible cases;
- 17 expected-path evaluation rows;
- 16 narrative scenario groups;
- 17 concrete OpenAPI operations;
- supplied permission/justification/action semantics;
- deterministic degraded-response controls.

Preserve scenario grouping where tickets share one narrative/causal path. Do not infer missing eval utilities that were referenced in prose but absent from the reviewed ZIP.

## 4. Work intentionally deferred

Do not start merely for aesthetics, novelty or signaling maturity:

- final production package structure before architecture evidence is sufficient;
- final provider/model declaration before systematic comparison;
- final runtime/orchestrator declaration;
- RAG/vector/reranking without a demonstrated retrieval requirement/bottleneck;
- persistent memory without measured multi-turn need;
- multi-agent decomposition without measured advantage over single-agent baseline;
- generalization to additional backend protocols not required by the supplied package;
- rich UI before real-path integration/evaluation is stable;
- FRESH_BLIND outcome access;
- LEGACY_LOCKED_TEST access.

## 5. Immediate priority order

```text
1. close deterministic-scoring provenance
2. execute/freeze deterministic scoring only when custody is valid
3. in parallel, close P0/P1 evidence gaps that do not depend on private outcomes
4. advance only newly authorized evaluation gates
5. freeze survivor/no-survivor evidence
6. run production-fit comparisons for material choices
7. freeze architecture
8. implement integrated agent + evaluator production path
9. reliability/security/reproducibility hardening
10. final rubric-indexed demo + documentation
```

## 6. Deadline protection rule

Final delivery is 2026-09-08. Preserve the last project days for P0 acceptance closure, integrated regression, robustness/failure evidence, documentation/reproducibility and demo quality.

After 2026-09-05, default against speculative P2 work unless it directly fixes a demonstrated blocker and can be re-evaluated safely.

## 7. Update rule

Update this file whenever either condition occurs:

1. the current authorized gate changes; or
2. a material blocker/source/acceptance change alters the short-horizon path.

Do not use this document as a historical ledger. Closed steps belong in `PROJECT-PROGRESS-LOG.md`; durable architecture direction belongs in `ARCHITECTURE-ROADMAP.md`; final required evidence belongs in `DELIVERY-ACCEPTANCE.md`.