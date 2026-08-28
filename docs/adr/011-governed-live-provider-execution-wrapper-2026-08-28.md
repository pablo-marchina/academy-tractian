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

A real network task adds two custody risks not solved by the in-memory `LiveCallBudget` alone:

1. a process can terminate after a provider invocation has become possible but before the returned attempt is durably recorded; and
2. after such a failure, an operator could otherwise construct a new wrapper with a different run directory and recreate an empty in-memory budget.

Issue #41 therefore implements both the lower-level write-ahead execution wrapper and an authorization-level governed entrypoint. It does not execute the live comparison.

## Decision

Accept the following two-layer production execution boundary for a future separately authorized invocation of the exact ADR-009/010 comparison:

```text
GovernedProviderLiveTask                 provider_live_task.py
        ↓ one durable ADR-009 custody marker
fixed <custody_root>/run
        ↓
GovernedLiveProviderComparison           provider_live_execution.py
        ↓ write-ahead attempt ledger
ProviderComparisonExecutor               frozen ADR-010
```

Direct live use of the lower-level wrapper is **not** the governed ADR-011 entrypoint. The separately governed execution task must enter through `GovernedProviderLiveTask` with one canonical durable custody root.

Provider-free frozen identities:

```text
initial wrapper validation head          82a0211dbded683b62859d3b621af3e3361f4d3b
provider_live_execution.py blob          e2e2f2c7350efc0ab67490027347d76a6da54914
test_provider_live_execution.py blob     769c319a7de6a62b83a94a378c05d6d0a1518569

authorization-custody validation head    4d6269b391eb6220d6a26b714d1c011849999e14
provider_live_task.py blob               6e86f008b5136c88cab574f64564709e1029a945
test_provider_live_task.py blob          cd232b6adf6fc4171e7596e0e7a3ecf1887e76cd

canonical ADR-010 plan SHA-256           69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f
production-runtime run                   33147651777 / #38 / success
production tests                         146 passed
ADR-004 controller regression            12 passed
triggered workflows                      11 / 11 success
live provider calls consumed             0
credential/account probes                0
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

No production mutating action is enabled and neither ADR-011 layer executes a TRACTIAN tool.

## Secret boundary

The governed task receives two explicit execution-owned values:

- OpenAI API key;
- Google API key.

It performs only local non-empty presence validation. It does not:

- read provider credentials inside `provider_clients.py`;
- send a capability/account probe;
- serialize a secret into custody, ledger or result artifacts;
- include a secret in object repr output;
- log raw provider headers or exception bodies.

If either value is absent, preparation stops before the authorization custody root/marker, run directory or attempt is created and before any provider client invocation.

## Authorization-level custody rule

A future live task must provision **one canonical durable custody root** for the ADR-009 authorization. `GovernedProviderLiveTask.prepare(...)` creates, with exclusive-create semantics:

`<custody_root>/adr-009-live-comparison-custody.json`

The sanitized marker pins:

- the exact ADR-009 authorization blob;
- the exact ADR-010 plan SHA;
- the governed task/wrapper versions;
- the fixed internal run directory name `run`;
- zero calls consumed at reservation;
- explicit false values for credential/raw-provider-material recording.

After reservation, the caller cannot choose a different run directory: the lower-level wrapper is fixed at `<custody_root>/run`.

If the custody marker already exists, a second governed run in that root is refused before any provider call. If preparation fails after the marker was durably reserved, the marker is intentionally retained and blocks automatic retry/reset.

A different custody root is a **different external custody decision**, not an implicit reset mechanism. ADR-011 does not authorize switching roots after a failure. The future live execution task must name and preserve its canonical root as part of execution evidence.

This additional layer closes the normal restart loophole where a new run-directory argument could otherwise recreate an empty in-memory budget.

## Run-directory and attempt-ledger rule

Inside the reserved authorization root, the lower wrapper creates the single fixed `run/` directory and a canonical 32-entry sanitized attempt ledger containing frozen attempt identity and frozen input hashes.

The run directory is exclusive. ADR-010 has no approved state-rehydration API, so reconstructing an executor around partially consumed live evidence remains forbidden in this version.

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

Operational provider/client/parsing failures that the unchanged ADR-010 executor converts into a normal `ProviderComparisonAttempt` remain completed evidence and stay in frozen denominators as designed.

## Fixed M5 failure probes

Before any live-capable attempt, ADR-011 runs the preregistered fixed provider-client failure probe for both concrete ADR-009 clients using an injected local transport that always fails.

This path:

- makes zero network calls;
- exercises each exact provider client class;
- requires one sanitized ADR-007 failure record;
- requires `CLIENT_FAILURE` containment;
- requires one invocation, zero retries and zero fallback;
- requires no raw request/response/exception persistence.

If either probe fails, execution stops before attempt 0 and emits `NO_SELECTION`.

## Live client construction

Only the exact classes already frozen by ADR-009 are eligible:

```text
OpenAIResponsesDecisionClient
GoogleInteractionsDecisionClient
```

They retain the frozen model/route identities. The lower wrapper supplies one stdlib `UrllibProviderJsonTransport` and explicit secrets after all provider-free preflight checks pass.

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

### Initial lower-wrapper validation

Head `82a0211dbded683b62859d3b621af3e3361f4d3b` proved:

```text
production-runtime #33       success
production tests             140 passed
ADR-004 regression            12 passed
all triggered workflows      11 / 11 success
live calls                     0
credential probes              0
```

Those tests proved missing-secret fail-before-run, secret redaction, exact 32-entry sanitized ledger creation, same-run restart refusal, provider-free fixed failure probes, exact live-client construction without network, write-ahead `CLAIMED` ordering and crash-after-claim sanitization.

### Authorization-custody hardening

Review identified that same-run-directory refusal alone did not prevent a restart from selecting another directory and obtaining a fresh in-memory budget. The governed entrypoint was therefore added before merge rather than weakening the claim.

Head `4d6269b391eb6220d6a26b714d1c011849999e14` proved:

```text
production-runtime #38       success
production tests             146 passed
ADR-004 regression            12 passed
all triggered workflows      11 / 11 success
live calls                     0
credential probes              0
```

The added custody tests prove:

1. missing secrets fail before authorization custody exists;
2. the ADR-009 marker is sanitized and pins the canonical fixed `run/` location;
3. a second governed run in the same custody root is refused;
4. the caller cannot choose an alternate run directory through the governed task;
5. a failure after authorization reservation preserves the marker and fails closed.

## Rejected alternatives

### Put persistence inside ADR-010

Rejected because ADR-010 is already frozen and changing it would conflate experiment semantics with execution-process custody.

### Resume from a partially consumed ledger

Rejected because ADR-010 exposes no governed rehydration API. Replaying or mutating private executor state would create an unvalidated execution path.

### Retry an uncertain attempt

Rejected because the provider may already have received the request. Automatic replay could exceed the frozen call budget and duplicate evidence.

### Allow caller-selected run directories as the authorization boundary

Rejected after review because a restart could select a different directory and recreate an empty in-memory budget. Run-directory selection is now hidden behind one authorization-level custody root.

### Probe credentials before execution

Rejected because ADR-009 explicitly forbids credential/account probing merely to determine availability. Presence is checked locally only.

## Authorization after this ADR

ADR-011 freezes **capability**, not execution.

After PR #42 merges and canonical status is reconciled, a later separately governed execution task may:

1. provision one canonical durable custody root;
2. provision both required secrets explicitly;
3. invoke `GovernedProviderLiveTask` exactly once through that root;
4. consume at most the remaining ADR-009 32-call envelope;
5. preserve the custody marker, attempt ledger and sanitized result as execution evidence;
6. freeze the resulting candidate ID or `NO_SELECTION` evidence.

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
- switching to a different custody root after reservation/failure;
- a different secret/credential delivery topology;
- different live client classes/routes/models;
- parallel provider execution;
- changing the canonical plan or call budget;
- persisting additional provider material;
- enabling production mutating actions.
