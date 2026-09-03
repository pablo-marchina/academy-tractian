# Semantic evaluation calibration design — 2026-09-03

## Decision question

How should Academy × TRACTIAN evaluate terminal response qualities that the deterministic production trace cannot prove, without turning an uncalibrated LLM judge into false authority?

## Existing baseline

`ProductionEvaluator` remains the primary production evaluator for properties observable from the trace. It already evaluates lifecycle, production identity/config, typed proposal validity, model-controlled field isolation, execution-chain integrity, policy containment, read-only action safety, provider-call provenance and terminal consistency. Its own contract intentionally does **not** claim semantic task correctness that is absent from public deterministic contracts.

The new semantic layer must therefore be additive and post-runtime. It must not weaken, replace or reinterpret deterministic safety checks.

## Evidence reviewed

1. Updated TRACTIAN TAPI and project requirement matrix: response quality, evidence use, escalation quality and customer-safe communication are material evaluation dimensions in addition to tool/argument/trajectory/safety checks.
2. Airbnb Engineering, *Eval-driven development: Lessons from evaluating GenAI at scale* (2026): recommends programmatic checks first, a small set of dimension-specific LLM judges, human-labelled calibration sets, explicit schemas, disagreement analysis, and high human agreement before trusting a virtual judge. Source: https://airbnb.tech/ai-ml/eval-driven-development-lessons-from-evaluating-genai-at-scale/
3. Mukherjee et al., *The Geometry of LLM-as-Judge: Why Inter-LLM Consensus Is Not Human Alignment* (2026): reports that strong inter-judge agreement can coexist with weak human alignment on subjective rubrics and that human-anchored calibration materially changes validity. Source: https://arxiv.org/abs/2606.03043
4. Han et al., *Judge's Verdict: A Comprehensive Analysis of LLM Judge Capability Through Human Agreement* (2025): argues that correlation alone is insufficient and uses agreement analysis including Cohen's kappa against human judgments. Source: https://arxiv.org/abs/2510.09738

## Alternatives

| Alternative | Benefit | Main failure mode | Decision |
| --- | --- | --- | --- |
| deterministic evaluator only | reproducible, free, auditable | cannot prove nuanced semantic quality | retain as mandatory Layer 1, insufficient alone |
| one monolithic LLM judge | simple | hides dimension-specific disagreement and can produce false confidence | reject |
| multiple LLM judges without human calibration | scalable | inter-LLM consensus is not evidence of human validity | reject |
| dimension-specific semantic judges + human calibration | nuanced and measurable | human-label cost and judge variability | **preferred candidate** |
| human-only evaluation | strongest judgment authority | not scalable for every regression run | required calibration/adjudication layer, not sole automation |

## Rubric v1

Only four dimensions are introduced because each corresponds to a material TAPI gap not already proven by the deterministic trace evaluator:

1. `groundedness`
2. `operational_usefulness`
3. `customer_safe_clarity`
4. `escalation_quality` — applicable only to escalation outputs

Each uses an ordinal 0/1/2 scale with explicit anchors. This keeps the judge task criterion-referenced and allows both exact-agreement and ordinal-error analysis.

## Calibration data boundary

Calibration records intentionally contain no raw prompt, raw response, chain-of-thought, credentials, identity, seed, account identifiers or private evaluator gold.

Pairing identity is:

```text
scenario_id
+ SHA256(terminal output)
+ response_mode
+ rubric dimension
```

Human reference records store only adjudicated score, resolution state and annotator count. Judge observations store only structured score/validity/error code and rubric hash. The agent/runtime never receives human labels.

## Metrics

Per dimension:

- expected and valid pair count;
- exact agreement;
- adjacent agreement;
- mean absolute ordinal error;
- quadratic-weighted Cohen's kappa;
- false-pass rate: judge=2 when human<2;
- false-fail rate: judge<2 when human=2;
- judge invalid/schema-failure rate;
- 3×3 confusion matrix.

Correlation alone is intentionally not an acceptance metric.

## State machine

```text
NOT_CALIBRATED
  structural mismatch, unresolved human labels, rubric mismatch, empty data

DESCRIPTIVE_ONLY
  structurally valid calibration data exists but no preregistered acceptance policy exists,
  or an explicit policy exists and the judge fails it

CALIBRATED_GATE
  structurally valid data + explicit preregistered policy + every dimension passes
```

`DESCRIPTIVE_ONLY` can be visualized and analyzed but **cannot affect EDD promotion or merge gating**.

## No implicit thresholds

The implementation deliberately defines no production threshold defaults. Thresholds must be preregistered as an explicit `SemanticCalibrationAcceptancePolicy` before the held-out calibration run.

Threshold selection itself follows a two-stage experimental process:

1. **rubric-development/pilot set**: collect representative good, partial and bad outputs; measure human-human disagreement; refine only rubric wording/examples and candidate judge configuration;
2. **freeze** rubric + judge configuration + acceptance policy;
3. **held-out group-aware calibration set**: evaluate once using scenario groups not used to tune the judge/rubric;
4. only a passing held-out report can become `CALIBRATED_GATE`.

This prevents choosing thresholds after seeing held-out judge performance.

## Human-label requirements before gating

- public/sanitized outputs only;
- representative complete/partial/inconclusive/conflicting/unavailable and escalation cases;
- include deliberately bad outputs so discrimination is measured;
- at least two independent labels where feasible, with unresolved disagreements explicitly marked and adjudicated before calibration;
- scenario-group split, not row-random leakage;
- human disagreement reported, not hidden;
- a final human adjudicator remains authoritative for ambiguous/high-impact examples.

## Judge-candidate experiment, later slice

No judge provider/model is selected by this design. Candidate judges must be compared under the same rubric, same frozen labelled set and same structured-output schema. Selection metrics include agreement/error above plus latency/resource/cost and invalid-output rate. `NO_SELECTION` is valid.

## Production integration rule

Even after calibration:

```text
runtime trace
→ deterministic ProductionEvaluator first
→ semantic evaluator post-runtime only where applicable
→ safe projected semantic checks
→ EDD aggregate/slices
```

A semantic pass can never override a deterministic safety/integrity failure. Private human labels and calibration references remain outside the agent-time and browser-safe product state.

## Reversal triggers

Recalibrate or demote a judge from `CALIBRATED_GATE` to descriptive-only if any of the following materially changes:

- rubric version/hash;
- judge model/provider/configuration;
- structured-output schema;
- observed failure distribution;
- production response modes/use cases;
- human disagreement profile;
- material judge drift on a fixed calibration subset.
