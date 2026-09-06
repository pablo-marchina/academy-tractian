# Academy × TRACTIAN — Current Project Status

**Status:** production implementation / final remote promotion  
**Checkpoint:** 2026-09-05 BRT  
**Current `main`:** `12b4753d3e39c86f7c68f0ea7b4f321549049fc7`  
**Final implementation branch:** `release/production-final`  
**Validated implementation head:** `6ec5dcd7f5a4b4db81c3951d3592c955e3c64a4e`  
**Draft integration PR:** `#196`  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)  
**Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)  
**Principles:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file is the mutable source of truth for current state. Frozen/source-pinned historical evidence must not be rewritten.

## 1. Executive status

```text
formal product scope                         Agent + Evaluation in one solution
project cash-cost constraint                 USD 0 HARD CONSTRAINT
current main                                 12b4753d3e39c86f7c68f0ea7b4f321549049fc7
final implementation branch                  release/production-final
draft integration PR                         #196 / OPEN / DRAFT
validated implementation head                6ec5dcd7f5a4b4db81c3951d3592c955e3c64a4e
validated complete-head required gate         PASS / 11 of 11 workflows green
GitHub main protection                       BLOCKED_USER_ACTION / connector has no admin write

production agent runtime                     IMPLEMENTED / REGRESSION PASS
production deterministic evaluator           IMPLEMENTED
TRACTIAN typed tool registry                  18 operations / 17 paths
PostgreSQL serving persistence               IMPLEMENTED + REMOTE SCHEMA APPLIED
PostgreSQL observability/evaluation           IMPLEMENTED + REMOTE SCHEMA APPLIED
realtime durable truth                       PostgreSQL rows + sequence cursor
realtime wake-up                             LISTEN/NOTIFY + durable catch-up
read-only cross-replica handoff              IMPLEMENTED / required gate PASS
consequential-action safety                  IMPLEMENTED / action-lease PASS
React operator control room                  IMPLEMENTED
material decision registry                   IMPLEMENTED / ACTIVE
backend immutable release identity           IMPLEMENTED / REQUIRED GATE PASS
read-response semantic source gate           IMPLEMENTED / REQUIRED GATE PASS

Railway production-web                       ONLINE / HTTPS / US East
Railway production-api                       CRASHED FAIL-CLOSED / missing only two Postgres DSNs
Railway API healthcheck desired state         /health / 60s / ON_FAILURE configured
Railway production topology IaC              VERSIONED / live plan+apply pending
Neon production schema                       APPLIED / STRUCTURALLY VALIDATED
Neon scoped role                             academy_tractian_rls / NOBYPASSRLS / non-superuser
remote RLS validation                        PASS on isolated validation branch
Neon Auth / Better Auth                      PROVISIONED on production main
browser IAM                                  CODE + HOSTED AUTH / LIVE E2E PENDING

provider tournament v3                       PREREGISTERED / PROVIDER-FREE VALIDATOR PRESENT
production provider/model                    NO_SELECTION
production DecisionSource                    FAIL-CLOSED placeholder
production TRACTIAN HTTP adapter              IMPLEMENTED / WHEEL+IMAGE PASS
production TRACTIAN composition state         UNCONFIGURED by default
possible configured state                    CONFIGURED_UNVERIFIED only
TRACTIAN read semantic classifier             SOURCE-GATED / TRACE-ONLY
real TRACTIAN reachability                    NOT PROVED
production authorization resolver            DENY-ALL baseline
remote capacity/SLO                          NOT PROVED
remote recovery/reconnect                    NOT PROVED
human semantic calibration                   NOT READY — labels required
operational-value claim                      NOT READY — observations required
adaptive runtime policy                      NOT PROMOTED; baseline first
```

## 2. Current target topology

```text
browser
→ production-web HTTPS
→ same-origin /auth
→ Neon Auth managed session
→ same-origin /api + SSE
→ Railway production-api
→ immutable artifact SHA verification
→ server-side session revalidation
→ server-owned user / organization / permissions
→ Neon PostgreSQL + RLS
→ durable runtime handoff / leases / fencing
→ selected hosted DecisionSource                  [OPEN / NO_SELECTION]
→ AgentController
→ 18 typed TRACTIAN tools
→ hardened production TRACTIAN transport          [IMPLEMENTED / UNCONFIGURED]
→ authoritative remote TRACTIAN endpoint/auth     [OPEN]
→ live TRACTIAN read evidence                     [OPEN]
→ deterministic read-semantics acceptance gate    [SOURCE-GATED / LIVE EVIDENCE OPEN]
→ evidence-grounded final/clarify/abstain/escalate/action proposal
→ governed action confirmation + authorization    [OPEN remotely]
→ ProductionEvaluator
→ PostgreSQL observability/evaluation
→ durable cursor + LISTEN/NOTIFY
→ React Control Room
```

No component marked OPEN may be described as production-ready before hosted evidence closes it.

## 3. Release artifact identity

The backend production image has an independent immutable source-identity contract:

```text
Railway Git-backed build input       RAILWAY_GIT_COMMIT_SHA
baked runtime file                   /app/.academy-release-identity.json
identity schema                      academy-release-artifact-v1
OCI revision                         org.opencontainers.image.revision
public metadata schema               remote-production-release-v3
```

Image construction fails if the build SHA is missing or malformed. Serving boot fails before product/database builders if configured `ACADEMY_RELEASE_GIT_SHA` disagrees with the baked artifact, or if Railway's runtime SHA is present and disagrees with it.

At validated head `6ec5dcd7f5a4b4db81c3951d3592c955e3c64a4e`, `production-runtime`, its standalone-wheel smoke, production-image smoke, clean-clone reproduction and `final-ci-required / required-gate` all passed. This proves the source/artifact contract in CI; it does not prove the currently hosted Railway backend is serving that head.

Hosted G2 evidence must still show:

```text
release_git_sha == artifact_git_sha == exact deployed commit
artifact_identity_verified == true
railway_runtime_identity_verified == true  # when runtime system SHA is exposed
```

## 4. TRACTIAN production boundary

The canonical registry remains hash-pinned to the supplied contract and contains 18 operations over 17 paths. The production HTTP boundary is now implemented separately from the benchmark transport.

`ProductionTractianTransport` enforces:

```text
remote HTTPS base URL only
exact canonical operation/method/path matching
canonical path encoding / traversal rejection
runner-bound x-user-id only
server-managed credentials injected only at the network boundary
redirect following disabled
no automatic retry for reads or writes
bounded query/body/response sizes
finite JSON request bodies
sanitized response headers
invalid/oversized upstream payload -> deterministic 502
transport unavailable -> deterministic 599
```

Production composition is independent of model/provider selection:

```text
provider state                         NO_SELECTION
TRACTIAN default state                 UNCONFIGURED
explicit complete config state         CONFIGURED_UNVERIFIED
actions                                DENY-ALL / disabled
```

`CONFIGURED_UNVERIFIED` means only that a remote HTTPS base URL plus server-managed header map passed deterministic configuration validation. Construction performs zero remote I/O, so this state is intentionally not called READY, CONNECTED or VERIFIED.

No authoritative remote TRACTIAN base URL or authentication-header contract has been recovered from the supplied project material. The runtime therefore does not assume Bearer, API key or another scheme. Exact endpoint/auth configuration must come from the partner-provided contract/environment before live composition.

### Deterministic read-response semantics

`read-semantics-v1` and `production-read-semantics-gate-v1` now classify existing immutable `tool_result` evidence without modifying `HarnessRunner`, `ProductionRuntime`, `ProductionEvaluator`, provider request v1, or frozen EV-* traces.

The source-gated contract is:

```text
non-2xx read                         -> unavailable / source=http_status
2xx + body.mode in canonical enum    -> exact structured mode
2xx + missing/invalid mode           -> inconclusive / fail_closed + contract issue
non-object successful body           -> inconclusive / fail_closed + contract issue
status/result integrity mismatch     -> inconclusive / fail_closed + contract issue
prose/text heuristic                 -> forbidden
ACTION result                        -> never classified as a read
```

Canonical structured modes are `complete`, `partial`, `inconclusive`, `conflict` and `unavailable`. The acceptance report is sanitized: it records mode/provenance/status/issue codes but does not copy raw TRACTIAN response bodies. A safely degraded `inconclusive` result does not hide malformed upstream structure: any semantic contract issue makes the source gate fail.

The initial attempt to instrument the frozen runner was rejected by the historical freeze validators and reverted byte-for-byte instead of repinning evidence. The final implementation consumes raw frozen traces post-hoc and derives read membership from the canonical `ToolSpec` registry, preventing self-reported trace metadata from shrinking the denominator.

At validated head `6ec5dcd7f5a4b4db81c3951d3592c955e3c64a4e`:

```text
full Python + PostgreSQL clean-clone           PASS
read-semantics classifier/gate regressions     PASS
frozen EV-007 / EV-008 / EV-011 reproduction  PASS
TRACTIAN transport/composition regressions     PASS
standalone production wheel smoke              PASS
production Docker image smoke                  PASS
full-product Playwright                        PASS
final-ci-required / required-gate              PASS
```

These are source/artifact claims only. No real TRACTIAN request has been executed or promoted by this evidence.

## 5. External infrastructure state

### Railway

`production-web` is online on `release/production-final` with React/Vite, Caddy, public HTTPS, same-origin `/auth`, same-origin `/api` + SSE, one `us-east4-eqdc4a` replica, explicit `ON_FAILURE` restart policy and `/` healthcheck.

`production-api` exists separately from historical `hosted-pilot` and uses the repository production Dockerfile, one `us-east4-eqdc4a` replica, `ON_FAILURE`, `/health` with 60-second timeout, provider calls disabled, actions disabled and managed `neon-auth` browser IAM mode.

Current boot remains intentionally fail-closed because exactly these values are absent:

```text
ACADEMY_POSTGRES_INTERNAL_DSN
ACADEMY_POSTGRES_SCOPED_DSN
```

Those values must be inserted only through an approved Railway native secret channel. No DSN may be committed or pasted into documentation/chat.

### Railway Infrastructure as Code

`.railway/railway.ts` is a named `production` partial managing only `production-api` and `production-web`. Historical `hosted-pilot` remains outside the partial. Existing Railway-managed values and future PostgreSQL DSNs use `preserve()` and no secret value is stored in Git.

Static validation and TypeScript DSL CI pass. A real authenticated `railway config plan` followed by reviewed apply remains pending before IaC ownership convergence can be claimed.

### Neon

Validated production evidence remains:

```text
required product tables          15 / 15
required operational metadata     7 / 7
observability schema metadata     PASS
scoped role                       academy_tractian_rls
scoped superuser                  false
scoped BYPASSRLS                  false
run_ownership owner               academy_tractian_owner
tenant SELECT policies             5
cross-tenant validation           org-a visible / org-b denied
```

Production Neon Auth is provisioned and trusts the production-web origin. Email/password sessions are enabled; email verification is not required, so verified-email identity is not claimed.

## 6. Provider tournament state

Provider decision state remains `NO_SELECTION`.

The fresh v3 campaign is preregistered over:

```text
17 scenarios
× 5 repetitions
× 2 current candidates
= 170 future live calls / 85 per candidate
```

Historical D01/D02 results are excluded from the v3 denominator. Cash cost, gold leakage, unsafe unsupported actions, policy bypass, schema validity, quota, completeness, provenance and reliability remain hard gates. No v3 live run has selected a provider.

## 7. Immediate dependency gates

### Gate G1 — repository governance

Status: `BLOCKED_USER_ACTION`.

Required: protect `main`; require pull requests; require `final-ci-required / required-gate`; require up-to-date branch; block force push; block branch deletion.

### Gate G2 — remote backend serving

Status: `BLOCKED_USER_ACTION`.

Required after the two Railway DSNs are available:

1. inject both DSNs through Railway secrets;
2. deploy the exact current release branch SHA;
3. prove `/health` and `/api/meta/release` exact artifact/config/runtime SHA agreement;
4. verify real PostgreSQL roles/schema/stores;
5. restart and verify durable state/cursor.

### Gate G3 — live IAM and tenant isolation

Status: `WAITING_G2`.

Hosted acceptance must prove two users/two tenants, shared-organization behavior, zero cross-tenant REST/SSE/action leakage and fail-closed invalid/expired/mismatched/impersonated sessions.

### Gate G4 — hosted provider

Status: `PREREGISTERED / NO_SELECTION`.

Execute the v3 USD0 tournament only when hosted execution is permitted. Promotion requires complete quantitative evidence; preregistration alone cannot promote a provider.

### Gate G5 — real TRACTIAN path

Status: `ADAPTER_AND_READ_SOURCE_GATE_IMPLEMENTED / LIVE_CONFIG_AND_PROOF_PENDING`.

Already source-gated:

1. direct hardened transport/composition boundary;
2. fail-closed `UNCONFIGURED` / `CONFIGURED_UNVERIFIED` states;
3. deterministic post-hoc read semantics from canonical raw trace evidence;
4. exact preservation of `complete` / `partial` / `inconclusive` / `conflict` / `unavailable`;
5. contract drift fails acceptance while runtime-safe classification remains fail-closed;
6. no provider protocol or frozen trace mutation.

Still required before live promotion:

1. obtain authoritative partner base URL/auth contract;
2. configure it only through server-side secret/config channels;
3. enter `CONFIGURED_UNVERIFIED` without boot-time network side effects;
4. execute bounded live read acceptance against canonical tools;
5. prove the source-gated semantic classifier on real complete/partial/inconclusive/conflict/unavailable responses;
6. prove no secret/tenant leakage and no redirect/retry policy violation;
7. only then promote a live transport state.

Consequential actions remain a later gate after real authorization/confirmation composition.

## 8. Current non-claims

Do not claim yet: full remote production readiness; Railway IaC ownership convergence; currently deployed release SHA parity; IAM READY; verified-email identity; selected provider; real TRACTIAN reachability; real TRACTIAN reads; hosted proof of the five TRACTIAN response modes; remote action execution; enterprise availability; measured production SLO/HA/RTO/RPO; human semantic calibration; engineer-time savings; adaptive-runtime superiority; distributed exactly-once external side effects.

## 9. State update rule

Every material change must update implementation/infrastructure, validation evidence, this file, `DELIVERY-PLAN.md`, `decision-registry.yaml` when a material decision changes, and a chronological `docs/progress/` entry.

A green CI result is not a substitute for hosted production evidence.
