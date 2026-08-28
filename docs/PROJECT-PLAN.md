# Academy × TRACTIAN — Governed Project Plan to Production Delivery

**Status:** ACTIVE / canonical macro plan  
**Planning checkpoint:** 2026-08-28 09:17 BRT  
**Final delivery target:** 2026-09-08  
**Current status:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Immediate next steps:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Decision revalidation:** [`DECISION-REVALIDATION-MASTER-PLAN.md`](DECISION-REVALIDATION-MASTER-PLAN.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Source baseline:** [`../research/tractian-source-baseline-2026-08-27.md`](../research/tractian-source-baseline-2026-08-27.md)

## 1. Purpose

This document is the **master phase/milestone map** for delivering the strongest defensible TRACTIAN × Inteli individual project by 2026-09-08.

Use:

- `CURRENT-PROJECT-STATUS.md` — where the project is and what is authorized;
- `NEXT-STEPS.md` — what should be done next;
- `DECISION-REVALIDATION-MASTER-PLAN.md` — mandatory planning gate before all future material development;
- `DELIVERY-ACCEPTANCE.md` — what must demonstrably be true at final delivery;
- `ARCHITECTURE-ROADMAP.md` — how the integrated agent/evaluator reaches a production path;
- `PROJECT-PROGRESS-LOG.md` — completed evidence/history;
- `PROJECT-PRINCIPLES.md` — non-negotiable development rules.

The objective is not to maximize implementation volume. It is to maximize **required-scope coverage × scientific credibility × production quality × academic evidence quality** within the deadline and the permanent **USD 0 monetary hard constraint**.

## 2. Non-negotiable planning rules

All phases follow the fixed Project North Star and P1–P4:

- **P1 — systematic comparison:** no material architecture/product decision is final before credible alternatives are compared under explicit requirements;
- **P2 — production-first:** production constraints and partner-quality risks are part of selection, not post-hoc decoration;
- **P3 — quantitative/adaptive by default:** measurable decisions use metrics/uncertainty and adaptive policies must beat simpler static baselines;
- **P4 — eval-driven engineering:** requirements, evaluators, baselines and regression evidence drive implementation through delivery;
- **USD 0 — monetary hard constraint:** production/provider/service choices must not incur project API/service charges or require paid spillover.

A gate PASS means evidence for that gate. It does not automatically mean `PREFERRED`, `FROZEN`, final or production-ready.

### 2.1 Documentation-before-development rule

From the 2026-08-28 09:17 BRT checkpoint forward, every material workstream begins with:

```text
decision inventory / plan update
→ decision question + requirement/risk mapping
→ hard constraints
→ systematic research
→ credible alternatives + simple/null baseline
→ preregistered comparison
→ only then implementation / experiment
```

The mandatory checklist and initial revalidation inventory are in `DECISION-REVALIDATION-MASTER-PLAN.md`.

If a new credible alternative or a hard-constraint violation is discovered after a historical freeze, preserve the old evidence and create a prospective revalidation/supersession. Do not rewrite history and do not continue implementation merely because the current code works.

### 2.2 Acceptance-first priority rule

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

P0/rubric coverage must not be sacrificed to implement optional RAG, vector DB, reranking, persistent memory, multi-agent decomposition, protocol adapters, adaptive routing or richer UI merely because they are interesting. However, a material credible alternative that could improve the requested delivery must be systematically screened rather than deferred solely because the current baseline already passes acceptance.

### 2.3 Source-reconciliation rule

When a new upstream source is delivered or clarified:

```text
source audit
→ requirements reconciliation
→ delivery-acceptance reconciliation
→ decision revalidation
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
| **4R. Global decision revalidation — ACTIVE** | Reassess every material project choice under current rules, USD 0 and credible alternatives before further implementation | decision inventory + preregistered comparisons + prospective amendments |
| 5. Production-fit selection and independent validation | Compare material product choices, freeze candidate/evaluator and obtain authorized independent evidence | PREFERRED/FROZEN behavior + independent evidence |
| 6. Final architecture freeze and integrated implementation | Build the production-path agent + evaluation framework that covers P0/P1 | frozen architecture + integrated source/tests/config |
| 7. Integration, regression, demonstration and final delivery | Prove final acceptance rows end to end and make reviewer evidence easy to find | final reproducible package + demo + rubric evidence index |

`CURRENT-PROJECT-STATUS.md` remains authoritative for the active gate.

## 4. Active Phase 4R — decision revalidation

Phase 4R exists because final delivery acceptance and historical component freezes do not prove global optimality. It must complete before any new material implementation branch is treated as final-development work.

### 4.1 Immediate provider correction

The previous ADR-008 live packet is **not executable as-is** because it includes OpenAI GPT-5.6 Sol while the project now explicitly enforces USD 0 as a hard production eligibility constraint.

Therefore:

```text
ADR-008 historical artifact                 PRESERVED
old 32-call live packet                      SUSPENDED
calls consumed                               0 / 32
production provider selected                 NO
new requirement                              prospective zero-cost provider amendment
```

Provider discovery must search the current credible zero-cost space before preregistration. At minimum screen Gemini free-tier candidates, Groq free-tier candidates, OpenRouter explicitly free routes where identity/cost can be bounded, Cloudflare Workers AI free-tier candidates, and a feasible local/open-weight baseline. Other credible zero-cost providers discovered in current primary-source research must also be considered.

User-reported connection state is operational context only: Groq is reported connected; Gemini is pending user connection. Do not probe secrets/accounts before an amended provider experiment authorizes live execution.

### 4.2 Material decision review

The revalidation program covers at least:

- provider/model;
- agent topology including single-agent vs materially distinct multi-agent patterns;
- orchestration/runtime;
- tool topology/protocol;
- evidence/retrieval;
- memory/state;
- adaptive stopping/planning/routing;
- safety/authorization additions without weakening hard boundaries;
- evaluator/judge stack;
- observability;
- deployment;
- UI/integration where material to delivery quality.

Existing evidence may be enough to keep some decisions preferred; others require new controlled comparisons. The decision inventory in `DECISION-REVALIDATION-MASTER-PLAN.md` is the starting point.

### 4.3 C4 parallel recovery

C4 remains scientifically separate. First search for the exact original 177350-byte / 144-row artifact with SHA-256 `b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c`.

No reconstruction/rescoring/substitution is authorized by this planning update. If exact bytes are unavailable, any byte-identical recovery attempt requires its own prospective scientific amendment before execution.

## 5. Phase-transition rule

Every material transition follows:

```text
frozen inputs/current evidence
→ plan/decision question update
→ preregistered authorized work
→ validation
→ result artifact
→ provenance/hashes
→ freeze/closure
→ status update
→ next-step update
→ acceptance/architecture update if materially affected
```

For experimental/statistical gates, no later gate may run unless the new freeze explicitly opens it.

For architecture/product decisions, no choice may advance to `PREFERRED/FROZEN` merely because it exists, is popular, historically frozen in a narrower scope or performed well in a narrower research setting.

## 6. Phase 5 completion target — production-fit selection + independent evidence

Before final implementation:

- candidate behavior/configuration is frozen as required;
- evaluator generation/configuration is frozen as required;
- hidden independent outcomes remain inaccessible until separately authorized;
- material production choices have controlled comparison evidence;
- model/provider selection compares the strongest credible **zero-cost** quality frontier against feasible zero-cost hosted/local alternatives;
- single-agent/simple controller remains the topology baseline but is not final until materially credible alternative topologies are compared or prospectively excluded with evidence;
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
- reproducible zero-cost configuration/build/run path.

## 8. Phase 7 completion target — rubric-maximizing delivery

The final project window is protected for integration, regression, evidence closure and communication quality rather than unmeasured architecture breadth.

Required final evidence includes, where applicable:

- clean setup and reproducible run;
- unit/contract/integration/regression tests;
- real TRACTIAN API-path exercise;
- contextualization, investigation, execution, clarification/abstention and escalation coverage;
- degraded/conflicting/unavailable evidence handling;
- provider/tool/agent failure fallback;
- evaluator/behavior preservation tests;
- authorization/idempotency/security tests;
- latency/reliability/resource/quota measurements;
- observability/trace-inspection evidence;
- model/provider/runtime/architecture ADRs and trade-offs;
- quantitative experiment results with uncertainty;
- explicit USD 0 feasibility for the selected production path;
- limitations/non-claims and risks;
- runbook/fallback/rollback guidance;
- final integrated demonstration;
- concise rubric-to-evidence index.

The final demonstration must exercise the real integrated path rather than a mock-only path.

## 9. Deadline-protection plan

### 2026-08-28 → 2026-08-30 — global revalidation + scientific recovery search

Primary objective:

- freeze the new decision-revalidation governance;
- inventory every material decision and its evidence state;
- research/preregister the zero-cost provider comparison amendment;
- search for the exact C4 score-row artifact;
- preregister the first controlled topology/runtime comparisons before implementation.

### 2026-08-30 → 2026-09-02 — execute highest-value controlled comparisons

Target:

- provider/model comparison across the credible zero-cost set;
- agent-topology comparison;
- runtime/orchestration comparison where evidence shows it is material;
- adaptive policy comparisons where likely to affect quality/resource use;
- prospective ADR supersession only after results.

If a P2 experiment threatens P0/P1 completion, stop the P2 experiment.

### 2026-09-03 → 2026-09-05 — integrate Pareto-selected configuration + reliability

Target:

- integrate the best-supported zero-cost configuration;
- end-to-end scenario/regression suite;
- degraded/conflicting/unavailable evidence tests;
- action/permission/safety tests;
- human fallback/escalation handoff;
- model/tool/provider failure behavior;
- repeated-run reliability;
- latency/resource/quota/observability evidence;
- fix only evidence-backed failures.

### 2026-09-06 → 2026-09-07 — final documentation and demonstration hardening

Target:

- clean-environment reproduction;
- final architecture/decision records;
- rubric-to-evidence reconciliation;
- demonstration rehearsal using the real path;
- ensure every claim points to evidence and remains inside USD 0.

### 2026-09-08 — delivery

Only evidence-backed claims. No last-minute architecture change without regression/re-evaluation.

## 10. Stop / pivot rules

- preserve failed and consumed experiments; never silently erase or rerun them;
- do not score incomplete packets;
- do not cross evaluator/private/independent boundaries before authorization;
- do not promote `QUALIFIED` to `PREFERRED/FROZEN` without systematic comparison;
- do not freeze architecture because a component is already implemented, historically frozen in a narrower scope or popular;
- do not add optional complexity without measurable advantage over a simpler baseline;
- do not admit a paid provider/tool into the production feasible set while USD 0 is a hard constraint;
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
all material final choices revalidated against credible alternatives
+
USD 0 production/service feasibility
+
P1 production/partner-quality risks closed or explicitly bounded
+
official rubric dimensions backed by clear evidence
+
reproducible real-path delivery
```

If external constraints prevent the strongest intended target by 2026-09-08, deliver the strongest evidence-backed zero-cost scope achieved with explicit limitations rather than overstating readiness.
