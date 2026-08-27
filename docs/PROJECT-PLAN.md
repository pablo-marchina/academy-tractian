# Academy × TRACTIAN — Governed Project Plan to Production Delivery

**Status:** ACTIVE / canonical macro plan  
**Planning checkpoint:** 2026-08-27 00:27 BRT  
**Final delivery target:** 2026-09-08  
**Current status:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Immediate next steps:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

## 1. Purpose

This document is the **master phase/milestone map** for the project. It intentionally does not duplicate current-state details, short-horizon execution instructions, final acceptance rows or the full architecture decision register.

Use:

- `CURRENT-PROJECT-STATUS.md` for where the project is now and what is authorized;
- `NEXT-STEPS.md` for what should be done next;
- `DELIVERY-ACCEPTANCE.md` for what must demonstrably be true at final delivery;
- `ARCHITECTURE-ROADMAP.md` for the general system/research-to-production architecture;
- `PROJECT-PROGRESS-LOG.md` for completed history and evidence transitions.

The objective is to finish with the strongest defensible evidence and strongest production-path implementation achievable by 2026-09-08 without weakening requested scope, scientific validity, security boundaries, evaluator independence or production fitness.

## 2. Non-negotiable planning rules

All phases follow the four repository-wide principles:

- **P1 — systematic comparison:** no material architecture/product decision is final before credible alternatives are compared under explicit requirements;
- **P2 — production-first:** production constraints are part of selection, not post-hoc decoration;
- **P3 — quantitative/adaptive by default:** measurable decisions use metrics/uncertainty and adaptive policies must beat simpler static baselines;
- **P4 — eval-driven engineering:** requirements, evaluators, baselines and regression evidence drive implementation through delivery.

A gate PASS means evidence for that gate. It does not automatically mean `PREFERRED`, `FROZEN`, final or production-ready.

### 2.1 Acceptance-first priority rule

Every material workstream must map to at least one of:

1. a final requirement/acceptance row in `DELIVERY-ACCEPTANCE.md`;
2. a material production/security/reliability risk that could block such a row; or
3. an experiment required to choose among credible alternatives for such a row.

If it maps to none, defer it.

Priority order:

```text
P0 requested capabilities + trustworthy evaluation
        ↓
P1 production fitness / security / reliability needed to operate P0
        ↓
P2 optional complexity only when simple baselines are insufficient or measured benefit is material
```

P0 coverage must not be sacrificed to implement optional RAG, vector DB, reranking, persistent memory, multi-agent decomposition, protocol adapters, adaptive routing or richer UI merely because those components are interesting.

## 3. Macro phases

| Phase | Objective | State source |
|---|---|---|
| 1. Governance and benchmark foundation | Freeze evidence roles, benchmark integrity, access rules and evaluation semantics | progress ledger / current status |
| 2. Candidate exploration and failure learning | Preserve and learn from historical candidate/experiment evidence | progress ledger |
| 3. Confirmatory packet generation | Qualify serving route, collect required common parents, expand fixed candidates and freeze a complete packet | current status / frozen results |
| 4. Deterministic, statistical and semantic evaluation | Score immutable outputs, run only separately authorized analysis gates and qualify exact survivors | current status / next steps |
| 5. Production-fit selection and independent validation | Compare production choices, freeze candidate/evaluator generation and obtain authorized independent evidence | architecture roadmap / ADRs |
| 6. Final architecture freeze and production implementation | Freeze evidence-backed architecture and create the production code path that covers P0/P1 acceptance | architecture roadmap / acceptance matrix / ADRs |
| 7. Integration, regression, controlled deployment and final delivery | Prove all applicable final acceptance rows end to end and deliver reproducibly | acceptance matrix / release evidence |

`CURRENT-PROJECT-STATUS.md` is authoritative for the active phase/gate. Do not infer current state from this table alone.

## 4. Phase-transition rule

Every material transition follows:

```text
frozen inputs/current evidence
→ authorized work
→ validation
→ result artifact
→ provenance/hashes
→ freeze/closure
→ status update
→ next-step update
→ acceptance/architecture update if materially affected
```

For an experimental/statistical gate, no later gate may run unless the new freeze explicitly opens it.

For an architecture/product decision, no choice may advance to `PREFERRED`/`FROZEN` merely because it already exists in the repository or worked in a narrower experiment.

## 5. Phase 4 completion target — candidate evidence

Phase 4 is complete only when the applicable frozen evaluation sequence has produced an evidence-backed survivor decision.

Depending on the governing freezes, this may include:

- deterministic scoring;
- preregistered statistical analysis;
- robustness/sensitivity analysis;
- semantic child evaluation for exact survivors only;
- explicit no-survivor closure when applicable.

The exact immediate sequence is maintained in `NEXT-STEPS.md`, not here.

Phase 4 evidence informs final agent behavior, but does not by itself prove all TAPI delivery requirements or production readiness.

## 6. Phase 5 completion target — production-fit selection + independent evidence

Before independent measurement and final production selection:

- candidate behavior/configuration is frozen as required;
- evaluator generation/configuration is frozen as required;
- material production decisions have controlled comparison evidence;
- unresolved assumptions and reversal triggers are explicit;
- hidden independent outcomes remain inaccessible until separately authorized;
- every proposed final component has a clear requirement/risk rationale and simple baseline;
- the intended final acceptance claim is explicit.

Material architecture decisions and required comparison criteria are maintained in `ARCHITECTURE-ROADMAP.md` and their ADRs.

## 7. Phase 6 completion target — final integrated system

Final architecture freeze requires evidence-backed decisions for every material component applicable to the chosen system.

The production implementation must be a distinct engineering surface that preserves validated behavior while adding production concerns explicitly. Research runners are not automatically promoted into production code.

Before leaving Phase 6, the implementation must at minimum support the applicable P0 agent/evaluator capabilities in `DELIVERY-ACCEPTANCE.md`, including:

- real industrial API integration;
- contextualize / investigate / execute behavior;
- clarification or safe insufficiency handling;
- escalation/handoff;
- incomplete/conflicting/unavailable result handling;
- inspectable trace;
- integrated evaluation without gold leakage.

The exact productionization sequence, decision register and architecture-freeze criteria are maintained in `ARCHITECTURE-ROADMAP.md`.

## 8. Phase 7 completion target — prove the requested project, not only the architecture

Protect the final project window primarily for integration, regression and evidence closure rather than repeated speculative research.

Required delivery evidence includes, where applicable:

- unit and deterministic regression tests;
- evaluator/behavior preservation tests;
- real tool/API contract and integration tests;
- end-to-end production-path tests covering the required agent modalities;
- clarification/abstention/escalation tests;
- incomplete/conflicting/unavailable-data robustness tests;
- provider/tool failure and recovery tests;
- authorization/idempotency/security tests;
- latency/load/resource measurements;
- inspectable production traces and observability evidence;
- reproducible environment/build/deployment;
- rollback/reversal validation;
- versioned final release/configuration evidence;
- limitations/non-claims and operational runbooks;
- final acceptance crosswalk showing each applicable P0/P1 item and its evidence.

The final demonstration must exercise the real production path rather than a mock-only path and should show **live agent behavior + per-run evaluation + reliability/robustness evidence**, not only one happy-path answer.

## 9. Repository-wide definition of done

Project completion requires:

```text
requested P0 capabilities demonstrably covered
+
trustworthy integrated evaluation framework
+
scientific evidence strong enough for the claims
+
production-path engineering strong enough for real operation
+
material decisions satisfying PROJECT-PRINCIPLES
```

An uncovered P0 acceptance item is a blocker unless the final scope is explicitly reduced with an evidence-honest limitation.

If external constraints prevent the strongest intended target by 2026-09-08, deliver the strongest evidence-backed scope achieved with explicit limitations rather than overstating readiness.

## 10. Stop / pivot rules

- preserve failed and consumed experiments; never silently erase or rerun them;
- do not score incomplete packets;
- do not cross evaluator/private/independent boundaries before authorization;
- do not promote `QUALIFIED` to `PREFERRED/FROZEN` without systematic comparison;
- do not freeze architecture because a component is already implemented or popular;
- do not add RAG, multi-agent, memory, vector DB, reranking or similar complexity without measurable advantage over a simpler baseline **and a mapped acceptance/risk need**;
- do not accept adaptive complexity without measurable benefit over a static baseline and deterministic safety boundaries;
- do not infer production fitness from a demo or benchmark alone;
- do not treat C4 candidate evidence as proof that every required product behavior is integrated;
- after material implementation changes, rerun applicable regression/evaluation before release;
- preserve enough final-window capacity to close P0 acceptance, integration, documentation and reproducibility before pursuing P2 enhancements.
