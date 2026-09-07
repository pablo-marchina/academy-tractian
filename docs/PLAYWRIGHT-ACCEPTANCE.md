# Full-product Playwright Acceptance

**Status:** ACTIVE browser/product regression contract  
**Current hosted UX:** `1bc124a8d4dbd029178ff8129b25452129445de7` — deployed SUCCESS

This gate validates **user tasks and safety invariants**, not a brittle screenshot/layout implementation. It runs the product controller/tool/persistence/evaluation/SSE/frontend path with deterministic provider-free substitution so CI consumes no live provider quota.

Provider-free substitution is a CI dependency replacement, not a production claim. Production hosted validation separately proves real provider/IAM/TRACTIAN behavior.

## User-experience contract — current task-driven UI

A first-time browser session must be able to:

- start on **Home**;
- understand the read-only product boundary without engineering knowledge;
- enter/edit a normal equipment question;
- submit a run;
- see safe human-readable progress;
- receive a customer-safe result/next step;
- inspect supporting evidence contextually;
- navigate to **Analyses** and select persisted history;
- navigate to **Technical** and access Current analysis / Quality / Data / System / Actions / Studies;
- recover cleanly from invalid managed session;
- distinguish temporary auth unavailability with retry UI;
- reconcile session on focus/visibility return;
- remain usable at constrained/mobile viewports without horizontal overflow.

The previous Results/Evidence/Investigation/Engineering global tabs are not the current primary navigation acceptance contract.

## Evidence / runtime contract

- genuine persisted SSE events render in sequence without logical duplicates;
- reconnect/catch-up uses durable cursor semantics;
- evaluation does not appear before runtime completion;
- result/evidence detail derives from persisted safe run events;
- Technical Current analysis exposes trace/tool/policy evidence;
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

## Safety / isolation contract

- CLARIFY/ABSTAIN/ESCALATE/unavailable/failure outcomes remain visible when applicable;
- action proposal/confirmation semantics remain separate;
- duplicate confirmation is rejected in acceptance profiles that exercise governed action machinery;
- other user/organization contexts cannot read/stream/confirm protected state;
- forbidden private keys are absent from browser/API/SSE projections.

Provider-free action acceptance can exercise dormant governed action machinery for regression; it does **not** mean external actions are enabled in hosted Release 0.

## Agent/grounding contract in browser regression

Where deterministic fixture data permits, preserve regressions for:

- human-readable explicit asset label → authorized discovery rather than internal-ID question;
- no redundant `get_asset` after fleet discovery;
- condition evidence required before relevant diagnostic terminal;
- data-quality requirement and no same-resource quality repetition after success;
- response-mode label/message consistency;
- missing asset fails closed.

Do not encode brittle assumptions that every same-name RMS/spectrum call is redundant; point-specific drill-down can be valid.

## CI environment

Workflow uses PostgreSQL, scoped non-owner/non-superuser/non-BYPASSRLS role, Python 3.11, Node 24, committed npm lockfile and pinned Playwright Chromium.

On failure retain Playwright report/trace/screenshots/video and backend/frontend logs. Browser acceptance is valid only for the exact green SHA.

## Evidence boundaries

PR #209/current task-driven frontend passed the required frontend/browser regression surface before Railway deployment. PR #210/current V13 backend separately passed its required backend/full-product regression surface before backend promotion.

Do not use provider-free Playwright as evidence of production provider latency/quality, hosted IAM availability SLO or TRACTIAN availability.