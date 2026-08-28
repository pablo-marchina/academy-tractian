# 027 — Governed live provider wrapper — FROZEN / PROVIDER-FREE — 2026-08-28

Issue #41 / PR #42 closed the operational custody gap between the frozen ADR-010 comparison executor and a future real ADR-009 live invocation. No provider call or credential/account probe occurred.

## Delivered boundary

ADR-011 freezes two layers:

```text
GovernedProviderLiveTask                 src/academy_tractian/provider_live_task.py
        ↓ authorization-level custody
GovernedLiveProviderComparison           src/academy_tractian/provider_live_execution.py
        ↓ write-ahead attempt ledger
ProviderComparisonExecutor               frozen ADR-010
```

Frozen blobs:

```text
provider_live_execution.py   e2e2f2c7350efc0ab67490027347d76a6da54914
provider_live_task.py        6e86f008b5136c88cab574f64564709e1029a945
wrapper tests                769c319a7de6a62b83a94a378c05d6d0a1518569
custody tests                cd232b6adf6fc4171e7596e0e7a3ecf1887e76cd
```

Machine freeze:

`research/frozen/provider-live-execution-wrapper-freeze-v1.json`

ADR:

`docs/adr/011-governed-live-provider-execution-wrapper-2026-08-28.md`

## Secret and preflight boundary

The governed task receives explicit OpenAI and Google secret values. It only checks local presence.

If either secret is absent:

```text
provider calls          0
credential probes       0
authorization marker    not created
attempt 0               not reached
```

Secrets are excluded from repr output, custody artifacts, attempt ledgers and result artifacts. No capability/account probe is allowed.

## Authorization-level custody hardening

Initial review showed that refusing reuse of the same run directory alone did not prevent a restart from selecting another run directory and recreating an empty in-memory ADR-010 budget.

The final implementation therefore added `GovernedProviderLiveTask` before merge.

A future live task must designate one canonical durable custody root. The governed entrypoint exclusively reserves:

`<custody_root>/adr-009-live-comparison-custody.json`

and fixes the lower run path to:

`<custody_root>/run`

The caller cannot select a second internal run directory through the governed path. If authorization custody already exists, a second run in that root is refused before provider invocation.

If preparation fails after custody reservation, the marker remains. Automatic cleanup/retry is intentionally forbidden. Switching to another custody root is a new external custody decision and is not implicitly authorized.

## Write-ahead attempt custody

For each exact ADR-010 attempt:

```text
pending
→ CLAIMED persisted + fsync
→ executor network-capable invocation
→ completed sanitized attempt
```

If an exception escapes after `CLAIMED`, the attempt becomes `uncertain`, the run stops and raw exception text is discarded. The wrapper never automatically retries/resumes that attempt.

Operational provider/client/parsing failures already represented by ADR-010 remain ordinary completed evidence and stay in frozen denominators.

## Fixed provider-free M5 probes

Before any future live-capable attempt, both exact ADR-009 client classes are exercised through an injected local failing transport.

Required evidence:

- exactly one client invocation per probe;
- `CLIENT_FAILURE` sanitized provenance;
- zero retries;
- zero fallback;
- zero raw request/response/exception persistence;
- zero network calls.

Probe failure stops before attempt 0.

## Validation history

Initial lower-wrapper validation head:

`82a0211dbded683b62859d3b621af3e3361f4d3b`

```text
production-runtime #33       success
production tests             140 passed
ADR-004 regression            12 passed
triggered workflows          11 / 11 success
provider calls                0
```

Authorization-custody hardening head:

`4d6269b391eb6220d6a26b714d1c011849999e14`

```text
production-runtime #38       success
production tests             146 passed
ADR-004 regression            12 passed
triggered workflows          11 / 11 success
provider calls                0
```

Final branch head:

`ea099d023ea004a15c066aa8a4cccfa7c322c513`

Final validation:

```text
production-runtime #41       success
production tests             146 passed
ADR-004 regression            12 passed
triggered workflows          11 / 11 success
provider calls                0
credential/account probes     0
```

PR #42 merged with expected-head guard as:

`7e8cbacf4f704bb1ec6a81b627c18cf7c595d703`

## Post-merge boundary

```text
ADR-009 max live calls                    32
ADR-009 calls consumed                     0
ADR-010 executor                          FROZEN
ADR-011 governed live wrapper/custody     FROZEN
first live attempt                        NO
production provider/model selected       NO
production mutating actions              DISABLED
scientific provider calls                 0
scientific gate   REQUIRED_PER_GROUP_AND_SLICE_REPORTING
```

The implementation step is complete. The next provider task is a separately governed real invocation that must provision one canonical durable custody root plus both required secrets. If those prerequisites are absent, it must stop before attempt 0.

In parallel, delivery work should now start on controlled action enablement and EV-007/EV-008/EV-011 using provider-free/scripted paths; those tracks do not need to wait for provider selection.
