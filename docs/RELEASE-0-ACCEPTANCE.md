# Academy × TRACTIAN — Release 0 Acceptance

**Status:** **PASS / RELEASE 0 PROMOTED**  
**Promoted runtime SHA:** `082d6f115c070fdc898df749b4b3018efd9ceeab`  
**Hosted acceptance workflow:** `hosted-production-release0-agent`  
**Workflow run:** `34069562818`

## Release decision

Release 0 satisfied the minimum Definition of Ready for first-user access on the remotely hosted product path.

| Gate | Required state | Observed state |
|---|---|---|
| Remote frontend/API | PASS | **PASS** |
| Remote durable PostgreSQL | PASS | **PASS** |
| Immutable release identity | PASS | **PASS — exact promoted SHA** |
| Managed browser authentication | PASS | **PASS** |
| Cross-tenant release negatives | zero disclosure | **PASS** |
| Real hosted provider | provisional allowed | **PASS — provisional Cloudflare** |
| Real TRACTIAN read path | PASS | **PASS — remote typed read observed** |
| Real read-only agent vertical slice | PASS | **PASS** |
| FINAL basic behavior | PASS | **PASS** |
| CLARIFY basic behavior | PASS | **PASS** |
| ABSTAIN basic behavior | PASS | **PASS** |
| ESCALATE basic behavior | PASS | **PASS** |
| Evidence + terminal + persistence | PASS | **PASS** |
| Authenticated SSE/live path | PASS | **PASS** |
| Consequential action execution | DISABLED | **DISABLED / 0 external calls** |
| USD0 cash-cost policy | PASS | **PASS** |
| Paid spillover | IMPOSSIBLE | **disabled** |
| Local/mock production dependency | ZERO | **ZERO** |
| External two-user smoke | PASS | **PASS** |

## Hosted vertical-slice evidence

The promoted path proved:

```text
real browser auth
→ server-owned tenant context
→ real Cloudflare model call
→ canonical typed TRACTIAN read
→ remote HTTP 2xx evidence
→ hosted model terminal decision
→ persisted terminal output
→ deterministic post-runtime evaluation
→ output lineage
→ Neon PostgreSQL
→ authenticated public REST/SSE
```

The same acceptance also proved second-user isolation, browser-forged authority rejection, and zero external action calls.

## Provider qualification boundary

Cloudflare `@cf/zai-org/glm-4.7-flash` is authorized only as the **provisional Release 0 provider** under the release constraints.

This acceptance does **not** change the frozen full Provider Tournament v3 decision. `DP-004` remains `NO_SELECTION` until the preregistered final campaign is executed.

## Security boundaries retained

Release 0 remains blocked from consequential external actions. The promotion does not authorize:

- browser-controlled tenant or privilege authority;
- hidden or paid provider fallback;
- raw provider/TRACTIAN/database/session secret projection;
- local/mock production serving;
- chain-of-thought exposure;
- action execution without the later governed-action gate.

## User-experience acceptance achieved

A tester can now:

1. create/sign into a managed account;
2. submit an industrial request;
3. observe live run progress;
4. receive FINAL, CLARIFY, ABSTAIN or ESCALATE safely;
5. inspect safe evidence and lineage;
6. inspect deterministic evaluation;
7. reload persisted runs;
8. use a second account without cross-tenant state disclosure.

This is the **minimum** product UX acceptance, not the endpoint for product quality. Post-release UX work now focuses on reducing cognitive load, improving onboarding, summarizing evidence, clarifying next actions and collecting lightweight usefulness feedback.

## Post-release non-claims

Release 0 does not by itself authorize claims of:

- final provider superiority;
- exhaustive semantic accuracy;
- full SECURITY-V1 completion;
- measured production capacity/SLO/HA/RTO/RPO;
- governed consequential action readiness;
- human-calibrated semantic judge readiness;
- operational time savings;
- adaptive-policy superiority.

These remain post-release/final-delivery work.
