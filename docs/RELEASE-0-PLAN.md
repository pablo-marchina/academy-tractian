# Academy × TRACTIAN — Release 0 Plan

**Status:** COMPLETED / PROMOTED  
**Promoted backend/runtime SHA:** `082d6f115c070fdc898df749b4b3018efd9ceeab`  
**Hosted acceptance:** `hosted-production-release0-agent` run `34069562818`  
**Public product:** https://production-web-production-c9d1.up.railway.app

This document is now the concise completion record for the first-user Release 0 milestone. Active future work lives in [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md).

## Objective achieved

Release 0 proved that a real authenticated remote user can use a live hosted DecisionSource to investigate the supplied TRACTIAN API through the typed production boundary, persist safe evidence and evaluation, receive genuine live progress, and terminate safely as FINAL/CLARIFY/ABSTAIN/ESCALATE.

External consequential action execution remains disabled.

## Completed critical path

| Gate | Result |
|---|---|
| R0-00 rebaseline | **PASS** |
| R0-01 hosted IAM / two-user isolation | **PASS** |
| R0-02 bounded real TRACTIAN read | **PASS** |
| R0-03 provisional USD0 provider qualification | **PASS — provisional** |
| R0-04 production DecisionSource composition | **PASS** |
| R0-05 genuine agent → TRACTIAN → evidence E2E | **PASS** |
| R0-06 modes/evidence/minimum user UX | **PASS** |
| R0-07 external two-user smoke | **PASS** |
| release to users | **PROMOTED** |

## Promoted boundary

```text
authenticated remote user
→ Railway/Caddy frontend
→ managed auth + FastAPI
→ server-owned tenant context
→ provisional Cloudflare provider
→ AgentController / HarnessRunner
→ canonical typed TRACTIAN read
→ real remote evidence
→ FINAL | CLARIFY | ABSTAIN | ESCALATE
→ deterministic evaluation
→ Neon PostgreSQL
→ REST/SSE/history
```

## Provider decision boundary

Cloudflare `@cf/zai-org/glm-4.7-flash` is **provisional for Release 0 only**. The frozen final Provider Tournament v3 remains `NO_SELECTION` until its 170-attempt protocol runs.

## UX work that followed promotion

The post-release UX pilot has since implemented and hosted:

- onboarding and read-only guardrails;
- guided/starter investigation entry;
- human-readable progress;
- customer-first outcomes + mode-specific next steps;
- evidence summary;
- four-level progressive disclosure: Results → Evidence → Investigation → Engineering;
- keyboard-accessible tab navigation;
- full technical observability preserved in deeper layers.

UX implementation baseline `2ca6215...` passed current required CI/Playwright and deployed successfully to the Railway frontend.

The next UX task is separate lightweight run feedback followed by first-time-user measurement. Controlled semantic-review/operational-value collectors remain scientifically isolated.

## Release 0 non-claims

Release 0 does not prove final provider superiority, full SECURITY-V1, final capacity/SLO/HA/RTO/RPO, consequential action readiness, human semantic calibration, operational time savings or adaptive-policy superiority.