# Academy × TRACTIAN — Project Progress Ledger

**Purpose:** chronological evidence ledger.  
**Current snapshot:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Active plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file records how the project reached its current state. It does not override frozen experiment manifests, protocols or canonical result artifacts.

## Phase 1 — benchmark integrity and protocol governance — COMPLETE

### BIG-B0 — benchmark integrity audit

Reconstructed historical benchmark access and decision events.

Canonical artifacts:

- `research/big-b0-benchmark-integrity-audit-2026-08-21.md`
- `research/results/big-b0-benchmark-access-ledger-2026-08-21.json`

### BIG-B1 — exposure / contamination ledger

Reclassified historical DEV/VALIDATION/LOCKED_TEST evidence under strict independence rules.

### BIG-B2 — benchmark-design alternatives

Compared balanced folds, LOGO, leave-two-out and fresh-blind designs using the known exposed geometry.

### BIG-B3 — evaluation protocol selection

Selected `P12_FRESH_BLIND_HYBRID_EXTERNAL_FIRST` and established Tier A/Tier B source deadlines and breach semantics.

### BIG-B4 — P12 protocol freeze

Frozen evidence roles:

- `EXPOSED_POOL` — adaptive development/comparison;
- `FRESH_BLIND` — primary independent real-domain evidence;
- `LEGACY_LOCKED_TEST` — supplementary held-out characterization;
- `SYNTHETIC_ADVERSARIAL` — robustness/evaluator qualification.

Also froze repeated-run, group-cluster bootstrap, LOGO, missingness and access-control semantics.

## Phase 2 — historical implementation reinterpretation — COMPLETE

Historical implementation evidence was reclassified under P12. No historical implementation remained `PREFERRED` at project level.

Retained evidence-backed foundations include ScenarioSchema, Canonical ToolSpec, TraceSchema, deterministic replay, HarnessRunner/HttpxTransport, LangGraph runtime candidate, native ToolSpec/MCP-compatible boundaries and the E9/E14 evaluator, provenance and safety foundations.

## Phase 3 — P12-C1 prospective evidence-route comparison — COMPLETE / SCIENTIFIC FAIL

Final packet:

```text
36 common parents
72 fixed C0/C1 outputs
72/72 scoreable
```

C1 reduced extra public reads but materially worsened expected-read recall and did not improve decision/action/escalation. Both arms failed frozen deterministic gates.

Decision:

```text
QUALIFIED arms  none
PREFERRED arm   none
```

Canonical result:

- `research/results/p12-c1-deterministic-paired-result-2026-08-23.json`

## Phase 4 — P12-C2 factorial experiment — CONSUMED_OPERATIONAL_FAILURE

Frozen 2×2 arms:

```text
A00 = E0 + S0
A10 = E1 + S0
A01 = E0 + S1
A11 = E1 + S1
```

Run `32663659575`:

```text
31 successful parents
5 failed parents
failure family: rate_limit_long_window
144-output packet: not created
private scoring: not executed
```

No arm-level scientific conclusion is permitted.

## Phase 5 — P12-C3 capacity-controlled factorial experiment — CONSUMED_TERMINAL_OPERATIONAL_FAILURE

C3 kept the same A00/A10/A01/A11 candidate definitions and added prospective capacity control.

Initial run `32671370930` stopped before provider access on an infrastructure compatibility assertion. A narrow pre-outcome infrastructure amendment was frozen without changing candidate/model/prompt/evaluator/seeds/metrics/gates.

Continued run `32672167702` reached live provider execution and then entered the preregistered terminal state:

```text
completed cells         3
pending cells           33
transport failures       1
rate-limit events        1
terminal failure      true
36/36 freeze          false
144-output packet     absent
private scoring       not executed
```

C3 cannot be resumed, rerun, partially scored or reinterpreted as complete-case evidence.

Canonical closure:

- `research/results/p12-c3-live-cycle-closure-2026-08-23.json`

## Phase 6 — provider-capacity decision and P12-C4 qualification preparation

### Provider ADR — ACCEPTED / CONDITIONAL GO

ADR-001 selected Cerebras Free Trial + `gpt-oss-120b` as the qualification path for P12-C4 while treating the serving-provider change as an explicit confound.

The decision did **not** authorize EXPOSED_POOL generation and did not freeze Cerebras as the final production provider.

### C4 serving contract and isolation

Frozen:

- provider: Cerebras;
- model: `gpt-oss-120b`;
- SDK: `cerebras_cloud_sdk==1.91.0`;
- `temperature=0`;
- `reasoning_effort=medium`;
- hidden reasoning;
- strict JSON schema;
- `max_completion_tokens=4096`;
- `warm_tcp_connection=false`;
- retries = 0;
- automatic failover = false;
- 36 fresh common-parent seeds;
- no C1/C2/C3 partial-output or live-seed reuse.

### Prompt sizing and pacing — PASS / FROZEN

Provider-free measurement:

```text
serialized request token range       2195..2217
max system + user tokens              1691
max conservative prompt bound         3284
max reserved admission/request        7380
36-request reserved upper bound     265002
minimum request spacing                75 s
```

### Account capacity — NUMERIC PASS

First-party organization/project limits recorded:

```text
RPM             5
uncached TPM    30,000
total TPM       90,000
TPH             1,000,000
TPD             1,000,000
```

Authenticated model-catalog access to `gpt-oss-120b` was also confirmed.

### Synthetic authorization — ONE-SHOT FROZEN

Authorization `p12-c4-cerebras-synthetic-probe-live-authorization-v1` allowed exactly one workflow attempt containing exactly the two preregistered synthetic requests, with no automatic retries or rerun.

It did not authorize EXPOSED_POOL, scoring, FRESH_BLIND or LEGACY_LOCKED_TEST access.

## Phase 7 — P12-C4 synthetic live qualification — CONSUMED_OPERATIONAL_FAILURE

Live workflow:

```text
workflow        research-p12-c4-cerebras-synthetic-live-probe
run             32901958789
run attempt     1
job             97977601612
head            9e0a89e1959dcc4ffd659baef1a4f07e137a7245
preflight       PASS
SDK pin         PASS
live step       FAIL
```

The first preregistered provider request failed with:

```text
HTTP 402
payment_required_error
code = payment_required
param = quota
```

Observed consequences:

```text
provider request attempts          1
successful generation calls        0
model outputs                       0
first synthetic complete       false
second synthetic attempted     false
benchmark inputs loaded             0
private-oracle accesses             0
FRESH_BLIND accesses                0
LEGACY_LOCKED_TEST accesses         0
```

The one-shot authorization attempt is consumed and may not be rerun or reused.

Canonical closure:

- `research/results/p12-c4-cerebras-synthetic-live-probe-closure-2026-08-25.json`

Scientific state after closure:

```text
synthetic compatibility gate       FAIL / operational access
P12-C4 activation                  BLOCKED
P12-C4 live manifest               BLOCKED
P12-C4 common parents              0 / 36
P12-C4 fixed outputs               0 / 144
private scoring                    BLOCKED
semantic gate                      BLOCKED
```

The prior account attestation remains historical evidence for numeric capacity, authentication and model-catalog access, but it is insufficient to establish current generation access after the HTTP 402 result.

## Current checkpoint — 2026-08-25 22:50 BRT

```text
Benchmark Integrity Gate        CLOSED
P12 protocol                    FROZEN
P12-C1                          CLOSED / deterministic fail
P12-C2                          CONSUMED_OPERATIONAL_FAILURE
P12-C3                          CONSUMED_TERMINAL_OPERATIONAL_FAILURE
P12-C4                          BLOCKED / synthetic operational access failure / 0 of 36
Cerebras numeric capacity       PASS
Cerebras generation access      FAIL / payment required
QUALIFIED current candidate     none
PREFERRED current candidate     none
FRESH_BLIND                     no source authorized
LEGACY_LOCKED_TEST              blocked
architecture                    unfrozen
production-readiness            not authorized
```

Current critical path:

```text
first-party generation/billing activation evidence
        ↓
narrow pre-outcome infrastructure amendment
        ↓
new versioned one-shot synthetic authorization only after provider-free PASS
        ↓
2/2 synthetic PASS
        ↓
full provider-free P12-C4 activation
        ↓
live manifest freeze
        ↓
36/36 common parents
        ↓
144/144 fixed outputs
        ↓
deterministic gate + 20k bootstrap + LOGO + slices/failure analysis
        ↓
semantic child gate for deterministic survivors only
        ↓
production-fit decision + generation/evaluator freeze
        ↓
authorized FRESH_BLIND measurement
        ↓
architecture freeze / regression / final delivery
```

FRESH_BLIND source preparation remains a parallel critical path with no outcome exposure. Tier A target remains 2026-08-25 23:59 BRT; Tier B fallback deadline remains 2026-08-28 23:59 BRT.
