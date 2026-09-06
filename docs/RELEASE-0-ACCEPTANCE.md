# Academy × TRACTIAN — Release 0 Acceptance

**Status:** ACTIVE / immediate user-release Definition of Ready  
**Purpose:** define the minimum evidence required to safely expose the real read-only product to users before the final project evidence program is complete.

## Release decision

Release 0 is approved when every blocker below is PASS on the remotely hosted product path. Final-delivery gates not listed here remain post-release work and do not block first-user access.

| Gate | Required state |
|---|---|
| Remote frontend/API | PASS |
| Remote durable PostgreSQL | PASS |
| Immutable release identity | PASS |
| Managed browser authentication | PASS |
| Cross-tenant release negatives | PASS / zero disclosure |
| Real hosted provider | PASS / provisional qualification allowed |
| Real TRACTIAN read path | PASS |
| Real read-only agent vertical slice | PASS |
| FINAL / CLARIFY / ABSTAIN / ESCALATE basic behavior | PASS |
| Evidence + terminal output + persistence + SSE | PASS |
| Consequential action execution | DISABLED |
| USD0 actual cash cost | PASS |
| Paid spillover | IMPOSSIBLE |
| Local/mock production dependency | ZERO |
| External two-user smoke | PASS |

## Mandatory security boundaries

Any one of these blocks release:

- cross-tenant run/evidence/evaluation/SSE disclosure;
- browser-controlled tenant or privilege authority;
- exposed provider/TRACTIAN/database/session secrets;
- production action execution enabled before governed-action acceptance;
- local or mock serving dependency;
- paid route or automatic paid spillover;
- production provider/model route ambiguity or hidden fallback.

## Provider release qualification

A provider may be used provisionally for Release 0 before the full tournament only when:

- the route/model is explicitly configured and observed;
- actual cash cost remains USD 0;
- no paid fallback exists;
- no private benchmark/gold enters the model context;
- representative governed attempts show the strict DecisionSource contract can complete useful read-only cases;
- no unsafe external action execution or policy bypass occurs;
- provider failures degrade safely;
- the UI/telemetry labels the provider state as provisional until the full tournament is complete.

## TRACTIAN release qualification

At least one genuine remotely observed read path must prove the existing typed transport contract against the authoritative configured endpoint. The release smoke must exercise that real path. Configuration-only or source-only evidence is insufficient.

## User experience minimum

A first-time tester must be able to:

1. authenticate without developer assistance;
2. understand where to start an investigation;
3. submit a question;
4. see that work is progressing;
5. receive a useful terminal result or safe clarification/abstention/escalation;
6. inspect safe evidence supporting the result;
7. reload and recover the run;
8. understand failures without seeing secrets/internal chain-of-thought.

## External smoke evidence

The release evidence record must capture:

- exact source/deploy SHA;
- public product origin;
- provider/model/route identity;
- TRACTIAN transport state and one real read result summary;
- auth/tenant identities in sanitized form;
- run id + terminal mode;
- persistence/reload result;
- two-user isolation result;
- action execution state = disabled;
- observed cash cost = USD 0;
- confirmation that no localhost/mock/developer process participated.

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

These remain in the final delivery plan and are improved after real-user release.
