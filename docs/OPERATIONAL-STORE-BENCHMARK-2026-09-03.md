# Operational Store Decision — Preregistered Benchmark

Date: 2026-09-03  
Decision ID: `OPS-STORE-001`  
Status: `PREREGISTERED / NOT YET DECIDED`

## 1. Decision question

For the bounded production target **authenticated multi-user, durable, single-node product**, should mutable operational state remain on the current DuckDB baseline or move to PostgreSQL while DuckDB remains the analytical/evaluation read model?

This document is frozen before interpreting benchmark results. The benchmark may produce only one of:

- `PROMOTE_POSTGRES_OPERATIONAL`
- `KEEP_DUCKDB_SINGLE_NODE`
- `INCONCLUSIVE`

No database is selected by popularity, familiarity, or architecture fashion.

## 2. Requirement mapping

The decision exists because the production target now requires all of the following simultaneously:

- multiple authenticated users;
- immutable run ownership;
- cross-user / cross-organization isolation;
- concurrent small operational transactions;
- durable execution status;
- restart-safe recovery;
- atomic idempotency / consequential-action state;
- auditable, reproducible behavior.

DuckDB remains valuable as the current safe analytical/evaluation store. This experiment is only about **mutable operational state**.

## 3. Candidates

### A — Baseline: DuckDB operational state

Current product pattern:

- `DuckDBRunAccessStore` for immutable ownership;
- `DuckDBRunExecutionStore` for durable execution state;
- separate DuckDB observability/analytics read model.

Production claim if retained: **single process / single node, multi-user application boundary**, with no horizontal multi-instance claim.

### B — Candidate: PostgreSQL operational state

Candidate pattern:

- PostgreSQL for ownership, execution state, action custody/idempotency/checkpoint/audit candidates;
- transaction-safe concurrent mutations;
- row-level security as defense in depth for tenant-scoped data;
- DuckDB retained for safe analytical/evaluation workloads.

PostgreSQL is experimental in this branch and must not become a core runtime dependency before promotion.

## 4. Pre-benchmark evidence

Official documentation creates a material reason to run the experiment, but is **not** sufficient to choose the winner:

- DuckDB documents concurrency primarily around one process with multiple writer threads and explicitly notes that writing from multiple processes is not an automatically supported primary mode; it is optimized for analytical/bulk workloads rather than many small transactions.
- PostgreSQL provides multi-version concurrency control and transactional concurrency primitives designed for multi-user database workloads.
- PostgreSQL row-level security can enforce per-row policies and defaults to deny when row security is enabled without an applicable policy.

The benchmark therefore tests the project-specific workload rather than extrapolating from generic database claims.

## 5. Hypothesis

`H1`: Under the product's small-transaction multi-user workload, PostgreSQL will preserve all safety/correctness hard gates and provide lower concurrent failure/conflict rates and more stable p95 latency than the DuckDB operational baseline, at acceptable single-user overhead.

Null / non-promotion interpretation: if PostgreSQL does not materially improve the production-relevant frontier, keep DuckDB for the bounded single-node claim and avoid unnecessary operational complexity.

## 6. Hard gates

A candidate is **ineligible for promotion** if any applicable hard gate fails:

| Gate | Required |
|---|---:|
| unexpected operational errors inside the tested envelope | `0` |
| conflicting ownership takeover | `0` |
| duplicate logical ownership creation | `0` |
| lost committed operational rows | `0` |
| invalid execution-state transition accepted | `0` |
| cross-tenant rows returned through scoped API | `0` |
| terminal execution state corrupted after reconnect | `0` |
| orphaned normal execution replayed automatically | `0` |
| orphaned consequential action replayed automatically | `0` |
| candidate-advertised PostgreSQL RLS cross-tenant visibility | `0` |

A benchmark infrastructure failure is not a candidate failure; it produces `INCONCLUSIVE` until the experiment itself is valid.

## 7. Workloads

### W1 — Mixed lifecycle workload

Each logical operation executes the same contract:

1. claim immutable run ownership;
2. create durable `accepted` execution;
3. transition `accepted -> running`;
4. read ownership through tenant scope;
5. transition `running -> completed`;
6. re-read terminal execution.

Concurrency levels:

- `1`
- `5`
- `10`
- `25`

PR/CI profile: at least `3` repetitions and `50` lifecycle operations per worker.  
Full/manual profile: at least `5` repetitions and `200` lifecycle operations per worker.

A short warm-up runs before timed samples and is excluded from metrics.

### W2 — Contended idempotent ownership claim

Multiple workers concurrently claim the **same** logical run for the same owner.

Expected:

- exactly one logical row;
- ownership never changes;
- repeated identical claims are idempotent;
- no second logical owner can take over.

### W3 — Cross-tenant isolation

Create data for organization A and query as organization B.

Expected: zero visible A rows to B through the candidate's scoped contract.

PostgreSQL additionally receives a direct non-superuser RLS probe; this verifies that its defense-in-depth claim is real, not documentation-only.

### W4 — Restart / reconnect

After committed terminal state:

- close/recreate the store adapter;
- ownership remains exact;
- terminal state remains exact.

For non-terminal recovery:

- ordinary runtime `running -> interrupted`;
- consequential action `running -> uncertain`;
- neither is automatically reaccepted or replayed.

## 8. Quantitative measurements

For W1, collect per candidate, concurrency and repetition:

- successful logical lifecycles;
- operation errors;
- error rate;
- end-to-end lifecycle latency p50/p95/p99;
- throughput (completed lifecycles/second);
- ownership-claim latency p50/p95/p99;
- scoped-read latency p50/p95/p99;
- execution-transition latency p50/p95/p99.

Aggregate across repetitions without hiding individual repetition failures.

Secondary engineering evidence:

- runtime dependency delta;
- configuration/migration complexity;
- clean-start/reconnect behavior;
- operational topology implications.

## 9. Experimental controls

- Python 3.11.
- Same logical workload generator and IDs for both candidates.
- Connections/setup/warm-up are excluded from timed lifecycle samples where practical.
- Candidate order alternates across repetitions to reduce systematic order bias.
- Fixed deterministic benchmark seed.
- No external LLM/provider calls.
- No TRACTIAN API calls.
- PostgreSQL service version and DuckDB/Python package versions are emitted in the machine-readable artifact.
- Results are environment-scoped; absolute latencies are not generalized beyond the measured runner.

## 10. Decision rule

1. Validate benchmark integrity.
2. Apply hard gates before looking at aggregate speed.
3. Remove candidates that fail a hard gate.
4. If only PostgreSQL remains eligible: `PROMOTE_POSTGRES_OPERATIONAL`.
5. If only DuckDB remains eligible: `KEEP_DUCKDB_SINGLE_NODE`.
6. If neither remains eligible or the experiment is invalid: `INCONCLUSIVE`.
7. If both remain eligible, PostgreSQL is promoted only when at least one preregistered materiality condition is met **without creating a material regression**:
   - at any concurrency `>1`, DuckDB has a nonzero operational error rate and PostgreSQL has zero; or
   - at concurrency `25`, PostgreSQL lifecycle p95 is at least `20%` lower (`<= 0.80 × DuckDB p95`) while PostgreSQL throughput is at least `90%` of DuckDB throughput; or
   - at concurrency `25`, PostgreSQL throughput is at least `25%` higher (`>= 1.25 × DuckDB throughput`) while PostgreSQL lifecycle p95 is no worse than `110%` of DuckDB p95.
8. PostgreSQL single-user lifecycle p95 must be no worse than `2.0 ×` DuckDB single-user p95 for a performance-based promotion. If that guardrail fails, the outcome is `INCONCLUSIVE` unless DuckDB failed a hard gate.
9. If both pass hard gates and no materiality condition is met, return `KEEP_DUCKDB_SINGLE_NODE`; the extra service/dependency is not justified for the bounded target.

A simple weighted score must not override hard gates, the preregistered thresholds, or a dominated Pareto position.

## 11. Promotion boundary

This benchmark branch may add:

- experimental PostgreSQL adapter;
- optional benchmark-only dependency;
- benchmark runner/tests/workflow;
- evidence artifacts and decision documentation.

It must **not** switch the production runtime to PostgreSQL.

A separate promotion PR is required after a valid result. That PR must preserve:

- trusted server-side identity;
- current authorization semantics;
- run ownership contract;
- restart/no-replay safety;
- observability separation;
- all existing tests.

## 12. Reversal trigger

Reopen `OPS-STORE-001` if any of the following materially changes:

- production becomes multi-process/horizontally scaled;
- operational write rate or concurrency exceeds the tested envelope;
- restart/recovery requirements add resumable checkpoints;
- action custody/idempotency moves into a shared service;
- a promoted backend violates a hard gate in regression or load testing.
