# Academy × TRACTIAN — Governed Project Plan to Production Delivery

**Status:** ACTIVE / canonical macro plan  
**Planning checkpoint:** 2026-08-27 08:46 BRT  
**Final delivery target:** 2026-09-08  
**Current status:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Immediate next steps:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Source baseline:** [`../research/tractian-source-baseline-2026-08-27.md`](../research/tractian-source-baseline-2026-08-27.md)

## 1. Purpose

This document is the **master phase/milestone map** for delivering the strongest defensible TRACTIAN × Inteli individual project by 2026-09-08.

Use:

- `CURRENT-PROJECT-STATUS.md` — where the project is and what is authorized;
- `NEXT-STEPS.md` — what should be done next;
- `DELIVERY-ACCEPTANCE.md` — what must demonstrably be true at final delivery;
- `ARCHITECTURE-ROADMAP.md` — how the integrated agent/evaluator reaches a production path;
- `PROJECT-PROGRESS-LOG.md` — completed evidence/history;
- `PROJECT-PRINCIPLES.md` — non-negotiable development rules.

The objective is not to maximize implementation volume. It is to maximize **required-scope coverage × scientific credibility × production quality × academic evidence quality** within the deadline.

## 2. Non-negotiable planning rules

All phases follow the fixed Project North Star and P1–P4:

- **P1 — systematic comparison:** no material architecture/product decision is final before credible alternatives are compared under explicit requirements;
- **P2 — production-first:** production constraints and partner-quality risks are part of selection, not post-hoc decoration;
- **P3 — quantitative/adaptive by default:** measurable decisions use metrics/uncertainty and adaptive policies must beat simpler static baselines;
- **P4 — eval-driven engineering:** requirements, evaluators, baselines and regression evidence drive implementation through delivery.

A gate PASS means evidence for that gate. It does not automatically mean `PREFERRED`, `FROZEN`, final or production-ready.

### 2.1 Acceptance-first priority rule

Every material workstream must map to at least one of:

1. a P0/P1 row in `DELIVERY-ACCEPTANCE.md`;
2. an official academic evaluation criterion;
3. a material production/security/reliability risk that can block such a row; or
4. an experiment needed to select among credible alternatives for the above.

If it maps to none, defer it.

Priority order:

```text
P0 requested capabilities + trustworthy evaluation
        ↓
P1 production/partner-quality fitness needed to operate P0
        ↓
P2 optional complexity only with measured benefit
```

P0/rubric coverage must not be sacrificed to implement optional RAG, vector DB, reranking, persistent memory, multi-agent decomposition, protocol adapters, adaptive routing or richer UI merely because they are interesting.

### 2.2 Source-reconciliation rule

When a new upstream source is delivered or clarified:

```text
source audit
→ requirements reconciliation
→ delivery-acceptance reconciliation
→ architecture/next-step review
→ continue development
```

Do not allow implementation momentum to override a newer formal requirement or the actual delivered package.

## 3. Macro phases

| Phase | Objective | Exit evidence |
|---|---|---|
| 1. Governance and benchmark foundation | Freeze evidence roles, access rules, requirements and evaluation semantics | governance/source/benchmark foundations |
| 2. Candidate exploration and failure learning | Learn from historical implementation/experiment evidence without over-promoting it | preserved candidate/failure evidence |
| 3. Confirmatory packet generation | Collect and freeze a complete comparable candidate packet | frozen complete packet |
| 4. Deterministic, statistical and semantic evaluation | Score immutable outputs and select/reject exact survivors under frozen rules | evidence-backed survivor/no-survivor decision |
| 5. Production-fit selection and independent validation | Compare material product choices, freeze candidate/evaluator and obtain authorized independent evidence | PREFERRED/FROZEN behavior + independent evidence |
| 6. Final architecture freeze and integrated implementation | Build the production-path agent + evaluation framework that covers P0/P1 | frozen architecture + integrated source/tests/config |
| 7. Integration, regression, demonstration and final delivery | Prove final acceptance rows end to end and make reviewer evidence easy to find | final reproducible package + demo + rubric evidence index |

`CURRENT-PROJECT-STATUS.md` remains authoritative for the active gate.

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

For experimental/statistical gates, no later gate may run unless the new freeze explicitly opens it.

For architecture/product decisions, no choice may advance to `PREFERRED/FROZEN` merely because it exists, is popular or performed well in a narrower research setting.

## 5. Phase 4 completion target — candidate evidence

Phase 4 is complete only when the applicable frozen evaluation sequence produces an evidence-backed survivor/no-survivor decision.

Depending on the governing freezes, this may include:

- deterministic scoring;
- preregistered statistical analysis;
- robustness/sensitivity analysis;
- semantic child evaluation for exact eligible survivors only;
- explicit no-survivor closure when applicable.

Phase 4 does **not** by itself prove final TAPI delivery or production readiness.

## 6. Phase 5 completion target — production-fit selection + independent evidence

Before final implementation:

- candidate behavior/configuration is frozen as required;
- evaluator generation/configuration is frozen as required;
- hidden independent outcomes remain inaccessible until separately authorized;
- material production choices have controlled comparison evidence;
- model/provider comparison includes a credible quality frontier and feasible cost/local baselines rather than premature cost-only restriction;
- single-agent/simple controller remains the topology baseline;
- stable typed tool contract is compared against protocol/framework alternatives where material;
- failure continuity/human fallback, action safety, communication and observability requirements are explicit;
- every proposed final component has a requirement/risk rationale and reversal trigger.

## 7. Phase 6 completion target — integrated agent + evaluator

Final architecture freeze requires evidence-backed decisions for every applicable material component.

The production implementation must be a distinct engineering surface that preserves validated behavior while adding production concerns explicitly. Research runners are not automatically promoted into production code.

The integrated implementation must cover, as applicable:

- supplied TRACTIAN API contract through a stable typed tool boundary;
- contextualize/investigate/clarify-or-abstain/execute/escalate outcomes;
- authorization and action semantics;
- safe human fallback when evidence or system availability is insufficient;
- normalized inspectable traces;
- customer-safe response boundary;
- integrated evaluation of the same traces without leaking gold;
- robustness and repeated-run reliability;
- reproducible configuration/build/run path.

## 8. Phase 7 completion target — rubric-maximizing delivery

The final project window is protected for integration, regression, evidence closure and communication quality rather than speculative architecture work.

Required final evidence includes, where applicable:

- clean setup and reproducible run;
- unit/contract/integration/regression tests;
- real TRACTIAN API-path exercise;
- contextualization, investigation, execution, clarification/abstention and escalation coverage;
- degraded/conflicting/unavailable evidence handling;
- provider/tool/agent failure fallback;
- evaluator/behavior preservation tests;
- authorization/idempotency/security tests;
- latency/reliability/resource measurements;
- observability/trace-inspection evidence;
- model/provider/runtime/architecture ADRs and trade-offs;
- quantitative experiment results with uncertainty;
- limitations/non-claims and risks;
- runbook/fallback/rollback guidance;
- final integrated demonstration;
- concise rubric-to-evidence index.

The final demonstration must exercise the real integrated path rather than a mock-only path.

## 9. Deadline-protection plan

The exact gate sequence overrides calendar assumptions, but the remaining time should be protected with these planning windows.

### 2026-08-27 → 2026-08-29 — close current scientific decision path

Primary objective:

- close deterministic-scoring provenance and execute/freeze only the currently authorized gate;
- advance only through newly authorized statistical/semantic gates;
- produce the strongest defensible survivor/no-survivor conclusion.

Parallel, non-leaking work:

- complete P0/P1 gap inventory;
- prepare production decision questions/baselines;
- validate final demo/eval scenario coverage against the delivered package;
- do not prematurely freeze implementation technology.

### 2026-08-30 → 2026-09-02 — freeze material product decisions and implement core

Target:

- close highest-impact model/runtime/tool/topology decisions with controlled evidence;
- freeze validated behavior and production contracts;
- create the distinct production code boundary;
- integrate the agent and evaluation framework on the real supplied API path.

If a P2 feature threatens P0/P1 completion, drop the P2 feature.

### 2026-09-03 → 2026-09-05 — reliability, security and integrated evaluation

Target:

- end-to-end scenario/regression suite;
- degraded/conflicting/unavailable evidence tests;
- action/permission/safety tests;
- human fallback/escalation handoff;
- model/tool/provider failure behavior;
- repeated-run reliability;
- latency/resource/observability evidence;
- fix only evidence-backed failures.

### 2026-09-06 → 2026-09-07 — final documentation and demonstration hardening

Target:

- clean-environment reproduction;
- final README and architecture diagrams;
- ADR/limitations/risk review;
- rubric-to-evidence index;
- demonstration rehearsal using the real path;
- ensure every claim points to evidence.

### 2026-09-08 — delivery

Only evidence-backed claims. No last-minute architecture change without regression/re-evaluation.

## 10. Stop / pivot rules

- preserve failed and consumed experiments; never silently erase or rerun them;
- do not score incomplete packets;
- do not cross evaluator/private/independent boundaries before authorization;
- do not promote `QUALIFIED` to `PREFERRED/FROZEN` without systematic comparison;
- do not freeze architecture because a component is already implemented or popular;
- do not add optional complexity without measurable advantage over a simpler baseline;
- do not artificially constrain model quality only to reduce cost before value/quality is measured;
- do not accept adaptive complexity without measurable benefit over static baseline and deterministic safety boundaries;
- do not infer production fitness from a demo or benchmark alone;
- do not expose internal implementation detail to customers when it is not needed for resolution;
- do not let agent/provider failure break the underlying support path;
- after material implementation changes, rerun applicable regression/evaluation before release;
- after 2026-09-05, default against speculative P2 work unless it fixes a demonstrated delivery blocker.

## 11. Repository-wide definition of done

Project completion requires:

```text
all requested P0 capabilities demonstrably covered
+
trustworthy integrated evaluation framework
+
scientific evidence strong enough for the claims
+
P1 production/partner-quality risks closed or explicitly bounded
+
official rubric dimensions backed by clear evidence
+
reproducible real-path delivery
```

If external constraints prevent the strongest intended target by 2026-09-08, deliver the strongest evidence-backed scope achieved with explicit limitations rather than overstating readiness.