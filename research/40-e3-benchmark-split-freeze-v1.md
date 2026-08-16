# E3 — Benchmark Split Freeze v1

**Date:** 2026-08-16  
**Status:** FROZEN  
**Output:** `BENCHMARK-SPLIT-v1`

E3 freezes the development, validation and locked-test assignment across the ten asset/storyline groups identified in E1. It does not select a runtime, model, MCP topology, prompt, architecture or demo flow.

## Why group-level splitting is mandatory

The supplied benchmark has 16 scenarios, 17 tickets and only 10 independent asset/storyline groups. Several scenarios share the same industrial story and must remain in the same split to avoid leakage:

- `asset_G501`: CEN-01, CEN-10
- `asset_C710`: CEN-02, CEN-14
- `asset_S420`: CEN-03, CEN-16
- `asset_B204`: CEN-07, CEN-12
- `asset_V301`: CEN-08, CEN-13, CEN-15

A random scenario-level or ticket-level split would leak the same asset narrative across train/validation/test.

## Frozen assignment

| Split | Groups | Scenarios | Purpose |
|---|---:|---:|---|
| DEV | 5 | 8 | Build/debug the agent and run early B0-B3 experiments. |
| VALIDATION | 2 | 3 | Select/tune candidate approaches without touching locked test. |
| LOCKED_TEST | 3 | 5 | Final withheld evaluation only after architecture/model/prompt decisions. |

### DEV

| Group | Scenarios | Coverage role |
|---|---|---|
| `asset_G501` | CEN-01, CEN-10 | Missing data, baseline learning/invalidated, human escalation, over-escalation variant. |
| `asset_C710` | CEN-02, CEN-14 | Pending/delayed model behavior, `action_low`, request specialist, remote vs human escalation. |
| `asset_S420` | CEN-03, CEN-16 | False positive, specialist conflict, `action_high`, high-impact retreinamento. |
| `asset_M208` | CEN-04 | Symptom detection without baseline, partial evidence, knowledge support. |
| `asset_M101` | CEN-11 | Contextualization, procedure retrieval, source fidelity, baseline invalidation context. |

### VALIDATION

| Group | Scenarios | Coverage role |
|---|---|---|
| `asset_B204` | CEN-07, CEN-12 | Stale analysis, reprocess action, 400 negative case, glossary contextualization. |
| `asset_M102` | CEN-09 | Model coverage, `can_learn_baseline=false`, partial coverage, high-impact action candidate. |

### LOCKED_TEST

| Group | Scenarios | Coverage role |
|---|---|---|
| `asset_V301` | CEN-08, CEN-13, CEN-15 | Data quality vs confidence, baseline alarm threshold, `PATCH` criticity, 400/403 cases, high-impact action. |
| `asset_M605` | CEN-05 | Partial spectrum, missing frequency band, honesty under uncertainty. |
| `asset_M205` | CEN-06 | Conflicting diagnoses, automatic vs specialist evidence, conflict resolution. |

## Coverage rationale

The split deliberately prioritizes leakage protection over perfect balance. With only ten independent groups, perfect coverage in all three partitions is impossible.

The selected assignment preserves these properties:

1. every split has investigation coverage;
2. every split has contextualization coverage;
3. every split has execution/action coverage;
4. `LOCKED_TEST` retains a rich high-impact action family (`asset_V301`) plus uncertainty (`asset_M605`) and conflict (`asset_M205`);
5. DEV has enough action, escalation, false-positive, symptom and contextualization diversity to build the system without needing locked-test access;
6. VALIDATION contains both action/contextualization (`asset_B204`) and model coverage uncertainty (`asset_M102`), giving meaningful selection signal while leaving a stronger final holdout.

## Locked-test policy

Before final evaluation, `LOCKED_TEST` may be used only for:

- counting groups/scenarios;
- public metadata coverage inspection;
- programmatic leakage assertions.

It may not be used for:

- prompt tuning;
- model selection;
- runtime selection;
- agent policy debugging;
- architecture ablation;
- threshold fitting;
- optimizer feedback;
- manual inspection of evaluator-only gold beyond already frozen public metadata.

## Programmatic guard

The split is stored in:

```text
research/frozen/benchmark-split-v1.json
```

Leakage and coverage assertions are checked by:

```bash
python scripts/research/e3_validate_split.py --split research/frozen/benchmark-split-v1.json
```

The validator asserts:

- all 10 groups appear exactly once;
- all 16 scenarios appear exactly once;
- no group appears in multiple splits;
- every split has investigate/contextualize/execute coverage;
- aggregate counts match the manifest;
- locked-test selection is marked unavailable for architecture/model/prompt optimization.

## Known compromises

- `VALIDATION` has only two groups because preserving a meaningful locked final holdout is more important than equal-size partitions.
- Exact action endpoints are not duplicated across all splits; action *classes* and risk levels are covered instead.
- Contextualization appears in all splits but with different task families rather than identical retrieval patterns.
- `LOCKED_TEST` is intentionally rich; this raises final-test value but reduces validation breadth. This is acceptable because DEV already contains multiple action and escalation families.

**E3 is frozen.** Any split change now requires a new versioned `BENCHMARK-SPLIT` manifest and an explicit reason.
