# P12-C1 — Activation / Eligibility Gate

**Date:** 2026-08-23  
**Activation ID:** `P12-C1-ACTIVATION-2026-08-23`  
**Parent experiment:** `P12-C1_EXPOSED_POOL_EVIDENCE_ROUTE_SELECTION`  
**State at commit:** `ACTIVATION_ELIGIBILITY_PASS_PENDING_CI_CONFIRMATION`  
**Execution authorized before CI:** **NO**

## Frozen activation decision

The activation review was completed without observing any new `EXPOSED_POOL` candidate outcome, without provider/model inference and without new private benchmark semantic access.

The prospective participating set is frozen to:

```text
C0  E14T_REFERENCE_PORT_V1       ELIGIBLE
C1  PARENT_TOP7_CANONICAL_V1     ELIGIBLE
C2  ISOLATED_PUBLIC_ROUTE_PLANNER_V2  INELIGIBLE_THIS_CYCLE
```

C2 is excluded because no **fresh** public synthetic qualification pass exists before the first `EXPOSED_POOL` outcome. Historical E14v, E14v-A and E14v-B attempts remain consumed. This activation neither reruns them nor substitutes a new planner after seeing exposed outcomes.

Therefore the only confirmatory comparison authorized if CI passes is:

`C1 - C0`.

## Public corpus freeze

The activation pins exactly **7 independent asset/story groups, 11 scenario families and 12 agent-visible ticket cases**. The apparent 11-scenario/12-ticket asymmetry is resolved from public committed provenance: the delivered benchmark has one narrative scenario combining stale-analysis investigation and its reprocess execution flow. Together with the frozen B204 scenario/ticket membership, this fixes:

```text
asset_B204 / CEN-07 / TKT-INV-09 / investigate
asset_B204 / CEN-07 / TKT-EXE-12 / execute
asset_B204 / CEN-12 / TKT-CTX-02 / contextualize
```

No private expected-path value is needed or used for this mapping.

The other exposed mappings are frozen directly from the public split metadata. Overall case modalities are 6 investigate, 4 execute and 2 contextualize.

## Repetition and common-parent freeze

Each of the 12 ticket cases has three repetitions using the preregistered seed schedule:

`2026082301`, `2026082302`, `2026082303`.

This yields 36 common-parent generations. For each matched case/repetition, C0 and C1 receive the **same fixed upstream output**; candidate-specific regeneration is prohibited. The provider/model/runtime configuration and the E14o/E14l → E14f → E14n-v1.1 → E14p → E14q → E14q2 lineage are hash-pinned in the machine manifest.

## Candidate implementation

The activation introduces `scripts/research/p12_c1_evidence_route_candidates.py` solely to make the preregistered C0/C1 policies executable.

C0 is a prospective rate-normalized E14t reference port. Its global restoration budget is `floor(0.4 × N)`; with 36 outputs, the maximum is 14 additions, with at most one addition/output and at most seven final reads/output.

C1 is a materially simpler deterministic baseline. It retains only canonical public GET routes already present in the parent `evidence_plan`, preserves first occurrence, deduplicates, and caps at seven. It cannot add or infer routes.

Both arms may modify only `evidence_plan`; all non-evidence fields must remain unchanged.

## Evaluation and access controls

E9 v4.1 selected-ticket deterministic evaluation is hash-pinned and remains evaluator-side only after candidate outputs are fixed. P12 currently classifies the v4.1 direction as `QUALIFIED`; the exact evaluator implementation is frozen for this cycle.

The semantic v4.2 stage is **not** activated here. Only deterministic-gate passers may enter a separately preregistered semantic child stage.

Access remains fail-closed:

- candidate private oracle: `DENY_ALWAYS`;
- `FRESH_BLIND`: `DENY`;
- `LEGACY_LOCKED_TEST`: `DENY`;
- final measurement: not authorized;
- architecture freeze: not authorized;
- production-readiness claim: not authorized.

## CI gate

The activation becomes executable only if `.github/workflows/research-p12-c1-activation-self-check.yml` passes. The workflow is provider-free and checks immutable Git pins, P12 guard state, 7/11/12 mapping, B204 multi-ticket mapping, repetition policy, common-parent config, C0/C1 policy hashes, consumed E14v locks, deterministic gates, statistical protocol, evaluator pin, access controls, candidate source selectors and public synthetic candidate invariants.

A failing check keeps execution denied. A passing run is recorded in the activation manifest before the single C0-vs-C1 `EXPOSED_POOL` cycle is authorized.
