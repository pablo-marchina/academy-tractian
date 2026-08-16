# E1 — Gold / ScenarioSchema v1 Freeze

**Status:** FROZEN  
**Date:** 2026-08-16  
**Scope:** scenario representation, oracle semantics and leakage grouping. The actual evaluator-only gold remains private.

## Evidence basis

The supplied TRACTIAN package contains:

- 17 agent-input cases;
- 16 narrative evaluation scenarios;
- 17 unique tickets;
- 10 primary asset/story groups;
- all eight required narrative sections for all 16 scenarios;
- an explicit scenario audit table stating that all 16 scenarios sustain their expected resolution after API validation and that the 39 supplied API assertions remain green in the partner environment.

Our independent structural pass additionally confirms 16/16 scenario sections, 17/17 ticket coverage and the 10 asset/story split groups.

The partner audit is retained as source evidence; it is not silently represented as an independent rerun of the 39 tests in this environment.

## Frozen semantic decisions

1. The machine-readable expected path is **reference supervision**, not an exact trajectory script.
2. Narrative policy, P1 success criteria and expected resolution are authoritative inputs to oracle construction when they add constraints missing from the compact machine path.
3. Equivalent evidence-gathering trajectories may pass when they satisfy required evidence/policy predicates.
4. Identity (`user_id`) and evaluation seed are runner-bound and never model-controlled.
5. Canonical action success uses the supplied environment's `accepted_event_non_persistent` semantics; final-state equality is not required unless a future environment explicitly persists the mutation.
6. Action oracles distinguish required, forbidden and optional execution and record target, permission, justification and duplicate-action constraints.
7. Conclusion evaluation is fact/claim based rather than exact response-text matching.
8. Uncertainty/conflict behavior is represented explicitly; the agent is not rewarded for unsupported certainty.
9. `ACT_REQUEST_SPECIALIST` is distinct from `ESCALATE_HUMAN`.
10. Universal requester confirmation is **not** promoted into canonical scenario policy because the delivered scenarios do not encode it universally; it remains a separate safety extension.

## Frozen leakage groups

| Split group | Scenarios |
|---|---|
| `asset_G501` | CEN-01, CEN-10 |
| `asset_C710` | CEN-02, CEN-14 |
| `asset_S420` | CEN-03, CEN-16 |
| `asset_M208` | CEN-04 |
| `asset_M605` | CEN-05 |
| `asset_M205` | CEN-06 |
| `asset_B204` | CEN-07, CEN-12 |
| `asset_V301` | CEN-08, CEN-13, CEN-15 |
| `asset_M102` | CEN-09 |
| `asset_M101` | CEN-11 |

These groups are frozen as **grouping constraints**, not as train/validation/test assignments. Assignment is E3 and must occur before architecture/model/prompt optimization.

## Frozen source manifest

- `agent-input/cases.json`: `804b1269ad5cc6867c6f74d30fb985ff70af52a30ec207f0c60118e1fe677c0d`
- `eval/expected-paths.json`: `d6fb6186e4c035effe7dafa44758eaf40948ac334f0a91f8634a5731b7e0cb38`
- `eval/test-scenarios.md`: `c087660173b4b0a03857848f8fe4a1f262e3cbeb57e1d6044a917be07dcb53b9`
- normalized contract dependency: `c15c44ac84f77a6efe0fe1a4ed1e35f02dcf24d72d66b04bb028b5cb67cb958c`

## Exit checklist

- [x] 16/16 scenarios structurally normalized
- [x] 17/17 tickets mapped
- [x] 10 leakage groups frozen
- [x] narrative/machine trajectory divergence treated as diagnostic rather than exact-match gold
- [x] action persistence semantics represented correctly
- [x] identity/seed isolation represented
- [x] decision/evidence/policy/conclusion/action/trajectory oracle layers defined
- [x] partner scenario audit incorporated as source evidence
- [x] private gold remains outside public repository

**E1 is frozen.** Any substantive oracle change requires a new ScenarioSchema/Gold version and a documented source-backed change.
