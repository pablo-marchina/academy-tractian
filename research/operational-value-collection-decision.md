# Operational-value collection timing and custody decision

**Status:** IMPLEMENTED BASELINE / NO HUMAN MEASUREMENTS COLLECTED / NOT HORIZONTALLY PROMOTED

## Decision question

How should the DEV operational-value pilot assign blinded MANUAL/ASSISTED tasks and measure human effort without allowing the browser to forge elapsed time, leaking evaluator-only material, or fabricating a duration after a collector failure?

This record governs the collection mechanism only. It does **not** claim that the agent saves engineer time; that claim requires real paired human measurements plus the evaluator-only operational-correctness join defined by the operational-value evaluation contract.

## Frozen constraints and hard gates

The collection path must:

1. reuse the product's trusted `AuthenticatedRuntimeContext`, authorization boundary, FastAPI application and PostgreSQL operational state;
2. require an explicit `operational-value:participate` permission rather than granting pilot access through default runtime permissions;
3. never accept `elapsed_seconds`, operator identity, pair identity, scenario/group/split labels, gold answers, private truth, or evaluator oracle material from the browser;
4. expose only one opaque operator task at a time;
5. enforce the independent-matched anti-crossover rule so the same operator cannot complete both arms of one pair;
6. reserve a task atomically under concurrent requests and permit at most one valid measurement per task;
7. keep organization isolation enforced by the existing restricted `NOSUPERUSER NOBYPASSRLS` PostgreSQL role plus RLS for scoped reads;
8. never reconstruct a lost authoritative timer after process restart;
9. preserve interrupted/technical trials as non-valid observations rather than silently imputing effort;
10. keep `LOCKED_TEST` unavailable to pilot preparation and collection.

Any violation of these invariants is a hard failure, not a metric to average against speed or convenience.

## Alternatives considered

### A. Browser-owned timer

The browser starts/stops a JavaScript timer and submits the measured duration.

**Rejected by hard gate.** It allows direct client manipulation, creates different timing authorities across clients, and makes the core business KPI dependent on untrusted input. Browser timing may still be shown as non-authoritative UX state, but it cannot become evaluation evidence.

### B. PostgreSQL wall-clock interval

Persist `started_at` and compute completion time from PostgreSQL wall-clock timestamps.

**Retained as a future challenger.** It is naturally durable and horizontal, but a process/network interruption can inflate measured human effort with downtime or an abandoned tab unless additional lease/heartbeat semantics are introduced. Promoting it without measuring this contamination would trade deployment convenience for uncertain experimental validity.

### C. Host monotonic timer + persistent assignment custody + explicit session-loss invalidation

PostgreSQL atomically owns assignment/reservation and completion custody. The serving host owns only the monotonic interval. Each assignment is bound to a unique collector `host_session_id`. A restart or loss of an already-started timer turns the trial into `TECHNICAL_FAILURE`; no wall-clock interval is reconstructed.

**Selected as the DEV pilot baseline.** This is an invariant-driven baseline selection, not an empirical performance victory. It minimizes measurement ambiguity for the first human pilot while preserving durable assignment state and deterministic failure semantics.

## Implemented concurrency semantics

- PostgreSQL serializes assignment for `(organization_id, user_id)` with a transaction-scoped advisory lock.
- Eligible task reservation uses `FOR UPDATE ... SKIP LOCKED`.
- Partial unique indexes enforce one ACTIVE assignment per user, one ACTIVE assignment per task, and one VALID measurement per task.
- The host timer uses an atomic `ensure_started` operation. Concurrent retries that converge on the same database assignment keep the original start time.
- The timer registry remembers assignments that were already started. If such a timer disappears within the same host session, it cannot be recreated with a shorter interval.
- Database state constraints reject a `VALID` trial unless it has positive elapsed time, a non-empty terminal decision, a non-empty conclusion summary and no invalid reason.

## Current deployment boundary

The baseline supports concurrent **multiple users** on one active collection host and persistent PostgreSQL custody. It is **not** promoted for active-active collection across multiple application workers without sticky routing.

That limitation is intentional and visible. Starting multiple independent collector sessions can make a task owned by one session appear stale to another. The general product can remain horizontally scalable; only the human-effort collection endpoint is constrained until the timing challenger is evaluated.

## Required evidence before horizontal promotion

Before changing the collection mechanism, freeze the comparison protocol and evaluate at least:

- authoritative/reference timer agreement;
- lost/invalid trial rate;
- duplicate valid measurement count (hard target: zero);
- same-pair same-operator exposure count (hard target: zero);
- cross-tenant disclosure count (hard target: zero);
- p50/p95 assignment and completion overhead;
- concurrent operator throughput and saturation point;
- restart/recovery behavior;
- fraction of human effort contaminated by infrastructure interruption.

Compare the current host-monotonic baseline against a durable challenger such as PostgreSQL wall-clock + explicit lease/heartbeat semantics. Use the same tasks and controlled interruption campaign where possible.

## Reversal conditions

Re-open this decision if any of the following becomes true:

1. the pilot must run active-active across multiple application workers without sticky routing;
2. observed technical-failure/lost-trial rate materially threatens the pre-frozen pilot sample plan;
3. host timer overhead or operational complexity is materially worse than a durable challenger;
4. a controlled benchmark shows a durable mechanism preserves measurement validity while improving reliability or throughput;
5. the production identity/deployment topology makes host-session affinity unverifiable.

Thresholds for promotion must be frozen **before** observing the comparative result. A challenger does not win merely because it is newer, more distributed, or easier to describe architecturally.

## Evidence status

As of this implementation record:

- collection contract: implemented;
- PostgreSQL assignment custody: implemented;
- authenticated/permissioned API: implemented;
- server-owned monotonic timing: implemented;
- same-principal concurrency controls: implemented;
- restart invalidation semantics: implemented;
- human DEV measurements: **not collected**;
- engineer-minutes-saved result: **not available**;
- horizontal timing benchmark: **not run**;
- production multi-worker promotion for the collector: **not granted**.

This status must remain explicit in presentation and documentation until real evidence changes it.
