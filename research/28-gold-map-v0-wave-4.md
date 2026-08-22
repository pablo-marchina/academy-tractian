# Wave 4 — GOLD-MAP-v0

Status: **CANONICAL-CASE INVENTORY / ORACLE NORMALIZATION PENDING v1**

Date: 2026-08-15

## Delivered evaluation corpus

The package contains:

- 17 agent-input cases in `agent-input/cases.json`;
- 17 machine-readable case records in `eval/expected-paths.json`;
- 16 richer narrative benchmark scenarios in `eval/test-scenarios.md` / `docs/test-scenarios.md`.

The 16 scenarios cover all 17 support tickets because one narrative scenario combines the stale-analysis investigation and the corresponding reprocess execution flow.

Case modality counts:

- Contextualizar: 3;
- Investigar: 9;
- Executar: 5.

## Agent-visible case fields

Each agent case currently contains only:

- `id`;
- `ticket_id`;
- `company_id`;
- `user_id`;
- `asset_id`;
- `message`.

This is a clean input boundary. It does **not** include root cause, expected mode, reference trajectory or target resolution.

## Evaluation-only fields

`eval/expected-paths.json` contains:

- `id`;
- `ticket_id`;
- `root_question`;
- `mode`;
- `expected_path`.

Important semantic warning: the `mode` field is a **scenario label**, not always an API envelope mode. It includes values such as `pending` and `stale`, which are analysis/scenario states rather than members of the API response-mode enum. ScenarioSchema v1 should rename/separate this field instead of overloading `mode`.

## Machine path statistics

Across the 17 machine-readable references:

- 57 total reference steps;
- mean path length: ~3.35;
- median: 4;
- minimum: 1;
- maximum: 5;
- 50 GETs;
- 6 POSTs;
- 1 PATCH.

The gold is therefore small enough for detailed trace-level evaluation but too small for careless train/test splitting or large statistical claims without controlled variants/repetitions.

## Reference trajectory is explicitly not a script

The supplied scenario documentation states that the expected trajectory is a **reference**, not a mandatory script. The goal is to satisfy the scenario's success criterion and policies.

Therefore evaluation should not use raw sequence exact-match as the main trajectory metric.

Correct design:

- required evidence/tools when semantically necessary;
- forbidden tools/actions;
- action ordering when a policy genuinely requires it;
- redundant/unnecessary calls as efficiency signals;
- reference trajectory distance as diagnostic information;
- final conclusion/action correctness as a separate oracle.

Equivalent valid read-only paths should remain passable.

## `expected-paths.json` is a minimal reference, not the complete oracle

The narrative scenarios are materially richer than the machine-readable paths.

Examples of divergence:

- break-without-warning narrative includes analysis + model coverage reads that the machine path omits;
- rising-RMS narrative includes data-quality investigation and recommends/executes reprocess, while the machine path stops after model inspection;
- electrical-vs-mechanical narrative includes analysis detail, asset electrical configuration and knowledge guidance, while the machine path contains only RMS + spectrum;
- stale-analysis narrative includes RMS verification and post-action validation, while machine paths omit those steps;
- human-escalation machine path contains only the escalation action, while the narrative scenario expects the context investigation before escalating.

Therefore:

> `expected-paths.json` must not be treated as a complete strict gold trajectory.

ScenarioSchema v1 should merge machine and narrative supervision into separate oracle fields.

## Final conclusion is not currently machine-readable

The kickoff suggested target final output/conclusion would be provided. In the delivered package, the machine JSON does **not** contain a structured final answer or conclusion field.

The richer `test-scenarios.md` contains, per scenario:

- objective;
- policy;
- reference trajectory;
- expected resolution;
- variations;
- P1 success criterion;
- P2 metrics.

Therefore final-answer evaluation requires a normalization step that converts the narrative expected resolution/P1 criterion into structured oracles such as:

```yaml
conclusion_oracle:
  required_facts: []
  required_decision: null
  forbidden_claims: []
  uncertainty_required: false

action_oracle:
  required_action: null
  forbidden_actions: []
  required_permission: null
  required_justification_facts: []
```

This normalization must be human-reviewed once before it becomes benchmark ground truth.

## Shared-asset leakage risk

The 17 cases use only **10 unique primary assets**. Several assets occur in related investigation/execution/context cases.

Examples:

- G501 -> investigation + escalation;
- C710 -> delayed insight + specialist request;
- S420 -> false positive + retraining;
- B204 -> stale post-maintenance analysis + reprocess + BPFO context;
- V301 -> data-quality trust + RMS threshold + criticality change.

A random case split could therefore place nearly identical asset facts in development and locked test.

### Split rule candidate

At minimum, benchmark splitting should be **group-aware by `asset_id` or explicit storyline group**, not independent per ticket.

However, because there are only 10 asset groups and action types are sparse, the exact split must be chosen carefully to preserve evaluation coverage. Do not freeze the proportions until we inspect the capability/action stratification.

## Canonical evaluation modes unlocked by deterministic seeds

The actual API supports a cleaner experimental decomposition than we could define pre-artifact.

### A. Canonical task correctness

- fixed scenario environment;
- `seed=complete` where no scenario override exists;
- scenario overrides remain active;
- compare agent to normalized gold oracles.

### B. Environment robustness

- choose explicit deterministic seeds that induce targeted `partial`, `inconclusive`, `conflict`, or `unavailable` modes;
- keep agent/model config fixed;
- measure robustness drop and decision changes.

### C. Agent/model reliability

- hold the exact same environment seed/observations fixed;
- repeat the agent run `k` times;
- measure consistency/pass-style reliability.

This separates API variation from agent/model variation instead of mixing them.

## Controlled-pair opportunities from supplied cases

The data directly supports project-authored controlled variants such as:

- permission allowed vs denied;
- valid vs invalid justification;
- same diagnosis with complete vs partial evidence;
- good vs below-model-requirement data quality;
- established vs invalidated/learning baseline;
- supported-and-learnable vs supported-but-not-learnable model coverage;
- conclusive vs inconclusive spectrum evidence;
- remote-resolvable vs human-escalation case.

Generated variants must remain linked to the same base `split_group_id` to prevent leakage.

## Action oracle semantics

Because supplied action endpoints are accepted-event simulations rather than persistent state mutations, action correctness should be evaluated using:

1. correct decision to act/not act;
2. correct endpoint;
3. correct target resource;
4. permission/policy compliance;
5. argument/schema validity;
6. evidence-backed justification;
7. API `accepted=true` when execution is expected;
8. no duplicate/unnecessary action calls.

Do not require final-state equality that the supplied API cannot expose.

## Escalation evaluation

The package provides two distinct concepts:

- `request-specialist` — internal technical specialist action (`action_low`);
- `cases/{id}/escalate` — human/field escalation (`escalate`).

This makes over/under-escalation measurable and allows a more precise confusion matrix than a single generic `ESCALATE` label.

Suggested decision taxonomy for v1:

- ORIENT;
- INVESTIGATE;
- ACT_REPROCESS;
- ACT_REQUEST_SPECIALIST;
- ACT_UPDATE_CONFIG;
- ACT_REQUEST_RETRAINING;
- ESCALATE_HUMAN;
- ASK_CLARIFICATION;
- ABSTAIN.

The high-level `ASK / INVESTIGATE / ACT / ABSTAIN / ESCALATE` taxonomy can remain for aggregate reporting.

## Gold normalization required before final benchmark

Next step is not to hard-code exact trajectories. It is to create **ScenarioSchema v1** by extracting and reviewing, for each scenario:

- input/provenance;
- allowed/required/forbidden decisions;
- evidence requirements;
- action requirements;
- permission constraints;
- conclusion facts;
- uncertainty/honesty requirements;
- acceptable equivalent trajectories;
- fault/seed profile;
- split group.

Only after this normalization should automated metric code be considered benchmark-authoritative.
