# ADR-011 — Governed live provider execution wrapper — 2026-08-28

**Status:** ACCEPTED  
**Decision state:** `FROZEN_FOR_GOVERNED_LIVE_EXECUTION_WRAPPER`  
**Issue:** #41  
**PR:** #42  
**Scientific state changed:** NO  
**Production provider/model selected:** NO  
**Production mutating actions enabled:** NO  
**Live provider/model calls consumed by this decision task:** 0

## Decision question

Can the bounded ADR-009 live comparison be wrapped operationally without modifying the frozen ADR-010 executor, while preventing credential probing, secret persistence, hidden call-budget reset, automatic replay after crashes and raw provider-material leakage?

## Context

ADR-010 froze the exact 32-attempt comparison executor and validated it provider-free. The executor intentionally owns comparison geometry, M1–M10, hard gates and deterministic `NO_SELECTION`; it does not own execution secrets or durable process-level recovery semantics.

A real network task adds one operational risk not solved by the in-memory `LiveCallBudget`: a process can terminate after a provider invocation has become possible but before the returned attempt is durably recorded. Restarting from an empty in-memory executor would then risk silently replaying an already-consumed index.

Issue #41 therefore implements only the execution wrapper required around ADR-010. It does not execute the live comparison.

## Decision

Accept `src/academy_tractian/provider_live_execution.py` as the governed operational boundary for a future separately authorized invocation of the exact ADR-009/010 comparison.

Provider-free validated identity:

```text
validated pre-freeze head                  82a0211dbded683b62859d3b621af3e3361f4d3b
provider_live_execution.py blob            e2e2f2c7350efc0ab67490027347d76a6da54914
test_provider_live_execution.py blob       769c319a7de6a62b83a94a378c05d6d0a1518569
canonical ADR-010 plan SHA-256             69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f
production-runtime run                     33147359747 / #33 / success
production tests                           140 passed
ADR-004 controller regression              12 passed
triggered workflows                        11 / 11 success
live provider calls consumed               0
credential/account probes                  0
```

Machine-readable freeze:

`research/frozen/provider-live-execution-wrapper-freeze-v1.json`

## Preserved frozen boundaries

ADR-011 does not alter:

- ADR-008 candidates, population, metrics, thresholds or selection rule;
- ADR-009 exact provider classes/routes or maximum 32-call envelope;
- ADR-010 executor implementation or plan geometry;
- ADR-004 controller ownership;
- ADR-005 action-safety ownership;
- ADR-006 strict provider-neutral parsing;
- ADR-007 sanitized model-call provenance;
- the scientific `REQUIRED_PER_GROUP_AND_SLICE_REPORTING` gate.

No production mutating action is enabled and the wrapper never executes a TRACTIAN tool.

## Secret boundary

The wrapper receives two explicit execution-owned values:

- OpenAI API key;
- Google API key.

It performs only local non-empty presence validation. It does not:

- read provider credentials inside `provider_clients.py`;
- send a capability/account probe;
- serialize a secret into the run ledger or result;
- include a secret in object repr output;
- log raw provider headers or exception bodies.

If either value is absent, preparation stops before a run directory or attempt is created and before any provider client invocation.

## Run-directory and budget-custody rule

Each future live execution must use a fresh exclusive run directory.

Preparation creates a canonical 32-entry sanitized ledger containing only frozen attempt identity and frozen input hashes. If the directory already exists, the wrapper refuses to resume or reset it.

This is intentional. ADR-010 has no approved state-rehydration API, so reconstructing an executor around partially consumed live evidence would create a new semantic path. Until a prospective recovery protocol exists, fail-closed non-resume is safer than replay.

## Write-ahead attempt rule

For every planned live index:

```text
canonical pending attempt
→ persist state = CLAIMED
→ fsync ledger contents
→ call ProviderComparisonExecutor.execute_next()
→ persist sanitized completed attempt
```

Therefore a process failure after `CLAIMED` but before a completed attempt is available cannot be silently retried. The index becomes `uncertain`, the run stops and the sanitized wrapper result is `NO_SELECTION`.

A wrapper/internal exception is persisted only as a coarse stop code such as `EXECUTOR_INTERNAL_FAILURE`; raw exception text is discarded.

Operational provider/client/parsing failures that the unchanged ADR-010 executor converts into a normal `ProviderComparisonAttempt` remain completed evidence and remain in frozen denominators as designed.

## Fixed M5 failure probes

Before any live-capable attempt, ADR-011 runs the preregistered fixed provider-client failure probe for both concrete ADR-009 clients using an injected local transport that always fails.

This path:

- makes zero network calls;
- exercises each exact provider client class;
- requires one sanitized ADR-007 failure record;
- requires `CLIENT_FAILURE` containment;
- requires one invocation, zero retries and zero fallback;
- requires no raw request/response/exception persistence.

If either probe fails, the wrapper stops before attempt 0 and emits `NO_SELECTION`.

## Live client construction

Only the exact classes already frozen by ADR-009 are eligible:

```text
OpenAIResponsesDecisionClient
GoogleInteractionsDecisionClient
```

They retain the frozen model/route identities. The wrapper supplies one stdlib `UrllibProviderJsonTransport` and explicit secrets after all provider-free preflight checks pass.

Any different class, route, model or hidden retry/fallback remains outside this freeze and requires prospective governance.

## Result custody

The mutable run ledger contains only sanitized attempt evidence. A final `result.json` is created once with exclusive-create semantics.

The wrapper result records:

- frozen plan identity;
- run completion/stopped state;
- completed attempt count;
- consumed-or-uncertain count;
- sanitized stop code when applicable;
- deterministic candidate ID or `NO_SELECTION` from ADR-010 when available;
- sanitized ADR-010 result only after executor finalization.

It fixes:

```text
production_selection_claim       false
raw_provider_material_recorded   false
```

A candidate ID in a future complete live result is evidence for the subsequent provider-selection/status transition. ADR-011 itself does not select a production provider.

## Provider-free validation

PR #42 initially added only the wrapper and tests. The first validation head `82a0211dbded683b62859d3b621af3e3361f4d3b` produced:

```text
production-runtime #33       success
production tests             140 passed
ADR-004 regression            12 passed
all triggered workflows      11 / 11 success
live calls                     0
credential probes              0
```

The tests explicitly prove:

1. missing secrets fail before run-directory creation;
2. secret repr output is redacted;
3. preparation creates the exact 32-entry sanitized ledger without network access;
4. an existing run directory cannot be reused to reset budget state;
5. fixed client-failure probes are provider-free and pass for both exact client classes;
6. exact live clients can be constructed without invoking network transport;
7. `CLAIMED` is persisted before every executor invocation in the orchestration test;
8. an exception after claim becomes sanitized `uncertain` evidence and the run cannot be resumed.

## Rejected alternatives

### Put persistence inside ADR-010

Rejected because ADR-010 is already frozen and changing it would conflate experiment semantics with execution-process custody.

### Resume from a partially consumed ledger

Rejected for this version because ADR-010 exposes no governed rehydration API. Replaying or mutating private executor state would create an unvalidated execution path.

### Retry an uncertain attempt

Rejected because the provider may already have received the request. Automatic replay could exceed the frozen call budget and duplicate evidence.

### Probe credentials before execution

Rejected because ADR-009 explicitly forbids credential/account probing merely to determine availability. Presence is checked locally only.

## Authorization after this ADR

ADR-011 freezes **capability**, not execution.

After PR #42 merges and canonical status is reconciled, a later separately governed execution task may:

1. provision both required secrets explicitly;
2. create one fresh run directory;
3. invoke the exact ADR-011 wrapper once;
4. consume at most the remaining ADR-009 32-call envelope;
5. freeze the resulting candidate ID or `NO_SELECTION` evidence.

Until that separate task actually runs:

```text
ADR-009 calls consumed               0 / 32
production provider/model selected   NO
production actions enabled           NO
scientific provider calls            0
```

## Reversal triggers

A prospective amendment is required if any of the following becomes necessary:

- partial-run resume or executor-state rehydration;
- any retry of a claimed/uncertain attempt;
- a different secret/credential delivery topology;
- different live client classes/routes/models;
- parallel provider execution;
- changing the canonical plan or call budget;
- persisting additional provider material;
- enabling production mutating actions.
