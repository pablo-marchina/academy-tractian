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

**Benchmark Integrity Gate — BIG-B0/B1/B2/B3 complete / BIG-B4 active — agent optimization paused**

BIG-B0 reconstructed benchmark usage, BIG-B1 classified adaptive influence/independence, BIG-B2 preregistered and executed the benchmark-design comparison, and BIG-B3 selected the best-supported protocol architecture as `PREFERRED` without yet freezing it.

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
- [`research/results/big-b3-evaluation-protocol-selection-2026-08-21.json`](research/results/big-b3-evaluation-protocol-selection-2026-08-21.json) — machine-readable B3 selection and reversal triggers.

Current evidence status:

- **DEV:** development-exposed by design; not an independent holdout.
- **VALIDATION:** adaptively exposed; permanently treated with DEV as part of the seven-group exposed development/selection pool for future work.
- **LOCKED_TEST:** no committed candidate/task-quality execution established, but structurally exposed for evaluator design; `untouched/pristine` is unsupported and its future role is qualified supplementary held-out domain characterization.

### BIG-B3 selected protocol

**`P12_FRESH_BLIND_HYBRID_EXTERNAL_FIRST` — Fresh-Blind Hybrid with External-First Source Hierarchy**

Decision state: **`PREFERRED`**, not yet `FROZEN`.

```text
7 exposed historical DEV+VALIDATION groups
  → group-aware paired selection / sensitivity
  → candidate + evaluator + judge + seed/outcome freeze
  → fresh blind real-domain measurement
       Tier A: partner-held external blind source (preferred)
       Tier B: independently authored + independently adjudicated hidden source (fallback)
  + qualified legacy LOCKED_TEST characterization
  + synthetic/adversarial robustness and regression
```

P3 (legacy-only final path) is **not** selected as evidentially equivalent. It remains an explicit degraded emergency path only if neither fresh-blind source can be operationalized, and activating it requires a B3 amendment plus downgraded final claims.

Operational reversal triggers selected in B3:

- **2026-08-25 23:59 America/Sao_Paulo:** if Tier A has no credible custodian/blind-feedback path, B4 planning moves to Tier B;
- **2026-08-28 23:59 America/Sao_Paulo:** if neither Tier A nor Tier B is feasible, a B3 amendment is required before any P3 degraded fallback;
- any blind-source semantic leak or adaptive partial feedback reclassifies that source as exposed;
- material evaluator/judge adaptation after blind outcomes consumes that blind measurement for the affected evaluation-stack generation.

The active blocking sequence remains defined in [`docs/BENCHMARK-INTEGRITY-GATE.md`](docs/BENCHMARK-INTEGRITY-GATE.md):

`BIG-B0 ✓ → BIG-B1 ✓ → BIG-B2 ✓ → BIG-B3 ✓ → BIG-B4 executable protocol freeze → resume agent optimization`

BIG-B4 must now turn P12 into an executable, access-controlled, reproducible protocol with versioned manifests, exact allowed/forbidden split reads, evaluator/judge prerequisites, uncertainty rules, final-test authorization and provider-free structural self-checks.

Until B4 closes:

- no new E14v-C or other agent-optimization candidate is authorized;
- historical E14v work is preserved but not advanced;
- historical VALIDATION is exposed development/selection data, not blind feedback;
- LOCKED_TEST candidate evaluation remains blocked;
- no fresh blind source may return adaptive candidate-development feedback;
- final production architecture remains unfrozen.

Current blocking/canonical status: [`docs/BENCHMARK-INTEGRITY-GATE.md`](docs/BENCHMARK-INTEGRITY-GATE.md)  
BIG-B3 selected protocol: [`research/big-b3-evaluation-protocol-selection-2026-08-21.md`](research/big-b3-evaluation-protocol-selection-2026-08-21.md)  
Historical agent execution plan (paused/subordinate during B0–B4): [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md)  
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

Frozen artifacts:

- `research/34-e0-contract-freeze-v1.md`
- `research/frozen/e0-contract-freeze.manifest.json`
- `research/frozen/API-BEHAVIOR-MAP-v1.json`
- `research/35-e1-gold-freeze-v1.md`
- `research/frozen/e1-gold-freeze.manifest.json`
- `research/40-e3-benchmark-split-freeze-v1.md`
- `research/frozen/benchmark-split-v1.json`

The historical benchmark split remains an immutable historical artifact while B0–B4 determine its current evidential status and the future evaluation protocol.

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

The immediate critical path is:

`BIG-B0 ✓ → BIG-B1 ✓ → BIG-B2 ✓ → BIG-B3 ✓ → BIG-B4 executable freeze → resume eval-driven agent optimization`

After the evaluation protocol is frozen, production freeze still requires broad candidate comparison, full deterministic + semantic evaluation gates, production fitness/integration verification, architecture freeze and a final-only blind test under the frozen protocol.

Final delivery/presentation target: **2026-09-08**.

## Development rule

No component remains merely because it looks sophisticated. RAG, reranking, multi-agent, routing, persistent memory, prompt optimization, judge selection, model selection and similar techniques require a measurable hypothesis or explicit requirement, systematic alternatives research and controlled comparison. They must remain removable when evidence does not support them.

No demo-first development: test doubles and scripted paths validate infrastructure only; agent-quality and production-readiness claims require controlled experiments against the TRACTIAN environment plus production-relevant reliability, security, observability and operational evaluation.