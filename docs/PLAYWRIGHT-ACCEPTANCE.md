# Full-product Playwright Acceptance

**Status:** ACTIVE browser/product regression contract  
**Current hosted UX:** `1bc124a8d4dbd029178ff8129b25452129445de7` — deployed SUCCESS  
**Current smoke-capable backend source:** `3545d75c00ca30419e0f47e8b1950aa50cbbf462`

This gate validates **user tasks and safety invariants**, not a brittle screenshot/layout implementation. It runs the product controller/tool/persistence/evaluation/SSE/frontend path with deterministic provider-free substitution so CI consumes no live provider quota.

Provider-free substitution is a CI dependency replacement, not a production claim. Hosted production validation separately proves real provider/IAM/TRACTIAN behavior, including vendor action acceptance.

## User-experience contract — current task-driven UI

A first-time browser session must be able to:

- start on **Home**;
- understand the product without engineering knowledge;
- enter/edit a normal equipment question;
- submit a run;
- see safe human-readable progress;
- receive a customer-safe result/next step;
- inspect supporting evidence contextually;
- navigate to **Analyses** and select persisted history;
- navigate to **Technical** and access specialist analysis / Quality / Data / System / Actions / Studies;
- recover cleanly from invalid managed session;
- distinguish temporary auth unavailability with retry UI;
- reconcile session on focus/visibility return;
- remain usable at constrained/mobile viewports without horizontal overflow.

The previous Results/Evidence/Investigation/Engineering global tabs are not the current primary navigation acceptance contract.

### UX simplification regression principle

The next structural simplification should preserve behavior while reducing default density. Browser tests should prefer task assertions such as:

```text
where am I?
what happened?
what should I do now?
can I open evidence/technical detail when needed?
```

Do not encode card counts, decorative containers or exact visual hierarchy unless they are themselves an accessibility/usability requirement.

Automated acceptance does not prove representative-human usability.

## Evidence / runtime contract

- genuine persisted SSE events render in sequence without logical duplicates;
- reconnect/catch-up uses durable cursor semantics;
- evaluation does not appear before runtime completion;
- result/evidence detail derives from persisted safe run events;
- Technical analysis exposes trace/tool/policy evidence;
- Technical Quality exposes post-runtime evaluation;
- Technical System exposes architecture/capability/health evidence;
- terminal UI is derived from persisted terminal evidence, not fabricated progress;
- long requests and empty states behave predictably.

## Auth/session contract

Browser acceptance should cover the #207 semantics at the UI boundary:

- protected API invalid-session signal clears authenticated product state;
- temporary `managed_session_unavailable` enters a distinct retryable unavailable state;
- unavailable state does not invite credential entry until session service is retryable;
- focus/visibility triggers session reconciliation;
- frontend never becomes tenant/role/permission authority.

Backend unit/integration tests own the exact 2-second cache/singleflight/fresh-non-read behavior; Playwright owns the user-visible browser state transitions.

## Governed action UI/safety contract

Provider-free acceptance can exercise the deterministic governed-action machinery without claiming a real vendor side effect.

The browser must preserve:

- proposal and execution are visibly distinct;
- exact confirmation is required for an existing action;
- confirmation payload cannot replace action arguments, permissions, resource authority, idempotency material or vendor actor identity;
- consequence/impact appears before the primary confirmation control;
- duplicate confirmation is rejected;
- cross-user/organization action access/confirmation is denied;
- `PENDING_CONFIRMATION`, `EXECUTING`, `ACCEPTED`, `BLOCKED`, `NOT_ACCEPTED` and `UNCERTAIN` states are not collapsed into generic success/failure;
- only canonical backend `ACCEPTED` is rendered as external acceptance;
- `UNCERTAIN` never becomes a blind retry CTA;
- raw grants, private custody, idempotency keys and vendor actor mappings are absent from browser/API/SSE projections.

Current hosted production has the governed action path enabled, but the live five-action vendor smoke has not yet passed 5/5. Playwright passing must **not** be described as proof that TRACTIAN accepted every action.

## Agent/grounding contract in browser regression

Where deterministic fixture data permits, preserve regressions for:

- human-readable explicit asset label → authorized discovery rather than internal-ID question;
- no redundant `get_asset` after fleet discovery;
- condition evidence required before relevant diagnostic terminal;
- data-quality requirement and no same-resource quality repetition after success;
- response-mode label/message consistency;
- missing asset fails closed.

Do not encode brittle assumptions that every same-name RMS/spectrum call is redundant; point-specific drill-down can be valid.

## Safety / isolation contract

- CLARIFY/ABSTAIN/ESCALATE/unavailable/failure outcomes remain visible when applicable;
- other user/organization contexts cannot read/stream/confirm protected state;
- forbidden private keys are absent from browser/API/SSE projections;
- browser/model cannot become upstream action actor authority;
- failed/not-accepted action is not reworded as accepted.

## CI environment

Workflow uses PostgreSQL, scoped non-owner/non-superuser/non-BYPASSRLS role, Python 3.11, Node 24, committed npm lockfile and pinned Playwright Chromium.

On failure retain Playwright report/trace/screenshots/video and backend/frontend logs. Browser acceptance is valid only for the exact green SHA.

## Current evidence boundaries

PR #209/current task-driven frontend passed the required frontend/browser surface before Railway deployment.

PR #213 required-gate workflow run `34164123263` passed the smoke-capable source, including `chromium-full-product`, clean-clone reproduction, production runtime, action lease/fencing and horizontal runtime contracts.

A separate hosted action smoke then failed safely on `update_asset_config` HTTP 403 / `accepted=false`. That live result takes precedence over provider-free CI for the vendor-acceptance claim.

Do not use provider-free Playwright as evidence of production provider latency/quality, hosted IAM availability SLO, TRACTIAN availability or five-action upstream acceptance.

See [`progress/2026-09-07-production-governed-actions-ux-and-validation.md`](progress/2026-09-07-production-governed-actions-ux-and-validation.md).