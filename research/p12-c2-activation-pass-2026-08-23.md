# P12-C2 Activation / Eligibility — PASS

**Activation:** `P12-C2-ACTIVATION-2026-08-23`  
**Experiment:** `P12-C2_EXPOSED_POOL_FACTORIAL_EVIDENCE_SAFETY`  
**State:** `ACTIVATION_ELIGIBILITY_PASS`  
**Execution authorized:** **Yes — exactly one EXPOSED_POOL factorial live cycle.**

## What passed

The P12-C2 child activation was qualified entirely provider-free and without candidate access to private evaluation material.

Final verification run: **32661560570**, job **97248418351** — `success`.

```text
activation self-check                    97 / 97 PASS
provider/model calls during activation    0
private-oracle access                     0
FRESH_BLIND access                        0
LEGACY_LOCKED_TEST access                 0
new P12-C2 candidate outcomes observed    0
```

The pre-promotion qualification run **32661467838** also passed 96/96 checks while the manifest was still explicitly non-authorized. The manifest was promoted only after that provider-free qualification, and the second run independently verified the final `execution_authorized=true` state.

## Frozen execution lineage

P12-C2 derives its execution runner from the already-qualified P12-C1 common-parent runner rather than reconstructing generation behavior.

```text
qualified P12-C1 runner bundle blob
  a5c27394014bac656faa0a2f923a5c5da72d66f5

qualified parent source SHA-256
  be16ec6d2c33ad68134a0fbf7aa280b4103ee411b01233b6de7a76668e899a50

P12-C2 derived runner source SHA-256
  f494eeac56d69cee85609e79d383b150ccc9e1a51a6e2bf61913bf07cef84d59

common-parent configuration SHA-256
  9033a78a5bab46e4c48ebfc0ec70b6476570519fa62f0526625916d0cd3d3b89
```

The retained generation/repair/guard lineage remains E14o/E14l/E14f through E14n v1.1 and E14p. The P12-C2 runner changes the post-parent candidate expansion to the preregistered factorial `E0/E1 × S0/S1` design.

## Provider-free E1 qualification

`E1 = BOUNDED_PUBLIC_INTENT_DEPENDENCY_CLOSURE_V1` passed:

- all **13/13** public read-route families;
- all **5/5** public action-dependency closure cases;
- max-seven read cap;
- zero unknown/action routes emitted into `evidence_plan`;
- zero group/ticket selectors;
- no private evaluator/oracle input.

The exact generic public intent map is frozen at:

`research/frozen/p12-c2-public-intent-map-v1.json`.

## Provider-free S1 qualification

`S1 = STRICT_PUBLIC_AUTHORIZATION_CERTIFICATE_V1` produced all **7/7** expected synthetic outcomes:

- valid authorized reprocess retained;
- missing identity read fails closed;
- missing target read fails closed;
- unsupported identifier provenance fails closed;
- role/purpose inconsistency fails closed;
- human handoff without explicit public human-review reason fails closed;
- inactive output is never promoted.

Across qualification:

```text
S1 promotions              0
invented endpoints         0
invented handoffs          0
```

## Full factorial dry execution

The exact derived runner was materialized from the pinned parent bundle and executed with `--dry-run` across the complete frozen public geometry:

```text
EXPOSED_POOL groups              7
scenario families               11
agent-visible tickets           12
repetitions / ticket             3
common parents                 36 / 36 PASS
fixed arm outputs             144 / 144 PASS
same parent for all four arms  YES
arm-specific provider calls      0
private-oracle accesses          0
FRESH_BLIND accesses             0
LEGACY_LOCKED_TEST accesses      0
```

The four authorized arms remain exactly:

```text
A00 = E0 + S0
A10 = E1 + S0
A01 = E0 + S1
A11 = E1 + S1
```

Seeds remain `2026082304`, `2026082305`, `2026082306`.

## Authorization

The activation authorizes exactly:

`ONE_P12_C2_FACTORIAL_A00_A10_A01_A11_EXPOSED_POOL_COMMON_PARENT_GENERATION_EVALUATION_CYCLE`

The live cycle must generate **36 new common parents** and derive the **144 arm outputs** from those shared parents. P12-C1 outputs may not be reused as P12-C2 measurement.

A consumed P12-C2 generation job must not be rerun. P12 failure/replacement rules remain binding.

## Still not authorized

This activation does **not** authorize:

- semantic v4.2 scoring;
- FRESH_BLIND access;
- LEGACY_LOCKED_TEST access;
- final measurement;
- architecture freeze;
- production-readiness claims.

Passing this activation is an execution eligibility result, not evidence that any P12-C2 arm is good, qualified, preferred, or production-ready.

## Next step

Execute the **single authorized P12-C2 EXPOSED_POOL live factorial cycle**, freeze all 144 candidate outputs before private evaluator scoring, then apply the unchanged deterministic gates and preregistered factorial contrasts.
