# State, Memory & Context Management — Wave 2

Status: **PROVISIONAL RESEARCH CONCLUSION — architecture not frozen**

Research questions: R09 (state/memory), R10 (evidence acquisition/stopping), R19 (reproducibility)

## 1. Why this distinction matters

Agent systems often use the word “memory” for several fundamentally different things. That is dangerous in this project because state contamination can invalidate experiments and stale remembered information can cause industrial actions based on obsolete evidence.

The project will therefore treat **environment state, execution state, conversation state, persistent memory, evidence cache and model-visible context as distinct data planes**.

## 2. Proposed state taxonomy

| Plane | Source of truth? | Lifetime | Typical contents | Reset rule |
|---|---:|---|---|---|
| Industrial environment state | **Yes** for platform facts/actions | API-defined | assets, analyses, configuration, permissions, actions | API/reset semantics |
| Execution/workflow state | No | one run/thread | current objective, step status, selected evidence, pending action | fresh per run unless resumable test |
| Conversation/session state | No | one dialogue/session | user turns, clarifications, session-scoped facts | fresh per scenario/session |
| Persistent application memory | No | cross-session | explicitly persisted user/project facts if justified | namespaced + explicit lifecycle |
| Evidence cache | No, derived | bounded by freshness | retrieved API observations + provenance/version | invalidate by freshness/state change |
| Model-visible context | No | one model call | selected projection of the above | rebuilt every call |
| Trace/event log | Audit source, not world truth | experiment retention | calls, decisions, tool I/O refs, timing, evaluator annotations | immutable/versioned |

### Core invariant

> **The model context is never the source of truth.**

A fact copied into context does not become authoritative merely because the model saw it earlier. For mutable facts, the canonical source remains the current API/environment state unless a scenario explicitly tests stale/offline behavior.

## 3. Evidence from current research

### LangGraph persistence

Official LangGraph documentation separates thread-scoped checkpointed state from cross-thread storage. Checkpoints support persistence at graph steps and enable human-in-the-loop, fault tolerance, replay/time-travel style inspection and resumption. Its Store abstraction covers cross-thread long-term memory.

This is useful evidence for what a runtime *can* provide, but does not prove LangGraph should be selected. Our project should require equivalent semantics from any runtime finalist.

### Long-horizon context engineering

Anthropic's official context-engineering guidance emphasizes that context remains a finite attention resource even as windows grow. It recommends preserving high-signal information, using just-in-time retrieval/progressive disclosure, and using compaction or structured note-taking for long-running tasks instead of accumulating an unbounded raw transcript.

This supports separating **stored state** from **what is injected into each model call**.

### Long-term memory benchmarks

LongMemEval evaluates capabilities including extraction, multi-session reasoning, temporal reasoning, knowledge updates and abstention. Its findings support treating memory as a system design problem involving indexing, retrieval and reading rather than as “append the entire chat history.”

LoCoMo similarly demonstrates that long, multi-session conversational memory remains non-trivial. MemGPT provides a useful architecture analogy: virtual/hierarchical context management rather than assuming all information fits efficiently in the active context.

These works motivate experiments if cross-session memory is actually required by the TRACTIAN scenarios; they do **not** justify adding long-term memory by default.

## 4. Project decision hypothesis: persistent memory OFF by default

For the benchmark and most industrial tasks, persistent cross-scenario memory should be **disabled by default**.

Reasons:

1. **Experimental isolation** — one scenario must not leak facts into another.
2. **Freshness** — industrial state can change; stale remembered state may be worse than no memory.
3. **Security** — persistent memory expands the attack and privacy surface.
4. **Attribution** — a failure should be attributable to current evidence/policy, not hidden historical residue.
5. **Reproducibility** — a run should start from an explicit state snapshot/namespace.

Persistent memory becomes eligible only if the supplied API/scenario design requires cross-session continuity that cannot be represented as ordinary environment state or explicit conversation state.

## 5. Benchmark isolation requirements

Every scenario/run must have explicit identifiers and namespaces:

```text
experiment_id
  └── scenario_id
       ├── environment_snapshot / reset token
       ├── conversation_namespace
       ├── workflow_thread_id
       ├── evidence_cache_namespace
       └── run_id
```

Required invariants:

- no persistent memory shared across unrelated scenarios;
- no evidence cache shared unless explicitly version/freshness-safe;
- no model conversation implicitly reused across runs;
- configuration/version hashes stored on every run;
- reset failure is an infrastructure failure, not an agent failure;
- multi-turn scenarios may share state only inside their declared scenario boundary.

## 6. Context construction policy hypothesis

Instead of “send everything,” construct context from typed sources:

```text
System policy / capability contract
            +
Current user objective / latest clarification
            +
Minimal typed workflow state
            +
Relevant evidence with provenance/freshness
            +
Small recent conversational window
            +
Optional summary/notes when justified
```

Raw traces, full tool payload history and irrelevant prior turns stay outside the model context unless specifically retrieved.

### Context priority

1. hard policy/capability constraints;
2. current request and explicitly confirmed user constraints;
3. current authoritative environment/evidence;
4. unresolved contradictions/limitations;
5. recent dialogue needed for reference resolution;
6. summaries/long-term memory only when necessary.

## 7. Staleness and evidence cache semantics

Any cached evidence should carry at minimum:

```yaml
source_endpoint:
entity_id:
observed_at:
source_version_or_etag: null
state_version: null
freshness_class:
confidence_or_quality: null
limitations: []
conflicts_with: []
```

Cache validity must be invalidated after relevant mutations or when API freshness metadata indicates expiry. If the API exposes no explicit version/freshness metadata, the project must not pretend it can prove cache validity; use conservative re-query rules and document the limitation.

## 8. Memory update policy if persistent memory becomes necessary

If cross-session memory is justified, writes must be explicit, inspectable and typed rather than an unconstrained LLM-generated blob.

Candidate record:

```yaml
memory_id:
namespace:
type:
value:
source_trace_id:
source_evidence_ids: []
created_at:
valid_from:
valid_until: null
supersedes: null
confidence: null
sensitivity:
```

Required behaviors:

- provenance mandatory;
- update/supersession explicit;
- conflicts preserved rather than silently overwritten;
- deletion/reset supported;
- sensitive memory classes blocked or redacted unless required;
- retrieval results treated as evidence candidates, not permissions.

## 9. Context-management experiments

Only run these once the API/scenario distribution shows meaningful long interactions.

### CM-1 — Raw history vs structured state

A. Full/raw available history

B. Recent turns + typed workflow state

C. Recent turns + typed state + summary/notes

Measure:

- task success;
- tool/argument correctness;
- stale-evidence errors;
- unsupported claims;
- latency/tokens;
- context size;
- robustness as conversation length grows.

### CM-2 — Memory contamination

Run scenario families in randomized order with:

A. fresh isolated namespace;

B. intentionally shared memory namespace.

Expected purpose: quantify contamination risk and prove isolation controls.

### CM-3 — Knowledge update/conflict

If persistent memory is needed, create controlled pairs where a previously stored fact is superseded or contradicted by newer API evidence.

Evaluate whether the system:

- identifies the update;
- prefers current authoritative evidence;
- preserves provenance;
- avoids acting on stale memory;
- abstains/escalates when conflict cannot be resolved.

## 10. Runtime requirements derived from this research

The runtime comparison spike must test whether each finalist can provide or integrate with:

- typed execution state;
- checkpoint/resume;
- deterministic reset/namespace control;
- state inspection without model involvement;
- pre-action interception;
- explicit context construction rather than hidden framework memory;
- pluggable persistent store (if needed);
- test doubles/fake tools/models;
- OTel-compatible tracing.

Framework-provided “memory” is not a selection criterion by itself; controllability and evaluability are.

## 11. Provisional decision

**Recommended default for FROZEN-v1 unless API evidence changes it:**

- environment/API = canonical mutable truth;
- typed workflow state = per-run, checkpointable;
- conversation state = scenario/session-scoped;
- long-term memory = **off unless a requirement proves it necessary**;
- evidence cache = provenance + freshness + invalidation;
- model context = minimal dynamically constructed projection;
- traces = immutable experiment/audit record, not injected wholesale into prompts.

## 12. Open dependencies

Cannot close this research item before TRACTIAN provides/clarifies:

- whether any task explicitly spans sessions;
- state mutation persistence;
- reset/snapshot support;
- entity/version/freshness fields;
- user/company tenancy boundaries;
- whether knowledge resources can change during a scenario;
- whether conversations have server-side state.

## 13. ADR impact

This document will feed the future State/Memory ADR. It does **not** select LangGraph or another runtime.
