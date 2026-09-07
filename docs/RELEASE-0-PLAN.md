# Academy × TRACTIAN — Release 0 Immediate User Plan

**Status:** **COMPLETED / PROMOTED**  
**Promoted runtime SHA:** `082d6f115c070fdc898df749b4b3018efd9ceeab`  
**Public product:** https://production-web-production-c9d1.up.railway.app  
**Current phase:** post-release UX pilot and real-user feedback

## 1. Outcome

Release 0 achieved its objective: a real remotely hosted, authenticated, read-only industrial agent can use a live hosted DecisionSource, investigate through the supplied TRACTIAN API, persist evidence, stream progress, and return safe terminal outcomes.

Consequential external action execution remains disabled.

## 2. Promoted architecture

```text
authenticated remote user
→ public HTTPS React product
→ managed server-owned tenant context
→ FastAPI
→ provisional Cloudflare Release 0 provider
→ AgentController
→ HarnessRunner
→ canonical TRACTIAN read tool
→ real remote TRACTIAN evidence
→ FINAL | CLARIFY | ABSTAIN | ESCALATE
→ deterministic post-runtime evaluation
→ Neon PostgreSQL
→ authenticated REST/SSE + persisted history
```

## 3. Completed critical path

| Gate | State |
|---|---|
| R0-00 rebaseline | **PASS** |
| R0-01 minimum hosted IAM acceptance | **PASS** |
| R0-02 real TRACTIAN bounded-read acceptance | **PASS** |
| R0-03 provisional USD0 provider qualification | **PASS — provisional only** |
| R0-04 production DecisionSource composition | **PASS** |
| R0-05 genuine read-only agent vertical slice | **PASS** |
| R0-06 minimum mode/evidence/user UX acceptance | **PASS** |
| R0-07 external two-user smoke | **PASS** |
| Release to users | **PROMOTED** |

Hosted Release 0 acceptance run: `34069562818`.

## 4. Release constraints preserved

The promoted release maintains:

- actual project cash-cost policy USD0;
- no automatic paid fallback;
- no localhost/developer-machine/local-model dependency;
- managed browser authentication;
- server-owned tenant/role/permission authority;
- tested zero cross-tenant disclosure in the release campaign;
- explicit provider/model route;
- typed canonical TRACTIAN transport;
- safe evidence/terminal/evaluation persistence;
- no hidden chain-of-thought exposure;
- consequential action execution disabled.

## 5. Provider state

The Release 0 provider is **provisional**. It is not the final provider-selection decision.

The frozen Provider Tournament v3 remains unchanged and retains `NO_SELECTION` until its preregistered 170-attempt campaign is executed. Release 0 promotion must not be used as evidence of final provider superiority.

## 6. Current execution plan — UX pilot

The immediate goal is no longer to prove that the product can run. It is to make the product easy to understand and useful without developer guidance.

### UX-01 — First-run orientation

A new user should understand within the first screen:

- what the product does;
- that Release 0 is read-only;
- what type of question to ask;
- what evidence the agent can inspect;
- what FINAL / CLARIFY / ABSTAIN / ESCALATE mean.

### UX-02 — Guided investigation entry point

Guided intents should be promoted above the full technical capability registry. Presets remain backend-owned and should prepare, not bypass, the runtime.

### UX-03 — Human-readable progress

Translate safe runtime evidence into user-facing stages without exposing hidden reasoning:

```text
Preparing
→ AI deciding
→ Reading TRACTIAN
→ Reviewing evidence
→ Evaluating
→ Complete
```

### UX-04 — Customer-first result

The primary result surface should answer:

1. What is the conclusion?
2. How certain/complete is it?
3. What evidence supports it?
4. What should the user do next?

Engineering metadata remains accessible through progressive disclosure.

### UX-05 — Mode-specific recovery

- **CLARIFY:** show the missing information as a direct question and make continuation obvious.
- **ABSTAIN:** explain why the evidence is insufficient and what would unblock a conclusion.
- **ESCALATE:** explain why human review is needed and what context should be handed over.
- **FINAL:** foreground the conclusion and compact supporting evidence.

### UX-06 — Feedback and telemetry

Reuse the existing semantic-review / operational-value surfaces where possible before adding another persistence subsystem. Measure user friction and usefulness without collecting hidden chain-of-thought or sensitive raw payloads.

## 7. Post-UX work

After user-blocking UX/correctness issues:

1. full Provider Tournament v3;
2. full SECURITY-V1 campaign;
3. load/capacity/SLO evidence;
4. recovery/restore/RTO/RPO evidence;
5. governed consequential actions;
6. human semantic calibration;
7. operational-value study;
8. adaptive challengers only after measured gaps;
9. final evidence freeze and delivery bundle.

## 8. Scope control

Do not add optional orchestration or infrastructure layers merely because Release 0 is promoted. New architecture must answer a measured user/product gap under the same cost and safety constraints.

## 9. Documentation rule

The promoted runtime SHA remains the release evidence anchor even as documentation and UX development advance the branch. A later runtime is not promoted merely because it is newer; it must clear the applicable gates again.
