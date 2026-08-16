# E7 Topology ADR — Native Tools Internal Default + MCP-Compatible Adapter

**Status:** ADR decision prep / topology candidate recorded / not final architecture freeze  
**Date:** 2026-08-16  
**Gate:** E7 native tools vs MCP-compatible surface comparison  
**Scope:** DEV + VALIDATION only  
**LOCKED_TEST accessed:** false

## Decision

Adopt the following topology candidate until the final architecture freeze gate:

1. **Native ToolSpec calls remain the internal default candidate.**
   - Internal agent/runtime execution should continue to call the canonical `ToolSpec` registry through the native `{tool_name, arguments}` envelope.
   - This path stays closest to the existing `HarnessRunner`, B3 guard, evidence-sufficiency policy, adaptive evidence planner and RunTrace schema.
   - It preserves the same execution behavior with lower envelope complexity.

2. **MCP-compatible exposure remains the external interoperability candidate.**
   - Keep an MCP-compatible `tools/list` + `tools/call` adapter as a compatibility layer over the same `ToolSpec` registry.
   - The adapter must normalize back into the same `HarnessRunner` and deterministic B3/evidence path.
   - The E7 evidence supports MCP compatibility as an adapter, not as a required core runtime topology.

3. **MCP is not required for final delivery at this gate.**
   - No current evidence shows that MCP must replace native ToolSpec calls inside the core runtime.
   - MCP should become required only if a future delivery constraint, evaluator integration, partner integration, deployment topology or tooling requirement demands an MCP server/client boundary.
   - Until that happens, MCP remains optional external interoperability, not a final architecture freeze.

4. **Preserve the current candidate bundle.**
   - Boundary: B3 guarded boundary.
   - Evidence/stopping: evidence-sufficiency policy.
   - Evidence planning: adaptive from missing evidence requirements.
   - Runtime: LangGraph current candidate.
   - Transport: `HttpxTransport` live API path.
   - Comparators retained: Pydantic AI/Graph and OpenAI Agents SDK.

## Evidence used

E7 compared native tools against an MCP-compatible envelope while holding the same ToolSpec, HarnessRunner, B3 boundary, evidence-sufficiency policy, adaptive evidence planning and transport path constant.

| Metric | Native tools | MCP-compatible |
|---|---:|---:|
| Tool coverage | 18 | 18 |
| Representative scenarios | 4 | 4 |
| Splits | DEV + VALIDATION | DEV + VALIDATION |
| Request count | 18 | 18 |
| Successful request count | 18 | 18 |
| Trace complete | true | true |
| RunTrace-compatible output | true | true |
| B3 policy events | 2 | 2 |
| B3 allows actions | true | true |
| Evidence-sufficiency events | 4 | 4 |
| Action execution proxy | 2/2 | 2/2 |
| Avg latency ms | 1.9855 | 1.8158 |
| Complexity proxy | 1.0 | 2.0 |
| Portability proxy | 3.0 | 4.5 |

Comparison checks passed:

- schema equivalence;
- invocation equivalence;
- guard-fidelity equivalence;
- trace-completeness equivalence;
- DEV + VALIDATION only;
- LOCKED_TEST blocked.

## Rationale

Native ToolSpec calls are the right internal default candidate because they preserve the same behavior with lower envelope complexity. They also minimize unnecessary topology decisions before the final architecture freeze.

The MCP-compatible surface is worth retaining because it preserves fidelity while improving external interoperability. However, the E7 result does not prove that MCP should become the core internal execution topology. It proves that an MCP-compatible adapter can be kept without changing the safety boundary or trace semantics.

## Consequences

### Accepted

- The core runtime can continue using native ToolSpec calls.
- An MCP-compatible adapter can be maintained for external interoperability.
- Both surfaces must map to the same canonical ToolSpec registry.
- Both surfaces must preserve B3, evidence-sufficiency, adaptive evidence planning and RunTrace compatibility.

### Rejected for now

- Replacing the internal ToolSpec envelope with MCP as the only execution topology.
- Freezing MCP topology before statistical pilot/model benchmark and final architecture decision.
- Letting MCP adapter behavior diverge from HarnessRunner/B3/evidence-sufficiency behavior.

### Open

- Whether final delivery will require an actual MCP server/client runtime boundary.
- Whether external evaluator/integration constraints require MCP beyond adapter compatibility.
- Whether model/provider selection changes the preferred external tool surface.

## Safeguards

- `LOCKED_TEST` remains blocked.
- Model/provider remains unfrozen.
- MCP topology remains unfrozen.
- RAG/vector DB remains unfrozen.
- Multi-agent decomposition remains unfrozen.
- Observability backend remains unfrozen.
- UI/demo flow remains unfrozen.
- Final architecture remains unfrozen.

## Next gate

Proceed to E8 statistical pilot/model benchmark preparation while carrying this candidate topology:

```text
internal default: native ToolSpec calls
external interoperability: MCP-compatible adapter
required constants: B3 + evidence-sufficiency + adaptive evidence planning + HttpxTransport
architecture: not frozen
```
