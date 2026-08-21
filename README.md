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

**Benchmark Integrity Gate — BIG-B0 complete / BIG-B1 complete / BIG-B2 active — agent optimization paused**

BIG-B0 reconstructed benchmark use from E3 onward. BIG-B1 then classified independence and adaptive influence for every B0 event without redesigning the benchmark.

Canonical audit artifacts:

- [`research/big-b0-benchmark-integrity-audit-2026-08-21.md`](research/big-b0-benchmark-integrity-audit-2026-08-21.md) — factual chronological reconstruction;
- [`research/results/big-b0-benchmark-access-ledger-2026-08-21.json`](research/results/big-b0-benchmark-access-ledger-2026-08-21.json) — B0 machine-readable access inventory;
- [`research/big-b1-exposure-contamination-ledger-2026-08-21.md`](research/big-b1-exposure-contamination-ledger-2026-08-21.md) — B1 independence/influence classification;
- [`research/results/big-b1-exposure-contamination-ledger-2026-08-21.json`](research/results/big-b1-exposure-contamination-ledger-2026-08-21.json) — B1 machine-readable 20-record ledger.

Current split evidence status from BIG-B1:

- **DEV:** development-exposed by design; not an independent holdout.
- **VALIDATION:** adaptively exposed; not independent for current/future descendant candidate-generalization claims because aggregate and split-level feedback repeatedly informed downstream development.
- **LOCKED_TEST:** no committed candidate/task-quality execution established, but structurally exposed for evaluator design; the stronger `untouched/pristine` full-stack claim is unsupported and final-holdout eligibility is unresolved pending BIG-B2.

The active blocking sequence remains defined in [`docs/BENCHMARK-INTEGRITY-GATE.md`](docs/BENCHMARK-INTEGRITY-GATE.md):

`BIG-B0 factual audit ✓ → BIG-B1 exposure/influence classification ✓ → BIG-B2 benchmark-design comparison → BIG-B3 protocol selection → BIG-B4 protocol freeze → resume agent optimization`

BIG-B2 must now compare credible evaluation-design alternatives systematically and quantitatively. No split redesign or final protocol has been selected yet.

Until B4 closes:

- no new E14v-C or other agent-optimization candidate is authorized;
- historical E14v work is preserved but not advanced;
- VALIDATION candidate feedback is blocked;
- LOCKED_TEST candidate evaluation remains blocked;
- final production architecture remains unfrozen.

Current blocking/canonical status: [`docs/BENCHMARK-INTEGRITY-GATE.md`](docs/BENCHMARK-INTEGRITY-GATE.md)  
BIG-B0 factual audit: [`research/big-b0-benchmark-integrity-audit-2026-08-21.md`](research/big-b0-benchmark-integrity-audit-2026-08-21.md)  
BIG-B1 exposure ledger: [`research/big-b1-exposure-contamination-ledger-2026-08-21.md`](research/big-b1-exposure-contamination-ledger-2026-08-21.md)  
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

`BIG-B0 factual reconstruction ✓ → BIG-B1 exposure/influence classification ✓ → BIG-B2 benchmark-design comparison → BIG-B3 evaluation-protocol selection → BIG-B4 executable freeze → resume eval-driven agent optimization`

After the evaluation protocol is frozen, production freeze still requires broad candidate comparison, full deterministic + semantic evaluation gates, production fitness/integration verification, architecture freeze and a final-only blind test under the frozen protocol.

Final delivery/presentation target: **2026-09-08**.

## Development rule

No component remains merely because it looks sophisticated. RAG, reranking, multi-agent, routing, persistent memory, prompt optimization, judge selection, model selection and similar techniques require a measurable hypothesis or explicit requirement, systematic alternatives research and controlled comparison. They must remain removable when evidence does not support them.

No demo-first development: test doubles and scripted paths validate infrastructure only; agent-quality and production-readiness claims require controlled experiments against the TRACTIAN environment plus production-relevant reliability, security, observability and operational evaluation.
