# Benchmark Integrity Gate — BIG-B0→BIG-B4

**Status:** COMPLETE / CLOSED  
**Opened:** 2026-08-21  
**Closed:** 2026-08-22  
**Governance:** subordinate to [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Frozen protocol:** `P12_FRESH_BLIND_HYBRID_EXTERNAL_FIRST`  
**Agent optimization:** may resume only under the frozen P12 protocol

## Why this gate existed

A retrospective review found that the historical benchmark policy evolved over time: original E3 allowed `VALIDATION` to support selection/tuning, later aggregate validation feedback shaped subsequent development, and evaluator-validity work structurally inspected the legacy `LOCKED_TEST`. The repository therefore could not continue treating historical split names as proof of current independence.

The gate reconstructed the chronology, classified exposure, compared replacement evaluation designs, selected the best-supported protocol and made it executable/fail-closed before permitting further agent optimization.

Historical experiments remain immutable evidence under their contemporaneous protocols; this gate does not erase or retroactively falsify them.

## Completed sequence

```text
BIG-B0 — Benchmark Integrity Audit                 COMPLETE
          ↓
BIG-B1 — Exposure / Contamination Ledger          COMPLETE
          ↓
BIG-B2 — Evaluate Benchmark-Design Alternatives   COMPLETE
          ↓
BIG-B3 — Select New Evaluation Protocol           COMPLETE
          ↓
BIG-B4 — Freeze Evaluation Protocol               COMPLETE
          ↓
resume agent optimization under frozen P12
```

## BIG-B0 — factual reconstruction

Question answered: what benchmark information was accessed, measured, exposed or reused from E3 onward, under which policy and for what purpose?

Artifacts:

- [`../research/big-b0-benchmark-integrity-audit-2026-08-21.md`](../research/big-b0-benchmark-integrity-audit-2026-08-21.md)
- [`../research/results/big-b0-benchmark-access-ledger-2026-08-21.json`](../research/results/big-b0-benchmark-access-ledger-2026-08-21.json)

B0 preserved `UNKNOWN` where committed history could not prove local/operator-only behavior and did not infer independence from absence of committed evidence.

## BIG-B1 — exposure / independence classification

Artifacts:

- [`../research/big-b1-exposure-contamination-ledger-2026-08-21.md`](../research/big-b1-exposure-contamination-ledger-2026-08-21.md)
- [`../research/results/big-b1-exposure-contamination-ledger-2026-08-21.json`](../research/results/big-b1-exposure-contamination-ledger-2026-08-21.json)

Key classifications:

- `DEV` — development-exposed by design;
- historical `VALIDATION` — adaptively exposed and not independent for descendant generalization;
- legacy `LOCKED_TEST` — no committed candidate/task-quality execution established, but structurally exposed for evaluator design; `pristine/untouched` is unsupported.

The governing rule is retained: split-derived information that materially influences later development breaks independent-holdout status for the affected lineage even when feedback is aggregate-only.

## BIG-B2 — benchmark-design comparison

Artifacts:

- [`../research/experiments/big-b2-benchmark-design-comparison-preregistration.json`](../research/experiments/big-b2-benchmark-design-comparison-preregistration.json)
- [`../research/big-b2-benchmark-design-alternatives-2026-08-21.md`](../research/big-b2-benchmark-design-alternatives-2026-08-21.md)
- [`../research/results/big-b2-public-benchmark-geometry-2026-08-21.json`](../research/results/big-b2-public-benchmark-geometry-2026-08-21.json)
- [`../research/results/big-b2-benchmark-design-comparison-2026-08-21.json`](../research/results/big-b2-benchmark-design-comparison-2026-08-21.json)

B2 preregistered hard constraints/candidate families before comparative conclusions and identified three non-dominated families rather than selecting a winner. It established that historical DEV+VALIDATION must truthfully become one seven-group exposed development/selection pool and that grouped CV/LOGO is a prospective sensitivity/selection layer, not an independence repair.

## BIG-B3 — protocol selection

Artifacts:

- [`../research/big-b3-evaluation-protocol-selection-2026-08-21.md`](../research/big-b3-evaluation-protocol-selection-2026-08-21.md)
- [`../research/results/big-b3-evaluation-protocol-selection-2026-08-21.json`](../research/results/big-b3-evaluation-protocol-selection-2026-08-21.json)

Selected as `PREFERRED`:

> `P12_FRESH_BLIND_HYBRID_EXTERNAL_FIRST`

Core design:

```text
7 exposed historical DEV+VALIDATION groups
  → adaptive paired selection / group sensitivity
  → candidate + evaluator + judge + seed/outcome freeze
  → FRESH_BLIND real-domain measurement
       Tier A: partner-held external blind source
       Tier B: independently authored + independently adjudicated hidden source
  + qualified legacy LOCKED_TEST characterization
  + synthetic/adversarial robustness/regression
```

P3 remains only an explicit degraded fallback and requires a B3 amendment if no fresh blind path is feasible.

## BIG-B4 — executable protocol freeze

Freeze record:

- [`../research/big-b4-evaluation-protocol-freeze-2026-08-22.md`](../research/big-b4-evaluation-protocol-freeze-2026-08-22.md)

Canonical frozen artifacts:

- [`../research/frozen/big-b4-evaluation-protocol-v1.json`](../research/frozen/big-b4-evaluation-protocol-v1.json)
- [`../research/frozen/big-b4-blind-source-registry-v1.json`](../research/frozen/big-b4-blind-source-registry-v1.json)
- [`../research/frozen/big-b4-candidate-freeze-template-v1.json`](../research/frozen/big-b4-candidate-freeze-template-v1.json)
- [`../research/frozen/big-b4-final-access-authorization-template-v1.json`](../research/frozen/big-b4-final-access-authorization-template-v1.json)
- [`../research/experiments/validation-usage-superseding-correction-2026-08-22.json`](../research/experiments/validation-usage-superseding-correction-2026-08-22.json)

Executable enforcement/regression:

- [`../scripts/research/big_b4_protocol_guard.py`](../scripts/research/big_b4_protocol_guard.py)
- [`../scripts/research/big_b4_protocol_self_check.py`](../scripts/research/big_b4_protocol_self_check.py)
- [`../.github/workflows/research-big-b4-protocol-self-check.yml`](../.github/workflows/research-big-b4-protocol-self-check.yml)
- [`../research/results/big-b4-protocol-self-check-2026-08-22.json`](../research/results/big-b4-protocol-self-check-2026-08-22.json)

Provider-free self-check result: **24 / 24 PASS**. Git blob pins for benchmark split, B2 preregistration and B3 selection matched exactly. No provider inference or private benchmark semantic read was required.

## Frozen evidence roles

### `EXPOSED_POOL`

Historical DEV + VALIDATION, exactly seven independent asset/story groups.

Allowed:

- candidate development;
- model/prompt/policy/runtime/retrieval/planner/guard research;
- paired candidate selection;
- ablations;
- evaluator development/qualification;
- failure analysis;
- regression and robustness work.

Forbidden claim: fresh/blind independent generalization.

### `FRESH_BLIND`

Primary independent real-domain generalization evidence.

Current state: `NO_BLIND_SOURCE_AUTHORIZED`.

A source must be registered, unbreached and under custody. Candidate/evaluator/judge/seed/outcome policy must be frozen before one-shot final authorization. Developers may not inspect hidden semantics or receive iterative partial feedback.

### `LEGACY_LOCKED_TEST`

Three historical groups retained as **qualified supplementary held-out domain characterization**.

- development/selection/ablation access: denied;
- developer semantic inspection: denied;
- candidate execution: denied until final authorization;
- private scoring: only after outputs are fixed and final authorization exists;
- at most one final measurement cycle per frozen candidate generation;
- `pristine` / `untouched` wording: forbidden.

### `SYNTHETIC_ADVERSARIAL`

Supplementary robustness, evaluator/judge qualification and regression only. It is never sufficient by itself for a production-domain generalization claim.

## Frozen statistical and comparison rules

- primary independent/generalization unit: `asset_story_group`;
- hierarchy: `asset_story_group → scenario → repeated_run`;
- groups receive equal primary weight;
- candidate comparisons are paired on the same groups and matched seeds where supported;
- stochastic candidates require at least 3 repetitions per scenario for stability/reliability claims;
- repetition count is frozen before observing candidate outcomes;
- LOGO group sensitivity is mandatory;
- `investigate`, `execute` and `contextualize` slices are retained;
- for at least 5 independent groups: 95% group-cluster percentile bootstrap, 20,000 resamples, seed `20260822`;
- for fewer than 5 groups: per-group outcomes and coverage limitations are primary; no population-style bootstrap interval is promoted as primary evidence;
- naive fold standard error is not represented as a universally unbiased uncertainty estimator;
- effect sizes and intervals are primary; formal p-values are secondary;
- if two or more related confirmatory p-value tests are used, Holm family-wise correction is required.

This supersedes the older provisional scenario-as-primary-unit language where multiple scenarios share one asset/story lineage.

## Frozen safety / evaluator / judge rules

Hard safety violations are non-compensable. A confirmed hard-safety failure blocks promotion regardless of quality or efficiency improvement.

Candidate paths may never read private oracle material.

Private evaluator scoring requires candidate outputs to be fixed first. Evaluator validity/qualification and exact version hash are frozen per final candidate generation.

A semantic judge is used only where semantic adjudication is required; a gating judge needs separate qualification evidence and frozen identity/prompt/runtime/parameters. Material evaluator/judge changes after blind outcomes consume the previous blind measurement for the new stack generation.

## Failure and retry policy

No failed run is silently dropped.

- task/agent/candidate-caused failure → task failure;
- expected scenario/API fault → part of scenario;
- external provider/infrastructure/evaluator-process failure → separate operational category;
- at most one replacement attempt, and only for pre-model transport, runner/repository infrastructure or evaluator-process crash without outcome exposure;
- task-quality/safety failures are never rerun as replacements;
- exhausted external failure remains explicit missing operational evidence with denominators/sensitivity disclosed.

## Blind-source reversal / breach rules

- Tier A operational cutoff: **2026-08-25 23:59 America/Sao_Paulo**;
- Tier B operational cutoff: **2026-08-28 23:59 America/Sao_Paulo**;
- if Tier A is not operational, planning moves to Tier B;
- if neither is operational, P3 requires an explicit B3 amendment and downgraded claims;
- hidden semantic leak, expected-label exposure, iterative partial feedback, or material candidate/evaluator/judge adaptation to blind outcomes consumes/reclassifies the affected source for that lineage;
- consumed measurements and breach records are preserved, never erased.

## Post-B4 project state

```text
benchmark integrity / protocol validity   FROZEN / GATE CLOSED
agent optimization                        AUTHORIZED ON EXPOSED_POOL UNDER P12
historical VALIDATION                     EXPOSED_POOL; ADAPTIVE USE ALLOWED
FRESH_BLIND                               NO SOURCE AUTHORIZED; FINAL ACCESS BLOCKED
LEGACY_LOCKED_TEST                        FINAL ACCESS BLOCKED
E14v historical line                      PRESERVED; MUST BE REINTERPRETED UNDER P12
final architecture                        UNFROZEN
production-readiness claim                NOT AUTHORIZED
```

Closing BIG-B4 does **not** mean any historical model/runtime/judge/architecture is now final. It freezes the evaluation protocol that must govern the remaining systematic research, candidate comparison, candidate-generation freeze and eventual blind/final evidence.
