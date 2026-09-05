# P0 production baseline and first migration decision

Status: `FROZEN_BASELINE`

Base commit: `acb786e3a4cf45500fd68741e1ecedba1f624e5d`

## Objective

Move the current product from an authenticated durable single-node topology to a cloud-ready, horizontally scalable topology without weakening the validated agent, evaluator, safe-projection, authorization, confirmation or idempotency contracts.

The production invariant is explicit: no mandatory runtime service may depend on a developer machine or local persistent service.

## Baseline facts

At the frozen base commit:

- PostgreSQL already owns mutable multi-user operational state, including run ownership, execution state, action custody, action idempotency, operational-value collection and semantic-review collection.
- the browser-safe observability/evaluation read model is still a DuckDB file;
- observability access uses a stable safe-projection contract and run authorization before run-scoped reads;
- SSE already uses stable event IDs, monotonic event sequences, `Last-Event-ID` recovery and catch-up semantics;
- the current DuckDB store serializes access with a process-local lock to avoid file-handle races;
- the production product therefore remains single-node for the observability path even though mutable operational state is PostgreSQL-backed;
- `main` is not protected at this baseline;
- provider/model selection is not yet final.

## P0 gap matrix

| Gap | Current state | Target evidence | Priority |
| --- | --- | --- | --- |
| Local observability persistence | DuckDB file + process-local lock | all serving observability/evaluation state in shared managed PostgreSQL; no file path required | P0 |
| Multi-instance realtime | durable events are local-file-backed and stream wake-up is polling | two independent app/store instances observe the same durable sequence; reconnect/catch-up has zero loss | P0 |
| Cloud product | no final hosted production topology frozen | hosted staging + production, reproducible from CI/IaC, no local runtime dependency | P0 |
| Identity | custom signed runtime identity | managed authentication benchmarked and integrated with application-owned authorization | P0 |
| Repository governance | `main` protection disabled | active ruleset + required checks | P0 |
| Model selection | `NO_SELECTION` | repeated paired frontier-model campaign with hard safety gates and Pareto decision | P0 |

## OBS-STORE-002 — shared PostgreSQL safe read model

Decision state: `IMPLEMENTING`

### Problem

The DuckDB observability store is safe at the data-projection layer but is not a valid production persistence primitive for horizontally scaled stateless application replicas. A process-local file handle and process-local serialization lock make the read model node-affine.

### Hard constraints

1. Preserve the existing safe projection; raw `RunTrace` material must never become browser-readable persistence.
2. Preserve stable safe run IDs and event IDs.
3. Preserve monotonic sequence ordering and SSE replay semantics.
4. Preserve idempotent duplicate event publication.
5. Preserve evaluation persistence and current frontend API shapes.
6. Reuse the existing PostgreSQL production stack rather than introduce a second database technology.
7. Serving must fail closed when the PostgreSQL schema is absent; production serving must not auto-migrate implicitly.
8. No file-backed or in-memory fallback may be required by the production topology.

### Alternatives considered

A. Keep DuckDB and mount network storage.

Rejected: retains file-lock/node-affinity semantics and does not provide a clean multi-replica database contract.

B. Add a second managed analytical database now.

Rejected at P0: increases operational surface without evidence that PostgreSQL cannot meet current read/write volume or latency requirements.

C. Reuse the existing PostgreSQL database and connection pools for the sanitized read model.

Selected baseline. It minimizes new infrastructure, provides shared durable state across replicas, supports transactional idempotent writes and creates a direct path to PostgreSQL `LISTEN/NOTIFY` as a wake-up optimization.

### Hypothesis

Replacing file-backed DuckDB observability with PostgreSQL while preserving the current store contract will remove the node-affinity blocker without materially changing functional behavior. Two independent store/app instances connected to the same database will observe the same run/event/evaluation state and duplicate publication will remain idempotent.

### Acceptance metrics

Hard gates:

- raw secret leakage into observability tables: `0`;
- duplicate logical event rows for one `event_id`: `0`;
- event loss during cross-instance read/replay campaign: `0`;
- run/evaluation API contract regression: `0` in the required regression suite;
- local filesystem persistence required by the PostgreSQL production app: `0`.

Measured after functional gates:

- write p50/p95;
- read p50/p95;
- event-to-persistence p50/p95;
- reconnect catch-up latency;
- concurrent stream/read behavior;
- database pool pressure.

### Implementation sequence

1. Introduce a PostgreSQL-backed implementation of the existing safe store contract.
2. Make the PostgreSQL product topology inject that store instead of a file path.
3. Add cross-instance persistence/idempotency tests in hosted CI.
4. Remove DuckDB from the production topology and dependency surface once all remaining consumers are migrated.
5. Preserve SSE polling temporarily as a correctness baseline.
6. Benchmark PostgreSQL `LISTEN/NOTIFY` wake-up against polling; promote it only if it improves latency/load without harming replay reliability.

### Reversal trigger

PostgreSQL remains the baseline unless measured production-like tests show that it cannot satisfy the eventual SLOs without unacceptable database pressure. Only then should Pub/Sub, managed Redis/Valkey or another managed realtime/analytics service be promoted through a preregistered challenger experiment.

## Scope guard

Until the P0 production foundation is closed, do not add RAG, multi-agent orchestration, a new agent framework or an additional persistence technology unless a measured blocker demonstrates the need.
