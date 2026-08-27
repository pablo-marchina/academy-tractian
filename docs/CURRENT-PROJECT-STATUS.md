# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-27 10:41 BRT  
**Canonical branch after merge:** `main`  
**Current working branch:** `eval/c4-bootstrap-20000`  
**Final delivery target:** 2026-09-08  
**Audited project source baseline:** [`../research/tractian-source-baseline-2026-08-27.md`](../research/tractian-source-baseline-2026-08-27.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Progress ledger:** [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)  
**Repository guide:** [`REPOSITORY-GUIDE.md`](REPOSITORY-GUIDE.md)  
**Machine-readable checkpoint:** [`research/results/project-progress-checkpoint-2026-08-27-1041-brt.json`](../research/results/project-progress-checkpoint-2026-08-27-1041-brt.json)

This document is the **sole canonical human-readable source for current project state and authorization**. Frozen experiment artifacts remain authoritative for exact semantics.

## Executive state

```text
Project North Star                           maximize actual TRACTIAN/Inteli delivery under P1-P4
Benchmark Integrity Gate                    CLOSED
P12 evaluation protocol                     FROZEN
P12-C1                                      CLOSED / DETERMINISTIC FAIL / NO ARM QUALIFIED
P12-C2                                      CONSUMED_OPERATIONAL_FAILURE / 31 OF 36 / NO SCORING
P12-C3                                      CONSUMED_TERMINAL_OPERATIONAL_FAILURE / 3 OF 36 / NO SCORING
P12-C4 common parents                       PASS / 36 OF 36
P12-C4 local factorial outputs              PASS / 144 OF 144
P12-C4 packet                               FROZEN_COMPLETE_C4_PACKET
P12-C4 deterministic scoring                FROZEN / 144 OF 144 / 0 RECOMPUTATION MISMATCHES
P12-C4 bootstrap 20k                        FROZEN / PASS / INDEPENDENT RECOMPUTATION PASS
current authorized gate                     LEAVE_ONE_GROUP_OUT_SENSITIVITY
LOGO                                        AUTHORIZED / NOT EXECUTED
slice analysis                              NOT AUTHORIZED
semantic evaluation                         NOT AUTHORIZED
FRESH_BLIND                                 NOT AUTHORIZED
LEGACY_LOCKED_TEST                          NOT AUTHORIZED
provider calls authorized now               0
current project-level PREFERRED             NONE
final architecture                          UNFROZEN
production-readiness claim                  NOT AUTHORIZED
```

## Current scientific evidence

Deterministic scoring is frozen in:

`research/results/p12-c4-deterministic-scoring-freeze-2026-08-27.json`

Bootstrap is frozen in:

`research/results/p12-c4-bootstrap-20000-freeze-2026-08-27.json`

Bootstrap integrity:

- input: exact deterministic score-row SHA-256 `b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c`;
- 144 rows / 36 common parents / 4 arms / 7 independent groups;
- 20,000 whole-`asset_story_group` percentile resamples;
- seed `20260822`;
- 95% intervals;
- exact historical C2 aggregate/contrast/factorial helper equivalence: PASS;
- independent mismatch sections: 0;
- full bootstrap artifact SHA-256 `08977c0d419144b885a7d2da6ffb73796ca43d80aa4e330a462d33c058464526`;
- provider/model calls: 0;
- private oracle loaded by bootstrap: false;
- LOGO/slices/semantic/blind: not executed.

Observed bootstrap evidence is recorded without making a survivor decision. The evidence intervention E1 has a negative point estimate for evidence correctness and expected-read recall while reducing extra reads; all corresponding 95% intervals include zero. The S1 safety factor produces zero measured effect on every frozen report metric in this C4 packet. These are measured results, not authorization to redesign the same confirmatory packet.

All four arm aggregates still contain nonzero confirmed hard-safety violations. The formal survivor/no-survivor decision remains deferred until the preregistered robustness/reporting gates close.

## Current authorization boundary

The bootstrap freeze opens only:

### `LEAVE_ONE_GROUP_OUT_SENSITIVITY`

Allowed now:

- consume the same frozen deterministic score rows and frozen bootstrap evidence;
- compute only the preregistered leave-one-`asset_story_group`-out sensitivity quantities;
- independently validate and freeze the LOGO result.

Still forbidden:

- provider/model generation;
- deterministic score changes or recomputation in response to outcomes;
- modality/failure-family slices;
- semantic evaluation;
- FRESH_BLIND;
- LEGACY_LOCKED_TEST;
- candidate regeneration;
- survivor/PREFERRED decision before the applicable reporting gates close;
- final architecture freeze;
- production-readiness claims.

## Current non-claims

The project does **not** currently claim that:

- any C4 arm is a final survivor, `PREFERRED` or final `FROZEN` candidate;
- LOGO or required slices have passed;
- any arm is eligible for semantic evaluation;
- independent generalization has been measured;
- NVIDIA or any runtime/retrieval/memory topology is final;
- the architecture is frozen;
- the system is production-ready.

## Delivery coverage state

The requested final product remains an integrated **industrial agent + trustworthy evaluation framework**. C4 is candidate-selection evidence, not the final product.

Priority remains:

```text
P0 requested capability + trustworthy evaluation
        ↓
P1 production/security/reliability/partner quality
        ↓
P2 optional complexity only with measured benefit
```

Parallel P0/P1 work is permitted only when it cannot contaminate the frozen C4 path and maps directly to `DELIVERY-ACCEPTANCE.md` or a material delivery risk.

## Planning pointers

- **What happens next:** [`NEXT-STEPS.md`](NEXT-STEPS.md)
- **What final delivery must prove:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)
- **General architecture:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)
- **Macro plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)
- **Historical ledger:** [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)

When the LOGO gate closes, freeze it first, then update status/checkpoint/ledger/next steps before executing any newly authorized gate.
