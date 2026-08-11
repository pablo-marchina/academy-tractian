# Wave 3 — MCP 2026-07-28 + Python SDK v2

Status: **PROTOCOL REVIEW COMPLETE / TOPOLOGY DECISION PENDING SPIKE**

## Why revisit MCP now

The project specification allows tools, MCP or an equivalent integration. MCP is therefore an architectural option, not a requirement. The relevant protocol changed materially in the 2026-07-28 release, so older session/SSE tutorials must not drive this project.

## Current protocol facts

The 2026-07-28 MCP revision makes the protocol core stateless:

- no modern `initialize` / `initialized` handshake;
- no modern `Mcp-Session-Id` requirement;
- each request carries protocol/client/capability metadata;
- `server/discover` is the discovery mechanism;
- Streamable HTTP remains the relevant HTTP transport while legacy HTTP+SSE is deprecated;
- method/name headers support routing/authorization scenarios;
- W3C Trace Context propagation is standardized in `_meta`;
- tool schemas use JSON Schema 2020-12, with object-rooted `inputSchema` and richer composition/reference capabilities;
- the release includes authorization/security hardening.

## Python SDK v2

The current official SDK documentation states that v2 is now the stable line and that `pip install mcp` installs 2.x. v2 implements the 2026-07-28 protocol and includes compatibility behavior for older clients/servers.

Important implementation consequences for this project:

1. Pin the exact SDK version in the experiment manifest; do not depend on an unrecorded floating install.
2. Use v2 APIs (`MCPServer`, current `Client`) rather than v1 `FastMCP` examples.
3. For HTTP, test the current Streamable HTTP path rather than deprecated legacy SSE.
4. Preserve protocol-version metadata in traces.
5. If transport/client dependencies change (e.g. the SDK's current HTTP client implementation), treat them as runtime details, not project tool semantics.

## Tool-schema implications

MCP can expose a rich JSON Schema contract, but this does not mean the TRACTIAN OpenAPI contract should be converted blindly into public MCP tools.

The canonical pipeline remains:

```text
TRACTIAN OpenAPI
      ↓
project-owned typed HTTP client / ToolSpec
      ↓
policy + risk metadata
      ↓
optional MCP adapter
```

Reasons:

- the project must compare runtimes fairly;
- tool metadata includes project semantics absent from generic protocol schemas (mutation, risk, evidence class, permission expectations);
- OpenAPI and JSON Schema feature conversion can be lossy;
- MCP annotations from an untrusted server cannot be treated as security truth;
- the policy gate must remain outside the model/protocol description.

## Topology candidates

### A — Native canonical tools only

Advantages:
- smallest local architecture;
- easiest instrumentation/fault injection;
- no protocol translation overhead.

Costs:
- less interoperability/reusability outside the selected runtime.

### B — Canonical tools + MCP adapter

Advantages:
- preserves one source of truth;
- lets us demonstrate MCP without making it the internal semantic core;
- allows native vs MCP comparison with identical underlying operations.

Costs:
- adapter code and transport overhead;
- an additional security/observability boundary.

### C — MCP-first canonical core

This is now **lower priority**, not rejected. It should only become the preferred topology if the partner requires MCP interoperability or the spike demonstrates a clear benefit.

Making MCP-first before the contract arrives would couple experiment semantics to a protocol layer that the TAPI explicitly treats as optional.

## MCP security requirements for the spike

- never use token passthrough as an authorization shortcut;
- validate authorization at the relevant resource/server boundary;
- least privilege for credentials/capabilities;
- treat remote tool descriptions/annotations/results as untrusted input;
- prevent tool output from acquiring instruction authority;
- bound URL/resource access to avoid SSRF-style pivots where applicable;
- record `Mcp-Method`, tool identity and protocol version without logging secrets;
- preserve `traceparent`/`tracestate`/`baggage` where applicable;
- permission/risk classification comes from project/API policy, not from model-selected annotations.

## MCP discriminating experiment

After Swagger delivery, compare A vs B using the same canonical tool implementations and the same model/runtime.

Measure:

- tool schema fidelity;
- argument/result fidelity;
- authorization/policy equivalence;
- trace continuity;
- transport latency overhead with fake/local API;
- implementation/dependency overhead;
- failure modes under timeout/malformed response;
- compatibility with mutation approval/resume;
- ability to reproduce the same scenario result through native and MCP paths.

MCP-first C is added only if A/B evidence or partner requirements justify it.

## Decision rule

MCP is selected for the final architecture only if it provides material interoperability/evaluation/demo value without weakening policy control, traceability or schema fidelity. Merely satisfying a suggested technology in the TAPI is not sufficient evidence.

## Primary/official sources

- MCP 2026-07-28 release: https://blog.modelcontextprotocol.io/posts/2026-07-28/
- MCP specification: https://modelcontextprotocol.io/specification/2026-07-28
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- MCP Python SDK v2 changes: https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/whats-new.md
- MCP security best practices: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
