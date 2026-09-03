# DuckDB Operational Concurrency Diagnostic

Date: 2026-09-03  
Related decision: `OPS-STORE-001`  
Diagnostic run: GitHub Actions `duckdb-operational-diagnostic` run `33773134487`  
Artifact ID: `9900481209`  
Artifact SHA-256: `052634e4bc70e7fe4cdd8d4e473a895e6374d07b3bc9c18ddb67acfac0b2f289`

## Purpose

Explain the `BinderException` hard-gate failures observed for the DuckDB baseline in the preregistered operational-store benchmark without modifying the benchmark protocol or decision thresholds.

This diagnostic calls the **current production classes directly**:

- `academy_tractian.run_access.DuckDBRunAccessStore`
- `academy_tractian.run_execution_store.DuckDBRunExecutionStore`

It does not use the PostgreSQL adapter and does not modify production code.

## Result

| Concurrent workers | Attempts | Successes | Errors | Error rate |
|---:|---:|---:|---:|---:|
| 1 | 50 | 50 | 0 | 0.00% |
| 5 | 250 | 197 | 53 | 21.20% |
| 10 | 500 | 62 | 438 | 87.60% |
| 25 | 1250 | 1243 | 7 | 0.56% |

The non-monotonic failure rate reproduces the qualitative shape seen in `OPS-STORE-001`; therefore it should not be simplified into a monotonic scaling claim.

## Exact failure signature

The failures were DuckDB `BinderException` instances with the message pattern:

```text
Binder Error: Unique file handle conflict: Cannot attach "run-access" - the database file ".../run-access.duckdb" is already attached by database "run-access"
```

or the equivalent for `run-execution.duckdb`.

At 5 workers:

- `run-access` unique-file-handle conflicts: 23
- `run-execution` unique-file-handle conflicts: 30

At 10 workers:

- `run-access`: 431
- `run-execution`: 7

At 25 workers:

- `run-access`: 7
- `run-execution`: 0

## Failing production stages

The error is not isolated to benchmark aggregation. It appears while the product stores open/use their connection-per-operation database handles.

At 5 workers the diagnostic observed failures in:

- `access.claim`: 20
- `access.get`: 3
- `execution.create_accepted`: 10
- `execution.accepted_to_running`: 1
- `execution.running_to_completed`: 17
- `execution.get`: 2

At 10 workers:

- `access.claim`: 385
- `access.get`: 46
- `execution.create_accepted`: 7

At 25 workers:

- `access.claim`: 4
- `access.get`: 3

## Interpretation

The existing DuckDB baseline is valid for the bounded single-user/low-contention behavior it already demonstrated, but its current **connection-per-operation mutable-store topology** is not reliable under the multi-user concurrent small-transaction workload required by the production target.

This diagnosis strengthens, but does not alter, the original `OPS-STORE-001` decision. PostgreSQL had already been selected because:

1. hard gates were preregistered before the result;
2. DuckDB recorded unexpected operational errors;
3. PostgreSQL recorded zero operational errors and zero safety/isolation violations;
4. PostgreSQL also materially improved measured p95 latency and throughput.

## Engineering consequence

Do not attempt to hide these failures by adding a global process lock around DuckDB and calling the production problem solved. That would change the concurrency semantics, serialize the workload, and require a new candidate benchmark. The already-qualified PostgreSQL candidate provides the stronger operational contract without requiring such a workaround.

DuckDB remains the analytical/evaluation read model, where its workload fit is materially different.
