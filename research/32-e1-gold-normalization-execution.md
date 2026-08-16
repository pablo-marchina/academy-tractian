# E1 — Gold Normalization / ScenarioSchema v1 Execution

Status: **IN PROGRESS — all scenarios source-normalized; human review still required before benchmark authority**

Date: **2026-08-16**

## Objective

Convert the delivered agent cases, machine reference paths and richer narrative scenarios into one source-faithful scenario representation without leaking evaluator-only material to the runtime agent and without pretending that one reference call sequence is the only correct trajectory.

## Reproducible pipeline

Implemented:

- `scripts/research/e1_normalize_gold.py`
- `research/schemas/scenario-v1-draft.schema.json`

The normalizer consumes only supplied artifacts plus the E0 normalized-contract candidate. It performs mechanical extraction and diagnostics, writes the full review-ready output to a private location, and emits a safe aggregate summary.

The private normalized gold is intentionally **not committed** while publication policy for partner evaluation material is unresolved.

## Source hashes for the current extraction

- `agent-input/cases.json`: `804b1269ad5cc6867c6f74d30fb985ff70af52a30ec207f0c60118e1fe677c0d`
- `eval/expected-paths.json`: `d6fb6186e4c035effe7dafa44758eaf40948ac334f0a91f8634a5731b7e0cb38`
- `eval/test-scenarios.md`: `c087660173b4b0a03857848f8fe4a1f262e3cbeb57e1d6044a917be07dcb53b9`
- E0 normalized contract candidate: `c15c44ac84f77a6efe0fe1a4ed1e35f02dcf24d72d66b04bb028b5cb67cb958c`

## E1.1 — Source-normalization result

The first pass extracted successfully:

- **16** narrative scenarios;
- **17** unique tickets represented by those scenarios;
- **10** primary split groups based on the bound asset/story context;
- all eight expected narrative sections for all 16 scenarios;
- zero parser-level missing-field issues.

For every scenario, the private draft preserves separately:

- agent-visible case input;
- bound company/user/asset context;
- machine reference gold;
- narrative objective;
- narrative policy statements;
- narrative reference trajectory;
- expected resolution text/label;
- variations;
- P1 success criterion;
- P2 metrics;
- provenance hashes and source location;
- machine-vs-narrative trajectory diagnostics.

Every record is marked:

`REQUIRES_HUMAN_REVIEW_BEFORE_BENCHMARK_USE`

No mechanically extracted oracle becomes benchmark truth automatically.

## E1.2 — Machine path is demonstrably incomplete as a standalone oracle

The source-normalization pass compares endpoint families in the narrative reference trajectory with the machine-readable `expected_path` material.

Result:

- **10 of 16 scenarios** contain an endpoint-set divergence between machine reference and narrative reference;
- **6 of 16** have matching endpoint families at this coarse diagnostic level.

This is not interpreted as ten broken scenarios. It confirms the package's own framing: the machine path is a compact reference, while narrative policy/P1 success criteria contain additional supervision.

Therefore exact machine-sequence equality is rejected as the canonical trajectory oracle.

## E1.3 — ScenarioSchema v1 draft changes driven by actual package data

The new draft schema separates concepts that were too generic in v0.

### Bound context

`user_id` and environment seed are explicitly runner-bound and not model-controlled.

### Scenario condition vs API response mode

The package uses labels such as `pending` and `stale` in evaluation data, while the API response-mode enum is only:

- complete;
- partial;
- inconclusive;
- conflict;
- unavailable.

ScenarioSchema v1 therefore does not overload those into one `mode` field.

### Decision oracle

The draft supports more precise outcomes while retaining high-level aggregation:

- ORIENT;
- INVESTIGATE;
- ACT_REPROCESS;
- ACT_REQUEST_SPECIALIST;
- ACT_UPDATE_CONFIG;
- ACT_REQUEST_RETRAINING;
- ESCALATE_HUMAN;
- ASK_CLARIFICATION;
- ABSTAIN.

### Policy oracle

Policy is separated from trajectory and can encode:

- required permissions;
- forbidden actions;
- resource/company scope;
- justification requirements;
- confirmation only when an authoritative scenario/source requires it.

Canonical delivered scenarios do not make confirmation universal, so the schema defaults to source-specific treatment rather than promoting kickoff guidance into hidden benchmark policy.

### Evidence oracle

Required evidence is represented independently from a single exact call sequence. This enables equivalent read trajectories to pass if they obtain the evidence demanded by the scenario policy/success criterion.

### Action oracle

Because actions are accepted events and do not persist state in the supplied environment, the v1 draft models:

- correct action type;
- correct target;
- required permission;
- accepted response;
- argument constraints;
- evidence-backed justification;
- duplicate action prohibition.

It does not require a state mutation the environment never persists.

### Conclusion oracle

Semantic conclusion facts and forbidden claims are separate from exact wording.

### Trajectory oracle

`reference_is_script` is fixed to false in the draft. Strict ordering/required-call constraints can still be added when an actual policy requires them.

## E1.4 — Privacy / benchmark-integrity handling

The private draft contains evaluator-only material. Accordingly:

- it is generated locally under ignored/private paths;
- only hashes, aggregate counts, schema and methodology are committed publicly;
- no expected resolution/reference trajectory is injected into runtime agent context;
- the final runner must keep gold loading in the evaluator process boundary.

## Human-review protocol

The next E1 pass is scenario-by-scenario review, not another automatic transformation.

For each of the 16 scenarios:

1. compare agent case, machine reference and narrative scenario;
2. mark every structured oracle field with its supporting source text;
3. separate required evidence from merely reference/diagnostic calls;
4. distinguish action requirement from optional recommendation;
5. translate P1 success criterion into minimal structured pass predicates;
6. identify claims that must be forbidden under incomplete/conflicting evidence;
7. confirm permission/resource constraints against the bound case user and executable API;
8. classify environment condition/override without conflating it with API response mode;
9. record any unresolved source conflict instead of deciding by inference;
10. set `benchmark_authoritative=true` only after review approval.

## Review order

To validate the schema across modalities before reviewing all 16, the first review batch should cover four different surfaces:

1. one investigation + human escalation story;
2. one knowledge/contextualization story;
3. one low-impact action story;
4. one high-impact action story.

If these four expose missing schema concepts, revise the draft schema before normalizing the remaining scenarios. This prevents repeating a flawed representation sixteen times.

## E1 exit conditions

- [x] source hashes recorded;
- [x] 16/16 narrative scenarios mechanically extracted;
- [x] 17/17 tickets mapped;
- [x] 10 split groups identified;
- [x] no missing expected narrative sections;
- [x] machine-vs-narrative trajectory divergence quantified;
- [x] ScenarioSchema v1 draft created from actual package needs;
- [ ] review first cross-modality batch and revise schema if necessary;
- [ ] human-review all 16 normalized oracles;
- [ ] explicitly resolve/log every machine-vs-narrative semantic discrepancy;
- [ ] freeze `ScenarioSchema-v1`;
- [ ] freeze reviewed normalized-gold manifest/hash;
- [ ] freeze leakage-aware benchmark split only after oracle review.

E1 is now **fully started and review-ready, but not yet benchmark-authoritative**.
