# E1 — Gold Normalization / ScenarioSchema v1 Execution

**Status: FROZEN**  
**Date:** 2026-08-16

## Result

E1 froze the benchmark semantics and grouping constraints required by E2.

Source normalization confirms:

- 16 narrative scenarios;
- 17 unique tickets;
- 10 primary asset/story groups;
- all eight required narrative sections present for all 16 scenarios;
- 17/17 agent cases and 17/17 machine gold tickets mapped.

The supplied scenario audit states that all 16 scenarios sustain their expected resolution after API validation and that the 39 supplied API assertions remain green in the partner environment. This is retained as partner-source evidence; it is not represented as an independent rerun in the current environment.

## Frozen semantic decisions

- `expected-paths.json` is reference supervision, not exact trajectory gold;
- narrative policy/P1 success/expected resolution can add constraints missing from the compact machine path;
- equivalent evidence trajectories are allowed when required predicates are satisfied;
- identity and seed are runner-bound;
- accepted action events are not treated as persistent state mutation;
- action oracles separately represent required/forbidden/optional execution, target, permission, justification and duplicate-action constraints;
- conclusion evaluation is fact/claim based rather than exact wording match;
- uncertainty/conflict behavior is explicit;
- `ACT_REQUEST_SPECIALIST` is distinct from `ESCALATE_HUMAN`;
- universal confirmation is not canonical because delivered scenarios do not encode it universally.

## Frozen leakage groups

- `asset_G501`: CEN-01, CEN-10
- `asset_C710`: CEN-02, CEN-14
- `asset_S420`: CEN-03, CEN-16
- `asset_M208`: CEN-04
- `asset_M605`: CEN-05
- `asset_M205`: CEN-06
- `asset_B204`: CEN-07, CEN-12
- `asset_V301`: CEN-08, CEN-13, CEN-15
- `asset_M102`: CEN-09
- `asset_M101`: CEN-11

These are grouping constraints only. Dev/validation/locked-test assignment remains E3.

## Source hashes

- `agent-input/cases.json`: `804b1269ad5cc6867c6f74d30fb985ff70af52a30ec207f0c60118e1fe677c0d`
- `eval/expected-paths.json`: `d6fb6186e4c035effe7dafa44758eaf40948ac334f0a91f8634a5731b7e0cb38`
- `eval/test-scenarios.md`: `c087660173b4b0a03857848f8fe4a1f262e3cbeb57e1d6044a917be07dcb53b9`
- normalized contract dependency: `c15c44ac84f77a6efe0fe1a4ed1e35f02dcf24d72d66b04bb028b5cb67cb958c`

## Exit

All E1 exit conditions are satisfied. The gold remains private; only schemas, hashes, grouping metadata and methodology are public.

**Any material oracle change requires a new ScenarioSchema/Gold version and documented source-backed change.**
