# Full-product Playwright Acceptance

**Status:** ACTIVE browser/product regression contract  
**Current UX baseline:** `2ca6215ccc07664a9551e8363e438f0930a4d995` — PASS

This gate validates **user tasks and safety invariants**, not a brittle screenshot/layout implementation. It runs the real product controller/tool/persistence/evaluation/SSE/frontend path with a deterministic provider-free dependency substitution so CI consumes no live provider quota.

## Executed test topology

```text
Chromium
→ React/Vite
→ REST/SSE
→ FastAPI
→ PostgreSQL operational/RLS state
→ production runtime/controller/HarnessRunner
→ typed ToolSpec + deterministic policy
→ bounded provider-free dependency substitute
→ RunTrace/evaluator
→ durable safe projection
→ React
```

Provider-free substitution is a CI dependency replacement, not a production claim. Production hosted acceptance separately proves real provider/IAM/TRACTIAN behavior.

## User-experience contract

A first-time browser session must be able to:

- start in **Results**;
- understand the Release 0 read-only product boundary;
- see Quick Start options even when server-owned Release 0 capability metadata is absent, with fallbacks explicitly labelled as examples;
- populate/edit a request;
- submit a run;
- see safe human-readable progress;
- receive a mode-specific terminal next step;
- move through **Results / Evidence / Investigation / Engineering**;
- navigate depth tabs by keyboard;
- select persisted history and return to Results-first interpretation;
- remain usable at constrained/mobile viewports without horizontal page overflow.

## Evidence / runtime contract

- genuine persisted SSE events render in sequence without logical duplicates;
- reconnect/catch-up uses durable cursor semantics;
- evaluation does not appear before runtime completion;
- Evidence shows canonical safe event/evidence context;
- Investigation exposes runtime metrics/history/Trace Graph/action state;
- Engineering exposes capability/architecture/evaluator/analytics surfaces;
- terminal UI is derived from persisted terminal evidence, not fabricated progress;
- long requests and empty states behave predictably.

## Safety / isolation contract

- CLARIFY, ABSTAIN, ESCALATE and failure/blocked-action outcomes are visible;
- proposal/confirmation action semantics remain separate;
- duplicate confirmation is rejected in the acceptance profile;
- other user/organization contexts cannot read/stream/confirm protected state;
- forbidden private keys are absent from browser/API/SSE projections;
- unsupported chart/data types remain constrained by server/browser contracts.

The provider-free action acceptance profile can exercise governed action machinery for regression purposes; that **does not mean external consequential actions are enabled in the hosted Release 0 product**.

## CI environment

The workflow uses PostgreSQL, a scoped non-owner/non-superuser/non-BYPASSRLS role, Python 3.11, Node 24, committed npm lockfile and pinned Playwright Chromium.

On failure, retain Playwright report/trace/screenshots/video and backend/frontend logs. A browser acceptance claim is valid only for the exact green SHA.

## Current evidence

At `2ca6215...`, `full-product-playwright` completed successfully alongside clean-clone and `final-ci-required`. The same frontend SHA later deployed successfully to Railway.

Do not use this provider-free gate as evidence of production provider latency/quality, hosted IAM reliability or TRACTIAN availability; those require hosted acceptance.