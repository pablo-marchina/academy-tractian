# Academy × TRACTIAN — Release 0 Acceptance

**Status:** PASS / PROMOTED  
**Backend/runtime SHA:** `082d6f115c070fdc898df749b4b3018efd9ceeab`  
**Workflow:** `hosted-production-release0-agent`  
**Run:** `34069562818`

Release 0 met the minimum Definition of Ready for real first-user access.

## Acceptance ledger

| Gate | Observed state |
|---|---|
| remote HTTPS frontend/API | **PASS** |
| Neon durable PostgreSQL | **PASS** |
| immutable backend release identity | **PASS — exact SHA** |
| managed browser auth | **PASS** |
| two-user/tenant negatives | **PASS — zero release-campaign disclosure** |
| real hosted provider | **PASS — provisional Cloudflare** |
| real typed TRACTIAN read | **PASS — remote 2xx observed** |
| provider → agent → TRACTIAN → evidence → terminal → evaluator | **PASS** |
| FINAL | **PASS** |
| CLARIFY | **PASS** |
| ABSTAIN | **PASS** |
| ESCALATE | **PASS** |
| evidence / lineage / persistence | **PASS** |
| authenticated REST/SSE | **PASS** |
| 18-operation capability contract | **PASS — 13 reads + 5 proposal-only actions** |
| external consequential action execution | **DISABLED / 0 calls** |
| USD0 / no paid spillover | **PASS Release 0 policy** |
| local/mock production dependency | **ZERO** |
| external two-user smoke | **PASS** |

## Proven hosted path

```text
real browser auth
→ server-owned tenant context
→ live Cloudflare model call
→ canonical typed TRACTIAN read
→ remote evidence
→ terminal mode
→ persisted output
→ deterministic post-runtime evaluation
→ safe lineage
→ Neon PostgreSQL
→ public authenticated REST/SSE
```

## Safety boundary

Release 0 does not authorize:

- browser-owned tenant/privilege authority;
- hidden model/route/paid fallback;
- raw provider/TRACTIAN/database/session secret projection;
- local/mock serving;
- hidden chain-of-thought exposure;
- consequential external action execution.

## UX acceptance: minimum versus current

The release gate proved the minimum user path: sign in, submit, watch live progress, receive safe terminal mode, inspect evidence/evaluation, reload history and remain tenant-isolated.

The **current hosted UX is stronger than the original minimum gate**. Baseline `2ca6215...` adds Results/Evidence/Investigation/Engineering progressive disclosure, onboarding, guided starts, mode-specific next steps and keyboard-accessible depth navigation, and passed the current Playwright/required regression surface before successful frontend deployment.

That later UX evolution does not alter the immutable backend Release 0 acceptance SHA.

## Non-claims

This acceptance does not prove final provider superiority, exhaustive semantic accuracy, full SECURITY-V1, final capacity/SLO/HA/RTO/RPO, consequential action readiness, human-calibrated judge readiness, operational time savings or adaptive-policy superiority.