# Academy × TRACTIAN — Next Steps

**Status:** ACTIVE  
**Checkpoint:** 2026-08-28 02:00 BRT  
**Canonical state:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)

This file is the short-horizon execution plan. It does not itself authorize a scientific gate, provider call, action execution or provider selection.

## 1. Scientific critical path — unchanged and parallel

Current scientific gate:

`REQUIRED_PER_GROUP_AND_SLICE_REPORTING`

The reporting runner remains blocked on the exact original evaluator-side deterministic score rows:

```text
SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bytes    177350
rows     144
```

Immediate scientific work is artifact recovery/provisioning only. Do not reconstruct, rescore or replace it.

If recovered exactly:

1. provision through the existing fail-closed path;
2. run required per-group/slice reporting only;
3. independently validate;
4. freeze the reporting artifact;
5. advance only to the next explicitly opened scientific gate.

Scientific provider/model calls remain 0.

## 2. Production P0 — prepare separate live comparison execution

ADR-010 now freezes the provider-free executor. The frozen production path is ready to materialize the ADR-008/009 comparison without changing geometry or metrics.

Canonical execution identity:

```text
executor freeze       ADR-010
plan SHA-256          69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f
units                 8
repeats               2
live candidates       2
max calls             32
calls consumed        0
```

The next Class C task should provide only the operational live-run wrapper around this frozen executor.

Required behavior before attempt 0:

1. load ADR-009 authorization + ADR-010 freeze and verify exact blobs/hashes;
2. obtain OpenAI/Google secret values from an execution-owned secret boundary, never from provider-visible state and never commit/log them;
3. do **not** send a capability/credential test request;
4. if either required secret is absent, stop before attempt 0 with a sanitized operational blocker;
5. instantiate only the exact ADR-009 client classes/routes;
6. ensure production actions remain disabled;
7. create a new immutable execution-result target before calls begin;
8. record consumed-call count durably as part of run evidence so the 32-call budget cannot be silently reset.

Credential presence validation may check only whether required secret values were provisioned. It must not probe provider accounts or call a model merely to test availability.

## 3. Execute ADR-009 only under the frozen geometry

Once secrets are explicitly provisioned, the live task may consume at most:

```text
OpenAI attempts                   16
Google attempts                   16
total attempts                    32
warm-up calls                      0
automatic retries                  0
fallbacks                          0
parallel provider calls            0
provider seed                      none
provider-side conversation state   none
production actions                 disabled
```

Every attempted provider invocation is consumed evidence, including operational failures.

The execution must stop on:

- frozen input/blob mismatch;
- route/model drift;
- raw/custody/provenance violation;
- hidden retry/fallback behavior;
- attempt-order/budget mismatch;
- unauthorized action/tool transport behavior.

Do not replace a failed candidate/route in place. Any material amendment must be prospective and preserve already-consumed evidence.

## 4. Freeze live comparison result

After the live task ends, produce one sanitized immutable result containing:

- exact frozen input/executor identities;
- attempted and unattempted indexes;
- candidate/unit/repeat mapping;
- sanitized ADR-007 provenance;
- M1–M10 with exact preregistered denominators;
- hard-gate status;
- operational failure families;
- exact provider usage where reported;
- latency distribution;
- normalized cost only where exact accounting inputs exist;
- deterministic final outcome: candidate ID or `NO_SELECTION`.

Incomplete evidence must not be converted into a winner. If the packet cannot satisfy the frozen rule, result is `NO_SELECTION`.

No semantic/private/blind judge is part of this comparison.

## 5. After live provider evidence

If a candidate is selected:

- bind it behind the existing provider-neutral ADR-006 interface;
- retain ADR-004 controller and HarnessRunner ownership;
- keep ADR-005 consequential actions disabled;
- run repeated-run stability, provider/client failure injection and latency/reliability evidence;
- verify customer-safe terminal communication and trace/evaluator behavior.

If outcome is `NO_SELECTION`:

- keep the provider-free safe baseline available;
- do not select a provider by intuition or historical C4 evidence;
- open a prospective amendment only if additional evidence is justified and the delivery deadline permits it.

## 6. Consequential actions remain separate

Do not enable production mutating actions during provider comparison work. Action enablement still requires trusted real sources for:

- permissions;
- resource/company scope;
- requester confirmation;
- durable idempotency/duplicate protection;
- retry/failure semantics;
- audit evidence.

## 7. Reliability / final delivery work after provider result

Close the remaining high-value P0/P1 evidence gaps:

- EV-007 failure-performance behavior;
- EV-008 repeated-run stability;
- provider/client outage and malformed-output handling;
- observability without raw provider leakage;
- latency/resource/cost reporting;
- customer-safe deterministic failure messages;
- integrated real Agent + Evaluator demonstration;
- reproducible final handoff/documentation.

Continue deferring RAG/vector DB/reranking, persistent memory, MCP, multi-agent orchestration, adaptive routing and rich UI unless a measured acceptance gap requires them.

## 8. Deadline sequence

```text
NOW        reconcile ADR-010 executor freeze
NEXT       build provider-free live-run wrapper + fail-before-attempt-0 secret boundary
THEN       provision explicit execution secrets
THEN       execute exact ADR-009 32-attempt envelope once
THEN       freeze candidate_id or NO_SELECTION result
PARALLEL   recover exact C4 reporting artifact
AFTER      reliability / security / observability / evaluator gaps
FINAL      integrated real-path demo + documentation + reproducible handoff
```
