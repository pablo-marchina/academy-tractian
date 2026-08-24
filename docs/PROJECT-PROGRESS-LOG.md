# Academy × TRACTIAN — Project Progress Ledger

**Purpose:** chronological evidence ledger.  
**Current snapshot:** [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md)  
**Active plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)

This file records how the project reached its current state. It does not override experiment manifests, frozen protocols or canonical result artifacts.

## Phase 1 — benchmark integrity and protocol governance

### BIG-B0 — benchmark integrity audit — COMPLETE

Reconstructed historical benchmark access and decision events, including adaptive use of validation-side information and later evaluator-structure access.

Canonical artifacts:

- `research/big-b0-benchmark-integrity-audit-2026-08-21.md`
- `research/results/big-b0-benchmark-access-ledger-2026-08-21.json`

### BIG-B1 — exposure / contamination ledger — COMPLETE

Reclassified historical DEV/VALIDATION/LOCKED_TEST evidence under a strict independence rule. Historical VALIDATION became exposed for future candidate-generalization claims; LOCKED_TEST retained candidate/task-quality blindness but not pristine evaluator-structure blindness.

Canonical artifacts:

- `research/big-b1-exposure-contamination-ledger-2026-08-21.md`
- `research/results/big-b1-exposure-contamination-ledger-2026-08-21.json`

### BIG-B2 — benchmark-design alternatives — COMPLETE

Compared balanced folds, LOGO, leave-two-out and fresh-blind designs using the known seven-group exposed geometry.

Canonical artifacts:

- `research/big-b2-benchmark-design-alternatives-2026-08-21.md`
- `research/results/big-b2-benchmark-design-comparison-2026-08-21.json`

### BIG-B3 — evaluation protocol selection — COMPLETE

Selected `P12_FRESH_BLIND_HYBRID_EXTERNAL_FIRST` and established Tier A/Tier B blind-source deadlines and breach semantics.

Canonical artifacts:

- `research/big-b3-evaluation-protocol-selection-2026-08-21.md`
- `research/results/big-b3-evaluation-protocol-selection-2026-08-21.json`

### BIG-B4 — P12 protocol freeze — COMPLETE / FROZEN

Frozen evidence roles:

- `EXPOSED_POOL` for adaptive development/comparison;
- `FRESH_BLIND` for primary independent real-domain evidence;
- `LEGACY_LOCKED_TEST` for supplementary held-out characterization only;
- `SYNTHETIC_ADVERSARIAL` for robustness/evaluator qualification.

Also froze repeated-run, group-cluster bootstrap, LOGO, failure/missingness and access-control semantics.

Canonical artifacts:

- `research/big-b4-evaluation-protocol-freeze-2026-08-22.md`
- `research/frozen/big-b4-evaluation-protocol-v1.json`

## Phase 2 — historical implementation reinterpretation

Historical implementation evidence was reclassified under P12. No historical implementation candidate remained `PREFERRED` at project level. The evaluation protocol is the only project-level technical item frozen by governance at this stage.

Reusable evidence-backed foundations include ScenarioSchema, Canonical ToolSpec, TraceSchema, deterministic replay, HarnessRunner/HttpxTransport, LangGraph runtime candidate, native ToolSpec/MCP-compatible boundaries, E9 v4.1/v4.2 and E14c/d/e/n/p/q/q2.

Canonical artifacts:

- `research/p12-historical-candidate-component-reinterpretation-2026-08-22.md`
- `research/results/p12-historical-candidate-component-reinterpretation-2026-08-22.json`

## Phase 3 — P12-C1 prospective evidence-route comparison

### Preregistration and activation — COMPLETE

Froze a paired EXPOSED_POOL comparison between C0 reference evidence restoration and C1 bounded canonical route selection using 36 common parents and three repetitions per visible ticket.

### Live execution and deterministic scoring — COMPLETE

Final packet:

```text
36 common parents
72 fixed C0/C1 outputs
72/72 scoreable
```

Key result:

- C1 reduced extra public reads;
- C1 materially worsened expected-read recall;
- decision/action/escalation did not improve;
- both arms retained hard-safety failures;
- both arms failed frozen deterministic gates.

Decision:

```text
C0  RESEARCHED_REFERENCE_FAILED_P12_C1_DETERMINISTIC_GATES
C1  SUPERSEDED_REJECTED_FOR_THIS_CANDIDATE_DEFINITION
QUALIFIED arms  none
PREFERRED arm   none
```

Canonical result:

- `research/results/p12-c1-deterministic-paired-result-2026-08-23.json`
- `research/p12-c1-deterministic-paired-result-2026-08-23.md`

## Phase 4 — P12-C2 factorial evidence/safety experiment

### Design — COMPLETE / FROZEN

Introduced 2×2 E0/E1 × S0/S1 arms:

```text
A00 = E0 + S0
A10 = E1 + S0
A01 = E0 + S1
A11 = E1 + S1
```

Activation passed provider-free.

### Live execution — CONSUMED_OPERATIONAL_FAILURE

Run `32663659575` attempted the complete 36-parent geometry but provider capacity prevented completion:

```text
31 successful parents
5 failed parents
failure family: rate_limit_long_window
144-output packet: not created
private scoring: not executed
```

No arm-level scientific conclusion is permitted from C2.

Canonical closure:

- `research/results/p12-c2-live-cycle-closure-2026-08-23.json`

## Phase 5 — P12-C3 capacity-controlled factorial experiment

### Preregistration / activation / live preparation — COMPLETE

Kept A00/A10/A01/A11 unchanged while prospectively adding:

- six fixed batches × six parents;
- reset-aware capacity control;
- immutable checkpoints;
- pending-only resume;
- 72-hour collection horizon;
- complete-packet-only scoring.

Provider-free activation and live infrastructure qualification passed before provider access.

### Initial B1 infrastructure failure — PRE-OUTCOME

Run `32671370930` stopped before provider access on a retained E14l transport-invariant compatibility assertion.

```text
provider requests      0
candidate outcomes     0
```

A narrow infrastructure amendment was frozen and provider-free qualified in runs `32671829920` and `32672049576` without changing model, prompt, candidates, evaluator, seeds, batch map, metrics or gates.

### Continued B1 live execution — CONSUMED_TERMINAL_OPERATIONAL_FAILURE

Run `32672167702` reached live provider execution and then entered the preregistered terminal state:

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

No same-experiment resume, rerun, partial scoring or complete-case reinterpretation is allowed.

Canonical closure:

- `research/results/p12-c3-live-cycle-closure-2026-08-23.json`
- `research/p12-c3-live-cycle-closure-2026-08-23.md`

## Phase 6 — canonical checkpoint and plan reset

After C3, the repository separated historical planning from current control documents:

- `docs/CURRENT-PROJECT-STATUS.md` — canonical current evidence/status;
- `docs/PROJECT-PLAN.md` — active reviewed action plan;
- `docs/PROJECT-PROGRESS-LOG.md` — this chronological ledger;
- `docs/archive/PROJECT-PLAN-2026-08-20.md` — archived historical plan;
- `research/results/project-progress-checkpoint-2026-08-23.json` — preserved prior machine checkpoint;
- `research/results/project-progress-checkpoint-2026-08-24.json` — current machine checkpoint.

## Current checkpoint — 2026-08-24 09:53 BRT

```text
Benchmark Integrity Gate        CLOSED
P12 protocol                    FROZEN
P12-C1                          CLOSED / deterministic fail
P12-C2                          CONSUMED_OPERATIONAL_FAILURE
P12-C3                          CONSUMED_TERMINAL_OPERATIONAL_FAILURE
QUALIFIED current candidate     none
PREFERRED current candidate     none
FRESH_BLIND                     no source authorized
LEGACY_LOCKED_TEST              blocked
architecture                    unfrozen
production-readiness            not authorized
```

Current critical path:

```text
provider-capacity alternatives ADR
        +
FRESH_BLIND readiness in parallel
        +
production-fit/architecture evidence in parallel
        ↓
conditional P12-C4 preregistration/activation
        ↓
complete prospective EXPOSED_POOL packet only
        ↓
deterministic gate + bootstrap + LOGO
        ↓
semantic child gate for deterministic survivors only
        ↓
production-fit decision + generation freeze
        ↓
authorized FRESH_BLIND measurement
        ↓
architecture freeze / regression / final delivery
```

The next material decision is the provider-capacity ADR. P12-C4 is conditional on that decision; it is not an automatic continuation label.
