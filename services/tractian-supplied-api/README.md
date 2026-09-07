# TRACTIAN supplied API — hosted runtime

This directory vendors a deterministic, sanitized serving artifact derived from the exact TRACTIAN package supplied to the project.

## Provenance

- upstream ZIP SHA-256: `37546f7abad4c573ab36384a171161f3ba6c7258024341cc42f0881d9606d134`
- supplied `api/app/main.py` SHA-256: `a9bdfb8a5fc85e8f169438984f787ad5fd0db95cdd2dc41a15e05ca363a3ca78`
- hosted `store.py` SHA-256: `f731965882e2be245ac69fe9f7d046c898a867d9a6c21239eed5470d20b053b3`
- hosting wrapper SHA-256: `ffb5ae45d1a341c404579cdef188b96a4bf7f24d32b899d14def60e90212c18d`
- reconstructed runtime tar.gz SHA-256: `0db58e29d6f5c86ef1838acf31c4caed788b393eb1807345fabd157c8de5bb9a`

The upstream ZIP hash matches `research/tractian-source-baseline-2026-08-27.md`.

## Custody boundary

The hosted artifact contains no `eval/`, no `expected-paths.json`, no narrative gold scenarios, and no gold-bearing `data/cases.parquet`. The escalation endpoint resolves case existence from the supplied agent-visible `agent-input/cases.json`, containing only `id`, `ticket_id`, `company_id`, `user_id`, `asset_id`, and `message`.

The TRACTIAN-provided API source remains unchanged except for the hosted `store.py` case lookup needed to eliminate gold custody. `hosting.py` adds only a public health endpoint and a service-to-service authentication boundary.

## Hosting boundary

- public health: `GET /healthz`;
- all supplied API routes require `x-academy-tractian-key`;
- secret source: `ACADEMY_TRACTIAN_SERVICE_TOKEN` environment variable;
- the secret is never committed.

## Railway service contract

- service name: `tractian-supplied-api`;
- root directory: `services/tractian-supplied-api`;
- Dockerfile: `Dockerfile`;
- healthcheck: `/healthz`;
- required environment: `PORT`, `ACADEMY_TRACTIAN_SERVICE_TOKEN`.

The Academy API points `ACADEMY_TRACTIAN_BASE_URL` to this service's HTTPS domain and injects the same secret exclusively through `ACADEMY_TRACTIAN_SERVER_HEADERS_JSON`.

The `runtime.bundle.b64.part*` files are an immutable transport encoding. Concatenate them lexicographically, Base64-decode, and verify the manifest SHA-256 to reproduce the tar.gz used by Docker.
