# Academy × TRACTIAN — Current Project Status

**Canonical status checkpoint:** 2026-08-27 10:20 BRT  
**Canonical branch after merge:** `main`  
**Current working branch:** `eval/c4-deterministic-scoring`  
**Final delivery target:** 2026-09-08  
**Audited project source baseline:** [`../research/tractian-source-baseline-2026-08-27.md`](../research/tractian-source-baseline-2026-08-27.md)  
**Governance:** [`PROJECT-PRINCIPLES.md`](PROJECT-PRINCIPLES.md)  
**Immediate execution plan:** [`NEXT-STEPS.md`](NEXT-STEPS.md)  
**Architecture roadmap:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)  
**Master plan:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)  
**Delivery acceptance:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)  
**Progress ledger:** [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)  
**Repository guide:** [`REPOSITORY-GUIDE.md`](REPOSITORY-GUIDE.md)  
**Machine-readable checkpoint:** [`research/results/project-progress-checkpoint-2026-08-27-1020-brt.json`](../research/results/project-progress-checkpoint-2026-08-27-1020-brt.json)

This document is the **sole canonical human-readable source for current project state and current authorization**. Exact experiment semantics remain governed by frozen manifests/results. Historical failures remain evidence and do not authorize rerun/reuse.

## Executive state

```text
Project North Star                           maximize actual TRACTIAN/Inteli delivery under P1-P4
Benchmark Integrity Gate                    CLOSED
P12 evaluation protocol                     FROZEN
P12-C1                                      CLOSED / DETERMINISTIC FAIL / NO ARM QUALIFIED
P12-C2                                      CONSUMED_OPERATIONAL_FAILURE / 31 OF 36 / NO SCORING
P12-C3                                      CONSUMED_TERMINAL_OPERATIONAL_FAILURE / 3 OF 36 / NO SCORING
P12-C4 NVIDIA common-parent collection      PASS / 36 OF 36
P12-C4 local factorial expansion            PASS / 144 OF 144
P12-C4 packet                               FROZEN_COMPLETE_C4_PACKET
P12-C4 deterministic scoring                FROZEN / 144 OF 144 / 0 RECOMPUTATION MISMATCHES
current authorized gate                     BOOTSTRAP_20000
bootstrap                                   AUTHORIZED / NOT EXECUTED
LOGO                                        NOT AUTHORIZED
slice analysis                              NOT AUTHORIZED
semantic evaluation                         NOT AUTHORIZED
FRESH_BLIND outcome access                  NOT AUTHORIZED
LEGACY_LOCKED_TEST                          NOT AUTHORIZED
provider calls authorized now               0
current project-level PREFERRED             NONE
final architecture                          UNFROZEN
production-readiness claim                  NOT AUTHORIZED
```

## Current scientific evidence

The deterministic-scoring closure is:

`research/results/p12-c4-deterministic-scoring-freeze-2026-08-27.json`

Status:

`FROZEN_C4_DETERMINISTIC_SCORING`

Evidence recorded by that freeze:

- exact frozen C4 packet consumed;
- 144/144 fixed outputs deterministically scored;
- 144/144 rows scoreable;
- 36 parents × A00/A10/A01/A11 preserved;
- evaluator-side preflight: PASS;
- 12/12 exposed ticket rows aligned exactly and uniquely;
- expected-step normalization failures: 0;
- independent deterministic recomputation: 144 rows, 0 mismatches;
- provider/model calls: 0;
- bootstrap/LOGO/slices/semantic: not executed;
- FRESH_BLIND/LEGACY_LOCKED_TEST accesses: 0;
- complete deterministic row artifact retained evaluator-side and frozen by SHA-256 `b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c`.

The private oracle remains evaluator-side. The scorer consumed only a 12-row EXPOSED_POOL subset derived by exact public ticket ID from the audited TRACTIAN package; non-exposed expected-path content was not loaded by the scorer.

## Current authorization boundary

The deterministic-scoring freeze explicitly opens only:

### `BOOTSTRAP_20000`

Frozen parameters:

```text
resamples         20,000
seed              20260822
confidence        95%
resampling unit   asset_story_group
input SHA-256     b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c
```

The bootstrap must consume that exact frozen deterministic score artifact and follow the preregistered factorial aggregation/comparison protocol.

Still forbidden:

- new provider/model generation;
- score changes or regeneration in response to observed statistical outcomes;
- LOGO;
- modality/failure slices;
- semantic evaluation;
- FRESH_BLIND;
- LEGACY_LOCKED_TEST;
- candidate regeneration;
- final architecture freeze;
- production-readiness claims.

## Current non-claims

The project does **not** currently claim that:

- any C4 arm has passed the preregistered aggregate deterministic gates;
- any factorial effect/confidence interval has been measured in C4;
- any C4 arm is project-level `PREFERRED` or final `FROZEN`;
- any arm is eligible for semantic evaluation yet;
- NVIDIA is the final production provider;
- any runtime/orchestrator/retrieval/memory topology is final;
- independent FRESH_BLIND evidence has been measured;
- the final architecture is frozen;
- the system is production-ready.

## Delivery coverage state

The required final product remains an integrated **industrial agent + trustworthy evaluation framework**. C4 is selection evidence, not the final product.

P0/P1 work outside the private/statistical boundary may continue only when it cannot contaminate the frozen C4 path and when it maps directly to `DELIVERY-ACCEPTANCE.md` or a material delivery risk.

The development priority remains:

```text
P0 requested capability + trustworthy evaluation
        ↓
P1 production/security/reliability/partner quality
        ↓
P2 optional complexity only with measured benefit
```

## Planning pointers

- **What happens next:** [`NEXT-STEPS.md`](NEXT-STEPS.md)
- **What final delivery must prove:** [`DELIVERY-ACCEPTANCE.md`](DELIVERY-ACCEPTANCE.md)
- **General system/production architecture:** [`ARCHITECTURE-ROADMAP.md`](ARCHITECTURE-ROADMAP.md)
- **Macro phases/deadline protection:** [`PROJECT-PLAN.md`](PROJECT-PLAN.md)
- **Historical ledger:** [`PROJECT-PROGRESS-LOG.md`](PROJECT-PROGRESS-LOG.md)

When the bootstrap gate closes, create a new immutable result/closure and then update status, checkpoint, ledger and next steps before executing any newly opened later gate.
