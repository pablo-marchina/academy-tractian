# Codebase Map

**Status:** ACTIVE implementation navigation  
**Last verified:** 2026-09-08 BRT

Use this before adding a file: **which existing domain owns the change?** Current production backend serves the V14 OpenRouter composition at `5611687556b3d50c31f20fa85ede794f2500f05c`; functional-closure work continues on draft PR #222.

## End-to-end ownership

```text
frontend task-driven UI
→ authenticated REST/SSE
→ managed-session product API
→ PostgreSQL runtime ownership/RLS
→ V14 DecisionSource / AgentController
→ HarnessRunner / ToolSpec / TRACTIAN transport
→ evidence / governed action proposal / terminal
→ evaluator + independent verification
→ PostgreSQL safe projection
→ result / Analyses / Technical UI
```

## Backend domains — `src/academy_tractian/`

### Runtime / orchestration

Core ownership remains the custom controller/harness stack. Do not create a parallel orchestration path merely because a provider adapter is failing.

Relevant modules include runtime/realtime/runtime-handoff code plus the newer functional-closure components:

- `production_controller.py` — production controller invariants, including provider-independent non-progress behavior;
- `production_observable_controller.py` — controller + safe observability integration;
- `production_runtime_v2.py` — current hardened runtime composition used by closure work;
- existing runtime/realtime/handoff modules — durable execution ownership and worker lifecycle.

### Release provider layers

Serving semantics remain explicitly layered:

- `release_provider.py` — base Release 0 provider/schema contract;
- `release_provider_v10.py` — nested ID grounding and condition-evidence/stopping;
- `release_provider_v11.py` — response-mode semantics;
- `release_provider_v12.py` — human asset labels, comparisons, data-quality requirements;
- `release_provider_v13.py` — initial identity grounding and completed data-quality suppression;
- `release_provider_v14.py` — fixed-free OpenRouter adapter preserving V13 agent semantics;
- `remote_server.py` — current production composition, V14 factory and governed action wiring;
- `production_config.py` — validated production environment contract.

Current V14 exact route:

```text
provider  openrouter
model     nvidia/nemotron-3-super-120b-a12b:free
route     openrouter.chat_completions.v1.fixed_free
fallback  disabled
cost      usd0-hard-gate
```

`release_provider_v14.py` owns only the provider adapter contract: strict JSON Schema request, exact model/choice/message validation, `finish_reason=stop`, no provider-side tool execution, usage provenance and no automatic retry/repair/fallback.

### Provider functional diagnostics / research

Current closure scripts:

- `scripts/verification/live_functional_campaign.py` — real managed-session B204 F01/F02/F03 acceptance;
- `scripts/verification/diagnose_openrouter_model_calls.py` — safe model-call failure diagnostics;
- `scripts/verification/probe_openrouter_v14_initial.py` — exact initial-call reproduction;
- `scripts/verification/probe_openrouter_v14_response_shape.py` — sanitized provider response-shape capture;
- `scripts/verification/experiment_openrouter_v14_length_fix.py` — bounded completion/reasoning comparison;
- `scripts/verification/probe_openrouter_key_tier.py` — safe key-tier/rate-limit eligibility probe.

These scripts must not log credentials, raw provider requests/responses or benchmark-private material.

### Provider tournament / eligibility

Current cross-provider research owners include:

- `provider_tournament_cross_provider_v1.py`;
- `provider_tournament_cross_provider_v2.py`;
- `scripts/research/run_provider_tournament_cross_provider_v1.py`;
- `scripts/research/run_provider_tournament_cross_provider_v2_eligibility.py`;
- `scripts/research/discover_hosted_provider_models_v1.py`;
- corresponding manifests/closures/workflows under `research/experiments/` and `.github/workflows/`.

Production qualification never silently rewrites frozen tournament evidence. A final provider claim still requires a new eligible governed comparison or explicit `NO_SELECTION`.

### TRACTIAN capability / transport

Canonical ToolSpecs remain under the accepted `research/e2` registry and production transport/normalization modules. `HarnessRunner` is the only canonical real tool execution boundary. Never let OpenRouter/provider code call TRACTIAN directly.

### Governed actions / safety

Current action ownership spans:

- production action/custody/idempotency/lease/evaluation modules;
- `production_actions_v3.py` — current closure action hardening;
- trusted server-owned authorization source/resolver;
- server-owned upstream TRACTIAN action actor source and transport;
- `remote_server.py` composition and boot-time actor/grant coverage validation.

Current authority model:

```text
proposal
→ deterministic policy/resource/schema
→ private custody
→ explicit opaque confirmation
→ fresh tenant/user authorization + kill switch
→ idempotency + non-transferable lease
→ server-owned upstream TRACTIAN actor
→ one bounded external attempt
→ persisted action outcome/evaluation
```

The controlled production smoke has exercised all five canonical action transports. Full SECURITY-V1/adversarial acceptance is still separate.

### Product APIs

Product/auth/observability/verification/action APIs own HTTP/runtime integration. `/api/runs` derives trusted identity server-side; its user payload remains the user request rather than tenant/permission authority.

### Identity / tenant scope

Key owners:

- `neon_auth_identity.py` — managed-session validation, bounded GET/HEAD cache, SHA-256 cookie key, singleflight, fresh non-read validation, 401/503 distinction;
- authenticated PostgreSQL product composition — server-owned browser/session context;
- PostgreSQL scoped product stores/RLS — independent tenant boundary.

### PostgreSQL persistence

Production mutable truth remains PostgreSQL: run ownership/execution, RLS, observability/evaluation, runtime handoff, action custody/idempotency/leases and research collection state. Do not move production truth to local files/DuckDB.

### Observability / verification

- `observability.py` and related modules own sanitized traces/provenance;
- current closure work adds normalized argument fingerprints so duplicate calls are evaluated by operation + arguments/resource, not name alone;
- `verification_api.py` and independent verification modules expose claim-bounded verification state;
- durable rows/cursors remain truth; SSE/NOTIFY are delivery/wake-up only.

### Evaluation / EDD

Deterministic structural/safety/trajectory evaluation remains authoritative where exact truth exists. New provider/model/adaptive/framework behavior must enter through eligibility + preregistered comparison before replacing a promoted path.

## Current functional failure location

Do not misdiagnose the B204 V14 failure as a tool bug:

```text
managed auth            PASS
run API/runtime worker  PASS
OpenRouter HTTP         200 in sanitized reproduction
exact model             observed
finish_reason           length
V14 adapter             rejects incomplete response
TRACTIAN calls          0
```

The immediate owning domain is the **V14 provider adapter / provider availability experiment**, not `HarnessRunner`, TRACTIAN transport or architecture topology.

## Frontend — `frontend/src/`

Current information architecture remains:

- **Home** — question entry, live progress and result;
- **Result/evidence** — conclusion/support for the selected run;
- **Analyses** — persisted history;
- **Technical** — trace, quality, data, system, actions, verification/studies.

`App.tsx`, primary navigation/product experience, run explorer/trace graph/operations workspace, architecture/capability/action surfaces and auth boundary remain the primary owners. Frontend visualizes server-owned truth and may expose current provider/action/release state safely, but never becomes authority.

## Tests

Current relevant regression areas include:

- backend product/auth/RLS/runtime/action/provider tests;
- `tests/test_observability_argument_fingerprint.py`;
- `tests/test_production_controller.py`;
- `tests/test_production_actions_v3.py`;
- provider tournament V1/V2 tests;
- frontend Vitest/Playwright;
- accepted `research/e2` controller/tool/evaluator tests.

The final candidate must run required CI on its exact SHA before production promotion.

## Workflows

See [`../.github/workflows/README.md`](../.github/workflows/README.md). Current closure adds provider-secret presence, hosted provider discovery, cross-provider tournament and functional/provider diagnostics. Distinguish:

```text
regression CI
≠ provider experiment
≠ exact-SHA production promotion
≠ hosted functional acceptance
```

## Research / scripts discipline

- `research/` preserves protocol/evidence; consumed/frozen evidence is not rewritten;
- `scripts/verification/` should exercise production/acceptance contracts safely;
- `scripts/research/` should remain controlled experimental wrappers;
- reusable production logic belongs in the package, not scripts.

## New-code checklist

1. Which existing domain owns the responsibility?
2. Is the observed gap provider, runtime, tool boundary, auth, persistence, frontend or evaluation?
3. Does existing code already expose the contract?
4. Is it production logic or experiment/CLI-only logic?
5. Does a measured gap justify a new abstraction?
6. Does behavior need an evaluator/baseline/preregistration before promotion?
7. Does the change preserve tenant/action/cost/provenance hard gates?
8. Can it be retested on the exact hosted candidate before a claim is made?

Prefer extending a clear owner over creating a parallel path. LangGraph/multi-agent/RAG/MCP/Redis/Kafka/Kubernetes remain `NO_CHANGE` unless a measured architecture gap and challenger win justify them.