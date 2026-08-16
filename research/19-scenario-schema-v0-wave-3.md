# Wave 3 — ScenarioSchema v0

Status: **SUPERSEDED AS DOMAIN-GENERIC RESEARCH CONTRACT / v1 NORMALIZATION NOW UNLOCKED BY WAVE 4**

This file records the pre-artifact scenario contract that intentionally avoided inventing TRACTIAN semantics. It remains useful as design history, but the delivered package now provides the real API/case/eval structure and requires ScenarioSchema v1 normalization.

## Goal

Define the minimum scenario representation needed to build, evaluate, replay and perturb industrial-agent tasks without encoding one arbitrary trajectory as the only correct solution.

## Design principles preserved after artifact delivery

1. **Goal/conclusion and policy are distinct from reference trajectory.** The delivered scenario docs explicitly confirm that trajectory is a reference, not a script.
2. **Reference actions are diagnostic unless policy/success criterion makes them required.**
3. **State, evidence, communication and policy have separate oracles.**
4. **Controlled pairs are first-class.**
5. **Leakage prevention is encoded.** Related variants share a `split_group_id`.
6. **Faults/environment modes are declarative.**
7. **No hidden chain-of-thought is required or stored.** Evaluation uses observable decisions, calls, results and state.

## Original canonical shape

```yaml
schema_version: scenario-v0
scenario_id: industrial.asset.example.001
family: placeholder_until_api
split_group_id: base-example-001
pair:
  pair_id: optional-controlled-pair
  variant: authorized
  controlled_changes: [actor.permissions]

provenance:
  source: authored
  api_contract_hash: null
  created_at: null
  reviewed_by: []

tags: []
difficulty: null
risk:
  mutation: false
  high_impact: false
  class: unknown

actor:
  actor_id: synthetic-user
  tenant_id: synthetic-company
  role: null
  permissions: []

conversation:
  initial_request: "..."
  prior_turns: []

initial_state:
  mode: reference
  snapshot_ref: null
  state_hash: null
  fixtures: null

policy_oracle:
  allowed_decisions: [ASK, INVESTIGATE, ACT, ABSTAIN, ESCALATE]
  required_decisions: []
  forbidden_decisions: []
  required_tools: []
  allowed_tools: []
  forbidden_tools: []
  required_actions: []
  forbidden_actions: []
  preconditions: []

evidence_oracle:
  required_evidence: []
  acceptable_evidence_sets: []
  freshness_requirements: []
  conflict_requirements: []

state_oracle:
  mode: none
  expected_state_ref: null
  predicates: []
  ignored_paths: []

communication_oracle:
  required_facts: []
  forbidden_claims: []
  required_disclosures: []

trajectory_oracle:
  mode: unconstrained
  reference_actions: []
  max_tool_calls: null
  max_turns: null
  forbidden_patterns: []

fault_profile:
  id: clean
  injections: []

limits:
  wall_time_s: null
  max_model_calls: null
  max_tool_calls: null

metadata:
  notes: null
```

## Oracle semantics

### `policy_oracle`

Represents behavior that must or must not happen even when the final conclusion looks correct. This is still essential for unauthorized/cross-company/invalid actions.

### `evidence_oracle`

Represents facts/evidence required before a decision or claim. Wave 4 now allows these to reference actual resources and scenario policies.

### `state_oracle`

The pre-API schema allowed exact/predicate/reference final state. Wave 4 found that the supplied action endpoints **do not persist state mutations**, so ScenarioSchema v1 must not require final-state equality for those actions. Instead it should use an action/event oracle (`accepted=true`, correct target/args/policy/no duplicate) while retaining state oracles only where observable state semantics genuinely support them.

### `communication_oracle`

Still needed because the partner target is semantic/operational conclusion, not exact wording.

### `trajectory_oracle`

Default remains `unconstrained/reference`: the delivered narrative scenarios explicitly say the trajectory is a reference, not a script.

## Controlled-pair design

Still valid, now grounded by the actual API:

- authorized vs unauthorized;
- same-company vs cross-company target;
- valid vs invalid action arguments;
- complete vs partial evidence;
- fresh vs stale analysis state;
- consistent vs conflict response;
- sufficient vs inconclusive evidence;
- healthy vs unavailable response mode.

All variants of one base task must share `split_group_id`.

## Wave 4 changes required for ScenarioSchema v1

Actual artifacts reveal additional distinctions:

- `agent-input` and eval gold must be physically/logically separated;
- case user/company/asset IDs are runtime-bound context;
- API `seed` is evaluator/environment configuration, never model input;
- eval JSON `mode` is overloaded (`pending`/`stale` vs API response modes) and must be split into separate fields;
- only 10 primary asset/story groups support 17 cases, so `split_group_id` should default to asset/storyline grouping rather than ticket ID;
- machine expected paths are incomplete relative to narrative scenario policies/P1 success criteria;
- final conclusions must be normalized from narrative text into human-reviewed structured facts/decisions;
- action oracle must model accepted execution event rather than persistent final state;
- confirmation is not a universal canonical action requirement in delivered scenarios and should remain a separate safety extension unless clarified.

## Transition to v1

`scenario-v1` should be frozen only after human review of all 16 narrative scenarios / 17 cases into:

- bound actor/company/asset context;
- scenario condition vs API response-mode profile;
- required/allowed/forbidden decisions;
- evidence requirements and acceptable alternatives;
- action endpoint/target/permission/argument/justification requirements;
- structured conclusion facts;
- escalation/uncertainty requirements;
- reference trajectory diagnostics;
- asset/storyline split group;
- source hashes and normalization provenance.

See `28-gold-map-v0-wave-4.md` and `30-post-artifact-experiment-program-wave-4.md`.