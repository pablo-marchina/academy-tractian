# Wave 3 — Swagger/OpenAPI Ingestion & Audit Pipeline

Status: **READY FOR CONTRACT ARRIVAL / NO DOMAIN ASSUMPTIONS**

## Objective

When TRACTIAN provides the API contract, convert it immediately into an auditable, versioned inventory for client/tool design, security classification, scenario creation and experiments.

This document defines the pipeline before seeing the contract so we do not tailor the methodology after observing convenient API features.

## Ground truth hierarchy

1. exact raw contract supplied by TRACTIAN;
2. normative OpenAPI specification matching the declared `openapi` version;
3. partner clarification for semantics not expressible in OpenAPI;
4. generated clients/tool schemas only as derived artifacts.

A code generator is never treated as contract truth.

## Intake versions

The ingestion layer should recognize the contract version rather than assume it. Current OpenAPI publishes 3.2.0 as latest and also publishes 3.1.x/3.0.x schemas/specs. The project should accept the supplied version and pin the corresponding normative specification.

If the partner supplies Swagger/OpenAPI 2.x, the pipeline records that fact and adds a conversion/compatibility decision rather than silently upgrading it.

## Pipeline

```text
RAW CONTRACT
   ↓
immutable archive + SHA-256
   ↓
parse JSON/YAML safely
   ↓
detect OAS version
   ↓
structural/schema validation
   ↓
semantic/audit checks
   ↓
reference/security normalization
   ↓
endpoint + schema + auth inventory
   ↓
feature-compatibility report
   ↓
provisional mutation/risk classification
   ↓
partner/manual semantic review
   ↓
canonical ToolSpec candidates
   ↓
client/runtime spikes
```

## Stage 1 — immutable acquisition

Record:

- original filename;
- exact bytes hash (SHA-256);
- acquisition timestamp;
- source/provenance;
- declared OpenAPI version;
- `info.title` / `info.version`;
- Git commit containing the archived artifact or a non-secret artifact reference.

Never normalize over the only copy of the original.

## Stage 2 — validation

Run a validator compatible with the detected OAS version, but preserve an important OpenAPI rule: published JSON Schemas can catch many violations, not all; normative specification text is authoritative if schema/tooling disagrees.

Audit additionally for:

- duplicate/missing `operationId`;
- unresolved/internal/external `$ref`;
- duplicate parameter name+location;
- path-template/parameter mismatches;
- missing success/error response documentation;
- response bodies lacking schemas where expected;
- ambiguous nullable/union/composition shapes;
- unconstrained objects/additional properties;
- discriminator/`oneOf`/`anyOf` usage;
- callbacks/webhooks/links;
- multipart/binary payloads;
- deprecated operations;
- custom `x-*` extensions;
- server overrides;
- security overrides at operation level.

## Stage 3 — endpoint inventory

Produce one row per operation with at least:

```text
operation_key
method
path
operationId
tags
summary
parameter_refs
request_body_schema
response_statuses
response_schema_refs
security_effective
security_override
servers
deprecated
callbacks_present
external_refs_present
```

`operation_key` is project-owned and stable even if `operationId` is absent/poor.

## Stage 4 — security inventory

OpenAPI security can be declared globally and overridden per operation; an empty security array can remove a top-level requirement and alternatives have OR semantics, while multiple schemes inside one requirement have AND semantics.

The audit therefore materializes the **effective** security requirement for every operation rather than reading only the top-level field.

Partner clarification is still required for business permissions/tenant authorization that may not be encoded in the API auth scheme.

## Stage 5 — mutation/risk classification

HTTP method is only a prior, not the final answer.

For each operation record:

- `read_only`: `yes/no/unknown`;
- `mutation`: `yes/no/unknown`;
- `high_impact`: `yes/no/unknown`;
- `idempotency`: `documented/inferred/unknown`;
- `requires_justification`: `yes/no/unknown`;
- `permission_class`: partner/API-derived;
- classification provenance.

Never automatically label every GET safe or every POST high-impact. Semantic review and partner policy win.

## Stage 6 — schema/entity inventory

Extract components/schemas and relationships:

- entity/schema name;
- inbound/outbound references;
- required fields;
- identifiers;
- enum/discriminator values;
- confidence/quality/freshness/limitations fields if present;
- timestamps/version fields;
- tenant/permission-related fields if present;
- fields changed by mutating operations where inferable.

The entity map is generated from actual schemas, then manually reviewed; public TRACTIAN product documentation must not invent API entities.

## Stage 7 — generator compatibility audit

Two candidate code generators are useful as experiments, not authorities.

### OpenAPI Generator Python

Official project compatibility currently covers OAS 3.0 and 3.1 (3.1 support is documented as beta in the project compatibility table). Generated-client behavior must be tested against the exact contract features.

### openapi-python-client

Official repository targets OpenAPI 3.0/3.1 and explicitly states that it is still in development and does not support every OpenAPI feature.

### Consequence

Before adopting generated code, produce a feature matrix from the actual spec. Any unsupported/partially supported feature becomes a red flag and live conformance test.

## Stage 8 — canonical ToolSpec candidate generation

For each reviewed operation, derive a ToolSpec candidate containing:

- stable tool ID/name;
- human description based on partner contract, not model invention;
- input schema;
- normalized result schema/reference;
- underlying operation key;
- mutation flag;
- high-impact flag;
- authorization/policy metadata;
- evidence category;
- timeout/retry policy placeholder;
- idempotency metadata;
- trace attributes.

Tool selection remains curated: not every endpoint must automatically become model-callable if exposing it increases ambiguity/risk without task value.

## Stage 9 — required output artifacts

Proposed structure after onboarding:

```text
artifacts/openapi/
├── raw/
│   └── supplied-contract.*
├── normalized/
│   └── openapi.normalized.json
├── manifest.json
└── reports/
    ├── validation.json
    ├── endpoint-inventory.csv
    ├── schema-inventory.csv
    ├── security-inventory.csv
    ├── refs-and-features.json
    ├── generator-compatibility.md
    ├── mutation-risk-review.csv
    └── open-questions.md
```

Sensitive credentials are never archived with the contract.

## Stage 10 — same-day onboarding workflow

Within the first session after receiving Swagger:

1. archive/hash contract;
2. run version/validation audit;
3. enumerate all operations/schemas/security;
4. produce unresolved semantic questions;
5. review mutations/high-impact/permissions with TRACTIAN while access is fresh;
6. identify state/reset endpoints and stochastic response metadata;
7. freeze `API-MAP-v0`;
8. only then implement the canonical client/tool spike.

## Key Wave 3 finding

**OpenAPI ingestion and client generation are two different problems.** We need a project-owned contract inventory even if we later choose generated client code. This protects evaluation and tool semantics from generator limitations or version drift.

## Primary/official sources

- OpenAPI versions and schemas: https://spec.openapis.org/oas/
- OpenAPI 3.2.0 normative specification: https://spec.openapis.org/oas/v3.2.0.html
- OpenAPI Generator: https://github.com/OpenAPITools/openapi-generator
- OpenAPI Python client generator project: https://github.com/openapi-generators/openapi-python-client
