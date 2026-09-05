# P0 hard-freeze closure — 2026-09-05

## Decision

Close the repository-side P0 distributed-product work as **`READY_FOR_HARD_FREEZE`**, subject only to the already-scheduled end-of-day hard freeze and final rehearsal/delivery checks.

This addendum supersedes only the mutable topology/status statements that changed after the 2026-09-04 freeze candidate. Historical experiment and decision artifacts remain immutable for their original scopes.

## Exact accepted integration

The final P0 architecture increments were merged to `main` through:

- PR #187 — read-only runtime cross-replica handoff;
- PR #188 — non-transferable consequential-action execution leases.

PR #188 squash merge SHA:

`9e160e9badcf6ba0d5ebba39b7d64d24380408c6`

The promoted `final-ci-required` contract now requires four reusable acceptance jobs before `required-gate` can pass:

1. current clean-clone reproduction;
2. full Chromium product acceptance;
3. horizontal read-only runtime handoff;
4. non-transferable action execution lease/fencing.

The final-freeze validator itself was not weakened. Its registered `final-ci-required.yml` artifact was repinned to the exact changed Git blob.

## Production topology now proven in repository evidence

### Shared production persistence

The promoted serving topology uses PostgreSQL for:

- run ownership and tenant-scoped durable execution state;
- runtime private handoff envelopes and lease/generation state;
- consequential-action custody;
- persistent action idempotency claims;
- non-transferable action execution leases;
- safe observability runs/events/evidence/evaluations;
- semantic-review and operational-value collection state.

The production package does not require DuckDB. DuckDB remains available only through explicit dev/benchmark compatibility extras.

### Realtime

Durable PostgreSQL observability rows are authoritative. One PostgreSQL `LISTEN/NOTIFY` listener per replica is wakeup-only; bounded durable cursor reads preserve catch-up if a notification is missed. `Last-Event-ID` / sequence replay and tenant authorization remain row-backed and independent from NOTIFY payloads.

### Read-only runtime execution

Read-only investigation runtimes use a PostgreSQL `FOR UPDATE ... SKIP LOCKED` handoff queue with expiring leases and monotonically increasing generation tokens.

Repository-level PostgreSQL-real cross-replica tests prove:

- one healthy lease is not double-claimed;
- a second replica does not interrupt a healthy owner;
- an expired runtime lease may be claimed by another replica;
- stale generations cannot renew/finalize/publish as current owners;
- the recovered runtime can reach evaluation/terminal persistence;
- private handoff payload is removed after terminal completion.

### Consequential actions

Actions deliberately use different semantics from read-only runtimes.

The exact confirmed action receives a non-transferable lease owned by the executing replica. A healthy owner may renew it; expiry or stale/missing ownership never authorizes a replacement transport attempt.

Repository-level PostgreSQL-real two-replica tests prove:

- replica B does not mark replica A's healthy leased action uncertain;
- duplicate confirmation cannot create a second transport call;
- expired action ownership cannot transfer to B;
- custody, execution and claimed idempotency state converge to `UNCERTAIN` after lost ownership;
- a stale late response cannot overwrite uncertainty with `ACCEPTED` / `NOT_ACCEPTED`;
- the forced-expiry campaign issues exactly one external transport call;
- automatic action replay remains disabled.

This is not an exactly-once external-side-effect claim. Exactly-once would require the external TRACTIAN API to participate in a common idempotency/fencing protocol.

## Restart and failure boundary

Recovery authority is intentionally split:

- runtime handoff recovery owns only read-only runtime executions;
- action execution lease recovery owns consequential action uncertainty.

A healthy action on another replica is therefore not treated as a startup orphan. `running + no action lease` is immediate ownership-loss evidence; only the short `accepted + no lease` confirmation setup window receives bounded grace.

Recovery remains conservative and idempotent. No restart or lease expiry is permission to blindly replay a consequential action.

## Realtime benchmark observation

One hosted-CI sample of the previously promoted realtime wakeup benchmark kept all hard gates green but missed an efficiency threshold, yielding an inconclusive sample. The exact same preregistered job was rerun on the same code SHA with no threshold/protocol change and passed:

- polling baseline event p95: 52.10 ms;
- PostgreSQL LISTEN/NOTIFY event p95: 23.71 ms;
- candidate-minus-baseline p95: -28.39 ms;
- idle durable-read ratio candidate/baseline: 0.375;
- idle durable-read reduction: 62.5%;
- hard gates: PASS;
- efficiency gates: PASS.

The first sample remains visible as hosted-runner timing variance; no criterion was relaxed to obtain a pass.

## Bounded claims

Repository evidence now supports a **cross-replica correctness claim for the tested PostgreSQL product algorithms**: read-only runtime takeover plus healthy-action non-interference/stale fencing.

It does **not** support claims of:

- deployed Cloud Run / Cloud SQL high availability;
- production RTO/RPO, uptime, multi-region failover or autoscaling capacity;
- distributed exactly-once external action side effects;
- enterprise OIDC/SSO;
- production provider/model selection;
- completed human semantic calibration;
- measured engineer time saved;
- production-capacity/SLO inference from CI load tests;
- superiority/necessity of LangGraph, multi-agent, RAG, Redis, Kafka, Temporal or another orchestration system;
- GitHub branch-protection enforcement before GitHub reports it active.

## Remaining delivery path

Before the 2026-09-08 delivery, the P0 path is limited to:

1. successful post-merge `required-gate` on the accepted `main` SHA;
2. synchronize the canonical current-status/freeze bundle with this closure;
3. end-of-2026-09-05 hard feature/visual/architecture freeze;
4. apply/verify GitHub branch protection if repository administration access becomes available;
5. final rehearsal and evidence inspection on 2026-09-06/07;
6. delivery on 2026-09-08.

Provider/model expansion is P1. D01/D02 are consumed governed experiments and must not be replayed. Any new provider/model campaign requires a new preregistered experiment ID and frozen evaluation protocol.