# Changelog

Notable user-, operator- and reviewer-visible changes are recorded here. This is a curated product changelog, not a dump of Git commits.

## Unreleased

### Added

- Canonical provider-selection status at `docs/PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`.
- Append-only 2026-09-08 provider qualification/causal-debug chronology.
- Frozen Groq-only 85-attempt qualification runner/bootstrap.
- Causal provider-failure diagnostic covering completion budget and reasoning effort.
- Health-preserving diagnostic bootstrap for Railway one-shot research jobs.
- Sanitized benchmark-shaped Groq rate/admission diagnostic and pinned bootstrap.
- Release 0 V13 live-hardening documentation and production validation matrix.
- Explicit customer-visible `response_mode` contract: `complete`, `partial`, `inconclusive`, `conflict`, `unavailable`.
- Human-readable explicit-asset grounding for labels such as R310/R420 without requiring users to know internal resource IDs.
- Per-asset evidence requirements for comparative questions.
- Data-quality-specific evidence requirement before answering data-quality questions.
- Managed-session resilience semantics distinguishing invalid session (`401`) from temporary identity-service unavailability (`503`).
- Task-driven hosted UX organized around **Home / Analyses / Technical**.

### Changed

- Provider finalization is no longer documented as a merely pending 170-attempt paired tournament. Cloudflare GPT-OSS was quota-blocked in non-scored preflight and then explicitly removed from the requested path; Groq was evaluated as a single-provider qualification.
- Groq `openai/gpt-oss-120b` completed 85/85 under the frozen population/rubric and returned **`NO_SELECTION`**.
- Provider-development priority changed from broad provider search to causal diagnosis of structured-output/finish/reasoning failures, followed by canonical `strict:true` challengers only if justified.
- Hard provider gates remain unchanged; no retry/fallback/JSON repair was introduced to manufacture a pass.
- Architecture documentation now separates production serving from provider-research challenger paths.
- Backend/frontend production serving was not changed by the 2026-09-08 provider research.
- Diagnostic asset investigations require condition evidence from analysis/RMS/spectrum before a diagnostic terminal where applicable.
- Fleet discovery suppresses redundant post-fleet metadata reads.
- Repetition analysis distinguishes exact duplicates from legitimate asset→point drill-down.
- Documentation/presentation material now reflects the real task-driven hosted UI and current provider non-selection state while preserving frozen history.

### Provider qualification evidence

Groq-only final qualification:

```text
attempts           85/85
rubric pass        69/85 = 81.18%
reliability        70/85 = 82.35%
contract failures  9
repeat stability   11/17 = 64.71%
p50 latency        1.154 s
p95 latency        2.904 s
selection          NO_SELECTION
```

Observed failure families include upstream-unavailable, action-governance, analysis-detail, model, spectrum and knowledge-search scenarios. Unknown tools and invalid known-tool arguments were not the limiting class.

### Causal-debug evidence

- Increasing `max_completion_tokens` to 2048 does not by itself eliminate structural decision failures.
- `ANALYSIS_DETAIL` has produced HTTP 200 + `finish_reason=stop` + valid JSON but a root `ProviderDecisionPayload` relational validation error.
- `low` reasoning materially reduces sampled reasoning tokens/latency on simple decisions and is therefore a legitimate challenger variable, not yet a promoted choice.
- `strict:false` best-effort structured output is strongly implicated in application-invalid relational states.
- Future strict schemas must derive from canonical ToolSpecs/OpenAPI and retain application-side deterministic validation.
- Exact supplied `ActionRequest` recovery remains required before complete strict action variants.

### Experiment infrastructure

- Railway's current five-service resource envelope prevented provisioning a sixth dedicated provider-lab service.
- Overlapping deployments on `qa-live-prompt-matrix` contaminated partial causal matrices; those attempts were discarded rather than combined.
- Benchmark-shaped 2048-token Groq calls exposed 429 admission behavior not fully predicted by the earlier emitted-token pacing formula; a dedicated sanitized diagnostic was frozen before further long runs.
- A concurrent OpenRouter free-tier capacity probe reported 50 free-model requests/day, below the 85-call final population; this observed route is not an eligible drop-in final qualification path under the current tier.

### Fixed

- Repeated identity/fleet-discovery loops that exhausted tool-call budget.
- Premature terminal responses before condition evidence.
- Useful directional answers incorrectly labelled `inconclusive` where `partial` was appropriate.
- Requests for discoverable `asset_id`/`company_id`.
- Explicit-asset comparison paths that under-grounded requested resources.
- Repeated completed `get_data_quality` calls.
- Managed-session read-burst instability and frontend ghost-auth behavior.

### Security

- GET/HEAD managed-session validation uses a bounded server cache/singleflight while non-read requests validate fresh.
- Invalid session (`401`) and temporary managed-auth unavailability (`503`) remain distinct fail-closed states.
- Consequential external actions remain disabled.
- Provider experiments do not log/persist raw credentials, raw provider payloads or private benchmark truth in public evidence artifacts.

## Provider qualification / causal debugging — 2026-09-08

- V4 Cloudflare/Groq GPT-OSS protocol frozen over the existing 17×5 population.
- Cloudflare GPT-OSS preflight quota-blocked; no scored paired campaign followed.
- Groq default `urllib` transport signature was rejected by provider edge; explicit application `User-Agent` restored normal API access without changing scoring semantics.
- User explicitly requested proceeding without Cloudflare.
- Groq-only qualification completed 85/85 and returned `NO_SELECTION`.
- Causal investigation started rather than weakening hard gates.
- Partial 21-call matrices affected by overlapping Railway deployments/rate admission were rejected as complete causal evidence.
- Strict structured-output design direction was narrowed to canonical closed ToolSpec/OpenAPI variants.
- Current continuation is rate/admission characterization → clean 21/21 → exact `ActionRequest` → strict preflight → unchanged-rubric challenger comparison → winner-only 85/85 → Academy live E2E.

## Task-driven UX promotion — 2026-09-07

- Primary navigation rebuilt around Home / Analyses / Technical while preserving contextual result/evidence and engineering observability.
- Frontend promotion remains tracked independently from backend/provider promotion.

## Release 0 live hardening — 2026-09-07

- Grounded fleet discovery and customer-safe ID behavior.
- Structured nested asset/analysis ID extraction.
- Redundant metadata-loop suppression.
- Condition-evidence requirement before diagnostic terminal.
- Explicit response-mode semantics.
- Managed-session resilience.
- Explicit label/comparison and data-quality grounding.
- Initial explicit-asset identity grounding and completed quality-read suppression.

## PR #196 integrated into `main` — 2026-09-06

PR #196 remains historical repository-integration evidence. It did not freeze all later hosted component identities. Current state lives in `docs/ACTIVE-PROJECT-STATUS.md`.

## Release 0 UX pilot — 2026-09-06

The earlier Results / Evidence / Investigation / Engineering progressive-disclosure UX established first-user baseline context. It was superseded by task-driven Home / Analyses / Technical navigation without removing underlying evidence/runtime capabilities.

## Release 0 — 2026-09-06

### Added

- Real remotely hosted multi-user product path.
- Managed browser authentication and server-owned tenant context.
- Neon PostgreSQL durable state and tenant isolation.
- Provisional hosted Release 0 DecisionSource.
- Real canonical TRACTIAN reads behind the typed tool boundary.
- Safe terminal behavior, evidence, evaluation, persistence and authenticated REST/SSE.
- Browser-safe 18-operation contract covering 13 reads and 5 proposal-only actions.

### Security

- Consequential external actions disabled for Release 0.
- Browser cannot own tenant/role/permission authority.
- Cross-tenant negatives passed in Release 0 scope.
- No hidden automatic paid/provider fallback in the promoted path.
- No local/mock dependency in production serving.
