# Codebase Map

**Status:** ACTIVE implementation navigation  
**Last verified:** 2026-09-08 BRT

Use this before adding a file: **which existing domain owns the change?** Production runtime and provider research are intentionally separate.

## End-to-end production ownership

```text
frontend task-driven UI
→ authenticated REST/SSE
→ managed-session product API
→ PostgreSQL runtime ownership/RLS
→ V13 DecisionSource / AgentController
→ HarnessRunner / canonical ToolSpec
→ typed TRACTIAN transport
→ evidence + terminal + response_mode
→ evaluator
→ PostgreSQL safe projection
→ result / Analyses / Technical UI
```

## `src/academy_tractian/` — production domains

### Runtime / orchestration

`runtime.py`, `realtime_runtime.py`, `decision_source.py`, runtime handoff/access/execution-store modules own decision-loop lifecycle and durable ownership.

### Release 0 provider composition

- `release_provider.py` — base Release 0 provider contract;
- `release_provider_v10.py` — nested ID extraction and condition/stopping constraints;
- `release_provider_v11.py` — response-mode semantics;
- `release_provider_v12.py` — explicit asset labels/comparisons/data-quality requirements;
- `release_provider_v13.py` — initial identity grounding and completed quality-read suppression;
- `remote_server.py` — production composition;
- `production_config.py` — production environment contract.

Do not infer final provider selection from the Release 0 serving wrapper.

### TRACTIAN capability / transport

Canonical ToolSpecs/accepted E2 registry and production normalization/transport modules own the 18-operation contract. `ProductionTractianTransport` owns real network I/O behind `HarnessRunner`.

Do not create a second model→network bypass.

### Identity / tenant / persistence

Managed Neon-auth modules derive server-owned runtime context; PostgreSQL scoped stores/RLS remain the independent tenant boundary. Browser state is a projection, not authorization truth.

### Consequential actions

Action-safety/custody/idempotency/lease/recovery modules contain future governed execution machinery. Release 0 external action execution remains disabled.

### Observability / evaluation

Observability/realtime/evaluator modules own safe traces, durable cursors, evaluation and browser-safe projections. Structural evaluation remains deterministic-first.

## `frontend/` — current product

Primary UX:

```text
Home → selected Result/Evidence
Analyses → persisted history
Technical → Current analysis / Quality / Data / System / Actions / Studies
```

Authentication components must distinguish invalid session from temporary managed-auth unavailability and must never become tenant authority.

## Provider research ownership

Provider experiments belong under `research/experiments/` and `scripts/verification/`. They are not production composition until separately promoted.

### Frozen population / manifests

- `research/experiments/provider-tournament-v3-population.json` — 17-scenario frozen population;
- `research/experiments/provider-tournament-v4-final-manifest.json` — V4 Cloudflare/Groq protocol and pre-scored transport amendment;
- `research/experiments/provider-qualification-v4-1-groq-final-manifest.json` — Groq-only 85-attempt qualification manifest.

Population SHA-256:

`4205d00931150d83c510c7c6e58ad48bbd88da55654bac69ec35819af41299b9`

### V4 tournament/transport artifacts

Important historical experiment identities:

- `scripts/verification/provider_tournament_v4_final.py` — generic V4 scoring/execution core;
- final transport/pacing protocol checkpoint — `22ef052b292bb77618973cc6447f08970dc13159`;
- pinned bootstrap — `a34f1c6cce26219df6c06772ec2ea5599637e391`.

Cloudflare quota preflights and Groq transport preflights are non-scored evidence.

### Groq-only final qualification

- `scripts/verification/provider_qualification_v4_1_groq_final.py` — runner commit `1ad041fdcbe4424a79239fff6382df67e8bc2bfe`;
- `scripts/verification/bootstrap_provider_qualification_v4_1_groq_final.py` — bootstrap `6fc9d84262efaf6d57925a83ba59f07425cfc717`.

This path completed 85/85 and returned `NO_SELECTION`; it must not be repurposed into a passing artifact.

### Causal failure diagnostic

- `scripts/verification/provider_failure_diagnostic_v1.py` — commit `426b0ecacf8b794199b78380a5de5837603e29e3`;
- frozen bootstrap — `7826a46d0209c1072a75b59f527dac82b3437a82`;
- health-preserving bootstrap — `b71172bf1f42d4be074560336e58c42539cbfe1c`.

Purpose: distinguish completion-budget, reasoning-effort and best-effort structured-output failure causes. It is not a promotion benchmark.

### Groq rate/admission diagnostic

- `scripts/verification/groq_benchmark_rate_diagnostic_v2.py` — `8cec9f8d7e596bda27a4459ac4130319547d2f5e`;
- pinned bootstrap — `0ecc8365f3908f6ddc8521998436a30eee2d5507`.

Purpose: explain HTTP admission/rate behavior for benchmark-shaped requests without storing raw prompt/response/credentials. At the current documentation checkpoint it has not yet produced a canonical result.

## Strict-output challenger ownership

Future strict-schema code should be generated from existing canonical ToolSpecs/OpenAPI/Release 0 decision structures. Do not hand-maintain a parallel generic action schema.

Required source chain:

```text
canonical tool registry / supplied OpenAPI
→ closed per-tool argument schema
→ closed TOOL/FINAL/CLARIFY/ESCALATE/ABSTAIN variants
→ provider strict structured output
→ ProviderDecisionPayload
→ canonical argument/policy validation
```

The exact supplied `ActionRequest` definition is still a prerequisite for complete strict action variants.

## Railway experiment boundary

`qa-live-prompt-matrix` is a disposable research execution slot, not production serving. Overlapping deployments have contaminated partial diagnostics; do not combine attempts from different deployment windows into one claimed causal matrix.

Account service capacity currently prevents a sixth dedicated provider-lab service, so experiment isolation must be explicitly controlled before long runs.

## Tests

- `tests/` — backend/product/regression/integration;
- frontend Vitest/Playwright — UI/auth/product acceptance;
- `research/e2/tests/` — controller/tool/evaluator harness;
- provider verification scripts — controlled research only, with frozen identities where required.

## New-code checklist

1. Which domain owns this behavior?
2. Production logic or research-only logic?
3. Is there already a canonical contract to derive from?
4. Does the change alter a frozen protocol/population/rubric?
5. Is a new abstraction justified by measured evidence?
6. Does the candidate require a preflight before benchmark exposure?
7. Can the change affect tenant/action/cost authority?
8. What regression/evaluation gates are required before promotion?

Prefer extending canonical owners over creating parallel contracts.
