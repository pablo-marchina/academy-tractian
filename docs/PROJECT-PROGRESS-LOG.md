# Academy × TRACTIAN — Project Progress Ledger

**Purpose:** chronological evidence ledger.  
**Current snapshot:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Active plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file explains how the project reached its current state. It does not override frozen experiment manifests, protocols or canonical result artifacts. Failed and consumed attempts remain evidence.

## 1. Benchmark integrity and protocol governance — COMPLETE

BIG-B0–BIG-B4 established benchmark access history, contamination/evidence roles, benchmark-design comparisons and the frozen P12 protocol.

Frozen evidence roles include:

- `EXPOSED_POOL` — adaptive development/comparison;
- `FRESH_BLIND` — independent real-domain evidence;
- `LEGACY_LOCKED_TEST` — supplementary held-out characterization;
- `SYNTHETIC_ADVERSARIAL` — robustness/evaluator qualification.

Canonical foundations include `research/big-b0-benchmark-integrity-audit-2026-08-21.md`, the benchmark access ledger and frozen P12 protocol artifacts.

## 2. Historical implementation reinterpretation — COMPLETE

Historical E-series implementation evidence was reclassified under P12. No historical implementation became automatically project-level `PREFERRED` merely because it had previously passed a narrower gate.

Evidence-backed foundations retained for later comparison include ScenarioSchema, Canonical ToolSpec, TraceSchema, deterministic replay, HarnessRunner/HttpxTransport, runtime/orchestration candidates, tool-protocol adapters and E9/E14 evaluator/provenance/safety foundations.

## 3. P12-C1 — CLOSED / SCIENTIFIC FAIL

C1 completed 36 common parents and 72 fixed C0/C1 outputs. Both arms were scoreable, but neither passed the frozen deterministic acceptance criteria.

```text
QUALIFIED arms   none
PREFERRED arm    none
```

Canonical result: `research/results/p12-c1-deterministic-paired-result-2026-08-23.json`.

## 4. P12-C2 — CONSUMED_OPERATIONAL_FAILURE

Frozen 2×2 design:

```text
A00 = E0 + S0
A10 = E1 + S0
A01 = E0 + S1
A11 = E1 + S1
```

Run `32663659575` completed 31/36 parents and failed five under the recorded rate-limit family. The required 144-output packet was not created and private scoring did not run. No arm-level scientific conclusion is permitted and the attempt remains consumed evidence.

## 5. P12-C3 — CONSUMED_TERMINAL_OPERATIONAL_FAILURE

C3 retained the same factorial candidates and added prospective capacity control. After an infrastructure-only amendment, the live continuation reached only 3/36 completed cells before the preregistered terminal operational state.

```text
completed cells       3
pending cells        33
36/36 freeze       false
144-output packet  absent
private scoring    not executed
```

Canonical closure: `research/results/p12-c3-live-cycle-closure-2026-08-23.json`. C3 cannot be resumed, rerun, partially scored or reinterpreted as complete-case evidence.

## 6. P12-C4 serving-route qualification history

### 6.1 Cerebras — CONSUMED_OPERATIONAL_FAILURE_NO_MODEL_OUTPUT

ADR-001 selected the Cerebras route only for C4 qualification. Numeric capacity/catalog checks passed, but the one-shot synthetic workflow failed on the first provider request with HTTP 402 `payment_required`. No model output or benchmark input was produced. The authorization remains consumed.

Canonical closure: `research/results/p12-c4-cerebras-synthetic-live-probe-closure-2026-08-25.json`.

### 6.2 OpenRouter + OpenInference — CONSUMED_OPERATIONAL_FAILURE_NO_MODEL_OUTPUT

ADR-002 prospectively selected a no-card route. Provider-free qualification passed, but the one-shot live synthetic request failed with HTTP 404 because the frozen free model variant was unavailable. No model output or benchmark input was produced. The authorization remains consumed.

Canonical closure: `research/results/p12-c4-openrouter-synthetic-live-probe-closure-2026-08-26.json`.

### 6.3 NVIDIA NIM — qualification route that enabled C4

ADR-003 selected NVIDIA hosted NIM only as a new C4 provider-qualification candidate, not as a final production-provider decision.

The frozen synthetic compatibility path subsequently passed, the provider-free activation/capacity gate passed, and a separate one-shot live C4 authorization was frozen.

The one-shot NVIDIA live collection then completed:

```text
workflow run       33020748838
job                98350245931
fresh parents      36 / 36
HTTP failures      0
automatic retries  0
warming requests   0
provider fallback  0
model fallback     0
```

The resulting common-parent evidence was independently validated and authorized local factorial expansion only.

## 7. P12-C4 local factorial expansion — COMPLETE

The provider-free local expansion consumed the exact 36 frozen common parents and the frozen C2/C3 factorial semantics.

After three transparent pre-transform infrastructure failures that produced zero arm outputs and zero provider calls, the runtime-only fixes were completed without changing candidate semantics. The valid run was:

```text
workflow run       33028989704
job                98376848407
parents            36
fixed outputs      144 / 144
A00                 36
A10                 36
A01                 36
A11                 36
provider calls       0
validation errors    0
```

The pre-transform infrastructure failures remain retained as operational evidence and are not counted as scientific candidate outputs.

## 8. Complete C4 packet freeze — COMPLETE

On 2026-08-26 the repository froze:

`research/results/p12-c4-complete-packet-freeze-2026-08-26.json`

Status:

```text
FROZEN_COMPLETE_C4_PACKET
fresh common parents           36 / 36
local factorial outputs       144 / 144
partial packet                    false
private scoring executed           false
bootstrap executed                  false
provider calls authorized after      0
next gate          DETERMINISTIC_SCORING
```

This supersedes the earlier project-status checkpoints that still described C4 as provider-blocked; those older snapshots remain historical evidence of the state at their timestamps.

## 9. Repository governance/organization refresh — 2026-08-26

A repository audit found stale status duplication across `README.md`, `CURRENT-PROJECT-STATUS.md`, `PROJECT-PLAN.md`, `PROJECT-PROGRESS-LOG.md` and `research/README.md` after the successful C4 transition.

The cleanup therefore:

- restored `CURRENT-PROJECT-STATUS.md` as the single detailed human current-status source;
- rewrote `PROJECT-PLAN.md` around the four non-negotiable project principles;
- turned root/research/script/workflow READMEs into navigation/lifecycle indexes instead of competing status sources;
- added `REPOSITORY-GUIDE.md` with source-of-truth and safe-cleanup rules;
- retained all frozen/consumed/failed experiment evidence and stable paths;
- added a new time-specific machine checkpoint rather than overwriting the earlier 2026-08-26 snapshot.

## Current checkpoint — 2026-08-26 22:51 BRT

```text
Benchmark Integrity Gate             CLOSED
P12 protocol                         FROZEN
P12-C1                               CLOSED / deterministic fail
P12-C2                               CONSUMED_OPERATIONAL_FAILURE
P12-C3                               CONSUMED_TERMINAL_OPERATIONAL_FAILURE
P12-C4 common parents                PASS / 36 of 36
P12-C4 factorial outputs             PASS / 144 of 144
P12-C4 packet                        FROZEN_COMPLETE_C4_PACKET
current gate                         DETERMINISTIC_SCORING
project-level PREFERRED              none
FRESH_BLIND outcome access           not authorized
LEGACY_LOCKED_TEST                   not authorized
architecture                         unfrozen
production-readiness                 not authorized
```

Current critical path:

```text
deterministic scoring only
        ↓
freeze deterministic result
        ↓
remaining frozen statistical gates when separately authorized
        ↓
deterministic survivor decision
        ↓
semantic child gate for exact survivors only
        ↓
production-fit comparative decision + candidate/evaluator freeze
        ↓
authorized independent evidence
        ↓
final architecture freeze
        ↓
production integration / regression / controlled delivery
```
