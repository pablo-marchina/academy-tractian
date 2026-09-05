# Remote production USD0 infrastructure eligibility screen — 2026-09-05

Status: **prospective P0 screen; no infrastructure is selected by this document**  
Owner issue: #193  
Decision rule: **USD0 is an eligibility hard gate, not a weighted preference.**

## 1. Question

Which currently available remote infrastructure candidates are eligible to enter a controlled production comparison for the existing Academy × TRACTIAN product while preserving all project hard constraints?

The promoted product to preserve is React + FastAPI + PostgreSQL/RLS + durable PostgreSQL observability/evaluation + PostgreSQL LISTEN/NOTIFY wake-up + SSE + horizontal runtime handoff + governed actions.

## 2. Hard eligibility gates

A candidate is not scored if it fails any applicable gate below.

| Gate | Requirement |
|---|---|
| G0 | Actual project cash cost remains **USD 0**. |
| G1 | No automatic paid spillover or paid fallback is required for normal operation. |
| G2 | Serving is remote; no developer machine, localhost, local model server, SQLite/DuckDB/local-file truth. |
| G3 | The topology can preserve PostgreSQL semantics needed by the promoted product, including RLS and session-capable direct connections where LISTEN/NOTIFY is used. |
| G4 | REST + SSE/reconnect semantics can be preserved without making notification delivery the source of truth. |
| G5 | Secrets and transport can be protected with TLS. |
| G6 | Multi-user/tenant isolation remains server-trusted. |
| G7 | Deployment can be reproduced and a release identity can be tied to a Git commit. |
| G8 | The provider does not explicitly position the exact free runtime as unsuitable for production where a stronger USD0 alternative exists. |
| G9 | No consumed provider/model experiment is silently replayed or rewritten. |

A candidate that passes this screen is **eligible for experiment**, not promoted. Promotion still requires remote measurements and failure evidence.

## 3. Primary-source snapshot

Sources were checked on 2026-09-05. URLs are recorded so the decision can be revalidated if provider terms change.

### Oracle Cloud Infrastructure Always Free

Primary sources:

- https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm
- https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources_Launching.htm
- https://letsencrypt.org/2026/01/15/6day-and-ip-general-availability.html

Observed contract:

- Always Free resources remain free for the life of the account in the tenancy home region.
- Ampere A1 Always Free allocation currently corresponds to **2 OCPUs + 12 GB RAM total** (1,500 OCPU-hours + 9,000 GB-hours/month).
- Up to two E2.1.Micro AMD instances are also eligible.
- Always Free Block Volume allocation is 200 GB total across boot/block volumes, with five volume backups included.
- One Always Free flexible load balancer is available at 10 Mbps for eligible tenancies.
- 10 TB/month outbound data transfer is included.
- Resource Manager/Terraform execution is itself available within Always Free limits.
- Free-tier signup usually requires phone and credit card, but Oracle states the card is not charged unless the account is upgraded.
- **Critical risk:** Oracle may reclaim an Always Free compute instance deemed idle over a seven-day window when CPU/network (and A1 memory) stay below the documented thresholds.
- **Critical capacity risk:** A1 Always Free shapes can return out-of-host-capacity.
- Public IPv4/IPv6 can be protected without buying a domain: Let's Encrypt made short-lived IP-address certificates generally available in January 2026; automated renewal is mandatory because IP certificates are short-lived.

Eligibility result: **PASS_TO_EXPERIMENT** for a remote VM topology, with reclamation/capacity explicitly treated as failure modes. Do not claim HA/SLO merely because OCI is remote.

### Cloudflare Workers Free

Primary sources:

- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/workers/platform/pricing/

Observed contract:

- 100,000 requests/day on Workers Free.
- 10 ms CPU/request and 128 MB memory on Workers Free.
- Free plan is the default plan; paid Workers starts at $5/month.
- Static assets can be served without Worker invocation charges within the documented static-asset model.

Architecture fit:

- The current backend is Python/FastAPI/psycopg with long-lived PostgreSQL/session behavior and is not a native Workers runtime.
- Rewriting the backend to Workers would be a material architecture replacement before a measured gap has justified it.
- 10 ms CPU/request is also a materially different runtime envelope from the current product.

Eligibility result: **REJECT_AS_BACKEND_BASELINE** for the current product. Workers can remain an optional static-edge or future challenger only if a preregistered experiment demonstrates a benefit worth the rewrite.

### Cloudflare Containers

Primary source:

- https://developers.cloudflare.com/containers/platform/pricing/

Observed contract:

- Containers have **no Free allocation**; included container usage starts with Workers Paid ($5/month).

Eligibility result: **REJECT_G0**.

### Neon Free PostgreSQL

Primary sources:

- https://neon.com/pricing
- https://neon.com/docs/reference/compatibility
- https://neon.com/docs/connect/connection-pooling

Observed contract:

- Free plan is $0, has no time limit and no credit card requirement on the pricing page.
- Free compute has a fixed scale-to-zero behavior after inactivity; it cannot be disabled on Free.
- Neon documents that session context, including `LISTEN`/`NOTIFY` listeners, is lost when a session ends/suspends.
- Neon PgBouncer uses transaction pooling, which does not support `LISTEN`; a direct connection is required for session semantics.
- Current project wake-up code already reconnects a failed direct listener and correctness remains in durable rows/cursors, but a persistent direct LISTEN connection may materially affect Free compute usage/suspension behavior. That interaction is not proved by documentation alone.

Eligibility result: **PASS_TO_EXPERIMENT_WITH_BLOCKER**. Must measure direct-connection/LISTEN behavior, monthly compute consumption implications, reconnect correctness and whether a continuously listening production replica can remain inside USD0 quota. No promotion from pricing-page evidence alone.

### Aiven Free PostgreSQL

Primary sources:

- https://aiven.io/docs/products/postgresql/concepts/pg-free-tier
- https://aiven.io/docs/products/postgresql/reference/pg-connection-limits
- https://aiven.io/docs/platform/concepts/service-pricing

Observed contract:

- No credit card required; free service can be used indefinitely at USD0.
- 1 CPU, 1 GB RAM, 1 GB disk, backups, encrypted network/storage.
- Single node, no HA/SLA.
- Free tier has `max_connections=20` and no managed connection pooling.
- Aiven reserves the right to power off free services with no continuing activity, with notification beforehand.

Architecture fit:

- Direct PostgreSQL sessions are available, so RLS + LISTEN/NOTIFY are structurally closer to the promoted architecture than a transaction-only pool.
- The current production DB layer can create multiple connections per replica; the 20-connection ceiling therefore requires an explicit low-pool configuration and load experiment before promotion.

Eligibility result: **PASS_TO_EXPERIMENT_WITH_BLOCKER**. Must prove connection budget, restart/power-off recovery, LISTEN/NOTIFY, RLS and sustained USD0 operation.

### Supabase Free PostgreSQL

Primary sources:

- https://supabase.com/pricing
- https://supabase.com/docs/guides/platform/free-project-pausing
- https://supabase.com/docs/guides/deployment/going-into-prod
- https://supabase.com/docs/guides/platform/backups

Observed contract:

- Free plan: 500 MB database, shared CPU/500 MB RAM, 5 GB egress.
- Free projects can be automatically paused after low activity over a seven-day period.
- Automatic backups/PITR are not included on Free; Supabase recommends external dumps for free-tier projects.
- Supabase explicitly presents Pro as the tier that guarantees no inactivity pausing.

Eligibility result: **PASS_TO_EXPERIMENT_ONLY_AS_DB_CHALLENGER**, but lower priority than Neon/Aiven because pausing + lack of managed free backups increase production/recovery burden. No promotion without independent backup/recovery evidence.

### Render Free

Primary source:

- https://render.com/docs/free

Observed contract:

- Render explicitly says not to use Free instances for production applications.
- Free web services spin down after 15 minutes idle and may take about a minute to return.
- Free Render Postgres expires after 30 days and has no backups.

Eligibility result: **REJECT_G8** (and database persistence gate).

### Koyeb Free

Primary sources:

- https://www.koyeb.com/docs/reference/instances
- https://www.koyeb.com/docs/run-and-scale/scale-to-zero

Observed contract:

- Free instance: 512 MB RAM, 0.1 vCPU, 2 GB SSD.
- Koyeb explicitly says Free Instances should not be used for production applications.
- Free instance forcibly scales to zero after one hour and this cannot be disabled.

Eligibility result: **REJECT_G8**.

### Northflank Developer Sandbox

Primary source:

- https://northflank.com/docs/v1/application/billing/pricing-on-northflank

Observed contract:

- All users must add a payment method to create resources.
- Northflank explicitly says its free Developer Sandbox should not be used for production applications.

Eligibility result: **REJECT_G8**. Billing alerts are not equivalent to the project's no-paid-spillover hard gate.

## 4. Eligible experimental topologies after screening

Only topologies surviving hard eligibility are allowed into the next experiment.

### T0 — current repository-only baseline

No remote deployment. Exists only as null baseline for reproducibility/correctness. It cannot satisfy the remote-production DoD.

### T1 — OCI A1 Always Free, single remote host

- one A1 VM within Always Free allocation;
- containerized/static frontend + FastAPI + PostgreSQL on remote host;
- PostgreSQL remains the one durable source of truth;
- HTTPS directly on public IP using automated short-lived Let's Encrypt IP certificates, or the OCI Always Free load balancer if its exact configuration remains cost-capped;
- systemd/container restart policy + explicit migration step + backup job to Always Free storage/volume backup;
- no paid account upgrade required.

Pros: minimum application rewrite; full PostgreSQL session semantics; easiest way to preserve RLS/LISTEN/NOTIFY/SSE.  
Risks: single failure domain, OCI idle-reclamation rule, A1 capacity availability, self-managed DB/patching.

Status: **PRIMARY EXPERIMENTAL BASELINE**.

### T2 — OCI A1 Always Free compute + Aiven Free PostgreSQL

Pros: managed DB, backups, direct PostgreSQL protocol, no credit card required for Aiven free service.  
Risks: 20 DB connections, no HA/SLA, inactivity power-off policy, cross-provider network latency, two operational dependencies.

Status: **CHALLENGER**.

### T3 — OCI A1 Always Free compute + Neon Free PostgreSQL

Pros: managed Postgres, no credit card, fast serverless resume, larger apparent compute envelope than the self-hosted DB during active periods.  
Risks: Free scale-to-zero cannot be disabled; session `LISTEN` state can disappear; transaction pool cannot be used for LISTEN; persistent direct listener vs CU-hour budget must be measured.

Status: **CHALLENGER WITH PRECONDITION**.

### T4 — OCI A1 Always Free compute + Supabase Free PostgreSQL

Pros: managed Postgres and integrated platform capabilities.  
Risks: inactivity pausing, 500 MB DB, no free automatic backup, extra product surface not currently needed.

Status: **LOWER-PRIORITY CHALLENGER**.

## 5. Preregistered comparison contract

Do not promote a topology from documentation alone. For each viable topology that can actually be provisioned at USD0, run the same frozen remote acceptance packet.

### Mandatory binary gates

1. observed cash charge = USD 0;
2. account/service configuration cannot silently consume a paid fallback;
3. clean remote boot from immutable release artifact;
4. `/api/meta/release` SHA/deployment identity matches the deployed commit;
5. no localhost/dev-machine dependency;
6. RLS cross-tenant negative test passes;
7. direct PostgreSQL LISTEN/NOTIFY wake-up works or an EDD-approved replacement wins without changing durable correctness;
8. SSE reconnect catches up with zero event gaps/loss under forced disconnect;
9. process restart preserves run/evidence/action state and converges according to current recovery contracts;
10. migration is separate from serving boot;
11. no secret/DSN/private evaluator data enters browser-safe surfaces;
12. platform remains usable after idle/cold-start behavior that is part of its documented free contract.

### Quantitative measurements

- HTTP p50/p95/p99 latency;
- run acceptance and terminal latency;
- SSE first-event and reconnect/catch-up latency;
- error rate;
- notification listener failures/reconnects;
- DB connection count peak/p95;
- CPU/RAM peak/p95 where available;
- startup/restart readiness time;
- restore/recovery time for the exact supported failure drill;
- free quota consumption and projected 30-day headroom;
- deployment reproducibility success rate across repeated clean releases.

No universal SLO is invented before measurement. Results are compared to the existing repository baseline and to each surviving remote candidate.

## 6. Current decision

**No production infrastructure is selected yet.**

The evidence supports the following order:

1. T1 OCI A1 self-contained PostgreSQL topology as the minimum-rewrite remote baseline;
2. T2 Aiven DB challenger;
3. T3 Neon DB challenger only after the direct-listener/free-compute interaction is measured;
4. T4 Supabase DB only if the first three fail or a measured gap justifies it.

If T1 cannot be provisioned within Always Free capacity or fails the reclamation/cost/reliability gates, that is evidence against T1, not authorization to spend money. If every surviving topology fails, the correct result remains `NO_SELECTION` with an explicit blocker.

## 7. User action boundary

No user action is required for this documentation/configuration slice.

The first expected owner dependency will occur only when the experiment reaches real cloud provisioning. At that point the exact selected experimental candidate, account requirement and secret/click required will be stated before anything external is created.
