# Observability & Trace Contract — Wave 2

Status: **PROVISIONAL RESEARCH CONCLUSION — backend not selected**

Research questions: R16 (observability), R17 (trace schema), R18 (backend), R19 (reproducibility)

## 1. Research conclusion

Observability must be designed **before baseline implementation**. The project should own a framework-neutral trace contract and export it through OpenTelemetry-compatible instrumentation. A visualization/observability backend is downstream infrastructure, not the canonical source of experiment truth.

This prevents the project from becoming locked to one agent framework or vendor-specific trace format and allows fair runtime/model comparisons.

## 2. Why OpenTelemetry-first

OpenTelemetry provides a vendor-neutral trace/metric/log model and W3C trace-context propagation. The GenAI semantic conventions now live in the dedicated `open-telemetry/semantic-conventions-genai` project, but several GenAI/agent conventions remain under active development.

Therefore:

1. use standard OTel attributes where stable/applicable;
2. **pin the semantic-convention version** used by experiments;
3. maintain project-owned `tractian.*` attributes for critical experimental semantics;
4. do not make the experiment database depend on unstable convention names;
5. retain raw structured run/evaluation artifacts outside the UI backend.

The current MCP 2026-07-28 specification also aligns with W3C trace propagation, which is useful if MCP is adopted later.

## 3. Canonical trace hierarchy

Proposed logical structure:

```text
run / scenario trace
│
├── request-understanding span/event
├── planning/decision span
├── evidence acquisition span(s)
│    └── tool/API span(s)
├── policy/precondition span/event
├── model inference span(s)
├── action proposal span
├── mutation gate span (if relevant)
├── mutation/API span (if authorized)
├── postcondition verification span
└── final response span

Offline evaluator annotations
└── linked by experiment_id / scenario_id / run_id / trace_id
```

Not every runtime must expose exactly these internal nodes. The canonical requirement is that equivalent semantically important events are observable and comparable.

## 4. Required run identity

Every run must be reproducibly addressable:

```yaml
experiment_id:
scenario_id:
scenario_version:
run_id:
trace_id:
config_hash:
agent_version:
api_contract_hash:
dataset_version:
fault_profile_id: null
```

A result without these fields is not acceptable as experimental evidence.

## 5. Project-specific telemetry namespace

Proposed `tractian.*` semantics. Exact field representation (span attribute vs event vs artifact) will be finalized after cardinality/privacy review.

### Run/scenario

- `tractian.experiment.id`
- `tractian.scenario.id`
- `tractian.scenario.version`
- `tractian.run.id`
- `tractian.config.hash`
- `tractian.dataset.version`
- `tractian.api.contract_hash`
- `tractian.agent.version`
- `tractian.fault.profile`

### Decision semantics

- `tractian.decision.type`: `ask | investigate | act | abstain | escalate | respond`
- `tractian.decision.reason_code`
- `tractian.stop.reason`
- `tractian.escalation.reason_code`

### Tool/action semantics

- `tractian.tool.canonical_name`
- `tractian.tool.mutation`: boolean
- `tractian.tool.risk_class`
- `tractian.tool.permission_required`
- `tractian.tool.idempotency_class`

### Policy semantics

- `tractian.policy.decision`: `allow | deny | require_approval | escalate`
- `tractian.policy.rule_ids`
- `tractian.policy.preconditions_passed`

### Evidence semantics

High-cardinality evidence identifiers should generally be events/artifact references rather than indiscriminate span attributes.

- evidence reference IDs;
- source endpoint/resource;
- observed timestamp;
- freshness class;
- quality/confidence/limitation metadata when the API exposes it;
- conflict flag/group;
- evidence selected vs observed.

### State semantics

Prefer hashes/version IDs instead of dumping full state into span attributes:

- `tractian.state.before_hash`
- `tractian.state.after_hash`
- `tractian.state.version`
- postcondition pass/fail

## 6. Content and privacy policy

Official OTel GenAI conventions warn that prompts, outputs, tool arguments and tool results can contain sensitive data. The project should therefore default to metadata-first tracing.

Hard rules:

- never record credentials, bearer tokens, API keys or auth headers;
- never expose connector/provider secrets in traces;
- use synthetic TAPI data as allowed by the project, but still apply redaction discipline;
- record raw prompt/tool payloads only in an explicitly enabled experiment mode;
- prefer payload hashes, IDs and bounded previews where full content is not required;
- separate raw-content storage from trace metadata;
- make redaction deterministic and tested;
- dashboard must not become a secret exfiltration surface.

## 7. Trace completeness test

Every runtime finalist must pass the same synthetic contract test.

Given one scenario containing:

1. user request;
2. read-only tool;
3. model decision;
4. policy check;
5. mutating tool;
6. postcondition check;
7. final answer;

we must be able to reconstruct from exported evidence:

- which model/config ran;
- what canonical tool was selected;
- validated arguments/reference;
- whether a mutation was proposed;
- policy result before execution;
- whether the external action actually executed;
- state before/after reference;
- latency and token/call accounting where provider supplies it;
- error/retry chain;
- final run result;
- evaluator results linked to the run.

If a framework cannot provide this without invasive hacks, that is a negative runtime-selection signal.

## 8. Backend candidate analysis

### Phoenix

Strengths from official documentation:

- open-source/self-hostable;
- OpenTelemetry/OpenInference-centered tracing;
- datasets, evaluations and experiments;
- experiment repetition/splits;
- suitable for trace inspection and evaluation workflows.

Risk:

- Phoenix has evolved rapidly and has had breaking releases; pin exact version and avoid using backend-internal schema as canonical project format.

### Langfuse

Strengths from official documentation:

- open-source/self-hosting path;
- OTel ingestion;
- traces, datasets, experiments/evaluators;
- broad LLM-observability workflow.

Research note:

- verify exact local/self-host resource footprint and dataset/experiment semantics against our intended offline runner. Some SDK workflows differ in how local dataset execution maps to server-side dataset runs.

### Framework-native tracing

Useful for debugging but should be considered supplementary because it would bias runtime comparison and reduce portability.

### Decision state

**No backend selected yet.**

Run a local spike after the trace contract is implemented once. Export the same trace dataset to Phoenix and Langfuse and compare:

- OTLP ingestion fidelity;
- ability to inspect nested tool/policy/action spans;
- evaluator annotation workflow;
- experiment comparison UX;
- local storage/resource footprint;
- exportability/data ownership;
- setup complexity;
- replay/debug utility.

## 9. Canonical experiment artifacts vs observability backend

The backend is for visualization and diagnosis. Canonical research artifacts should be project-owned, versioned and machine-readable, e.g.:

```text
artifacts/
  experiments/<experiment_id>/
    manifest.json
    runs.parquet
    decisions.parquet
    tool_calls.parquet
    evaluations.parquet
    failures.parquet
    traces/
      <run_id>.jsonl   # normalized export or references
```

Exact persistence format is not frozen, but the principle is.

This lets us:

- rerun statistics without a UI service;
- migrate observability backends;
- reproduce figures;
- compare traces produced by different runtimes;
- audit evaluator changes independently from agent execution.

## 10. Trace/event design rule

Do not turn every value into a span attribute.

Use:

- low-cardinality query/filter dimensions as attributes;
- high-cardinality lists/payloads as structured events/artifact references;
- large raw model/tool content in controlled artifact storage;
- metrics derived offline from canonical run records.

This avoids cardinality explosions and accidental data leakage.

## 11. Derived metrics

Telemetry should support deriving, without parsing free-form logs:

- end-to-end latency;
- model latency;
- API/tool latency;
- number of model calls;
- tool-call count;
- read vs mutation count;
- retry count;
- policy denials;
- escalation/abstention rate;
- token input/output where exposed;
- evidence count and conflict count;
- trajectory length;
- pre-action verification overhead;
- infrastructure-error rate.

## 12. Reproducibility requirements

Every experiment manifest must capture:

- git commit SHA;
- environment/container version;
- Python/package lock hash;
- model/provider exact identifier;
- generation parameters;
- prompt/policy/tool-contract versions;
- API contract hash;
- scenario/dataset version;
- seed if supported, with no false determinism claim when unsupported;
- observability semantic-convention version;
- fault profile;
- start/end timestamp.

## 13. Provisional decision

**OTel-first, framework-neutral trace contract is strongly recommended. Backend remains open.**

This is an architectural constraint for the runtime spike, not a runtime choice.

## 14. Open dependencies

- exact TRACTIAN API auth/data sensitivity;
- API trace/correlation IDs if any;
- whether synthetic payload capture is contractually unrestricted;
- MCP use/no-use decision;
- exact model provider token-usage metadata;
- final local resource constraints.
