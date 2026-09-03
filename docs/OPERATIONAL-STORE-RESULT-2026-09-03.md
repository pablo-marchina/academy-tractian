# OPS-STORE-001 — Operational Store Result

Date: 2026-09-03  
Decision: `PROMOTE_POSTGRES_OPERATIONAL`  
Evidence run: GitHub Actions `operational-store-benchmark` run `33772270034`  
Artifact: `operational-store-benchmark-33772270034` / ID `9900236708`  
Artifact SHA-256: `6cedd8fe1f81e1e657023d61bfcd8f077c650dc44f75dcbff7ed43f935258d8e`

## Decision

Promote PostgreSQL for **mutable operational state** in a separate production PR.

Keep DuckDB for the sanitized analytical/evaluation read model. This result does not justify replacing DuckDB for analytical workloads.

The promotion follows the preregistered rule in `OPERATIONAL-STORE-BENCHMARK-2026-09-03.md`: hard gates are applied before latency/throughput comparisons. PostgreSQL passed every hard gate. The current DuckDB production-store baseline failed `unexpected_operational_errors`, therefore PostgreSQL is the only promotion-eligible candidate in this experiment.

## Environment

- GitHub-hosted Ubuntu 24.04 runner
- Python `3.11.16`
- DuckDB `1.5.5`
- PostgreSQL `18.6`
- psycopg `3.3.5`
- CI profile: `3` repetitions
- workload: `50` lifecycles per worker per repetition
- concurrency: `1`, `5`, `10`, `25`
- candidate order alternated by repetition
- no LLM/provider calls
- no TRACTIAN API calls

Absolute latency values are environment-scoped; the hard-gate outcome and paired comparison are the evidence used for this decision.

## Hard gates

| Gate | DuckDB | PostgreSQL |
|---|---:|---:|
| unexpected operational errors | **1777** | **0** |
| conflicting ownership takeover | 0 | 0 |
| duplicate logical ownership creation | 0 | 0 |
| lost committed operational rows | 0 | 0 |
| invalid execution-state transition accepted | 0 | 0 |
| cross-tenant rows through scoped API | 0 | 0 |
| terminal execution corrupted after reconnect | 0 | 0 |
| orphaned normal execution replayed | 0 | 0 |
| orphaned consequential action replayed | 0 | 0 |
| PostgreSQL RLS cross-tenant visibility | n/a / 0-count baseline | 0 |

Result:

- DuckDB eligible after hard gates: **no**
- PostgreSQL eligible after hard gates: **yes**

The DuckDB mixed-workload errors were reported as `BinderException` by the benchmark. A separate diagnostic branch directly exercises `DuckDBRunAccessStore` and `DuckDBRunExecutionStore` to record exact stage/error signatures. That diagnostic does not modify the preregistered decision criteria or this hard-gate outcome.

## Quantitative workload results

### Lifecycle p95

| Concurrent workers | DuckDB p95 | PostgreSQL p95 | PostgreSQL reduction |
|---:|---:|---:|---:|
| 1 | 141.05 ms | 6.77 ms | 95.2% |
| 5 | 164.08 ms | 26.19 ms | 84.0% |
| 10 | 158.22 ms | 61.62 ms | 61.1% |
| 25 | 437.45 ms | 150.56 ms | 65.6% |

### Successful lifecycle throughput

| Concurrent workers | DuckDB | PostgreSQL | PostgreSQL / DuckDB |
|---:|---:|---:|---:|
| 1 | 7.42/s | 169.10/s | 22.79× |
| 5 | 22.69/s | 236.13/s | 10.41× |
| 10 | 12.74/s | 197.41/s | 15.50× |
| 25 | 80.73/s | 207.09/s | 2.57× |

Performance is secondary to the hard gates, but it independently supports the same production direction in the measured environment.

## Error behavior by concurrency

DuckDB aggregate mixed-workload error rates:

- 1 worker: `0 / 150` = `0%`
- 5 workers: `356 / 750` = `47.47%`
- 10 workers: `1378 / 1500` = `91.87%`
- 25 workers: `18 / 3750` = `0.48%`

PostgreSQL:

- all tested concurrency levels: `0%` operational errors
- 25 workers: `3750 / 3750` successful lifecycles

The non-monotonic DuckDB failure rate is a reason to preserve the raw artifact and diagnostic evidence rather than fit a simplified scaling narrative to one runner.

## Security / isolation evidence

The PostgreSQL candidate used a **non-superuser application role** with Row Level Security. A direct cross-tenant probe under that role returned zero rows. The application-layer scoped contract also returned zero cross-tenant rows.

RLS is defense in depth; trusted server-side identity, authorization, ownership checks and safe observability projections remain required.

## Production promotion boundary

The follow-up production PR must migrate mutable state without changing product semantics:

1. run ownership;
2. durable run execution state;
3. pending consequential-action custody;
4. consequential-action idempotency ledger;
5. restart/recovery reconciliation for normal and action executions.

It must preserve:

- fail-closed authorization;
- cross-user/cross-organization isolation;
- no browser-controlled identity/permissions;
- exact action confirmation binding;
- atomic idempotency;
- no blind replay after restart;
- `EXECUTING/CLAIMED -> UNCERTAIN` for ambiguous consequential actions;
- DuckDB sanitized observability/evaluation analytics;
- all existing tests.

PostgreSQL becomes a production dependency only in that promotion PR.

## Claim boundary after promotion

Passing this experiment supports the target **authenticated multi-user, durable, single-node product** and removes the mutable-store concurrency blocker inside that target.

It does **not** by itself prove:

- horizontal multi-instance execution;
- distributed queue semantics;
- shared SSE fan-out across instances;
- automatic resumable agent checkpoints;
- unlimited concurrency or capacity.

Those require separate evidence before being claimed.

## Reversal triggers

Reopen `OPS-STORE-001` or a successor decision if:

- measured production workload materially differs from the benchmark envelope;
- PostgreSQL violates any safety hard gate in integration/load testing;
- horizontal scaling introduces a different shared-state requirement;
- a durable workflow/checkpoint layer changes transaction boundaries materially;
- operational complexity dominates without the measured reliability benefit in the target deployment.
