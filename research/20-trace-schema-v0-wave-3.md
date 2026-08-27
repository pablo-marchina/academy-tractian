# Wave 3 — TraceSchema v0

Status: **FRAMEWORK-NEUTRAL CANONICAL EXPERIMENT TRACE**

## Goal

Define what every run must emit regardless of agent runtime or observability backend, so evaluations remain comparable and reproducible.

OpenTelemetry is the transport/semantic interoperability layer. It is **not** the canonical database schema for the experiment because GenAI agent semantic conventions are still evolving.

## Core rule

The project owns a stable versioned namespace (`tractian.*`) and maps it to currently applicable OpenTelemetry/GenAI attributes where useful.

Phoenix, Langfuse, LangSmith, OpenAI tracing or any other UI is downstream. Losing/changing the UI must not destroy our experiment record.

## No hidden chain-of-thought capture

The trace stores **observable execution artifacts**:

- user-visible input/output when capture policy allows;
- structured decisions (`ASK`, `INVESTIGATE`, `ACT`, `ABSTAIN`, `ESCALATE`);
- tool proposals and validated arguments;
- policy/authorization decisions;
- tool executions/results;
- state/evidence references and hashes;
- retries/faults;
- model/provider metadata and token/latency statistics;
- evaluator outputs.

It must not require or attempt to persist private hidden reasoning/chain-of-thought. If a provider explicitly returns a user-visible reasoning summary, it is treated as ordinary model output subject to the same redaction policy, not as canonical correctness evidence.

## Run-level manifest

Mandatory fields:

```yaml
trace_schema_version: trace-v0
experiment_id:
scenario_id:
run_id:
conversation_id:
config_hash:
git_commit:
scenario_hash:
api_contract_hash:
policy_version:
tool_contract_version:
runtime:
  name:
  version:
model:
  provider:
  model_id:
  reported_version:
  parameters_hash:
seed:
  requested:
  provider_guarantee: unknown
fault_profile_id:
started_at:
ended_at:
status:
```

## Project-owned span/event attributes

### Identity/versioning

- `tractian.experiment.id`
- `tractian.scenario.id`
- `tractian.run.id`
- `tractian.conversation.id`
- `tractian.config.hash`
- `tractian.git.commit`
- `tractian.scenario.hash`
- `tractian.api.contract_hash`
- `tractian.policy.version`
- `tractian.tool_contract.version`

### Agent decisions

- `tractian.decision.type`
- `tractian.decision.sequence`
- `tractian.stop.reason`
- `tractian.escalation.reason_code`

### Tool/action semantics

- `tractian.tool.id`
- `tractian.tool.mutation`
- `tractian.tool.high_impact`
- `tractian.tool.risk_class`
- `tractian.tool.call_id`
- `tractian.tool.transport` (`native`, `mcp`, etc.)

### Policy/safety

- `tractian.policy.decision`
- `tractian.policy.rule_ids`
- `tractian.permission.result`
- `tractian.approval.required`
- `tractian.approval.result`

### Evidence/state

- `tractian.evidence.ids`
- `tractian.evidence.status`
- `tractian.state.before_hash`
- `tractian.state.after_hash`
- `tractian.state.version`

### Fault/recovery

- `tractian.fault.profile`
- `tractian.fault.injection_id`
- `tractian.retry.number`
- `tractian.recovery.outcome`

### Evaluation

- `tractian.eval.name`
- `tractian.eval.version`
- `tractian.eval.outcome`
- `tractian.failure.code`
- `tractian.failure.severity`

## Canonical span/event taxonomy

A runtime adapter should map its native trace to these logical operations:

1. `run`
2. `model.request`
3. `decision`
4. `tool.proposal`
5. `policy.check`
6. `approval`
7. `tool.execute`
8. `state.observe`
9. `retrieval` (only if retrieval exists)
10. `fault`
11. `retry`
12. `final_response`
13. `evaluation`

Not every run needs every span. Missing mandatory spans for an operation that actually occurred counts against trace completeness.

## OpenTelemetry mapping

Current GenAI semantic conventions have agent/workflow/plan/tool operations, including `invoke_agent`, `invoke_workflow`, `plan`, `execute_tool` and retrieval/memory operations. Their status is still Development in key agent documents.

Therefore:

- use standard OTel trace/span IDs and W3C Trace Context;
- map model/tool spans to GenAI conventions where stable/applicable;
- preserve `tractian.*` semantics as the project contract;
- record the semantic-convention/schema version used by each run;
- never let an upstream semantic-convention rename invalidate historical experiment artifacts.

## MCP trace propagation

If the MCP adapter is enabled, preserve W3C `traceparent`, `tracestate` and baggage according to the current MCP revision. A native tool call and its MCP equivalent should be joinable into the same logical run tree.

## Sensitive-content policy

Default: **metadata first, content minimized**.

- credentials/tokens never recorded;
- permission/auth headers never recorded raw;
- payload bodies captured only when necessary for evaluation and permitted by the synthetic-data environment;
- prefer hashes/artifact references to duplicating payloads in span attributes;
- arbitrary high-cardinality/full content is stored in versioned artifacts, not metric labels;
- redaction must be deterministic and tested;
- actual API payloads will be reviewed after onboarding before finalizing `trace-v1`.

## Trace completeness metric

For each scenario, derive expected observable operations from the executed path and compute:

- mandatory operation spans present;
- mandatory project attributes present;
- parent/child continuity valid;
- proposal → policy → execution linkage valid for mutations;
- state before/after linkage valid where applicable;
- evaluator can reconstruct tool sequence and decisions from the normalized trace alone.

Do not collapse trace completeness into overall task correctness; report separately.

## Runtime spike requirement

Each finalist must convert its native instrumentation to the same `trace-v0` representation. A framework-specific tracing UI is allowed only as an additional view.

## Transition to TraceSchema v1

Freeze after:

- real TRACTIAN payload/redaction review;
- actual tool/entity metadata mapping;
- runtime spike confirms all finalists can emit the required fields;
- backend export spike confirms lossless-enough rendering;
- cardinality/storage footprint is measured.

## Primary/official sources

- OpenTelemetry GenAI conventions repository: https://github.com/open-telemetry/semantic-conventions-genai
- Agent/framework spans: https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md
- OpenTelemetry semantic-conventions releases/migration: https://github.com/open-telemetry/semantic-conventions/releases
- MCP 2026-07-28 trace-context changes: https://blog.modelcontextprotocol.io/posts/2026-07-28/
