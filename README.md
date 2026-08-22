# Academy × TRACTIAN — Industrial Agent Engineering & Evaluation

Repository central do TAPI individual **Engenharia e Avaliação de Agentes Industriais** (Inteli × TRACTIAN).

## Non-negotiable project governance

All work in this repository is governed by [`docs/PROJECT-PRINCIPLES.md`](docs/PROJECT-PRINCIPLES.md). The four repository-wide rules are:

1. **Systematic research + comparison before every material decision.** Passing a minimum gate means `QUALIFIED`, not “best” or final. A decision is final only after broad alternative search, controlled quantitative comparison, robustness/sensitivity analysis and production-fit confirmation.
2. **Production-first, never demo-first.** The final target is a real production-grade system. Demos, mocks and scripted happy paths may validate infrastructure but cannot establish production readiness or agent quality.
3. **Quantitative and adaptive by default.** Prefer measurable, calibrated, data-driven behavior and evaluate context-sensitive adaptation against simpler/static baselines while preserving deterministic safety boundaries.
4. **Eval-driven end to end.** Evaluation defines the engineering loop: requirement → evaluator → baseline → hypothesis → preregistered experiment → measurement → comparison → decision → regression coverage.

No material component is considered complete merely because it works or passes a gate. If a credible materially different alternative remains unevaluated, the choice remains experimental.

## Status

**Benchmark Integrity Gate — BIG-B0/B1/B2/B3/B4 COMPLETE — P12 evaluation protocol `FROZEN`**

The benchmark-integrity gate is closed. Agent optimization may resume **only under the frozen P12 protocol and only on permitted adaptive-development evidence**. FRESH_BLIND and LEGACY_LOCKED_TEST remain fail-closed until their separate final-authorization prerequisites are satisfied.

Canonical benchmark-integrity artifacts:

- [`research/big-b0-benchmark-integrity-audit-2026-08-21.md`](research/big-b0-benchmark-integrity-audit-2026-08-21.md) — factual chronological reconstruction;
- [`research/results/big-b0-benchmark-access-ledger-2026-08-21.json`](research/results/big-b0-benchmark-access-ledger-2026-08-21.json) — B0 machine-readable access inventory;
- [`research/big-b1-exposure-contamination-ledger-2026-08-21.md`](research/big-b1-exposure-contamination-ledger-2026-08-21.md) — B1 independence/influence classification;
- [`research/results/big-b1-exposure-contamination-ledger-2026-08-21.json`](research/results/big-b1-exposure-contamination-ledger-2026-08-21.json) — B1 machine-readable ledger;
- [`research/experiments/big-b2-benchmark-design-comparison-preregistration.json`](research/experiments/big-b2-benchmark-design-comparison-preregistration.json) — criteria/candidate-space freeze before B2 conclusion;
- [`research/big-b2-benchmark-design-alternatives-2026-08-21.md`](research/big-b2-benchmark-design-alternatives-2026-08-21.md) — B2 evidence synthesis and Pareto analysis;
- [`research/results/big-b2-public-benchmark-geometry-2026-08-21.json`](research/results/big-b2-public-benchmark-geometry-2026-08-21.json) — provider-free public group/fold geometry;
- [`research/results/big-b2-benchmark-design-comparison-2026-08-21.json`](research/results/big-b2-benchmark-design-comparison-2026-08-21.json) — machine-readable alternative comparison/Pareto frontier;
- [`research/big-b3-evaluation-protocol-selection-2026-08-21.md`](research/big-b3-evaluation-protocol-selection-2026-08-21.md) — B3 protocol decision record;
- [`research/results/big-b3-evaluation-protocol-selection-2026-08-21.json`](research/results/big-b3-evaluation-protocol-selection-2026-08-21.json) — machine-readable B3 selection and reversal triggers;
- [`research/big-b4-evaluation-protocol-freeze-2026-08-22.md`](research/big-b4-evaluation-protocol-freeze-2026-08-22.md) — executable B4 freeze record;
- [`research/frozen/big-b4-evaluation-protocol-v1.json`](research/frozen/big-b4-evaluation-protocol-v1.json) — canonical frozen P12 protocol manifest;
- [`research/results/big-b4-protocol-self-check-2026-08-22.json`](research/results/big-b4-protocol-self-check-2026-08-22.json) — provider-free 24/24 fail-closed self-check evidence.

Current evidence roles under P12:

- **EXPOSED_POOL = historical DEV + VALIDATION:** seven independent asset/story groups for adaptive development, selection, ablation, evaluator work and regression; never a fresh holdout.
- **FRESH_BLIND:** primary independent real-domain generalization evidence; currently `NO_BLIND_SOURCE_AUTHORIZED`.
- **LEGACY_LOCKED_TEST:** three historical groups retained as qualified supplementary held-out domain characterization; candidate execution remains blocked until final authorization and `untouched/pristine` is forbidden wording.
- **SYNTHETIC_ADVERSARIAL:** robustness, evaluator/judge qualification and regression only; never a real-domain substitute.

### Frozen protocol

**`P12_FRESH_BLIND_HYBRID_EXTERNAL_FIRST` — Fresh-Blind Hybrid with External-First Source Hierarchy**

Decision state: **`FROZEN`**.

```text
7 exposed historical DEV+VALIDATION groups
  → group-aware paired selection / LOGO sensitivity / modality slices
  → candidate + evaluator + judge + seed/outcome freeze
  → fresh blind real-domain measurement
       Tier A: partner-held external blind source (preferred)
       Tier B: independently authored + independently adjudicated hidden source (fallback)
  + qualified legacy LOCKED_TEST characterization
  + synthetic/adversarial robustness and regression
```

Frozen operational rules include:

- `asset_story_group` is the primary independent/generalization unit;
- candidate private-oracle access is always denied;
- evaluator private scoring requires fixed outputs;
- stochastic candidates require at least 3 repetitions per scenario for stability/reliability claims;
- paired candidates use the same groups/repetition count and matched seeds where supported;
- LOGO group sensitivity and modality slices are mandatory;
- for at least 5 independent groups, the primary interval is a 95% group-cluster percentile bootstrap with 20,000 resamples and seed `20260822`;
- hard safety violations are non-compensable and block promotion;
- final/blind access is one-generation/one-measurement-cycle authorization and defaults to deny;
- semantic leak, iterative partial feedback or material evaluator/judge adaptation consumes the affected blind measurement.

Blind-source reversal triggers remain:

- **2026-08-25 23:59 America/Sao_Paulo:** if Tier A has no operational blind-custody path, planning moves to Tier B;
- **2026-08-28 23:59 America/Sao_Paulo:** if neither Tier A nor Tier B is feasible, a B3 amendment is required before any P3 degraded fallback;
- P3 is never evidentially equivalent to P12 with fresh blind evidence.

The active protocol guard and regression check are:

- [`scripts/research/big_b4_protocol_guard.py`](scripts/research/big_b4_protocol_guard.py)
- [`scripts/research/big_b4_protocol_self_check.py`](scripts/research/big_b4_protocol_self_check.py)
- [`.github/workflows/research-big-b4-protocol-self-check.yml`](.github/workflows/research-big-b4-protocol-self-check.yml)

Benchmark Integrity Gate status:

`BIG-B0 ✓ → BIG-B1 ✓ → BIG-B2 ✓ → BIG-B3 ✓ → BIG-B4 ✓ → resume eval-driven agent optimization under P12`

Important: closing B4 does **not** authorize final measurement. Current blind registry state remains `NO_BLIND_SOURCE_AUTHORIZED`, and LEGACY_LOCKED_TEST also remains unauthorized.

Current canonical protocol: [`research/frozen/big-b4-evaluation-protocol-v1.json`](research/frozen/big-b4-evaluation-protocol-v1.json)  
B4 freeze record: [`research/big-b4-evaluation-protocol-freeze-2026-08-22.md`](research/big-b4-evaluation-protocol-freeze-2026-08-22.md)  
Historical execution plan: [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md)  
Research protocol: [`research/00-research-protocol.md`](research/00-research-protocol.md)  
Research hub: [`research/README.md`](research/README.md)

## Project goal

The updated TAPI requires both components:

1. **Industrial Agent Engineering** — contextualize, investigate, execute and escalate against the supplied industrial API.
2. **Agent Evaluation & Reliability** — quantitatively measure tool choice, arguments, trajectory, evidence, conclusion/response, safety, robustness, stability and action behavior.

The evaluation framework is part of the engineering loop, not a disconnected second product.

## Evidence-first rule

> **Best means best supported by systematic evidence for this problem — not newest, most popular, most complex, or merely the first option to pass.**

Decision flow:

`requirement → evaluator → systematic research → alternatives → baseline → hypothesis → preregistration → controlled experiment → robustness/production analysis → ADR → decision`

## Frozen TRACTIAN facts

- 17 agent-input cases and 16 narrative evaluation scenarios;
- 10 primary asset/story groups, so random ticket splitting is unsafe;
- evaluator-only gold separated from agent-visible input;
- 18 operations across 17 path templates;
- reference trajectories are not mandatory scripts;
- actions are accepted events and do not persist mutation state in the supplied environment;
- `x-user-id` and evaluation `seed` are runner-bound;
- response modes are reproducible through deterministic seeds/overrides;
- raw OpenAPI contains a duplicate `/assets/{assetId}` mapping;
- raw action validation is permissive and backend company/resource isolation is coarse;
- knowledge API exposes the supplied corpus directly.

Frozen historical artifacts:

- `research/34-e0-contract-freeze-v1.md`
- `research/frozen/e0-contract-freeze.manifest.json`
- `research/frozen/API-BEHAVIOR-MAP-v1.json`
- `research/35-e1-gold-freeze-v1.md`
- `research/frozen/e1-gold-freeze.manifest.json`
- `research/40-e3-benchmark-split-freeze-v1.md`
- `research/frozen/benchmark-split-v1.json`

The historical E3 split remains immutable evidence, while P12 now governs the future evidential role of those groups.

## Framework-neutral foundation

`research/e2/` contains executable:

- ScenarioSchema v1 models;
- 18-operation Canonical ToolSpec registry;
- runner-owned identity/seed binding;
- B0 HTTP transport + live/replay `HarnessRunner`;
- B1/B2/B3 deterministic boundaries;
- TraceSchema v1;
- deterministic replay;
- configuration/artifact hashing;
- integrated evaluator suite.

The existence or previous qualification of a runtime, model, MCP topology, RAG design, multi-agent design, judge, routing policy, memory strategy or observability stack does not automatically freeze it. Major final choices remain subject to the systematic-comparison and production-readiness rules.

## Critical path

The immediate critical path is now:

`P12 frozen evaluation protocol → reinterpret historical candidate state → resume systematic agent optimization on EXPOSED_POOL → freeze candidate generation → authorized fresh blind/final measurement → production-fit/architecture freeze`

Production freeze still requires broad candidate comparison, full deterministic + semantic evaluation gates, production fitness/integration verification, architecture freeze and final blind evidence under P12.

Final delivery/presentation target: **2026-09-08**.

## Development rule

No component remains merely because it looks sophisticated. RAG, reranking, multi-agent, routing, persistent memory, prompt optimization, judge selection, model selection and similar techniques require a measurable hypothesis or explicit requirement, systematic alternatives research and controlled comparison. They must remain removable when evidence does not support them.

No demo-first development: test doubles and scripted paths validate infrastructure only; agent-quality and production-readiness claims require controlled experiments against the TRACTIAN environment plus production-relevant reliability, security, observability and operational evaluation.
