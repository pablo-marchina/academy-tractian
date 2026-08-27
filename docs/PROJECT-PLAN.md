# Academy × TRACTIAN — Governed Project Plan to Production Delivery

**Status:** ACTIVE / canonical macro plan  
**Planning checkpoint:** 2026-08-26 22:51 BRT  
**Final delivery target:** 2026-09-08  
**Current status:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Immediate next steps:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

## 1. Purpose

This document is the **master phase/milestone map** for the project. It intentionally does not duplicate current-state details, short-horizon execution instructions or the full architecture decision register.

Use:

- `CURRENT-PROJECT-STATUS.md` for where the project is now and what is authorized;
- `NEXT-STEPS.md` for what should be done next;
- `ARCHITECTURE-ROADMAP.md` for the general system/research-to-production architecture;
- `PROJECT-PROGRESS-LOG.md` for completed history and evidence transitions.

The objective remains to finish with the strongest defensible evidence and strongest production-path implementation achievable by 2026-09-08 without weakening scientific validity, security boundaries, evaluator independence or production fitness.

## 2. Non-negotiable planning rules

All phases follow the four repository-wide principles:

- **P1 — systematic comparison:** no material architecture/product decision is final before credible alternatives are compared under explicit requirements;
- **P2 — production-first:** production constraints are part of selection, not post-hoc decoration;
- **P3 — quantitative/adaptive by default:** measurable decisions use metrics/uncertainty and adaptive policies must beat simpler static baselines;
- **P4 — eval-driven engineering:** requirements, evaluators, baselines and regression evidence drive implementation through delivery.

A gate PASS means evidence for that gate. It does not automatically mean `PREFERRED`, `FROZEN`, final or production-ready.

## 3. Macro phases

| Phase | Objective | State source |
|---|---|---|
| 1. Governance and benchmark foundation | Freeze evidence roles, benchmark integrity, access rules and evaluation semantics | progress ledger / current status |
| 2. Candidate exploration and failure learning | Preserve and learn from historical candidate/experiment evidence | progress ledger |
| 3. Confirmatory packet generation | Qualify serving route, collect required common parents, expand fixed candidates and freeze a complete packet | current status / frozen results |
| 4. Deterministic, statistical and semantic evaluation | Score immutable outputs, run only separately authorized analysis gates and qualify exact survivors | current status / next steps |
| 5. Production-fit selection and independent validation | Compare production choices, freeze candidate/evaluator generation and obtain authorized independent evidence | architecture roadmap / ADRs |
| 6. Final architecture freeze and production implementation | Freeze evidence-backed architecture and create the production code path | architecture roadmap / ADRs |
| 7. Integration, regression, controlled deployment and final delivery | Prove the production path end to end and deliver reproducibly | release/integration evidence |

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
```

For an experimental/statistical gate, no later gate may run unless the new freeze explicitly opens it.

For an architecture/product decision, no choice may advance to `PREFERRED`/`FROZEN` merely because it already exists in the repository or worked in a narrower experiment.

## 5. Phase 4 completion target

Phase 4 is complete only when the applicable frozen evaluation sequence has produced an evidence-backed survivor decision.

Depending on the governing freezes, this may include:

- deterministic scoring;
- preregistered statistical analysis;
- robustness/sensitivity analysis;
- semantic child evaluation for exact survivors only;
- explicit no-survivor closure when applicable.

The exact immediate sequence is maintained in `NEXT-STEPS.md`, not here.

## 6. Phase 5 completion target

Before independent measurement and final production selection:

- candidate behavior/configuration is frozen as required;
- evaluator generation/configuration is frozen as required;
- material production decisions have controlled comparison evidence;
- unresolved assumptions and reversal triggers are explicit;
- hidden independent outcomes remain inaccessible until separately authorized.

Material architecture decisions and required comparison criteria are maintained in `ARCHITECTURE-ROADMAP.md` and their ADRs.

## 7. Phase 6 completion target

Final architecture freeze requires evidence-backed decisions for every material component applicable to the chosen system.

The production implementation must be a distinct engineering surface that preserves validated behavior while adding production concerns explicitly. Research runners are not automatically promoted into production code.

The exact productionization sequence, decision register and architecture-freeze criteria are maintained in `ARCHITECTURE-ROADMAP.md`.

## 8. Phase 7 completion target

The final project window should be protected primarily for integration, regression and evidence closure rather than repeated speculative research.

Required delivery evidence includes, where applicable:

- unit and deterministic regression tests;
- evaluator/behavior preservation tests;
- real tool/API contract and integration tests;
- end-to-end production-path tests;
- provider/tool failure and recovery tests;
- authorization/idempotency/security tests;
- latency/load/resource measurements;
- observability evidence;
- reproducible environment/build/deployment;
- rollback/reversal validation;
- versioned final release/configuration evidence;
- limitations/non-claims and operational runbooks.

The final demonstration must exercise the real production path rather than a mock-only path.

## 9. Repository-wide definition of done

Project completion requires both:

```text
scientific evidence strong enough for the claims
        +
production-path engineering strong enough for real operation
```

If external constraints prevent the strongest intended target by 2026-09-08, deliver the strongest evidence-backed scope achieved with explicit limitations rather than overstating readiness.

## 10. Stop / pivot rules

- preserve failed and consumed experiments; never silently erase or rerun them;
- do not score incomplete packets;
- do not cross evaluator/private/independent boundaries before authorization;
- do not promote `QUALIFIED` to `PREFERRED/FROZEN` without systematic comparison;
- do not freeze architecture because a component is already implemented or popular;
- do not add RAG, multi-agent, memory, vector DB, reranking or similar complexity without measurable advantage over a simpler baseline;
- do not accept adaptive complexity without measurable benefit over a static baseline and deterministic safety boundaries;
- do not infer production fitness from a demo or benchmark alone;
- after material implementation changes, rerun applicable regression/evaluation before release.
