# RUNTIME-HANDOFF-001 — horizontal read-only runtime recovery

- Date: 2026-09-05
- Status: `EXPERIMENTING`
- Production scope: read-only investigation runtimes only
- Consequential actions: explicitly excluded from automatic replay

## Problem

The promoted product already has shared PostgreSQL state and cross-replica realtime delivery, but runtime execution is still attached to the process-local `ThreadPoolExecutor/Future` that accepted the HTTP request. A replica loss therefore leaves durable state readable but cannot move the investigation work to another healthy replica.

The old startup reconciliation is also too coarse for horizontal serving: an `accepted/running` runtime cannot be called orphaned merely because a different replica started.

## Hard constraints

1. No mandatory local service or process-local source of truth.
2. Multiple replicas may compete for work without duplicate ownership.
3. Read-only runtime work may be reconstructed after replica loss.
4. Consequential action execution must never be retried merely because a lease expired.
5. Tenant authorization and browser-safe observability boundaries remain unchanged.
6. Private request envelopes never enter observability/frontend and are deleted after a terminal runtime state.
7. A stale worker must be fenced from tool access, event projection and terminal state after lease loss.
8. Existing provider/model evaluation semantics must remain unchanged.

## Alternatives considered

### A — process-local Future only

Current baseline. Lowest implementation complexity but cannot satisfy horizontal recovery or rolling-replica ownership semantics.

### B — PostgreSQL `FOR UPDATE ... SKIP LOCKED` + lease + generation fencing

Uses the durable PostgreSQL substrate already required by the product. Enqueue, ownership, lease expiry and execution state remain queryable and auditable in one database. PostgreSQL 18 explicitly documents `SKIP LOCKED` as useful for avoiding lock contention with multiple consumers of a queue-like table.

Primary source:
- https://www.postgresql.org/docs/18/sql-select.html
- https://www.postgresql.org/files/documentation/pdf/18/postgresql-18-A4.pdf

### C — Google Cloud Tasks -> Cloud Run worker endpoint

Strong managed queue candidate once the final GCP deployment exists. Cloud Tasks retries failed/unacknowledged tasks and explicitly documents that duplicate executions can occur, so application-level idempotency/fencing is still required. HTTP task dispatch has a finite dispatch deadline and introduces another service/IAM/deployment boundary.

Primary sources:
- https://docs.cloud.google.com/tasks/docs/common-pitfalls
- https://docs.cloud.google.com/tasks/docs/creating-http-target-tasks
- https://docs.cloud.google.com/tasks/docs/reference/rest/v2/projects.locations.queues.tasks

### D — Google Pub/Sub pull subscription

Provides a highly scalable managed messaging substrate and supports exactly-once delivery for pull subscriptions within the documented regional constraints. It still requires progress/idempotency state in the application and adds topic/subscription/consumer lifecycle to a workload currently backed by one authoritative PostgreSQL state machine.

Primary source:
- https://docs.cloud.google.com/pubsub/docs/exactly-once-delivery

### E — Temporal

Provides durable workflow execution and crash recovery as a first-class abstraction. It is a credible challenger if the runtime evolves into long-lived workflows requiring durable timers, complex compensation or multi-service orchestration. Today it would add a second workflow state machine beside the project-owned deterministic controller/evaluator before a measured need exists.

Primary source:
- https://docs.temporal.io/

## Initial decision hypothesis

Promote **B — PostgreSQL SKIP LOCKED + lease/generation fencing** as the minimum-complexity production baseline if it satisfies all hard correctness gates. Do not claim it is globally superior to Cloud Tasks/Pub/Sub/Temporal; keep those as reversal candidates if quantitative load or operability evidence crosses the triggers below.

The decision follows the project rule: minimum complexity that wins quantitatively under production constraints.

## State model

For read-only runtimes:

1. HTTP request prepares/persists the initial browser-safe run state.
2. Ownership + `accepted` execution state are persisted.
3. A private runtime envelope is persisted in `runtime_work_items`.
4. A replica claims it with `FOR UPDATE ... SKIP LOCKED`.
5. Claim receives a monotonically increasing generation and expiry.
6. The active replica renews the lease while executing.
7. Every tool-policy boundary and live observability projection checks the current generation/lease.
8. Terminal persistence is generation-fenced.
9. On completion/failure, the private envelope is deleted.
10. If the replica disappears, another replica can claim only after expiry and receives a newer generation.

For consequential actions:

- this runtime queue is not used;
- no action transport retry is authorized by runtime lease expiry;
- action execution continues to require explicit confirmation and idempotency custody;
- horizontal action liveness/lease without replay is a separate safety decision and must receive its own gates before promotion.

## Preregistered hard gates

`RUNTIME-HANDOFF-001` fails if any item below is false:

1. A current lease cannot be claimed by a second replica.
2. Starting another product replica does not change a healthy leased runtime to `interrupted`.
3. Expired read-only runtime work can be claimed by a second replica.
4. Takeover increments the generation and recovery count.
5. An old generation cannot renew after expiry.
6. An old generation cannot write a terminal state after takeover.
7. Stale claim guard blocks tool-policy access and browser-safe projection.
8. Recovered execution reaches a terminal state through the normal evaluator path.
9. The private envelope is absent after terminal state.
10. Cross-tenant read authorization remains fail-closed.
11. No consequential action transport is replayed as part of runtime recovery.
12. Existing restart, load, PostgreSQL, browser and clean-clone acceptance remain green on the exact same SHA.

## Quantitative measurements

Before changing the backend away from PostgreSQL, measure at minimum:

- queue claim p50/p95/p99;
- accepted-to-execution-start p50/p95/p99;
- recovery latency after lease expiry;
- duplicate claim rate;
- stale terminal write rejection count;
- lease renewal failure rate;
- DB queries/transactions per active runtime;
- throughput under concurrent queued runs;
- PostgreSQL lock wait / pool pressure;
- completion rate and evaluator regression versus the local-executor baseline.

No arbitrary SLO is invented before the hosted baseline. Safety gates above are zero-tolerance.

## Reversal triggers

Benchmark Cloud Tasks and Pub/Sub as challengers if any of the following occurs under the hosted multi-replica load campaign:

- PostgreSQL queue contention materially degrades product read/write SLOs;
- queue claim/recovery latency fails the preregistered product SLO;
- connection-pool pressure becomes a dominant bottleneck;
- deployment expands to regions/topologies where one transactional PostgreSQL queue is no longer appropriate;
- workload requires rate scheduling, delayed tasks or backpressure that a managed task service materially improves;
- long-lived workflow semantics make Temporal materially simpler or safer under a paired implementation benchmark.

Any migration must preserve the same generation-fencing, tenant, evidence, safety and evaluator contracts.
