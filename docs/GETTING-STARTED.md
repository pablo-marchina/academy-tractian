# Getting Started — Hosted Product

**Audience:** first-time product user or reviewer  
**Goal:** understand and exercise the normal hosted industrial-agent product without internal runtime knowledge  
**Public product:** https://production-web-production-c9d1.up.railway.app  
**Current state:** [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md)

## Important current checkpoint

The product is live and multi-user, but the current OpenRouter V14 provider migration is still under functional acceptance. As of 2026-09-08, a real authenticated B204 campaign reaches the provider call but fails before the first TRACTIAN read because the provider completion ends with `finish_reason=length`.

This means the hosted UI/auth/history/system remain real, but a new live run may currently end in a safe provider failure rather than a successful industrial investigation. Do not interpret that safe failure as a successful functional result.

Governed consequential actions are no longer merely conceptual: the production transport architecture exists and a controlled 5/5 action smoke passed. However, final end-user/adversarial action acceptance remains open, so do not use Actions as if every live user/action scenario were fully certified.

## 1. Sign in

Open the public product and sign in/create an account. Tenant scope is server-owned. Browser headers, prompt text and model output cannot choose the canonical organization, permissions or action authority.

Invalid/expired sessions and temporary auth-service outages are distinct:

- invalid session → re-authentication;
- temporary managed-auth unavailability → retryable protected state.

## 2. Start on Home

Home asks the user what they want to understand. Use normal equipment language; do not provide internal `company_id`/`asset_id` values unless the workflow explicitly exposes a supported reason.

Examples:

```text
Which equipment needs attention today, and why?

Investigate B204 and explain its current condition using the available evidence.

Check the data quality for B204 and tell me whether the measurements are reliable enough for a maintenance decision.

Why is B204 vibrating more than usual? State the most likely mechanism only if the evidence supports it.
```

Human labels should resolve through authenticated identity → company → fleet discovery. Missing labels should fail closed rather than expand scope.

## 3. Understand live progress

Displayed progress is a safe runtime projection, not chain-of-thought.

A successful investigation may traverse:

```text
managed auth
→ provider decision
→ identity/fleet grounding
→ typed TRACTIAN analysis/RMS/spectrum/baseline/data-quality/knowledge reads
→ evidence
→ terminal + response_mode
→ post-runtime evaluation
```

Current V14 failure signature is different:

```text
managed auth          succeeds
run submission        succeeds
provider decision     fails closed
TRACTIAN tool calls   0
terminal reason       DECISION_SOURCE_FAILURE
```

A safe failure is preferable to accepting truncated model output, but it is not a completed investigation.

## 4. Read the result and evidence state

Two concepts remain distinct:

### Terminal outcome

The controller may answer/orient, clarify, abstain or escalate depending on the observed runtime state.

### `response_mode`

- **complete** — all material requested parts supported;
- **partial** — useful supported conclusion with a material incomplete/probabilistic part;
- **inconclusive** — inspected evidence cannot support a reliable directional answer;
- **conflict** — material evidence conflicts;
- **unavailable** — required authorized evidence could not be obtained.

A provider/runtime failure is not automatically one of these successful evidence modes; inspect Technical/Verification when the run did not reach the intended evidence path.

## 5. Navigate the product

### Home

Start a task and see current service/run state.

### Result / evidence detail

Shows the selected run's customer-safe conclusion/failure state, next step and contextual supporting evidence.

### Analyses

Browse persisted prior runs. Historical V13 successful runs may remain visible; they are valid historical evidence but must not be confused with proof that the current V14 provider path is green.

### Technical

Specialist depth includes, as available:

- **Current analysis** — trace/evidence/tools/policy;
- **Quality / Verification** — structural evaluation and independent claim state;
- **Data** — persisted quantitative views;
- **System** — health, architecture, provider/capability/release identity;
- **Actions** — governed proposal/confirmation/control state;
- **Studies** — controlled semantic/operational-value research.

Technical surfaces should distinguish `VERIFIED`, `FAILED`, `NOT_VERIFIED`, `NOT_REACHED` and similar scoped states rather than presenting one generic quality percentage.

## 6. Repeated tool calls

Repeated tool names are not automatically loops.

Valid example:

```text
get_rms(asset)
→ get_rms(asset, point_id=observed_point)
```

Current runtime hardening suppresses an **exact already-successful operation + normalized arguments/resource** from executing twice while preserving same-tool/different-argument drill-down.

## 7. Governed actions

Five canonical consequential actions exist under a server-owned governed path. The browser/model may propose, but cannot own permissions, resource/company authority, upstream TRACTIAN actor identity, credentials, confirmation fingerprints, idempotency or kill switch.

A real action requires:

```text
proposal
→ deterministic policy/resource validation
→ private custody
→ explicit opaque-ID confirmation
→ fresh server-owned authorization
→ idempotency + execution lease
→ server-owned TRACTIAN actor transport
→ persisted outcome/evaluation
```

The controlled transport smoke passed 5/5, but full hosted adversarial/end-user action acceptance is still pending. Treat that distinction explicitly.

## 8. Evidence discipline

- metadata/criticality may prioritize investigation but not prove a fault mechanism;
- baseline/data quality support context/trust but do not replace current-condition evidence;
- RMS supports magnitude/trend evidence without guaranteeing a precise cause;
- spectrum may support frequency-mechanism hypotheses but causal certainty must remain evidence-calibrated;
- comparison claims need evidence for every compared resource;
- missing resources fail closed;
- provider/model/dependency failures must remain visible rather than being converted into a confident answer.

## 9. What the product does not currently claim

Do not claim:

- current OpenRouter V14 functional acceptance while B204 is 0/3;
- that the current V14 B204 campaign reached TRACTIAN tools;
- final provider superiority;
- complete recent live coverage of all 13 reads;
- full governed-action SECURITY-V1/end-user readiness;
- distributed exactly-once external side effects;
- final production capacity/SLO/HA/RTO/RPO;
- human semantic calibration;
- measured human time savings;
- branch-protection enforcement while GitHub reports `main.protected=false`;
- superiority of LangGraph/multi-agent/RAG/etc. without a measured challenger win.

For exact current facts, always prefer [`ACTIVE-PROJECT-STATUS.md`](ACTIVE-PROJECT-STATUS.md) over historical Release 0/V13 documentation.