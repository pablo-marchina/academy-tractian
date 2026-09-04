# Load + concurrency CI evidence — 2026-09-03

## Evidence identity

This result is the first successful provider-free CI execution of the load/concurrency benchmark introduced in #168 / PR #169.

- benchmark code head: `71193f08255ca618c4e6d06f3f1b84f72cee5ff5`
- workflow run: `33830731867`
- artifact: `load-concurrency-ci-report`
- artifact archive digest: `sha256:ee29aadc84435aaa6438ea120f8e376d52e6c37bdfd97943a6bd7a3040dab2c1`
- report evidence SHA-256: `41892c773847ef694c91d9f9a17ead5c0e807e4537216dff6a35074c9cd1e5b9`
- report status: `MEASURED`
- thresholds preregistered: `false`
- production capacity claim ready: `false`

The artifact contains aggregate measurements only. It contains no run IDs, organization IDs, user IDs, identity IDs, bearer tokens, prompts or raw traces.

## CI workload

The CI integration intentionally uses a small deterministic workload to prove the measurement path rather than emulate production scale:

- authenticated PostgreSQL topology;
- real PostgreSQL 18 service in the GitHub runner;
- non-owner/non-BYPASSRLS scoped role;
- two synthetic tenants;
- provider-free final-only work with a deterministic 50 ms decision delay;
- product executor `max_workers = 2`;
- concurrency levels `1` and `4`;
- 6 measured requests per level;
- one unmeasured warmup request.

## Observed aggregate results

| Metric | Concurrency 1 | Concurrency 4 |
| --- | ---: | ---: |
| Requests | 6 | 6 |
| Accepted | 6 | 6 |
| Completed | 6 | 6 |
| Error rate | 0.0% | 0.0% |
| Wall duration | 1.966 s | 1.737 s |
| Completed throughput | 3.051 runs/s | 3.455 runs/s |
| Submit p50 | 63.760 ms | 222.795 ms |
| Submit p95 | 72.141 ms | 253.770 ms |
| Submit p99 | 73.624 ms | 256.807 ms |
| End-to-end p50 | 324.207 ms | 1030.951 ms |
| End-to-end p95 | 339.463 ms | 1259.472 ms |
| End-to-end p99 | 342.403 ms | 1262.147 ms |
| Peak active runs | 1 | 2 |
| Peak queued runs | 1 | 2 |
| Peak inflight runs | 1 | 4 |
| Peak executor utilization | 0.50 | 1.00 |
| Max observed persistence p95 | 50.834 ms | 129.356 ms |
| RSS peak | 204,099,584 B | 211,558,400 B |

All 12 measured requests completed without failure, interruption, uncertainty, rejection or timeout. Cross-tenant read isolation remained fail-closed during the same campaign.

## Interpretation

The higher-concurrency level visibly saturated the two-worker executor and produced queueing. End-to-end p99 increased by roughly 3.7× from concurrency 1 to concurrency 4, while completed throughput increased only modestly in this synthetic CI environment.

That is evidence that queue pressure and latency degradation are measurable with the current topology. It is **not** evidence that `max_workers=2` is the correct production setting, nor that ~3.5 runs/s is a production throughput limit.

The observed persistence p95 also increased under the higher-concurrency level, but this single CI run cannot attribute the latency increase to PostgreSQL, DuckDB observability persistence, executor scheduling, TestClient overhead or GitHub-runner contention independently.

## Claim boundary

This result may support the statement:

> The promoted authenticated PostgreSQL topology can be exercised concurrently with quantitative queue, latency, throughput, persistence and resource measurements while preserving tenant isolation in the provider-free CI campaign.

It must **not** be used to claim:

- production requests-per-second capacity;
- an SLO/SLA;
- autoscaling requirements;
- optimal worker or pool sizing;
- external TRACTIAN API capacity;
- model-provider concurrency or latency.

Any configuration challenger must use a separately frozen protocol and EDD comparison. Production-capacity claims require deployment-representative infrastructure and preregistered acceptance thresholds.