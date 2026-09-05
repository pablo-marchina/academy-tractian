# Academy × TRACTIAN — consolidated development update — 2026-09-05

**Checkpoint:** 2026-09-05 BRT  
**Purpose:** record the complete engineering progress made during the current development conversation without rewriting frozen historical evidence.  
**Current `main` observed at checkpoint:** `c5cc56acc74f5cc64b0f617ec718f95d01f8fca6`  
**Current remote-production stream before this documentation update:** PR #194 / `feat/remote-production-p0` at `8efdf18c41a8297c70289425a5f9046a2fabcde9`  
**Promotion state:** **NOT LIVE-PRODUCTION-READY**

This document is a progress record. It does not supersede frozen ADRs, consumed experiment packets, evaluator-only artifacts, or the canonical acceptance contracts. Where development happened on parallel branches, that distinction is explicit: a feature implemented in an open PR is not described here as already integrated into `main` or another open stream.

## 1. Executive summary

The project moved from a repository product with important single-process/local-state seams to a distributed PostgreSQL production substrate with explicit persistence, cross-replica realtime, recoverable read-only execution, and conservative consequential-action ownership. In parallel, the project established a hosted-production security boundary and a separate USD0 remote-production/build stream.

The main engineering progression was:

```text
local-compatible product composition
→ shared PostgreSQL observability/state
→ fail-closed storage injection
→ production wheel without DuckDB
→ distributed PostgreSQL LISTEN/NOTIFY wakeups
→ horizontal read-only runtime handoff
→ non-transferable consequential-action execution leases
→ evidence/documentation closure of the distributed baseline
→ hosted OIDC + tenant/resource authorization stream
→ repository cleanup/rebaseline
→ fail-closed USD0 remote-production boot/build stream
```

The resulting repository is materially closer to a production deployment, but the final claim remains intentionally blocked until the remote topology, standards-based identity, provider selection, clean-browser E2E, security/failure campaign, CI/deployment controls, and final exact-SHA evidence are all integrated and green.

## 2. Merged distributed production foundation — PRs #182–#189

The following increments are merged and form the accepted distributed repository baseline preserved in `main` history.

| PR | Merge SHA | Production property established |
|---|---|---|
| #182 — PostgreSQL observability | `b621557a18157b6c9cbd5e517142ee0b821b1c26` | Browser-safe observability/evaluation truth moved from local DuckDB to shared PostgreSQL; cross-instance durable visibility and SSE replay were proved. |
| #183 — no local action fallbacks | `2541c9e18204ccf75c290308362460f75ccc730c` | Production action custody/idempotency/run state can no longer silently fall back to file-backed local storage. |
| #184 — explicit durable stores | `24cd7ed28a1fb9c07854fc0ffb68d9004fee4a69` | Product/observability composition requires explicit storage backends; implicit path-derived persistence was removed from production-capable factories. |
| #185 — no-DuckDB production wheel | `b77579859a5289284f864aa9baaa08ebedcbbdec` | DuckDB was removed from production dependencies; clean production wheel imports the PostgreSQL entrypoints with DuckDB absent. |
| #186 — distributed realtime | `6a59d6758b89b9860ace84f6aa43764f5bf3498e` | PostgreSQL LISTEN/NOTIFY became the cross-replica SSE wakeup layer while durable event rows remained the sole source of truth. |
| #187 — horizontal read-only handoff | `3fecc8a495c79ad3f091ff8f986319943c0d8ab0` | Read-only investigations can be recovered across replicas using PostgreSQL `SKIP LOCKED`, expiring leases, and generation fencing. |
| #188 — consequential-action execution lease | `9e160e9badcf6ba0d5ebba39b7d64d24380408c6` | Consequential actions received non-transferable owner/generation leases; lost ownership converges to `UNCERTAIN`, never automatic replay. |
| #189 — distributed-baseline evidence closure | `d3bed06b132212c85b126f56708863d45f64e03e` | Current documentation/evidence was synchronized with the distributed PostgreSQL baseline while keeping stronger deployment claims out of scope. |

### 2.1 Shared PostgreSQL observability and product truth

PR #182 removed the local observability file from the promoted PostgreSQL path. Independent application/database-store instances can observe the same sanitized projection, and a run accepted by one instance can be authorized/read from another instance. Durable replay supports both explicit sequence cursors and `Last-Event-ID` without replaying the already acknowledged event.

The accepted boundary remains:

- PostgreSQL rows are product truth;
- sanitized browser projection is distinct from private execution state;
- raw secret material is not persisted in the observability tables;
- repository-level correctness does not imply deployed HA, RTO/RPO, or uptime.

### 2.2 Fail-closed storage composition

PRs #183 and #184 removed accidental production seams that could reconstruct local DuckDB files when dependencies were omitted. The promoted path now requires explicit durable stores for ownership, execution, observability, action custody, and idempotency.

Local compatibility remains an explicit test/development seam rather than a silent production fallback. Production PostgreSQL entrypoints no longer accept persistence path arguments that could misrepresent the actual state topology.

### 2.3 Production artifact without DuckDB

PR #185 removed DuckDB from root production dependencies and retained it only in explicit development/benchmark extras. The standalone production-wheel gate proves that:

- `duckdb` is not installed in the production wheel environment;
- runtime package imports still succeed;
- promoted PostgreSQL product entrypoints import with DuckDB absent;
- restoring DuckDB to production is not an accepted workaround for eager compatibility imports.

### 2.4 Distributed realtime wakeups

PR #186 added one dedicated PostgreSQL LISTEN connection per application replica. Notifications are wakeups only; they carry bounded `{run_id, sequence}` metadata and never replace durable event rows.

The design closes the query/wait race by observing wakeup generation before the durable cursor read and retains bounded sparse polling so a lost or duplicate notification cannot lose an event.

The `RT-WAKEUP-001` evidence kept all hard correctness gates at zero logical loss/duplication and demonstrated materially lower idle durable-read pressure. A later same-protocol sample recorded:

```text
polling baseline event p95       52.10 ms
LISTEN/NOTIFY event p95          23.71 ms
candidate - baseline p95        -28.39 ms
idle durable-read ratio           0.375
idle durable-read reduction       62.5%
```

One earlier CI timing sample was inconclusive on the efficiency threshold; it was preserved as variance rather than hidden or addressed by changing the preregistered threshold.

### 2.5 Horizontal read-only execution recovery

PR #187 replaced same-process `Future` ownership as the production execution contract for read-only investigations. PostgreSQL `runtime_work_items` provides a private durable execution envelope, `FOR UPDATE ... SKIP LOCKED` claiming, lease expiry, and monotonically increasing claim generations.

A replica-local thread pool is now compute capacity, not durable ownership. If a read-only owner disappears and its lease expires, another replica can reconstruct the runtime and finish it. A stale generation is fenced from:

- tool-policy access;
- sanitized observability publication;
- terminal execution writes.

EDD also found a real local capacity reservation race: multiple HTTP threads could observe a free worker before any claim was registered, producing utilization greater than one. The dispatcher was serialized around capacity observation + durable claim + submission, while execution remained concurrent. The load benchmark was corrected to observe durable terminal state instead of assuming the request replica owns a local `Future`.

### 2.6 Consequential-action liveness without replay

PR #188 intentionally uses a different recovery model for side effects:

```text
read-only lease expires
→ another replica may recover

consequential-action lease expires / ownership is lost
→ UNCERTAIN
→ no replacement transport attempt
```

The action execution lease is exact-owner, generation-fenced, renewable only by the live owner, and non-transferable. Startup of another replica does not disturb a healthy action. If the owner is lost, custody/execution/idempotency state converges conservatively and a stale late response cannot publish false success after ownership loss.

This proves an important product guarantee — **the product does not blindly replay an ambiguous external side effect** — but it is not a claim of distributed exactly-once behavior at the external TRACTIAN API boundary.

## 3. Hosted LIVE-PRODUCTION-READY stream — PR #191 — parallel, not yet integrated

PR #191 (`codex/live-demo-ready`) is an open draft and must be treated as a parallel hosted-security stream, not as code already merged into the #192/#194 stream.

It established or is establishing the following hosted-production boundaries:

- asymmetric OIDC/JWKS identity verification;
- issuer, audience, token lifetime and authorized-party validation;
- no demo/header identity fallback;
- remote PostgreSQL-only hosted composition;
- migration-owner credential separated from serving/scoped roles;
- serving hard-coded to `initialize_schema=False`, with no DDL credential;
- explicit hosted CORS/public frontend API routing;
- external TRACTIAN HTTP boundary with application-owned credentials;
- production runtime sandbox built only from allowed upstream runtime material.

The exact user-supplied TRACTIAN sandbox source used by this stream is recorded by SHA-256:

`37546f7a9af93e7364d35313c53a67621769d454a3803624aad4daffa4d0d134`

The hosted runtime artifact is restricted to `api/` + `data/`; evaluator/gold/challenge-answer material is excluded from the runtime and authorization decisions.

### 3.1 Tenant/resource authorization

Inspection of the supplied TRACTIAN upstream showed that `/users/me` exposes server-side company/permission data, while individual resource/action endpoints do not consistently prove tenant ownership themselves. The hosted design therefore adds a stricter server-owned boundary:

1. verified OIDC subject identifies the caller;
2. `/users/me` supplies TRACTIAN company and supported permission evidence;
3. OIDC organization is independently matched to the TRACTIAN company for new runs;
4. asset ownership is resolved from the normal asset endpoint;
5. analysis ownership is resolved through analysis → asset → company;
6. a guarded transport blocks cross-tenant reads before the response can become model evidence;
7. malformed/degraded/unknown authorization evidence fails closed.

The design explicitly rejects private sandbox stores, evaluator/gold data, identifier naming conventions, browser fields, model text, or JWT action claims as substitutes for resource ownership evidence.

### 3.2 Consequential actions in hosted serving

A configuration flag alone is not accepted as authority to enable side effects. Hosted actions remain blocked until target-specific authorization can be revalidated at both proposal and confirmation, including TOCTOU protection, exact confirmation binding, same-company ownership, permission, and idempotency.

Endpoints whose target ownership cannot be proven from the public upstream contract remain fail-closed.

### 3.3 #191 acceptance state

`docs/LIVE-PRODUCTION-READY-PLAN-2026-09-05.md` is the superseding acceptance contract for #191. The PR stays draft until remote hosted E2E, security/failure, provider, deployment provenance, and all exact-SHA CI gates are satisfied.

A green local/CI artifact or a successful live presentation alone is explicitly insufficient.

## 4. Repository cleanup/rebaseline — PR #192

PR #192 (`chore/repository-cleanup`) is an open repository rebaseline stream and is the base of #194.

Its purpose is to make the active repository surface reflect current project rules without destroying frozen scientific provenance. It adds/updates:

- concise root navigation;
- canonical documentation ownership rules;
- `docs/CODEBASE-MAP.md`;
- test/script/research navigation;
- stronger `.gitignore` hygiene;
- lifecycle classifications for active vs historical/research-only code;
- distinction between TAPI requirements and stronger project-added production gates.

The current hard project envelope is recorded consistently as:

```text
actual project cash cost = USD 0
+
remote serving with no developer-machine/local truth dependency
+
multi-user tenant safety
+
evidence-driven / quantitative engineering
+
EDD for material changes
+
adaptivity only when it wins a controlled comparison
+
live safe frontend visibility
+
systematic research before material architecture changes
```

USD0 is an eligibility gate, not a weighted cost preference and not an invitation to silently use a paid fallback.

### 4.1 Frozen-evidence correction caught by CI

During cleanup, an edit accidentally touched ADR-017-pinned `docs/RUBRIC-TO-EVIDENCE.md`. The hard-freeze integrity test correctly failed. The response was to restore the exact frozen blob and keep current rules in mutable canonical documentation — not to weaken or bypass the freeze validator.

### 4.2 Historical workflow cleanup

Legacy research suites are being removed from ordinary product-PR triggering while preserving workflow code/history/manual execution where appropriate. This reduces unrelated product CI noise without rewriting or deleting historical experiment evidence.

No inspected source family was deleted merely for cosmetic cleanup unless reachability/provenance proved it safe.

## 5. Remote USD0 production epic — issue #193

Issue #193 is the current P0 epic for turning the repository product into a remotely deployable baseline while preserving the project's simultaneous hard constraints.

Required characteristics include:

- remote production serving;
- actual cash cost USD0;
- no automatic paid spillover;
- remote PostgreSQL-compatible durable state;
- multi-user/RLS boundaries;
- reproducible deployment artifact;
- no dev identity/local model/local store dependency;
- remote smoke/RLS/SSE/restart/cost/quota evidence;
- explicit `NO_SELECTION` when no free candidate clears all gates.

External cloud/account provisioning is intentionally deferred until a candidate remains eligible and owner credentials/actions are actually required.

## 6. Current remote-production implementation — PR #194

PR #194 (`feat/remote-production-p0`) implements the first remote-production P0 slices on top of the cleanup stream.

### 6.1 Fail-closed remote production configuration

The remote configuration contract requires and validates before serving:

- `environment=production`;
- remote PostgreSQL URI(s);
- TLS for serving database roles;
- distinct internal/scoped PostgreSQL roles;
- strong non-placeholder runtime identity secret;
- remote HTTPS public origin;
- exact Git SHA and deployment ID;
- exact `cost_policy=usd0-hard-gate`;
- paid fallback disabled;
- local serving disabled;
- provider execution disabled until a governed provider selection exists.

The validator rejects localhost, loopback, unspecified/link-local endpoints, Docker-host aliases, local/Unix socket forms, and non-PostgreSQL serving DSNs before application boot. Private remote/VPC database addresses remain valid candidates because “private network” is not equivalent to “developer-local.”

### 6.2 Serving vs migration authority

Serving does not own schema migration authority:

- serving boot uses `initialize_schema=False`;
- schema bootstrap is a separate `academy_tractian.remote_migrate` operation;
- serving should carry no DDL credential;
- `/api/meta/release` returns only safe release identity/provenance, never DSNs, database hosts, role passwords, or runtime secrets.

The remote server remains provider-closed while the production model/provider state is `NO_SELECTION`. Consequential actions are also not promoted merely because code exists; deployment/IAM/action authorization gates still apply.

### 6.3 Reproducible production dependency surface

PR #194 adds:

- `requirements-production.lock` for the clean production runtime dependency set;
- exact wheel build backend pin (`hatchling==1.32.0`);
- standalone-wheel validation with `pip check` and exact locked versions;
- explicit proof that DuckDB and `httpx` development-only surfaces are absent from the production runtime environment.

### 6.4 Provider-neutral container artifact

The backend container is designed as a production artifact rather than a demo image:

- multi-stage build;
- Python 3.11.16 slim-bookworm base pinned by immutable multi-architecture image index digest;
- amd64 and ARM64/A1 viability retained;
- runtime process uses non-root UID/GID `10001`;
- release Git SHA/build identity/cost policy/provider-state labels are embedded;
- provider-state label remains `NO_SELECTION`;
- fail-closed remote server is the default entrypoint;
- migration is a separate command;
- `.dockerignore` excludes tests/docs/history/private artifacts while preserving required runtime code.

### 6.5 USD0 infrastructure eligibility research

The current experiment matrix is a preregistered comparison, **not a production selection**:

- **T1:** OCI A1 Always Free + self-hosted PostgreSQL — primary minimum-rewrite experimental baseline;
- **T2:** OCI + Aiven Free PostgreSQL — challenger;
- **T3:** OCI + Neon Free PostgreSQL — challenger, conditional on direct LISTEN/free-compute compatibility;
- **T4:** OCI + Supabase Free PostgreSQL — lower-priority challenger.

Current eligibility research rejects Render Free, Koyeb Free, Northflank Sandbox, and Cloudflare Containers for this production path. Cloudflare Workers is not the current backend baseline because adopting it would require a material FastAPI/psycopg architecture rewrite before a measured need justifies one.

If every USD0 topology fails, the correct result remains `NO_SELECTION`; the constraint is not silently relaxed.

## 7. Current CI/evidence state

### 7.1 Accepted merged foundation

The promoted heads of PRs #182–#189 passed their exact required PostgreSQL, restart/recovery, load, clean-clone, frontend/browser, and aggregate CI gates before merge. The distributed correctness properties summarized above therefore have repository-level evidence.

### 7.2 PR #194 pre-documentation head

On exact SHA `8efdf18c41a8297c70289425a5f9046a2fabcde9`, many current checks were green, including:

- action-execution-lease;
- horizontal-runtime-handoff;
- Chromium full-product browser acceptance;
- production runtime unit gate;
- standalone production-wheel smoke;
- remote-production image smoke;
- PostgreSQL product integration;
- contract/PostgreSQL integration;
- observability API;
- evaluator contract;
- operator frontend;
- final handoff audit.

However, at this checkpoint:

- `clean-clone / reproduce-current-product` was **red**;
- another `reproduce-current-product` check was **red**;
- aggregate `required-gate` was therefore **red**.

This head is **not merge-ready** and must not be described as fully green. The failures are diagnostic evidence to fix; acceptance criteria must not be weakened to make them disappear.

This documentation update creates a new exact branch SHA, so all final promotion/merge evidence must be collected again on the eventual intended head. Older green results are supporting evidence, not substitutes for an exact-head required gate.

## 8. Branch/integration model at this checkpoint

The current open work is not one linear branch and must not be treated as if it were already combined:

```text
main distributed baseline
├─ #190 old canonical-doc/freeze rehearsal stream
├─ #191 hosted LIVE-PRODUCTION-READY security/identity/tenant stream
└─ #192 repository cleanup/rebaseline
    └─ #194 remote-production boot/build/USD0 stream

#193 = remote-production P0 tracking issue
```

Consequences:

- #191's OIDC/JWKS and hosted TRACTIAN tenant/resource authorization are valuable implemented work, but are not yet automatically present in #194;
- #194's fail-closed remote configuration/container/USD0 deployment boundary is not automatically present in #191;
- final integration must preserve both sets of hard boundaries rather than choosing one branch by accident;
- #190 is historical/prospective documentation rehearsal and should not overwrite the newer production rebaseline;
- frozen historical evidence must remain byte/provenance stable while mutable current docs follow the eventually integrated product.

## 9. Remaining P0 path to LIVE-PRODUCTION-READY

The critical path after this checkpoint is:

1. **Restore exact-head clean reproduction on #194** without weakening hard-freeze or product gates.
2. **Integrate the hosted #191 security boundary with the #192/#194 production stream**: OIDC/JWKS, no demo identity, tenant/company binding, guarded TRACTIAN transport, least-privilege serving/migration roles, and exact-target action authorization.
3. **Select/provision a genuinely eligible USD0 remote topology** only after current eligibility checks; if none passes, retain `NO_SELECTION` and expose the blocker.
4. **Deploy the same production artifact remotely**: frontend, FastAPI backend, PostgreSQL, standards-based identity, and authorized TRACTIAN sandbox/endpoint; no localhost path in the request chain.
5. **Run a fresh USD0 provider/model tournament** using the frozen quality/safety/tool/latency/failure/cost evaluation design. Historical D01/D02 remain consumed and are not replayed merely to force a winner.
6. **Run clean-browser remote E2E from another network**, including auth, run creation, tool evidence, evaluator, SSE reconnect, durable replay, and `Last-Event-ID` catch-up.
7. **Execute the production security/failure campaign**: invalid/expired JWT, tenant mismatch, cross-tenant IDs, malicious tool arguments, confirmation/idempotency replay, provider outage, TRACTIAN outage, PostgreSQL transient failure, replica loss, and interrupted consequential actions.
8. **Protect deployment governance**: required status checks/branch protection or an equivalent enforced release control, deployment provenance, rollback path, and no secret-bearing build/runtime metadata.
9. **Collect human semantic calibration and operational-value evidence** before claiming semantic-human agreement or engineer-time/business-value gains.
10. **Complete production operator/control-room evidence** so the frontend exposes safe lifecycle, tool/evidence, policy, evaluation, provider provenance, distributed recovery, and health signals without hidden chain-of-thought.
11. **Freeze one exact promoted SHA/configuration** only after all required local/CI/remote gates are green on that artifact.

## 10. Explicit non-claims

At this checkpoint, do **not** claim:

- `LIVE-PRODUCTION-READY` has been achieved;
- #191 and #194 are already integrated;
- the product is currently deployed on a selected production cloud topology;
- a production model/provider is selected;
- any paid service/API/infrastructure is eligible for final project selection under the current USD0 hard constraint;
- historical Cloudflare D01/D02 were rejected for cost — they were USD0-eligible but failed technical promotion gates;
- repository-level PostgreSQL correctness proves deployed HA, SLO, RTO/RPO, failover, autoscaling, or uptime;
- consequential external side effects are distributed exactly-once;
- human semantic calibration or engineer-minutes-saved evidence is complete;
- GitHub `main` protection is enforced at this checkpoint;
- LangGraph, RAG, multi-agent orchestration, Redis, Kafka, Temporal, Kubernetes, memory, or another major technology is justified without a measured production gap and controlled challenger win.

## 11. Current evidence discipline

The project should continue following the same rule used successfully throughout this conversation:

```text
measured gap / requirement
→ explicit hard constraints
→ simple baseline
→ preregistered candidate or implementation hypothesis
→ exact failure/evidence capture
→ fix the real boundary
→ rerun unchanged acceptance criteria
→ promote only on one exact intended SHA
```

Observed failures are part of the evidence. The project does not obtain production status by hiding variance, weakening thresholds, adding local fallbacks, replaying consumed experiments, or silently relaxing USD0/security constraints.

## 12. Related current records

- `docs/CURRENT-PROJECT-STATUS.md` — mutable canonical integrated-state summary for the branch on which it lives.
- `docs/DELIVERY-PLAN.md` — current delivery sequence and acceptance ownership.
- `docs/DELIVERY-ACCEPTANCE.md` — Definition of Done and claim gates.
- `docs/ARCHITECTURE.md` — current integrated architecture for its branch.
- `docs/LIVE-PRODUCTION-READY-PLAN-2026-09-05.md` — #191 hosted promotion contract; branch-specific until integrated.
- issue #193 — USD0 remote-production P0 epic.
- PR #194 — active remote-production boot/build implementation stream.

When these parallel streams are integrated, canonical current-state documents should be updated to describe only the merged product truth; this development update should remain as a dated provenance record of how the system reached that point.
