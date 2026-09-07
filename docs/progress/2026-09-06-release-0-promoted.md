# Release 0 promoted — 2026-09-06 BRT

## Decision

Release 0 is **PROMOTED** for first-user access as the smallest safe real read-only product slice.

Promoted runtime SHA:

`082d6f115c070fdc898df749b4b3018efd9ceeab`

Public product:

`https://production-web-production-c9d1.up.railway.app`

## Evidence

The promoted SHA passed the same-candidate hosted and reproducible gates, including:

- `hosted-production-release0-agent` run `34069562818`;
- `hosted-production-g2-smoke`;
- `final-ci-required`;
- `clean-clone-full-product-reproduction`;
- `full-product-playwright`;
- `production-runtime`;
- `postgres-production-operational`;
- `horizontal-runtime-handoff`;
- `observability-api-provider-free`;
- `frontend-provider-free`;
- `cloudflare-provider-client-provider-free`;
- `eval-driven-development-provider-free`;
- `railway-iac-contract`;
- final delivery/handoff regression gates.

The hosted Release 0 acceptance proved:

```text
managed auth
→ server-owned tenant context
→ live Cloudflare provider
→ canonical typed TRACTIAN read
→ real remote 2xx evidence
→ safe terminal result
→ deterministic evaluation
→ lineage/persistence
→ authenticated REST/SSE
```

It also proved:

- FINAL path;
- CLARIFY path;
- ABSTAIN path;
- ESCALATE path;
- two-user isolation;
- browser-forged authority rejected/ignored;
- 18-operation capability surface = 13 reads + 5 actions;
- external action calls = 0;
- paid fallback disabled;
- raw secrets not projected.

## Provider state

Cloudflare `@cf/zai-org/glm-4.7-flash` is the **provisional Release 0 provider** only.

The frozen final provider decision is deliberately unchanged:

`DP-004 = NO_SELECTION`

Provider Tournament v3 remains preregistered for 17 scenarios × 5 repetitions × 2 candidates = 170 attempts. This progress record must not be interpreted as a final-provider superiority claim.

## Action boundary

All five consequential action capabilities remain visible for contract/policy/product transparency but external execution stays disabled. Release 0 is a read-only user-serving release.

## Non-claims

Promotion does not claim:

- exhaustive semantic correctness;
- final provider superiority;
- full SECURITY-V1 completion;
- governed action readiness;
- measured final capacity/SLO/HA/RTO/RPO;
- human-calibrated semantic evaluation;
- measured operational-value improvement.

## Phase transition

The project now moves from **release-blocker elimination** to **UX pilot + real-user feedback**.

Priority:

```text
first-run clarity
→ guided investigation entry
→ readable live progress
→ customer-first result/evidence
→ actionable safe terminal modes
→ lightweight feedback/telemetry
→ iterate from observed user friction and correctness gaps
```

The promoted runtime SHA remains the evidence anchor until a later candidate independently clears the applicable promotion gates.
