# Documentation + UX Rebaseline — 2026-09-06 BRT

**Status:** historical progress record  
**Release 0 backend anchor:** `082d6f115c070fdc898df749b4b3018efd9ceeab`  
**UX implementation baseline before docs rebaseline:** `2ca6215ccc07664a9551e8363e438f0930a4d995`

## Why this record exists

After Release 0 promotion, product UX advanced substantially while several canonical documents still described the pre-promotion candidate topology. This created a reviewer/user risk: correct historical evidence existed, but active docs could send readers to stale conclusions.

A focused documentation best-practices research pass reviewed Diátaxis, GitHub Docs guidance, C4, ADR practice, OWASP threat modeling and Keep a Changelog. The applied research is recorded in `docs/research/2026-09-06-documentation-best-practices.md`.

## UX progress incorporated

Since the earlier customer-first UX cut, the branch advanced to a four-level progressive workspace:

```text
01 Results        answer & next step
02 Evidence       why this answer
03 Investigation  runtime & operations
04 Engineering    architecture & evals
```

The implementation also includes:

- default Results-first navigation;
- onboarding/read-only guardrails;
- server-owned guided intents with explicitly labelled local starter examples as fallback;
- human-readable runtime stages;
- mode-specific next-step guidance;
- evidence summary before technical trace;
- same persisted run context across layers;
- keyboard tab semantics;
- history selection returning to Results;
- full engineering surfaces preserved behind progressive disclosure.

## Validation

At UX baseline `2ca6215...`, the observed GitHub workflow set was green, including:

- `frontend-provider-free`;
- `full-product-playwright`;
- `clean-clone-full-product-reproduction`;
- `final-ci-required`;
- production-runtime;
- PostgreSQL operational;
- observability;
- EDD;
- Railway IaC;
- handoff regressions.

Railway then reported a `SUCCESS` frontend deployment for commit `2ca6215...`.

This does **not** change the promoted backend/runtime SHA. Frontend and backend release identities are documented separately.

## Documentation changes made

The active surface was restructured around reader tasks and updated to current truth:

- root README;
- documentation hub;
- Getting Started;
- Active Project Status;
- Delivery Plan;
- Architecture;
- final Delivery Acceptance;
- Release 0 plan/acceptance;
- Codebase Map;
- Production Runbook;
- TAPI crosswalk;
- Playwright acceptance;
- workflow lifecycle guide;
- contribution guide;
- compatibility redirects;
- Changelog;
- security reporting policy;
- active security/threat model;
- documentation governance/research record.

Frozen/status-pinned historical evidence, dated audits and accepted ADRs were intentionally left unchanged.

## Important decisions preserved

- `DP-004` / final Provider Tournament remains `NO_SELECTION`;
- Cloudflare GLM-4.7-Flash remains provisional for Release 0 only;
- external consequential actions remain disabled;
- USD0/no-paid-spillover remains a hard gate;
- controlled semantic-review and operational-value collectors are not reused as casual user feedback;
- the next UX data task is a separate lightweight run-feedback channel followed by first-time-user measurement.

## Result

The active documentation now describes the product that actually exists and is hosted, while historical evidence continues to describe exactly what was known at the time it was created.