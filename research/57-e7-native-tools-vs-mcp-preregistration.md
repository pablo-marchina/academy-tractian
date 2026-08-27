# E7 — Native Tools vs MCP Discriminating Setup Preregistration

**Date:** 2026-08-16  
**Status:** PREREGISTERED  
**Prior gate:** E6 `LIVE_PASS`  
**Runtime candidate held constant:** LangGraph  
**Boundary held constant:** B3 guarded boundary  
**Evidence/stopping held constant:** evidence-sufficiency policy  
**Transport path held constant:** `HttpxTransport` live API path  
**Splits allowed:** DEV + VALIDATION only  
**LOCKED_TEST:** forbidden

## Purpose

E7 compares two exposure surfaces over the same frozen `ToolSpec` registry and the same execution boundary:

1. **Native tool surface:** internal tool-call envelope with `{tool_name, arguments}`.
2. **MCP-compatible surface:** JSON-RPC-style `tools/list` and `tools/call` envelopes mapped back into the same `HarnessRunner` execution boundary.

The goal is not to pick a final MCP topology yet. The goal is to test whether MCP compatibility adds interoperability benefits without reducing trace completeness, guard fidelity, split hygiene or evidence/stopping controls.

## Constants

The following are held constant from E6:

- canonical `research.e2.tool_registry.TOOLS` as the single tool contract source;
- `HarnessRunner` as the only execution boundary;
- B3 guarded boundary as deterministic policy enforcement;
- evidence-sufficiency policy as deterministic stopping/action-readiness enforcement;
- adaptive evidence planning from missing evidence requirements;
- runner-bound identity and seed;
- `HttpxTransport` live API path as the production transport path;
- DEV + VALIDATION only;
- `LOCKED_TEST` blocked;
- no model/provider, MCP topology, RAG, multi-agent, observability or UI freeze.

## Surface definitions

### Native tool surface

A native call is represented as:

```json
{"tool_name":"get_asset","arguments":{"asset_id":"asset_G501"}}
```

### MCP-compatible surface

An MCP-compatible list/call shape is represented as JSON-RPC-style envelopes:

```json
{"jsonrpc":"2.0","id":"e7-tools-list","method":"tools/list"}
```

```json
{
  "jsonrpc":"2.0",
  "id":"e7-call-1",
  "method":"tools/call",
  "params":{"name":"get_asset","arguments":{"asset_id":"asset_G501"}}
}
```

This is an MCP-compatible adapter test, not a claim that the final MCP server topology is frozen.

## Measured criteria

| Criterion | Measurement |
|---|---|
| Tool coverage | number of `ToolSpec` tools exposed by each surface |
| Schema equivalence | whether both surfaces expose the same normalized input schemas |
| Invocation equivalence | whether both surfaces execute the same tool plans through `HarnessRunner` |
| Trace completeness | whether outputs remain `RunTrace` compatible with required event types |
| Guard fidelity | whether B3 policy checks remain visible and equivalent for action cases |
| Evidence/stopping fidelity | whether evidence-sufficiency stays explicit before actions |
| Latency overhead | native vs MCP-compatible envelope overhead in contract execution |
| Complexity | request-envelope and adapter-complexity proxy |
| Portability | protocol/interoperability proxy, without architecture freeze |

## Interpretation rules

- Passing E7 proves that both surfaces can preserve the existing ToolSpec/HarnessRunner/B3/evidence path.
- It does **not** freeze the MCP topology.
- It does **not** freeze model/provider, RAG, memory, multi-agent, observability or UI.
- Native can remain the internal default if it is lower complexity/latency.
- MCP-compatible can remain the external interoperability candidate if it preserves trace and guard fidelity.
- Any locked-test access invalidates the run.

## Required outputs

- `research/experiments/e7-native-tools-vs-mcp-manifest.json`
- `scripts/research/e7_native_vs_mcp_runner.py`
- `research/results/e7-native-tools-vs-mcp-summary-2026-08-16.json`
- `research/58-e7-native-tools-vs-mcp-results.md`
