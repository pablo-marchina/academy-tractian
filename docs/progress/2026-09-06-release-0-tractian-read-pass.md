# 2026-09-06 — Release 0 TRACTIAN bounded-read promotion

## Decision

Release gate **R0-02 — real TRACTIAN bounded read** is promoted to **PASS for the service-to-TRACTIAN transport boundary**.

This does not yet close R0-05. A genuine agent run still must prove that the same real transport is exercised after a hosted provider decision and that resulting evidence is persisted, evaluated and surfaced to the user.

## Hosted evidence

The currently hosted `production-api` deployment executes:

```text
python -m academy_tractian.production_tractian_connectivity
```

as a Railway pre-deploy gate before serving traffic.

Observed hosted pre-deploy result on the last verified production deployment:

```text
operation=search_knowledge
transport_status=200
elapsed_ms=399.34
result=PASS
```

The probe uses the repository-owned `ProductionTractianTransport`, the configured remote HTTPS base URL, server-managed headers and canonical requested-user binding. It performs a bounded typed read (`search_knowledge`) and does not log response bodies, authentication headers or credentials.

## Source properties retained

The connectivity gate and transport preserve:

- remote HTTPS-only base URL validation;
- server-owned authentication headers;
- canonical method/path/argument binding;
- canonical requested-user runtime binding;
- redirects disabled;
- bounded timeout and response size;
- no automatic blind read/write retry;
- sanitized failure reporting;
- no credential/body logging in the hosted connectivity evidence.

## Release state

```text
R0-02A service → real TRACTIAN bounded read       PASS_HOSTED
R0-02B credential/redirect/blind-retry boundary   PASS_SOURCE + hosted probe
R0-05 provider → agent → TRACTIAN → evidence      PENDING
```

## Next dependency

The TRACTIAN transport no longer blocks provider composition by itself. The next functional dependency is a provisionally qualified hosted provider and real `DecisionSource`, followed by the first genuine read-only agent run through this transport.
