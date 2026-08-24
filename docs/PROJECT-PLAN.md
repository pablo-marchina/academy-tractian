# Academy × TRACTIAN — Current Project Action Plan

**Status:** ACTIVE / reviewed canonical plan  
**Planning checkpoint:** 2026-08-24 09:53 BRT  
**Final delivery target:** 2026-09-08  
**Supersedes:** the E14v-era plan from 2026-08-20, archived at `docs/archive/PROJECT-PLAN-2026-08-20.md`  
**Current status source:** [`docs/CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Progress ledger:** [`docs/PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)  
**Machine checkpoint:** [`research/results/project-progress-checkpoint-2026-08-24.json`](../research/results/project-progress-checkpoint-2026-08-24.json)

## 1. Planning objective

Finish the project with the strongest evidence obtainable under the frozen P12 governance while preserving scientific validity, production-first requirements and the 2026-09-08 delivery deadline.

The plan now runs three material tracks in parallel:

1. **Candidate-evidence / provider-capacity:** make a defensible capacity decision, then obtain one complete prospective EXPOSED_POOL comparison.
2. **Independent evidence:** authorize and prepare FRESH_BLIND without exposing outcomes to candidate development.
3. **Production-fit / architecture:** gather comparative evidence for serving/runtime/architecture choices without prematurely freezing the architecture.

No track may weaken P12 boundaries for schedule convenience.

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

The immediate problem is **not another P12-C3 retry**. The next scientific generation is blocked until provider-capacity alternatives are systematically compared and an explicit decision is frozen.

## 3. Reviewed priority order

### P0 — Preserve validity

Non-negotiable:

- no C1/C2/C3 rerun;
- no reuse of partial C2/C3 parents as a confirmatory packet;
- no private scoring on incomplete packets;
- no complete-case reinterpretation;
- no candidate tuning from FRESH_BLIND/LEGACY_LOCKED_TEST outcomes;
- no semantic measurement unless deterministic prerequisites pass;
- no architecture or production-readiness claim from dry-run/infrastructure evidence.

### P1 — Provider-capacity ADR before P12-C4

Two consecutive prospective experiments failed during provider collection. A new experiment without a materially improved feasibility argument is not justified.

### P2 — FRESH_BLIND readiness in parallel

Independent evidence is schedule-critical and cannot wait until the end of EXPOSED_POOL work. Preparation starts now; outcome access remains blocked until generation freeze.

### P3 — One complete prospective EXPOSED_POOL packet

Only a complete frozen packet may reach private deterministic scoring.

### P4 — Deterministic → semantic → production-fit gates

Only deterministic survivors advance. A gate pass is not automatically `PREFERRED` or final.

### P5 — Generation freeze → independent evidence → architecture freeze

FRESH_BLIND must remain independent until candidate/evaluator generation is frozen.

## 4. Workstream A — provider-capacity decision and next EXPOSED_POOL experiment

### A0 — P12-C3 closure — COMPLETE

Completed:

- sanitized terminal closure committed;
- run `32672167702` recorded as terminal operational failure;
- C3 resume/rerun/partial scoring forbidden;
- raw partial parents remain unavailable for candidate/scoring decisions;
- current-status, progress-ledger and action-plan documents updated.

### A1 — Provider-capacity alternatives ADR — HARD PREREQUISITE / 2026-08-24

Decision question:

> Which generation path gives the highest defensible probability of completing the full prospective geometry on schedule while preserving scientific comparability, reproducibility and acceptable cost/complexity?

At minimum compare:

1. **Same Groq model/config with materially different capacity arrangement** — e.g. verified quota/paid capacity or a contract that removes the failure mode rather than another timing tweak.
2. **Same model through another provider/serving path, if actually available.**
3. **Alternative model/provider path** with explicit scientific-confound analysis.
4. **Local/self-hosted inference** if throughput/hardware evidence shows it can finish on schedule.
5. **Scope-preserving operational alternatives** such as reserved capacity or another reproducible serving route; do not treat more retries as a new alternative by itself.

Required comparison dimensions:

- evidence-backed probability of completing the full packet;
- rate-limit/capacity guarantees;
- model/prompt equivalence;
- latency/throughput;
- total cost;
- reproducibility;
- operational complexity;
- scientific confound risk;
- provider-free prequalification feasibility;
- final production fit.

**Required output:** short ADR with alternative table, quantitative/qualitative evidence, Pareto frontier, selected path, rejected paths, reversal triggers and explicit assumptions.

**GO condition for A2:** selected path has a defensible feasibility argument materially stronger than C2/C3.

**NO-GO:** if no path is credible enough, do not preregister C4 merely to preserve schedule appearance; pivot scope transparently.

### A2 — P12-C4 preregistration + activation — target 2026-08-24/25

Only after A1 GO.

Requirements:

- fresh seeds;
- no C2/C3 partial-parent reuse;
- EXPOSED_POOL scope explicit;
- provider/model change isolated from candidate changes;
- complete-packet requirement frozen;
- deterministic scorer/aggregation/bootstrap/LOGO frozen before outcomes;
- missingness/failure semantics frozen;
- provider-free activation/eligibility child gate;
- no trigger/live call before activation PASS and live manifest freeze.

If A1 selects an alternative model/provider, C4 must state which effects remain comparable with C1/C2/C3 and which do not.

### A3 — Complete prospective collection — target 2026-08-25 to 2026-08-27

Exit gate:

```text
complete preregistered parent geometry
complete fixed compared-arm packet
same parent shared across compared arms where pairing is preregistered
candidate private-oracle accesses = 0
FRESH_BLIND accesses = 0
LEGACY_LOCKED_TEST accesses = 0
all operational missingness explicitly classified
```

If this gate is not reached, do not score partial data.

### A4 — Deterministic scoring and comparison — immediately after complete freeze

Required outputs:

- full-pool metrics;
- absolute deterministic gates;
- preregistered paired/factorial contrasts;
- 95% asset-story-group cluster percentile bootstrap, 20,000 resamples, seed 20260822 unless prospectively changed with justification;
- all 7 LOGO analyses when the seven-group geometry remains applicable;
- per-group results;
- modality slices;
- safety/failure families;
- operational denominators/missingness;
- no weighted utility score.

Decision:

- **no survivor:** semantic stage stops; diagnose and decide whether any additional EXPOSED_POOL cycle is worth the remaining schedule;
- **survivor(s):** only deterministic survivors become eligible for a semantic child preregistration;
- deterministic PASS = qualification at that gate only.

## 5. Workstream B — FRESH_BLIND readiness in parallel

This workstream is active now and is independent of A1–A4 outcome collection.

### B1 — Tier A external blind source — target 2026-08-25 23:59 BRT

Required properties:

- real-domain relevance;
- independent authorship/control from candidate development;
- no candidate-developer access to expected paths/outcomes;
- explicit source ownership and access log;
- fixed evaluation packet before final candidate access;
- no adaptive feedback during development.

Allowed before generation freeze: schema/contracts, ownership, access control, infrastructure readiness and packet sealing — **not outcome inspection**.

### B2 — Tier B independently authored blind fallback — target 2026-08-28 23:59 BRT

If Tier A cannot be authorized, prepare the independently authored fallback contemplated by BIG-B3/B4.

It cannot reuse or relabel exposed DEV/VALIDATION/LOCKED_TEST information.

### B3 — Blind execution gate

Do not access final blind outcomes until:

- candidate generation frozen;
- evaluator frozen;
- no further candidate/evaluator change allowed from blind outcomes;
- source authorization explicit and logged.

A breach consumes the source for the affected generation.

## 6. Workstream C — semantic gate

Target: immediately after deterministic survivors, ideally 2026-08-27/28.

### C1 — Semantic child preregistration

Before semantic labels:

- freeze exact survivor arms;
- claim-packet construction;
- judge/model/config;
- semantic metrics/thresholds;
- missingness/failure treatment;
- one-shot attempt semantics.

### C2 — Semantic measurement

Run only on deterministic survivors. Semantic failure prevents progression. Do not use labels as same-generation tuning data.

## 7. Workstream D — production-fit and architecture comparison

**Active in parallel: 2026-08-24 to 2026-08-31.**

Material open choices:

- provider/model serving strategy;
- orchestration/runtime final choice;
- retrieval/RAG vs simpler evidence routing;
- vector DB/reranking need;
- multi-agent decomposition vs single-agent orchestration;
- persistent memory need;
- observability backend;
- authorization/idempotency/retry boundaries;
- UI/demo architecture;
- deployment topology.

For each material choice:

1. define requirement and evaluator/measurement;
2. identify simple/null baseline and credible alternatives;
3. compare latency, reliability, cost, maintainability, observability and security;
4. keep optional complexity removable unless evidence supports it;
5. record state: `UNASSESSED`, `RESEARCHED`, `QUALIFIED`, `PREFERRED`, `FROZEN`.

### D1 — Immediate serving/capacity overlap

A1 and D share one question: the serving path chosen for the next experiment should also be evaluated for production fit. Avoid choosing an experimental transport that cannot plausibly support the final system unless explicitly treated as temporary experimental infrastructure.

## 8. Workstream E — final generation, blind evidence and architecture freeze

Target window: 2026-08-30 to 2026-09-04, conditional on prior gates.

### E1 — Generation freeze

Freeze candidate/evaluator generation only after:

- deterministic gates pass;
- required semantic gates pass;
- production-fit comparison supports the selected candidate;
- no material unevaluated alternative remains inside declared search scope.

### E2 — FRESH_BLIND measurement

Execute the separately authorized packet exactly as frozen.

- PASS may support independent generalization evidence.
- FAIL cannot be tuned against without consuming that blind generation and requiring a new independent source for a changed generation.

### E3 — LEGACY_LOCKED_TEST

Use only if separately authorized for supplementary final characterization. Never substitute it for FRESH_BLIND.

### E4 — Architecture freeze

Only after candidate evidence and production-fit validation support it.

## 9. Workstream F — regression, integration and delivery

Target window: 2026-09-03 to 2026-09-08.

Required before delivery:

- end-to-end real-contract regression;
- deterministic safety/security regression;
- provider failure/recovery tests;
- reproducible environment/secrets setup;
- deployment/runbook documentation;
- observability evidence;
- final architecture/ADR documentation;
- evaluation methodology/results narrative;
- explicit limitations/non-claims;
- demo/presentation from the production path, not a mock path.

## 10. Near-term execution board

### Next 24 hours — 2026-08-24

**Must complete:**

1. A1 provider-capacity alternatives research and ADR.
2. B1 Tier A FRESH_BLIND authorization/preparation work.
3. D1 serving/production-fit comparison evidence.

**Conditional:**

4. If and only if A1 = GO, draft/freeze P12-C4 preregistration and provider-free activation package.

### Next 48 hours — by 2026-08-25 23:59 BRT

- P12-C4 activation/live contract ready only if capacity decision supports it;
- Tier A FRESH_BLIND source authorized or explicit escalation to Tier B fallback;
- no new live generation without provider-free eligibility evidence.

### Next 72 hours — by end of 2026-08-27

Target:

- complete prospective EXPOSED_POOL packet frozen;
- deterministic scoring complete or immediately executable.

**Go/no-go:** if no complete packet exists, reassess project scope. Do not spend the remaining delivery buffer on repeated low-feasibility provider attempts.

## 11. Schedule checkpoints

### 2026-08-24

- provider-capacity ADR;
- FRESH_BLIND Tier A readiness;
- serving/production-fit research;
- conditional C4 preregistration.

### 2026-08-25 to 2026-08-27

- provider-free activation then complete prospective collection;
- deterministic scoring immediately after complete freeze;
- no partial scoring.

### 2026-08-27/28

- semantic child gate only for deterministic survivors;
- Tier B FRESH_BLIND fallback deadline 2026-08-28 23:59 BRT.

### 2026-08-28 to 2026-08-31

- production-fit comparison;
- candidate selection decision;
- close remaining material architecture alternatives;
- prepare generation freeze.

### 2026-08-31 to 2026-09-03

- generation/evaluator freeze;
- authorized FRESH_BLIND final measurement;
- supplementary locked characterization only if separately authorized.

### 2026-09-03 to 2026-09-05

- architecture freeze if evidence supports it;
- end-to-end regression and deployment validation.

### 2026-09-05 to 2026-09-08

- final documentation;
- reproducibility/runbook cleanup;
- production-path presentation/demo;
- delivery buffer for non-scientific defects.

## 12. Decision tree

```text
P12-C3 terminal operational failure
              │
              ▼
provider-capacity ADR ─────────────── FRESH_BLIND readiness (parallel)
              │                       production-fit research (parallel)
          ┌───┴────┐
          │        │
        NO-GO      GO
          │        │
          ▼        ▼
 honest scope   P12-C4 preregistration
 reassessment        │
                     ▼
             provider-free activation
                     │
                     ▼
            complete prospective packet?
                 ┌───┴───┐
                 │       │
                no      yes
                 │       │
                 ▼       ▼
           no partial   deterministic
             scoring      scoring
                           │
                    ┌──────┴──────┐
                    │             │
              no survivors   survivor(s)
                    │             │
                    ▼             ▼
             scope decision   semantic child
                                  │
                              ┌───┴───┐
                              │       │
                            FAIL     PASS
                              │       │
                              ▼       ▼
                          no freeze  production-fit
                                     + generation freeze
                                           │
                                           ▼
                                  authorized FRESH_BLIND
                                           │
                                     ┌─────┴─────┐
                                     │           │
                                    FAIL        PASS
                                     │           │
                              honest limitation  architecture/final
                                                 evidence freeze
```

## 13. Stop / pivot rules

- no repeated cycle on the same provider-capacity failure mode without materially improved feasibility evidence;
- if A1 has no credible GO option, do not create C4 merely because the label is next;
- if no complete prospective EXPOSED_POOL packet exists by end of 2026-08-27, reassess scope and prioritize evidence-honest delivery;
- if no FRESH_BLIND source is authorized by 2026-08-28 23:59 BRT, downgrade the final generalization claim rather than substitute exposed evidence;
- if no candidate passes deterministic/semantic gates, do not force a production-ready claim;
- preserve 2026-09-03 onward for integration/regression/documentation except for genuinely blocking corrections.

## 14. Definition of success

Strongest target:

1. at least one candidate passes deterministic and required semantic gates;
2. candidate is best-supported after credible alternative and production-fit comparison;
3. candidate/evaluator generation is frozen;
4. independent FRESH_BLIND evidence supports the intended generalization claim;
5. architecture passes production-fit validation and is frozen;
6. end-to-end regression and operational documentation are complete.

If external constraints prevent the full target, success becomes an **evidence-honest delivery**: preserve failed attempts, avoid unsupported claims, quantify remaining uncertainty and deliver only components whose states are supported by evidence.
