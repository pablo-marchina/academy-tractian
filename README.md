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

**Benchmark Integrity Gate active — agent optimization paused**

A retrospective governance review identified that historical benchmark usage must be audited before the evaluation stack can be treated as a trustworthy basis for further optimization or final claims. The active blocking sequence is defined in [`docs/BENCHMARK-INTEGRITY-GATE.md`](docs/BENCHMARK-INTEGRITY-GATE.md):

`B0 benchmark audit → B1 exposure/contamination ledger → B2 benchmark-design comparison → B3 protocol selection → B4 protocol freeze → resume agent optimization`

Until B4 closes:

- no new E14v-C or other agent-optimization candidate is authorized;
- historical E14v work is preserved but not advanced;
- VALIDATION candidate feedback is blocked;
- LOCKED_TEST candidate evaluation remains blocked;
- final production architecture remains unfrozen.

Current canonical status: [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md)  
Benchmark integrity gate: [`docs/BENCHMARK-INTEGRITY-GATE.md`](docs/BENCHMARK-INTEGRITY-GATE.md)  
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

Current execution details live in [`docs/PROJECT-PLAN.md`](docs/PROJECT-PLAN.md). The immediate critical path is:

`benchmark integrity B0 → exposure ledger B1 → benchmark-design comparison B2 → evaluation-protocol selection B3 → executable freeze B4 → resume eval-driven agent optimization`

After the evaluation protocol is frozen, production freeze still requires broad candidate comparison, full deterministic + semantic evaluation gates, production fitness/integration verification, architecture freeze and a final-only blind test under the frozen protocol.

Final delivery/presentation target: **2026-09-08**.

## Development rule

No component remains merely because it looks sophisticated. RAG, reranking, multi-agent, routing, persistent memory, prompt optimization, judge selection, model selection and similar techniques require a measurable hypothesis or explicit requirement, systematic alternatives research and controlled comparison. They must remain removable when evidence does not support them.

No demo-first development: test doubles and scripted paths validate infrastructure only; agent-quality and production-readiness claims require controlled experiments against the TRACTIAN environment plus production-relevant reliability, security, observability and operational evaluation.
