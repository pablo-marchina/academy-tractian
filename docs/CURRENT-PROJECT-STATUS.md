# Academy × TRACTIAN — Current Project Status

**Status:** `FREEZE_REOPENED` / hosted-only P0 closure in progress  
**Checkpoint:** 2026-09-04 BRT  
**Final delivery:** 2026-09-08  
**Canonical reopen manifest:** [`../research/results/final-freeze-reopen-2026-09-04.json`](../research/results/final-freeze-reopen-2026-09-04.json)

## 1. Executive status

```text
updated TAPI scope                         Agent + Evaluation in one solution
external API/hosted-service cash cost     USD 0 hard constraint
required local production components      TARGET 0 / hard constraint
production path hosted-only               REQUIRED
multi-user production path                REQUIRED
no demo-only production path              REQUIRED

hosted FastAPI product path                IMPLEMENTED / candidate
hosted OIDC/JWKS boundary                  IMPLEMENTED / provider-neutral
managed PostgreSQL production state        IMPLEMENTED / candidate
PostgreSQL tenant RLS                      IMPLEMENTED / repository-tested
hosted PostgreSQL live preflight           IMPLEMENTED / live execution pending
hosted TRACTIAN transport                  IMPLEMENTED / 18/18 proof pending
hosted semantic certification              IMPLEMENTED / 18/18 proof pending
hosted provider/model frontier             IMPLEMENTED / promotion pending
hosted consequential actions               FAIL-CLOSED / qualification pending
React operator control room                IMPLEMENTED
full-product Playwright                    IMPLEMENTED / hosted-live run pending

Python dependency lock                     IMPLEMENTED / gated
frontend lockfile + npm ci                 IMPLEMENTED / gated
current clean-clone reproduction           PASS / gated
final required CI                          PASS on current PR head

human semantic calibration                 NOT READY — real labels required
business-value MANUAL vs ASSISTED           NOT READY — real human data required
adaptive runtime stopping                  NOT PROMOTED
production SLO/capacity                    NOT CLAIMED
branch protection enforcement              PENDING EXTERNAL
```

The pre-cloud-only freeze candidate is historical evidence only. It is not the current production-readiness claim.

## 2. Why the freeze is reopened

The previous candidate was built before the final hard constraint that the delivered product must require **zero local runtime components**. That constraint is material and therefore reopens decisions that depended on local/provider-free production baselines.

The current manifest records:

```text
state                              FREEZE_REOPENED
local_required_components_target   0
production_path_hosted_only        true
multi_user_required                true
no_demo_only_path                  true
```

Historical ADRs, experiments and frozen bundles remain immutable for their original scope. They are not rewritten to make the new architecture appear continuous.

## 3. Current production candidate

```text
hosted browser
→ hosted OIDC/JWKS identity provider
→ bearer-authenticated REST + fetch-stream SSE
→ hosted FastAPI container
→ managed PostgreSQL
   - ownership/execution
   - tenant RLS
   - action custody/idempotency
   - safe observability/evaluation read model
   - transport + semantic campaign evidence
→ selected hosted provider/model
→ AgentController
→ HarnessRunner
→ 18 typed TRACTIAN tools
→ deterministic safety boundaries
→ supplied hosted TRACTIAN HTTPS API
→ RunTrace + ProductionEvaluator
→ PostgreSQL safe projection
→ REST/SSE
→ React control room
```

The hosted candidate requires no durable DuckDB/filesystem state. DuckDB and signed-HMAC paths remain only for bounded historical regression/reproduction where explicitly documented; they are not allowed to become required final-product dependencies.

## 4. Identity and multi-tenant boundary

The internet-facing candidate uses provider-neutral OIDC/JWKS with:

- asymmetric algorithm allow-list;
- issuer/audience/signature/time validation;
- mandatory organization/tenant claim;
- configurable required claims;
- optional authorized-party allow-list;
- external permissions intersected with application-owned allow-lists.

A regression found that a configured Auth0 role claim could be absent while the token was accepted. The boundary was corrected to make configured required claims fail closed, and the full regression/handoff suite returned green.

Signed HMAC bearer identity remains only a bounded backend/regression baseline and is not the hosted browser target.

## 5. Managed PostgreSQL state

`OPS-STORE-001` remains valid in its core conclusion: PostgreSQL is the mutable operational-state backend. The cloud-only revalidation changes the deployment requirement from local/self-hosted PostgreSQL to **managed hosted PostgreSQL**.

The hosted path stores:

```text
operational ownership/execution
consequential-action custody/idempotency
browser-safe observability/evaluation
TRACTIAN transport evidence
semantic campaign certification
```

Serving is fail-closed and does not auto-migrate schemas.

### Neon live pilot

An isolated hosted pilot exists in Neon:

```text
project        academy-tractian-hosted-pilot
region         AWS São Paulo (sa-east-1)
PostgreSQL     18
plan state     Free account project
```

Live pilot findings already observed:

- clean hosted database baseline;
- distinct internal and scoped credentials;
- TLS-required application DSNs;
- native Neon role creation produced a role incompatible with the project's RLS hard gate (`BYPASSRLS`); that path was rejected;
- the scoped application role was instead created with `NOSUPERUSER`, `NOBYPASSRLS`, no `CREATEDB/CREATEROLE`, and `NOINHERIT`;
- the incompatible experimental role was removed;
- sanitized evidence is stored in `research/neon-hosted-pilot-live-baseline-2026-09-04.md`.

This is qualification evidence, not a Neon production promotion decision.

## 6. Hosted PostgreSQL preflight

The repository now contains a read-only, secret-safe preflight:

```bash
python scripts/check_hosted_postgres_preflight.py
```

It validates before migration/serving that:

- both endpoints are non-local;
- internal and scoped connections resolve to distinct identities;
- PostgreSQL major version matches the required production version;
- the scoped role is not superuser and does not bypass RLS;
- both real application sessions use TLS;
- database identity is coherent.

The evidence output contains bounded/fingerprinted metadata only and must not expose DSNs, passwords or raw secrets.

## 7. Hosted deployment challenger

An isolated Railway project now exists only as a deployment/executor challenger:

```text
project        academy-tractian-hosted-pilot
purpose        run exact PR SHA with hosted secrets and current Docker/FastAPI path
promotion      NONE
```

The immediate experiment is:

```text
Railway exact PR branch
→ secret-injected Neon internal/scoped DSNs
→ hosted PostgreSQL preflight
→ explicit migration
→ RLS/isolation verification
→ readiness
```

Railway must not be described as the winning cloud vendor until the preregistered deployment evidence closes.

## 8. Provider/model state

The hosted candidate registry currently includes:

```text
OpenAI control candidate
Google Gemini 3.7 Flash
Google Gemini 3.8 Flash
Groq GPT-OSS-120B
```

Provider/model deployment inputs are not selection evidence. The promotion decision remains governed by the project's EDD gates, USD-zero eligibility, reliability, tool/argument correctness, trajectory quality, safety, latency and reproducibility.

Current production provider state remains:

**`NO_SELECTION`**.

## 9. TRACTIAN 18-operation evidence

The canonical contract contains 18 operations: 13 reads and 5 consequential actions.

The hosted campaign distinguishes three concepts that must never be conflated:

1. route/schema registration;
2. empirical hosted transport proof;
3. semantic runtime/evaluator proof.

Final claims require:

```text
TRACTIAN_TRANSPORT       18/18
TRACTIAN_SEMANTIC        18/18
combined end_to_end      PASS
```

Historical packaged evidence does not satisfy these hosted-live gates. No route is credited merely because it exists in code.

## 10. Consequential actions

The product runtime currently keeps hosted mutation capability fail-closed. This is intentional until production authorization and tenant/resource isolation are independently proven.

The target governed path is:

```text
agent proposes exact action
→ deterministic schema/scope/permission validation
→ tenant/resource authorization
→ private PostgreSQL custody
→ explicit authenticated confirmation
→ authorization + kill-switch revalidation
→ atomic persistent idempotency claim
→ exact action execution
→ action trace/evaluation
→ safe frontend projection
```

Integration-campaign approval is not production authorization.

## 11. Evaluation / EDD state

Implemented:

- deterministic structural/safety/trajectory evaluation;
- operation-level transport and semantic campaign gates;
- bounded evidence persistence;
- provider promotion decision gates;
- semantic review collection/adjudication machinery;
- paired MANUAL × ASSISTED business-value analysis machinery;
- evaluator-only adaptive stopping diagnostics.

Still intentionally not claimed:

- calibrated judge-vs-human agreement from real labels;
- real engineer-minutes-saved/business-value result;
- production runtime gain from adaptive stopping;
- production SLO/capacity from CI load tests.

Negative or `NO_SELECTION` experiment results remain valid evidence and must not be overwritten to manufacture a preferred architecture.

## 12. Frontend target

The final frontend must expose the normal production path and make evidence provenance visible. Required operator surfaces include:

- mission/runtime status;
- run timeline and trace graph;
- evidence lineage;
- tool coverage and 18-operation campaign state;
- evaluation results;
- action custody/confirmation state;
- provider/deployment decision evidence;
- production health;
- live architecture/dataflow explanation.

Truth provenance must distinguish at minimum:

```text
LIVE_PRODUCTION
LIVE_EXPERIMENT
HISTORICAL_EVIDENCE
SYNTHETIC_TEST
NOT_MEASURED
```

Visual density must improve understanding rather than turn the product into disconnected demo dashboards.

## 13. Current CI and reproducibility

On PR head `bf053129dea8293ca750dae52c00ddfe985d36d5`, the central gates returned green, including:

- `production-runtime`;
- PostgreSQL operational/restart checks;
- load/concurrency benchmark;
- frontend;
- observability;
- EDD;
- final-delivery reproduction;
- final-handoff acceptance;
- `final-ci-required`.

The current clean-clone gate validates the canonical `FREEZE_REOPENED` state instead of demanding byte identity with a superseded freeze candidate.

## 14. Remaining P0 gates before a new hard freeze

```text
HOSTED_POSTGRES_PREFLIGHT
HOSTED_POSTGRES_MIGRATION
HOSTED_POSTGRES_RLS_ISOLATION
HOSTED_OIDC_LIVE
HOSTED_PROVIDER_SELECTION
TRACTIAN_TRANSPORT_18_OF_18
TRACTIAN_SEMANTIC_18_OF_18
HOSTED_ACTION_AUTHORIZATION
HOSTED_FULL_PRODUCT_PLAYWRIGHT
HOSTED_SECURITY_CAMPAIGN
HOSTED_LOAD_CAMPAIGN_WITH_BOUNDED_CLAIM
HUMAN_SEMANTIC_CALIBRATION
CURRENT_DOCUMENTATION_RECONCILIATION
BRANCH_PROTECTION_ENFORCEMENT
EXACT_FINAL_SHA_EVIDENCE
```

The new hard freeze is allowed only when every hard gate that applies to the final claim is either `PASS` or explicitly recorded as a bounded non-claim that does not contradict the TAPI/kickoff/delivery requirements.

## 15. Current non-claims

Do not claim:

- the hard freeze is currently effective;
- unconditional production readiness;
- Neon or Railway has won the cloud decision;
- a production provider/model has been selected;
- hosted OIDC has been live-validated end to end;
- TRACTIAN transport or semantic coverage is 18/18 before empirical proof;
- hosted consequential actions are qualified;
- hosted full-product browser E2E has passed before the live deployment campaign;
- human semantic calibration or business-value measurement is complete;
- CI load measurements establish production SLO/capacity;
- branch protection is enforced before GitHub reports it active;
- RAG, multi-agent, MCP, LangGraph, memory, Kubernetes, Kafka, Redis or another additional framework is superior without a measured gap and controlled challenger result.

## 16. State update rule

This file is the mutable, canonical human-readable state. New live evidence may update it. Historical ADRs, frozen experiment artifacts and superseded freeze bundles remain immutable and authoritative for their original scopes.
