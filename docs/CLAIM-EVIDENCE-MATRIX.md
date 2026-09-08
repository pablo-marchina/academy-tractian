# Claim–Evidence Matrix

**Verification campaign:** `FINAL-V1-2026-09-08`  
**Rule:** `VERIFIED`, `FAILED`, `NOT_VERIFIED`, `NOT_APPLICABLE` are the only accepted evidence states. `NOT_VERIFIED` is never a pass.

This file is the verification source of truth for delivery claims. Historical experiment documents remain historical evidence; they do not override current live evidence.

| ID | Claim | Required evidence | Independent oracle / second source | Current state | Notes / next gate |
|---|---|---|---|---|---|
| C01 | Product is remotely hosted and usable without local production dependencies | deployed web/API + runtime config | Railway deployment identity + clean remote access | VERIFIED | Scope: hosted serving topology. Local test seams do not count as production dependencies. |
| C02 | Production release identity is tied to an exact source revision | embedded/reported SHA | GitHub commit vs Railway candidate/deployment identity | VERIFIED | Must be rechecked after every material promotion. |
| C03 | Runtime structural trace integrity is evaluated deterministically | persisted structural checks | mutation tests of structural evaluator | VERIFIED | This does **not** prove task correctness. |
| C04 | Structural PASS implies successful agent task execution | functional oracle on structural-green runs | hosted QA matrix | FAILED | Counterexample: `run_4b194352dd38da65490a` structural green + `FAIL_FUNCTIONAL`. This claim is prohibited. |
| C05 | Functional task success is independently evaluated for every production run | independent task rubric | live QA/golden functional oracle | NOT_VERIFIED | New `run-verification-v1` refuses to infer this from structural checks. |
| C06 | Evidence sufficiency is independently evaluated for every production run | task-specific evidence requirements | independent evidence oracle | NOT_VERIFIED | Must cover bilateral and condition/data-quality requirements. |
| C07 | Non-progress/retry loops are detected | progress evaluator + mutation fixtures | live regression using known repeated-401 failure | NOT_VERIFIED | Basic verifier implementation is under audit; exact-argument fingerprint remains a later improvement. |
| C08 | Semantic correctness is calibrated | blinded human labels | calibrated judge vs humans | NOT_VERIFIED | Do not show semantic correctness as verified until human evidence exists. |
| C09 | Agent supports all 13 TRACTIAN read operations in the final hosted topology | live successful canonical call per operation | supplied-API response + trace | NOT_VERIFIED | Registry presence is not coverage. Build 13/13 coverage matrix. |
| C10 | Agent resolves explicit human asset labels only inside authorized fleet | live grounding cases | functional oracle against expected canonical asset | VERIFIED | Verified for tested V13 cases only; broader prompt family remains required. |
| C11 | Bilateral comparison uses evidence from both requested valid assets | two-valid-assets live case | functional/evidence oracle | NOT_VERIFIED | Existing missing-second-asset fail-closed case is not bilateral-quality evidence. |
| C12 | Agent does not ask users for discoverable company/asset IDs | live prompt suite | functional oracle | NOT_VERIFIED | Several targeted cases pass; systematic coverage is still needed. |
| C13 | Tenant A cannot read tenant B's runs/events/evidence/history | cross-session tests | PostgreSQL/RLS or ownership-boundary evidence | VERIFIED | Scope: tested multi-user product paths; final adversarial campaign still required after final SHA. |
| C14 | Tenant A cannot confirm/execute tenant B's pending action | cross-tenant action tests | storage/authorization boundary | NOT_VERIFIED | Must be re-run hosted with action-enabled final release. |
| C15 | Managed browser session is server-authoritative | auth tests + code boundary | live invalid/expired session cases | VERIFIED | GET/HEAD short cache and fresh mutations are distinct contracts. |
| C16 | Multi-user architecture has known production capacity | hosted concurrency staircase | telemetry/DB/provider saturation | NOT_VERIFIED | Two-user isolation is not capacity. |
| C17 | Production has a measured availability SLO | hosted load/soak + uptime data | external continuous monitor | NOT_VERIFIED | Railway deploy healthcheck is readiness, not ongoing uptime monitoring. |
| C18 | PostgreSQL is the production state authority | runtime composition | live DB + no local fallback | VERIFIED | DuckDB/local paths are dev/benchmark seams only. |
| C19 | Realtime event delivery remains recoverable after missed wakeups | durable cursor tests | reconnect/catch-up campaign | VERIFIED | Scope: tested LISTEN/NOTIFY + durable row contract. |
| C20 | Backup/restore capability is operationally proven | real isolated restore | post-restore application/data verification | NOT_VERIFIED | Product RTO/RPO are not measured yet. |
| C21 | RTO and RPO are known | timed restore drill | recovered-data timestamp comparison | NOT_VERIFIED | Do not infer from provider feature documentation. |
| C22 | Read transport bounds redirects, response sizes and unsafe targets | deterministic transport tests | adversarial transport cases | VERIFIED | Final live failure campaign still independent. |
| C23 | Governed action contracts are implemented | action unit/integration tests | action lifecycle evaluator | VERIFIED | Contract implementation is not upstream execution evidence. |
| C24 | Five action transports reach supplied TRACTIAN API and are accepted | live write transport smoke | supplied-API accepted responses | VERIFIED | Transport-level only. Do not call this product E2E. |
| C25 | Five governed actions work through full user/product lifecycle | proposal→custody→confirmation→fresh auth→lease→transport→evaluation | hosted action E2E campaign | NOT_VERIFIED | P0 before claiming full governed execution. |
| C26 | Automated write smoke is isolated from benchmark/eval resources | explicit canary namespace + disjoint-set gate | before/after target manifest | NOT_VERIFIED | Must prevent deploy-time state contamination. |
| C27 | Unauthorized consequential effects are impossible in tested scope | SECURITY-V1 | upstream/action audit trail | NOT_VERIFIED | Hard gate: zero unauthorized effects. |
| C28 | Duplicate consequential effects are prevented/contained | replay/double-confirm/concurrency tests | action claim/lease audit trail | NOT_VERIFIED | Hard gate: zero platform-caused duplicates. |
| C29 | Credentials/private benchmark truth never reach browser/logs/model improperly | security/privacy tests | log/sample inspection | NOT_VERIFIED | Existing structural controls are strong; final campaign required. |
| C30 | Provider selection is empirically superior | frozen provider tournament | preregistered challenger comparison | NOT_VERIFIED | Current state may legitimately remain `NO_SELECTION`; provisional provider is not a superiority claim. |
| C31 | USD0 means no current cash spend | actual provider billing evidence | Railway/Cloudflare/Neon usage records | NOT_VERIFIED | Code policy alone cannot verify invoice/billing state. |
| C32 | Current topology is sustainably USD0 indefinitely | projected monthly usage within free allowances | provider billing/usage data | NOT_VERIFIED | Historical zero spend and sustainable zero cost are different claims. |
| C33 | Frontend technical metrics accurately represent backend semantics | metric lineage audit | endpoint/db/source comparison | FAILED | Previous generic quality presentation over-signalled structural checks. Must be corrected and re-audited. |
| C34 | Architecture shown to user reflects current runtime | production-truth endpoint + architecture manifest | Railway/runtime introspection | NOT_VERIFIED | Documentation/runtime action drift must be eliminated. |
| C35 | CI required gate covers material regression paths | workflow composition + green execution | exact-SHA workflow jobs | VERIFIED | Workflow presence alone is not enforcement. |
| C36 | Production branches enforce the required gate | branch protection/ruleset | GitHub branch/ruleset read | FAILED | Previously observed `protected=false`; must be changed before final assurance. |
| C37 | Supply-chain critical vulnerabilities are actively checked | dependency/container/secret scans | lock/image provenance | NOT_VERIFIED | Add USD0-compatible automated checks where feasible. |
| C38 | Failure handling is validated beyond happy path | fault-injection campaign | persisted traces + expected containment | NOT_VERIFIED | Must cover provider, auth, TRACTIAN, DB/realtime failure classes. |
| C39 | Product value is quantitatively demonstrated | manual-vs-agent-assisted paired study | human task outcome data | NOT_VERIFIED | Instrumentation exists; human study evidence is still required. |
| C40 | Final evidence bundle corresponds to exact final deployment | immutable manifest/hash | GitHub/Railway/DB evidence identities | NOT_VERIFIED | Final step after all promotable gates close. |

## Promotion rule

A final delivery may only make claims marked `VERIFIED`. A `FAILED` critical claim is a blocker until corrected and reverified. A `NOT_VERIFIED` item must remain visible as an explicit limitation or be completed before promotion if it is required by the promised delivery scope.

## Known immediate blockers

1. C04/C33 — structural evaluation was semantically over-presented as quality;
2. C05/C06/C07 — independent functional/evidence/progress assurance is incomplete;
3. C25/C26/C27/C28 — action-enabled production requires full lifecycle/security evidence;
4. C36 — required CI is not yet technically enforced by branch protection;
5. C34 — runtime/docs/capability truth is currently drifted;
6. C09/C11/C16/C17/C20/C21 — breadth/capacity/recovery proof remains incomplete.
