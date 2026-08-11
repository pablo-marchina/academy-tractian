# Wave 3 — ScenarioSchema v0

Status: **FRAMEWORK-NEUTRAL RESEARCH CONTRACT / DOMAIN FIELDS PENDING API**

## Goal

Define the minimum scenario representation needed to build, evaluate, replay and perturb industrial-agent tasks without encoding one arbitrary trajectory as the only correct solution.

The schema is intentionally domain-generic until the TRACTIAN OpenAPI contract arrives.

## Design principles

1. **Goal state and policy are distinct from reference trajectory.** A correct agent may reach the same valid final state through a different sequence of read-only calls.
2. **Reference actions are optional.** They are only strict oracles when the scenario explicitly declares trajectory/action constraints.
3. **State, evidence, communication and policy have separate oracles.**
4. **Controlled pairs are first-class.** Example: same base task, only permission or evidence completeness changes.
5. **Leakage prevention is encoded.** Related variants share a `split_group_id`.
6. **Faults are declarative.** The runner can inject them independently of the task goal.
7. **No hidden chain-of-thought is required or stored.** Evaluation uses observable decisions, calls, results and state.

## Canonical shape

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

Represents behavior that must or must not happen even when the final state looks correct. This catches cases such as an unauthorized mutation followed by a compensating action.

### `evidence_oracle`

Represents facts/evidence required before a decision or claim. After the API arrives, entries should reference stable evidence IDs/predicates rather than prose when possible.

### `state_oracle`

Supported conceptual modes:

- `none`: no state mutation is part of the goal;
- `exact`: exact projected state equality;
- `predicate`: required predicates over final state;
- `reference`: compare to a stored expected-state artifact after normalization.

The final evaluator should compare a **projected** state where volatile/non-semantic fields (timestamps, generated IDs where irrelevant) are explicitly excluded, never silently ignored.

### `communication_oracle`

Used for claims/disclosures that cannot be inferred solely from final database state. Deterministic assertions should be preferred; semantic/LLM judging is a last resort and must be separately validated.

### `trajectory_oracle`

Default is `unconstrained`: a reference trajectory is diagnostic, not automatically the only correct path.

Use strict requirements only for actual policies such as:

- must check permission before mutation;
- must not call a forbidden endpoint;
- must obtain required evidence before action;
- must not repeat a non-idempotent mutation.

This follows the lesson from current tau2/tau3 evaluation tooling: a reference action trajectory can be used to derive/understand a target state, while equivalent state-achieving trajectories should not be penalized unless action-level reward/policy explicitly requires it.

## Controlled-pair design

For causal/adversarial comparisons, pairs should differ in the smallest meaningful feature:

- authorized vs unauthorized;
- complete vs partial evidence;
- fresh vs stale evidence;
- consistent vs conflicting evidence;
- mutation allowed vs mutation forbidden;
- sufficient context vs missing required parameter;
- healthy endpoint vs timeout/unavailable endpoint.

All variants of one base task MUST share `split_group_id`, so development/test splitting cannot leak nearly identical tasks.

## Versioning

- schema changes: `scenario-v0`, later `scenario-v1` after API-derived validation;
- scenario content changes require a change log;
- benchmark manifest records scenario-file hashes;
- API contract hash is mandatory once Swagger is available;
- a locked test scenario cannot be edited after final evaluation begins without invalidating/re-versioning the test set.

## Transition to v1 after onboarding

`scenario-v1` will be frozen only after we can map:

- real entity identifiers/schema paths;
- actual permissions/tenant semantics;
- state-query/reset capabilities;
- actual evidence quality/confidence/freshness fields;
- real mutation/high-impact action taxonomy;
- API fault representation.

## Primary source informing the design

- tau2/tau3 evaluation documentation: https://github.com/sierra-research/tau2-bench
- Original τ-bench paper: https://arxiv.org/abs/2406.12045
