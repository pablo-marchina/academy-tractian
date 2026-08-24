# Academy × TRACTIAN — Current Project Action Plan

**Status:** ACTIVE / canonical plan  
**Planning checkpoint:** 2026-08-23 23:50 BRT  
**Final delivery target:** 2026-09-08  
**Supersedes:** the E14v-era plan from 2026-08-20, archived at `docs/archive/PROJECT-PLAN-2026-08-20.md`  
**Current status source:** [`docs/CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)

## 1. Planning objective

Finish the project with the strongest evidence that can be obtained under the frozen P12 governance while preserving scientific validity, production-first requirements and the 2026-09-08 delivery deadline.

The plan is no longer a linear "finish EXPOSED_POOL first, then think about everything else" sequence. Two critical dependencies must progress in parallel:

1. **Candidate-evidence track:** recover from the C2/C3 provider-capacity failures, obtain a complete prospective EXPOSED_POOL comparison, then run deterministic/semantic gates.
2. **Independent-evidence track:** authorize and prepare a FRESH_BLIND source without exposing its outcomes to candidate development.

Production-fit and architecture research also proceeds in parallel, but no architecture is frozen before evidence supports a candidate.

## 2. Current starting point

```text
P12-C1    complete scientific comparison; both arms failed deterministic gates
P12-C2    consumed operational failure; 31/36 parents; no scoring
P12-C3    consumed terminal operational failure; 3/36 parents; no scoring
QUALIFIED current candidate      none
PREFERRED current candidate      none
FRESH_BLIND source               none authorized
LEGACY_LOCKED_TEST               blocked
semantic v4.2 current candidate  not authorized
architecture                     unfrozen
```

The immediate problem is **not another blind retry of P12-C3**. The immediate problem is deciding how to obtain a complete 36-parent prospective packet reliably enough to justify a new experiment.

## 3. Priority order

### P0 — Preserve validity

Never trade scientific validity for schedule speed.

Non-negotiable:

- no C2 or C3 rerun;
- no reuse of partial C2/C3 parents as a confirmatory packet;
- no private scoring on incomplete packets;
- no complete-case reinterpretation;
- no candidate tuning from FRESH_BLIND/LEGACY_LOCKED_TEST outcomes;
- no semantic measurement unless deterministic gate prerequisites pass;
- no architecture or production-readiness claim from dry-run/infrastructure evidence.

### P1 — Solve provider-capacity collection before the next experiment

Two consecutive prospective cycles failed operationally at provider collection. A new experiment must be preceded by an explicit capacity decision.

### P2 — Prepare FRESH_BLIND in parallel

Independent evidence is now a schedule-critical dependency. Waiting until after candidate selection creates unacceptable deadline risk.

### P3 — Obtain one complete EXPOSED_POOL prospective comparison

Only a complete frozen packet may reach private deterministic scoring.

### P4 — Close deterministic → semantic → production-fit gates

Only survivors advance.

### P5 — Freeze generation/architecture, then execute final independent evidence

FRESH_BLIND must remain independent until candidate generation is frozen.

## 4. Workstream A — provider-capacity decision and next EXPOSED_POOL experiment

### A0 — Close P12-C3 formally — COMPLETE

Completed:

- sanitized C3 terminal closure committed;
- run `32672167702` recorded as terminal operational failure;
- artifact hashes and public checkpoint metadata preserved;
- C3 resume/rerun explicitly forbidden;
- raw parent outputs remain uncommitted and uninspected for candidate/scoring decisions.

### A1 — Provider-capacity alternative analysis — 2026-08-24

Decision question:

> Which operational generation path is most likely to complete the frozen 36-parent prospective geometry within the remaining schedule while preserving acceptable scientific comparability, cost and reproducibility?

At minimum compare these credible classes:

1. **Same Groq model/config with a newly preregistered longer-horizon/reset-aware schedule.**
   - strongest scientific comparability;
   - must prove capacity feasibility before live outcome collection;
   - cannot merely reuse the terminal C3 policy.
2. **Same model through another provider/serving path, if actually available.**
   - preserves model family but changes transport/provider behavior;
   - requires provider/config qualification and cost/availability evidence.
3. **Alternative model/provider candidate.**
   - larger scientific change;
   - requires a new model-selection rationale and prospective comparison;
   - may improve operational feasibility at the cost of comparability.
4. **Local or self-hosted inference path.**
   - evaluate hardware/runtime feasibility, throughput and reproducibility;
   - do not assume viability if it cannot complete the experiment on schedule.
5. **Paid/credit-backed provider capacity, if project constraints allow it.**
   - compare expected completion reliability and total cost against zero-cost paths;
   - cost is a production-fit metric, not an automatic disqualifier unless project constraints make it hard.

Required comparison dimensions:

- probability of completing 36 parents before deadline;
- rate-limit/reset behavior and capacity guarantees;
- model/prompt equivalence;
- latency/throughput;
- total cost;
- reproducibility;
- operational complexity;
- risk of introducing a scientific confound;
- ease of provider-free prequalification;
- fit with final production requirements.

Output: a short ADR/decision record with a Pareto comparison and reversal triggers.

### A2 — Preregister the next prospective experiment — target 2026-08-24/25

Provisionally call it **P12-C4** only after A1 selects the collection path.

Requirements:

- fresh seeds;
- no C2/C3 partial parent reuse;
- same 7-group EXPOSED_POOL unless the new hypothesis explicitly changes scope;
- clear provider-capacity policy before first outcome;
- complete packet requirement preserved;
- deterministic scorer/aggregation/bootstrap/LOGO frozen before outcomes;
- candidate definition changes explicitly isolated from operational changes;
- activation/eligibility child gate provider-free before live execution.

### A3 — Execute complete prospective collection — target 2026-08-25 to 2026-08-27

Exit gate:

```text
36/36 new common parents
144/144 fixed factorial outputs (if factorial design retained)
same parent shared across compared arms
candidate private-oracle accesses = 0
FRESH_BLIND accesses = 0
LEGACY_LOCKED_TEST accesses = 0
all operational missingness explicitly classified
```

If this gate is not reached, do not score partial data.

### A4 — Deterministic scoring and factorial/paired analysis — immediately after complete freeze

Use the frozen deterministic evaluator unless a prospectively justified evaluator amendment is required before scoring.

Required outputs:

- full-pool metrics;
- absolute deterministic gates;
- primary paired/factorial contrasts;
- 95% group-cluster percentile bootstrap, 20,000 resamples, seed 20260822;
- all 7 LOGO analyses;
- per-group results;
- modality slices;
- safety/failure families;
- operational denominators/missingness;
- no weighted utility score.

Decision:

- **no arm passes:** stop semantic stage, diagnose failures, decide whether another EXPOSED_POOL experiment is still justified by remaining time/evidence value;
- **one or more arms pass:** only deterministic survivors become eligible for a semantic child preregistration;
- deterministic PASS means `QUALIFIED` at that gate, not `PREFERRED`/final.

## 5. Workstream B — FRESH_BLIND readiness in parallel

This workstream starts **now**, without waiting for A4.

### B1 — Tier A external blind source — target by 2026-08-25 23:59 BRT

Attempt to authorize an external independently controlled blind source consistent with the frozen P12 protocol.

Required properties:

- real-domain relevance;
- independent authorship/control from candidate development;
- no candidate developer access to expected paths/outcomes;
- explicit source ownership and access log;
- fixed evaluation packet before candidate-final access;
- no adaptive feedback during candidate development.

Preparation may include schema/contracts and operational readiness, but not outcome exposure.

### B2 — Tier B independently authored blind fallback — target by 2026-08-28 23:59 BRT

If Tier A is unavailable, prepare the independently authored blind fallback already contemplated by BIG-B3/B4.

The fallback must be genuinely independent. It cannot be a relabeling of already-exposed DEV/VALIDATION/LOCKED_TEST information.

### B3 — Blind access gate

Do not execute the final blind packet until:

- candidate generation is frozen;
- evaluator is frozen;
- no further candidate/evaluator changes are allowed from blind outcomes;
- access authorization is explicit and logged.

Any blind breach consumes that source for the affected generation.

## 6. Workstream C — semantic gate

Target: immediately after deterministic survivors, ideally 2026-08-27/28.

### C1 — Child preregistration

Before any semantic label is produced, freeze:

- exact survivor arms;
- claim packet construction;
- judge/model/config;
- semantic metrics/thresholds;
- missingness/failure treatment;
- one-shot attempt semantics.

### C2 — Qualified semantic measurement

Run only for deterministic survivors. If semantic fails, candidate remains unqualified for progression.

Do not use semantic labels as candidate-tuning data in the same generation.

## 7. Workstream D — production-fit and architecture comparison

Target window: 2026-08-24 to 2026-08-31 in parallel with evidence collection.

This workstream is evidence gathering, not architecture freeze.

Material open choices include:

- orchestration/runtime final choice;
- retrieval/RAG vs simpler evidence routing;
- vector DB / reranking need;
- multi-agent decomposition vs single-agent orchestration;
- persistent memory need;
- observability backend;
- provider/model serving strategy;
- authorization/idempotency/retry boundaries;
- UI/demo architecture;
- deployment topology.

For each material choice:

1. define requirement and measurement;
2. identify simple/null baseline and credible alternatives;
3. compare latency, reliability, cost, maintainability, observability and security;
4. keep optional complexity removable unless evidence supports it;
5. record decision state (`UNASSESSED`, `RESEARCHED`, `QUALIFIED`, `PREFERRED`, `FROZEN`).

Do not let integration/demo work silently freeze architecture.

## 8. Workstream E — final generation, blind evidence and architecture freeze

Target window: 2026-08-30 to 2026-09-04, conditional on prior gates.

### E1 — Generation freeze

Freeze the candidate generation only after:

- deterministic gates pass;
- semantic gates pass where required;
- production-fit comparison supports the selected candidate;
- no material candidate alternative remains unevaluated within the declared search scope.

### E2 — FRESH_BLIND measurement

Run the separately authorized blind packet exactly as frozen.

- PASS can support independent generalization evidence.
- FAIL cannot be tuned against without consuming that blind generation and requiring a new independent source for a changed generation.

### E3 — LEGACY_LOCKED_TEST

Use only if separately authorized under P12 for supplementary final characterization. Do not substitute it for FRESH_BLIND.

### E4 — Architecture freeze

Only after candidate evidence and production-fit validation support the architecture.

A component becomes `FROZEN` only when the repository-wide completion gate in `PROJECT-PRINCIPLES.md` is satisfied.

## 9. Workstream F — regression, integration and delivery

Target window: 2026-09-03 to 2026-09-08.

Required before delivery:

- end-to-end real-contract regression;
- deterministic safety/security regression;
- provider failure/recovery tests;
- reproducible environment and secrets setup;
- deployment/runbook documentation;
- observability evidence;
- final architecture/ADR documentation;
- evaluation methodology/results narrative;
- limitations and non-claims explicitly documented;
- final demo/presentation built from the production path, not a separate mock path.

## 10. Schedule checkpoint

### 2026-08-24

- complete provider-capacity alternative analysis;
- start/continue FRESH_BLIND Tier A authorization work;
- continue production-fit research.

### 2026-08-24/25

- preregister and activate next EXPOSED_POOL experiment only after capacity decision;
- freeze live execution contract provider-free;
- target Tier A blind source authorization by 25 Aug 23:59 BRT.

### 2026-08-25 to 2026-08-27

- execute complete prospective EXPOSED_POOL collection;
- deterministic scoring immediately after freeze;
- no partial scoring.

### 2026-08-27/28

- semantic child gate only for deterministic survivors;
- Tier B blind-source fallback deadline by 28 Aug 23:59 BRT if Tier A fails.

### 2026-08-28 to 2026-08-31

- production-fit comparison and candidate-selection decision;
- close remaining material architecture alternatives;
- prepare generation freeze.

### 2026-08-31 to 2026-09-03

- freeze candidate generation/evaluator;
- execute authorized FRESH_BLIND final measurement;
- supplementary locked characterization only if separately authorized.

### 2026-09-03 to 2026-09-05

- architecture freeze if evidence supports it;
- end-to-end regression and deployment validation.

### 2026-09-05 to 2026-09-08

- final documentation;
- reproducibility/runbook cleanup;
- presentation/demo from production path;
- delivery buffer for non-scientific defects.

## 11. Decision tree

```text
P12-C3 terminal operational failure
              │
              ▼
provider-capacity alternatives + production-fit comparison
              │
              ▼
new preregistered EXPOSED_POOL experiment (provisionally C4)
              │
        ┌─────┴─────┐
        │           │
 incomplete       complete freeze
        │           │
        ▼           ▼
no partial      deterministic scoring
scoring             │
                 ┌──┴────────────┐
                 │               │
             no survivors     survivor(s)
                 │               │
                 ▼               ▼
      diagnose / decide      semantic child
      if another DEV loop       gate
      is worth schedule          │
                             ┌───┴───┐
                             │       │
                           FAIL     PASS
                             │       │
                             ▼       ▼
                         no freeze  production-fit
                                    comparison
                                         │
                                         ▼
                                candidate generation freeze
                                         │
                                         ▼
                                 authorized FRESH_BLIND
                                         │
                                  ┌──────┴──────┐
                                  │             │
                                FAIL           PASS
                                  │             │
                           no final claim   architecture/final
                                           evidence freeze
```

FRESH_BLIND source authorization/preparation runs in parallel on the left side of this tree but outcome access remains blocked until generation freeze.

## 12. Stop / pivot rules

To protect the 2026-09-08 delivery:

- do not spend repeated cycles on the same provider-capacity failure mode without a materially improved feasibility argument;
- if no complete prospective EXPOSED_POOL packet can be produced by the end of 2026-08-27, reassess scope and prioritize a scientifically honest final report over invalid repeated attempts;
- if no FRESH_BLIND source is authorized by the Tier B deadline, explicitly downgrade the final generalization claim rather than substituting exposed evidence;
- if no candidate passes deterministic/semantic gates, do not force a production-ready claim; deliver the strongest validated foundation, failure analysis and next research path;
- preserve time after 2026-09-03 for integration/regression/documentation.

## 13. Definition of project success

The strongest target remains:

1. at least one candidate passes deterministic and required semantic gates;
2. candidate is best-supported after credible alternative comparison and production-fit analysis;
3. candidate generation is frozen;
4. independent FRESH_BLIND evidence supports the generalization claim;
5. architecture passes production-fit validation and is frozen;
6. end-to-end regression and operational documentation are complete.

If external constraints prevent this full target, success becomes an **evidence-honest delivery**: preserve every failed attempt, avoid unsupported claims, quantify remaining uncertainty and deliver the strongest components whose states are actually supported by evidence.
