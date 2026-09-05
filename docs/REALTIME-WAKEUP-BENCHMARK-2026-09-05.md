# RT-WAKEUP-001 — Distributed realtime wakeup preregistration

Date: 2026-09-05
Decision state at registration: `CANDIDATE_NOT_PROMOTED`

## Decision

Select the realtime coordination mechanism for browser SSE in the multi-replica PostgreSQL product. Coordination is wakeup-only; durable observability rows and the `(run_id, sequence)` cursor remain authoritative under every candidate.

## Hard constraints

- No mandatory local runtime service.
- Zero logical event loss in normal delivery, duplicate-notification and missed-notification/fallback slices.
- Zero duplicate logical event delivery.
- Cross-replica delivery must work without session affinity.
- `Last-Event-ID` / explicit sequence replay semantics must not change.
- Tenant authorization must not move into or depend on the wakeup payload.
- Wakeup payload may contain only bounded `run_id` and `sequence` cursor material.
- Listener failure must not block runtime execution; durable fallback must preserve eventual catch-up.

## Candidates

A. `POLL-200` — accepted baseline: each following SSE client reads the durable store every 200 ms.

B. `PG-LN-1000` — candidate: one PostgreSQL `LISTEN/NOTIFY` listener per application replica, local fan-out to SSE waiters, plus a 1000 ms fallback durable read.

C. Managed Pub/Sub — reserved challenger. It is not added to the product unless candidate B fails a hard gate or cannot materially reduce polling pressure. This avoids adding a second distributed system before evidence requires it.

## Paired CI profile

- 100 concurrent logical SSE clients.
- 5 paired repetitions for event-delivery slices.
- Baseline polling interval: 200 ms.
- Candidate fallback interval: 1000 ms.
- Event publication delay: 350 ms.
- Idle observation window: 1250 ms.
- PostgreSQL 18 service supplied by hosted CI.
- The candidate uses a real PostgreSQL LISTEN connection and real NOTIFY delivery.
- Durable-read counts are counted at the SSE algorithm boundary; the synthetic visibility flag represents the already-committed durable row. Cross-replica PostgreSQL row + NOTIFY correctness is separately covered by product integration tests.

The `full` profile increases concurrency/repetitions but does not change thresholds.

## Metrics

1. logical event loss rate;
2. logical duplicate delivery rate;
3. missed-NOTIFY fallback recovery rate;
4. cross-replica notification delivery;
5. event-to-client p50/p95 latency;
6. durable reads per idle client-second;
7. durable reads per delivered event/client;
8. listener connections opened, failures and successful reconnects;
9. payload rejection/duplicate-notification counters.

## Promotion rule

Evaluate hard gates first. `PG-LN-1000` may be promoted only if all hard gates pass and:

- idle durable reads per client are at most 50% of `POLL-200`;
- normal event-delivery p95 is no more than baseline p95 + 50 ms;
- the CI run opens exactly one listener connection for the candidate instance before any induced reconnect test;
- listener failures are zero in the normal benchmark slice.

If a hard gate fails: `REJECT_PG_LISTEN_NOTIFY`.
If hard gates pass but the efficiency/latency rule fails: `INCONCLUSIVE_KEEP_POLLING_BASELINE`.
If all rules pass: `PROMOTE_PG_LISTEN_NOTIFY`.

## Reversal triggers after promotion

Re-open this decision if production evidence shows any logical loss/duplicate, persistent listener reconnect churn, fallback polling dominating wakeups, Cloud SQL connection pressure caused by listeners, or a managed messaging challenger demonstrates a material reliability/operational advantage under the same contract.
