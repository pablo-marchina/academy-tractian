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

**Benchmark Integrity Gate COMPLETE — P12 evaluation protocol `FROZEN` — P12-C1 CLOSED with no qualified arm — P12-C2 CONSUMED as provider-capacity operational failure — P12-C3 PREREGISTERED**

P12-C1 and P12-C2 are consumed and must not be rerun. P12-C2 produced no deterministic arm comparison because only 31/36 common parents completed before `rate_limit_long_window` failures. P12-C3 is a new `EXPOSED_POOL` experiment that preserves the same E0/E1 × S0/S1 candidate definitions while preregistering provider-capacity controls before any new outcome. Execution is **not authorized** until the child P12-C3 activation/eligibility gate passes.

Canonical current artifacts:

- [`research/frozen/big-b4-evaluation-protocol-v1.json`](research/frozen/big-b4-evaluation-protocol-v1.json) — frozen P12 protocol;
- [`research/results/p12-c1-deterministic-paired-result-2026-08-23.json`](research/results/p12-c1-deterministic-paired-result-2026-08-23.json) — sanitized P12-C1 result;
- [`research/results/p12-c2-live-cycle-closure-2026-08-23.json`](research/results/p12-c2-live-cycle-closure-2026-08-23.json) — P12-C2 consumed operational-failure closure;
- [`research/p12-c2-live-cycle-closure-2026-08-23.md`](research/p12-c2-live-cycle-closure-2026-08-23.md) — human P12-C2 closure;
- [`research/experiments/p12-c3-exposed-pool-capacity-controlled-factorial-preregistration-v1.json`](research/experiments/p12-c3-exposed-pool-capacity-controlled-factorial-preregistration-v1.json) — machine-readable P12-C3 freeze;
- [`research/p12-c3-exposed-pool-capacity-controlled-factorial-preregistration-2026-08-23.md`](research/p12-c3-exposed-pool-capacity-controlled-factorial-preregistration-2026-08-23.md) — human-readable P12-C3 preregistration.

Current evidence roles under P12:

- **EXPOSED_POOL = historical DEV + VALIDATION:** seven independent asset/story groups for adaptive development, selection, ablation, evaluator work and regression; never a fresh holdout.
- **FRESH_BLIND:** primary independent real-domain generalization evidence; currently `NO_BLIND_SOURCE_AUTHORIZED`.
- **LEGACY_LOCKED_TEST:** qualified supplementary held-out characterization; candidate execution remains blocked until final authorization.
- **SYNTHETIC_ADVERSARIAL:** robustness, evaluator/judge qualification and regression only.

### P12-C3 frozen design

P12-C3 keeps the P12-C2 2×2 factorial candidates unchanged:

```text
A00 = retained evidence reference + retained E14q/E14q2
A10 = bounded public intent/dependency closure + retained E14q/E14q2
A01 = retained evidence reference + strict public authorization certificate
A11 = bounded public intent/dependency closure + strict public authorization certificate
```

The scientific geometry remains:

```text
7 EXPOSED_POOL groups
11 scenario families
12 agent-visible tickets
3 repetitions/ticket
36 new common-parent generations
144 fixed arm outputs
new seeds 2026082307 / 2026082308 / 2026082309
```

The operational collection geometry is now preregistered as **6 fixed batches × 6 parents** with immutable checkpoints. Provider waits may depend only on `Retry-After` / rate-limit reset metadata, never candidate content or evaluator outcomes. A `429` before any model output leaves the same predeclared cell pending; a completed parent may never be regenerated. The complete collection horizon is frozen at 72 hours from the first P12-C3 live provider call.

No private scoring is allowed until **36/36 new parents and 144/144 arm outputs** are frozen. Partial/complete-case-only factorial analysis is forbidden.

Deterministic thresholds remain unchanged. Hard safety remains non-compensable. P12-C3 cannot authorize semantic v4.2, FRESH_BLIND, LEGACY_LOCKED_TEST, architecture freeze, or production-readiness claims.

### Next authorized step

The immediate next step is:

**create and pass the child `P12-C3 capacity-controlled activation / eligibility` gate before any P12-C3 provider call.**

Activation must freeze the unchanged E0/E1/S0/S1 hashes, common-parent runner/config, exact six-batch 36-cell map, checkpoint schema, provider reset/header parser, pre-output transport-attempt policy, 72-hour clock semantics, ToolSpec/corpus hashes, evaluator stack, and no-regeneration rules. Provider-free tests must prove checkpoint/resume correctness and a 36-parent → 144-arm dry cycle.

`FRESH_BLIND` and `LEGACY_LOCKED_TEST` remain inaccessible to candidate development/selection.

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

## Framework-neutral foundation

`research/e2/` contains executable ScenarioSchema models, the Canonical ToolSpec registry, runner-owned identity/seed binding, HTTP transport + HarnessRunner, deterministic boundaries, TraceSchema, replay, hashing and evaluator infrastructure.

The existence or previous qualification of a runtime, model, MCP topology, RAG design, multi-agent design, judge, routing policy, memory strategy or observability stack does not automatically freeze it. Major final choices remain subject to systematic comparison and production-readiness rules.

## Critical path

`P12-C1 closed → P12-C2 consumed operational failure → P12-C3 preregistered → P12-C3 capacity-controlled activation/eligibility NEXT → capacity-controlled EXPOSED_POOL factorial collection → deterministic gate → semantic child gate only for deterministic survivors → production-fit comparison → generation freeze → separately authorized blind/final evidence → architecture freeze`

Production freeze still requires broad candidate comparison, full deterministic + semantic evaluation gates, production fitness/integration verification, architecture freeze and final blind evidence under P12.

Final delivery/presentation target: **2026-09-08**.

## Development rule

No component remains merely because it looks sophisticated. RAG, reranking, multi-agent, routing, persistent memory, prompt optimization, judge selection, model selection and similar techniques require a measurable hypothesis or explicit requirement, systematic alternatives research and controlled comparison. They must remain removable when evidence does not support them.
