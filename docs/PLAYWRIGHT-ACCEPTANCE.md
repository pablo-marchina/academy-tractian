# Full-product Playwright Acceptance

**Status:** ACTIVE browser/product regression contract  
**Current hosted frontend:** `4364364266c6a88d4affd85cb3a734c774cd42c8` — deployed `SUCCESS`  
**Current hosted backend:** `5611687556b3d50c31f20fa85ede794f2500f05c` — OpenRouter V14 deployed, hosted functional gate currently failing

This gate validates **user tasks and deterministic safety/product invariants** with provider-free substitution so CI consumes no live provider quota. Provider-free Playwright is not evidence that the current OpenRouter V14 provider, TRACTIAN availability or hosted action path is functionally green.

## User-experience contract

A first-time browser session must be able to:

- start on **Home**;
- understand current product/capability state without internal IDs;
- enter/edit a normal equipment question;
- submit a protected run;
- see truthful human-readable progress/failure state;
- receive a customer-safe result/next step when the runtime succeeds;
- see explicit failure/`NOT_REACHED` state when a dependency fails before evidence;
- inspect contextual evidence;
- use **Analyses** for persisted history;
- use **Technical** for trace / Quality / Verification / Data / System / Actions / Studies;
- recover from invalid managed session;
- distinguish temporary managed-auth unavailability;
- reconcile session on focus/visibility return;
- remain usable on constrained/mobile viewports.

## Evidence / runtime contract

- persisted SSE events render in sequence without logical duplicates;
- reconnect/catch-up uses durable cursor semantics;
- evaluation is post-runtime;
- result/evidence derives from safe persisted truth;
- Technical exposes scoped trace/tool/policy/provider/release evidence;
- structural evaluation and independent functional verification are not collapsed into one generic quality score;
- terminal/failure UI is derived from persisted evidence, not fabricated progress;
- provider/tool/action states can render `FAILED`, `NOT_VERIFIED` or `NOT_REACHED` truthfully.

## Auth/session contract

- invalid protected-session signal clears authenticated product state;
- temporary `managed_session_unavailable` is a distinct retryable state;
- focus/visibility triggers reconciliation;
- browser never becomes tenant/role/permission/resource/action authority.

Backend tests own the exact bounded read-cache/singleflight/fresh-non-read implementation; Playwright owns user-visible state transitions.

## Safety / isolation contract

- CLARIFY/ABSTAIN/ESCALATE/unavailable/provider-failure outcomes stay visible;
- other user/organization contexts cannot read/stream/confirm protected state;
- forbidden private keys/material are absent from browser/API/SSE;
- action proposal and execution remain distinct;
- confirmation cannot submit canonical arguments/permissions/resource authority;
- duplicate confirmation is rejected in governed-action acceptance fixtures;
- `UNCERTAIN` action state is visible without automatic replay;
- action kill-switch/authorization state is server-owned.

Provider-free governed-action fixtures validate product mechanics only. The separate hosted controlled smoke currently proves 5/5 canonical action transports; full hosted action SECURITY-V1 remains independent.

## Agent/grounding/non-progress contract

Where deterministic fixtures permit, preserve regressions for:

- explicit human asset label → authorized discovery;
- no unnecessary request for discoverable internal IDs;
- condition evidence before diagnostic terminal where required;
- data-quality evidence for explicit quality requests;
- response-mode/message consistency;
- missing asset fail closed;
- exact successful operation + normalized arguments/resource does not execute twice;
- same-tool/different-argument progressive drill-down remains allowed.

Do not classify duplicate calls by tool name alone.

## Current hosted V14 counterexample

Browser/CI success is not hosted provider functional success. Current real B204 runs:

```text
run_437a59ba893a96e3f902
run_86c832ce46189200b613
run_f081d5d45b0cf4caf4b3
```

are functional failures because the first OpenRouter completion ends with `finish_reason=length`; no TRACTIAN tool is reached. Playwright must never be cited to override that hosted evidence.

## CI environment

Use PostgreSQL with scoped non-owner/non-superuser/non-BYPASSRLS role, Python 3.11, the repository's supported Node/npm lockfile and pinned Playwright browser tooling. Preserve reports/traces/screenshots/video/logs on failure. Acceptance applies only to the exact green SHA.

## Evidence boundaries

Keep separate:

```text
Playwright regression PASS
≠ OpenRouter V14 hosted functional PASS
≠ live 13-read coverage
≠ governed action transport smoke
≠ full action SECURITY-V1
≠ final production SLO/HA/recovery evidence
```

Final candidate requires both deterministic browser regression and separate exact-SHA hosted acceptance.