# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-27 11:02 BRT  
**Canonical branch after merge:** `main`  
**Current working branch:** `eval/c4-logo-sensitivity`  
**Final delivery target:** 2026-09-08  
**Audited project source baseline:** [`../research/tractian-source-baseline-2026-08-27.md`](../research/tractian-source-baseline-2026-08-27.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Progress ledger:** [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)  
**Repository guide:** [`REPOSITORY-GUIDE.md`](REPOSITORY-GUIDE.md)  
**Machine-readable checkpoint:** [`research/results/project-progress-checkpoint-2026-08-27-1102-brt.json`](../research/results/project-progress-checkpoint-2026-08-27-1102-brt.json)

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
P12-C4 LOGO sensitivity                     FROZEN / 7 OF 7 OMISSIONS / INDEPENDENT RECOMPUTATION PASS
current authorized gate                     REQUIRED_PER_GROUP_AND_SLICE_REPORTING
per-group reporting                         AUTHORIZED / NOT EXECUTED
modality slices                             AUTHORIZED ONLY IN CURRENT REPORTING GATE / NOT EXECUTED
safety/failure-family slices                AUTHORIZED ONLY IN CURRENT REPORTING GATE / NOT EXECUTED
semantic evaluation                         NOT AUTHORIZED
FRESH_BLIND                                 NOT AUTHORIZED
LEGACY_LOCKED_TEST                          NOT AUTHORIZED
provider calls authorized now               0
current project-level PREFERRED             NONE
survivor/no-survivor decision               NOT AUTHORIZED YET
final architecture                          UNFROZEN
production-readiness claim                  NOT AUTHORIZED
```

## Current scientific evidence

The C4 statistical chain is now frozen through LOGO:

1. `research/results/p12-c4-deterministic-scoring-freeze-2026-08-27.json` — 144/144 deterministic score rows, 0 independent score mismatches;
2. `research/results/p12-c4-bootstrap-20000-freeze-2026-08-27.json` — exact 20,000-resample whole-group percentile bootstrap;
3. `research/results/p12-c4-logo-sensitivity-freeze-2026-08-27.json` — exact seven leave-one-`asset_story_group`-out estimates per primary comparison.

Exact immutable statistical inputs remain:

```text
deterministic score rows SHA-256  b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
bootstrap result SHA-256           08977c0d419144b885a7d2da6ffb73796ca43d80aa4e330a462d33c058464526
LOGO full result SHA-256           bc62cc45b4e3344861a152825096a8a1b28f41f2d831f86fd81de35964363f8c
```

LOGO independent validation reproduced the frozen historical C2 `logo_effects(...)` semantics exactly with 0 mismatch sections, 7 omitted groups and 6 retained groups per estimate.

Observed robustness evidence, without candidate-selection inference:

- E1 expected-read recall effect remains negative under every group omission;
- E1 extra-public-read effect remains negative under every group omission;
- E1 evidence-correctness effect is not sign-robust: it becomes positive when `asset_M102` is omitted;
- E1 task/reference-quality effect is not sign-robust for the same omission;
- S1 remains exactly measurement-identical to S0 on every preregistered primary safety contrast under all seven omissions;
- A11 reproduces the E1 LOGO pattern on evidence metrics and remains zero on decision/action/escalation/safety contrast metrics.

All four arm aggregates still contain nonzero confirmed hard-safety violations. Under the frozen preregistration, hard safety is an exact gate rather than a statistical tradeoff, but the formal survivor/no-survivor decision remains deferred until the remaining required reporting gate is frozen.

## Current authorization boundary

The LOGO freeze opens only the staged project gate:

### `REQUIRED_PER_GROUP_AND_SLICE_REPORTING`

This label covers the still-unexecuted items explicitly required by the frozen C2 preregistration. It is a project gate label, not a claimed verbatim preregistration identifier.

Authorized now:

- all per-`asset_story_group` outcomes required for reporting;
- modality slices: `investigate`, `execute`, `contextualize`;
- safety and failure-family slices;
- operational failure counts and denominators;
- validation and freeze of those reporting outputs.

Still forbidden:

- provider/model generation;
- score recomputation or mutation;
- candidate regeneration;
- survivor/PREFERRED decision before the reporting freeze closes;
- semantic evaluation;
- FRESH_BLIND;
- LEGACY_LOCKED_TEST;
- final architecture freeze;
- production-readiness claims.

## Current non-claims

The project does **not** currently claim that:

- any C4 arm is a final survivor, `PREFERRED` or final `FROZEN` candidate;
- required per-group/modality/failure reporting is complete;
- any arm is eligible for semantic evaluation;
- independent generalization has been measured;
- NVIDIA or any runtime/retrieval/memory topology is final;
- the architecture is frozen;
- the system is production-ready.

## Delivery coverage state

The requested final product remains an integrated **industrial agent + trustworthy evaluation framework**. C4 remains candidate-selection evidence, not the final product.

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

When the required reporting gate closes, freeze it first, then update status/checkpoint/ledger/next steps before considering any survivor/no-survivor decision.
