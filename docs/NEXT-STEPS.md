# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE / FINAL SPRINT  
**Checkpoint:** 2026-09-02 — D01 complete; D02 provider-free ready; frontend visualization and test time promoted to P0  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Frontend execution:** GitHub issue #114  
**Final sprint:** GitHub issue #115  
**D02 live execution:** GitHub issue #117  
**Frontend source:** GitHub issue #118  
**UI acceptance matrix:** GitHub issue #119

This is the short-horizon execution plan. It does not authorize provider inference by itself.

## 1. Current priorities

Priority order is now:

```text
P0  frontend/demo visualization + integration + test window
P0  D02 live execution after the next eligible reset
P0  hard freeze + clean reproduction + final acceptance
P1  locate/version actual UI source and close UI state matrix
P2  anything not required to deliver or demonstrate the governed agent
```

Do not spend final-sprint capacity on LangGraph, multi-agent, RAG, persistent memory, MCP migration, adaptive routing or speculative observability infrastructure.

## 2. D01 is complete

Canonical D01 facts:

```text
attempts                  32 / 32 completed
cash cost                 USD 0.00
observed Neurons          2813.628464
selection                 NO_SELECTION
raw provider material     not persisted
CLIENT_FAILURE            24 / 24 at exactly 512 output tokens
```

This is strong evidence for a completion-budget diagnostic. It is not evidence for topology changes.

## 3. D02 is implementation-ready but current-window blocked

D02 changes only:

```text
completion cap          512 -> 1024
client diagnostics      sanitized failure_subtype added
```

Full-packet worst-case:

```text
9352.805376 Neurons
```

Modeled remaining capacity in the current 2026-09-02 UTC allocation after D01:

```text
7186.371536 Neurons
```

Therefore do not invoke the full D02 packet before the next reset.

Next reset:

```text
2026-09-03 00:00 UTC
2026-09-02 21:00 America/Sao_Paulo
```

After reset, execute #117 only if a fresh zero-use attestation is truthful. Evidence must be <=600 seconds old and the D02 receipt <=300 seconds old. Credentials are provisioned only after evidence/receipt validation. No retry/replay after a claimed or uncertain attempt.

## 4. NOW — use the pre-reset window for frontend work

The canonical repository audit did not find a versioned frontend application. First resolve #118: identify the actual UI source/artifact and either version it in the governed delivery path or document its exact external ownership. Do not create a second throwaway frontend without first locating the existing visualization.

Once identified, execute #114.

### 13:55–14:30 BRT — visual contract / inventory

- identify UI source and run command;
- list current screens/components;
- map actual runtime/evaluator fields to the UI;
- freeze the minimum visible state contract from #119;
- mark requested visual changes P0/P1/P2;
- defer P2.

### 14:30–16:30 — visual + integration implementation

- implement P0/P1 visualization changes;
- keep decision outputs connected to the real project runtime/demo boundary rather than invented frontend decisions;
- preserve action authorization/idempotency boundaries;
- do not expose evaluator-private truth or raw provider material.

### 16:30–18:00 — first exploratory frontend test pass

Exercise at least:

```text
success/orient
clarify missing context
abstain/unavailable evidence
escalation + structured handoff
policy/action blocked
loading
empty
error/provider/tool failure
long content / overflow
presentation viewport / responsive sanity
```

Record defects by severity.

### 18:00 — soft visual freeze

After 18:00 today:

- no cosmetic redesign;
- only P0/P1 correctness, usability, integration or demo-blocking fixes;
- rerun every affected state after a fix.

### 18:00–19:30 — integrated provider-free demo regression

- run the frontend against provider-free real runtime/evaluator traces;
- verify status/outcome/trace consistency;
- verify escalation handoff readability;
- verify no credentials, account ID, evaluator-private truth or forbidden raw material appears;
- preserve a usable fallback demo independent of live provider availability.

### 19:30–20:15 — P0/P1 fixes only

Close demo blockers and rerun targeted regression.

### 20:15–20:45 — D02 preflight

```text
sync exact main
prepare new private evidence path
prepare new private receipt path
prepare new custody root
ensure Cloudflare provider credentials are absent
ensure no background Workers AI consumer will use the account after reset
```

Do not capture evidence before the new UTC reset.

### 21:00+ — execute D02 once if freshly authorized

Sequence:

```text
fresh D02 zero-use evidence
→ fresh D02 receipt
→ only then provision token/account ID
→ governed D02 launcher
→ 32-attempt packet or hard governed stop
→ clear credentials
→ inspect custody/ledger/result
→ analyze D02 vs D01
```

If any attempt is `claimed`/`uncertain` or provider-call outcome is ambiguous, do not blind rerun.

## 5. 2026-09-03 — provider-state integration + frontend regression

Immediately after D02 analysis:

- apply the frozen Pareto/hard-gate rule;
- accept `NO_SELECTION` if no candidate qualifies;
- integrate only the bounded provider state needed by the final demo;
- do not redesign the UI around the provider result;
- rerun frontend success/clarify/abstain/escalate/failure states.

A second provider experiment is not automatically authorized just because D02 is inconclusive.

## 6. 2026-09-04 — dedicated frontend test day

This day is protected for testing rather than feature expansion.

Test:

- full end-to-end state matrix;
- loading/empty/error paths;
- layout/overflow/presentation viewport;
- status terminology and information hierarchy;
- failure communication;
- escalation handoff usability;
- runtime→UI consistency;
- sensitive/private field exclusion;
- demo repeatability.

P2 visual polish is deferred unless trivial, isolated and regression-safe.

## 7. 2026-09-05 — HARD VISUAL + FEATURE FREEZE

By end of 2026-09-05 freeze:

```text
layout
information hierarchy
copy/status terminology
runtime→UI mapping
feature set
provider-state presentation
```

After this point, changes require explicit P0/P1 delivery justification plus targeted regression.

## 8. 2026-09-06 — clean reproduction + acceptance

- clean checkout/install;
- full production/runtime tests;
- final-delivery reproduction;
- integrated demo from clean environment;
- frontend run/setup verification;
- documentation/status audit;
- close all P0s.

## 9. 2026-09-07 — rehearsal + contingency

- run the exact final demo flow;
- verify presentation-machine setup;
- verify provider-independent fallback demo;
- make P0 demo-blocking fixes only;
- rerun affected tests after every fix.

## 10. 2026-09-08 — delivery

No same-day feature development.

Run only a short smoke check and present the frozen/bounded evidence accurately.

## 11. Stop rules

Still forbidden:

- paid provider spillover;
- fabricated quota evidence;
- credential/account probing as a quota shortcut;
- provider calls outside the governed authorization/launcher;
- replay of claimed/uncertain attempts;
- D01 retroactive repair/rescore;
- C4 reconstruction or substitution;
- exposing credentials/evaluator-private/raw provider material in the UI;
- speculative architecture work;
- cosmetic redesign after hard visual freeze;
- forcing a provider selection when the evidence says `NO_SELECTION`.
