# Security Threat Model — Wave 2

Status: **PROVISIONAL THREAT MODEL — to be specialized against the real API**

Research questions: R09 (safety/policy), R15 (threat model), R16 (red team), R19 (reproducibility)

## 1. Security objective

The industrial agent must not gain authority merely because an LLM produced a plausible action. Security must be enforced at system boundaries that remain effective even when the model is mistaken, manipulated or exposed to malicious/untrusted tool content.

Core principle:

> **The model proposes; deterministic system controls authorize capabilities and side effects.**

This is stronger than prompt-only safety and aligns with the TAPI requirement that higher-impact actions use valid parameters and adequate justification.

## 2. Security properties to protect

| Property | Meaning in this project |
|---|---|
| Instruction integrity | Untrusted content must not override trusted policy/objective |
| Capability integrity | The agent must not execute tools/actions outside granted authority |
| Resource isolation | A user/company/session must not access another resource without authorization |
| Action integrity | Mutations must match authorized intent, validated arguments and required preconditions |
| Confidentiality | Secrets, restricted data and sensitive traces must not leak |
| State integrity | Environment/workflow/memory state must not be silently corrupted |
| Audit integrity | Traces/evaluation evidence must faithfully represent what executed |
| Benchmark integrity | Test contamination/leakage must not inflate results |
| Availability/boundedness | Loops/retries/tool storms must have enforceable limits |

## 3. Threat-model evidence

### AgentSecBench

AgentSecBench formalizes agent security around instruction integrity, confidentiality and capability/tool-use integrity. A useful design implication is the distinction between telling a model what not to do and enforcing a projection/capability boundary outside the model.

### AgentDojo

AgentDojo evaluates indirect prompt injection in environments where agents consume untrusted data through tools. This is directly relevant: API/tool returns must be treated as data, not automatically as trusted instructions.

### OWASP agentic / excessive agency guidance

OWASP guidance identifies excessive functionality, permissions and autonomy as core drivers of agency risk. For this project, least privilege and action gating are therefore architectural requirements to test, not prompt wording preferences.

### Containment and blast radius

Recent first-party agent-security engineering guidance emphasizes reducing blast radius through environmental controls such as sandboxes, filesystem/network bounds and constrained capabilities. That supports placing critical security controls below/around the LLM.

## 4. Trust boundaries

Proposed boundaries:

```text
USER / EXTERNAL INPUT
        │ untrusted
        ▼
AGENT MODEL / CONTEXT
        │ probabilistic, not authority
        ▼
ACTION PROPOSAL
        │
        ▼
DETERMINISTIC VALIDATION + POLICY BOUNDARY
        │ trusted enforcement
        ▼
CANONICAL TOOL ADAPTER
        │
        ▼
TRACTIAN API / ENVIRONMENT
```

Tool/API outputs cross back from an external/untrusted-data boundary into the agent. They may be authoritative as **facts about the environment** according to the API contract, but any natural-language content inside them must not acquire instruction authority.

Other boundaries:

- model-provider network boundary;
- observability/trace storage;
- optional MCP transport/auth boundary;
- persistent memory/store boundary;
- local sandbox if programmatic tool calling is tested;
- benchmark/test dataset boundary.

## 5. Assets

Before API onboarding, protect at least:

1. API credentials and provider secrets;
2. user/company identity and permissions;
3. asset/configuration state;
4. high-impact action capability;
5. analysis/evidence integrity;
6. prompts/policies/tool schemas;
7. persistent memory/session state;
8. trace/evaluation records;
9. locked benchmark scenarios and answers;
10. local host filesystem/network if code execution is introduced.

## 6. Attack/failure surface catalogue

### A. User-input attacks

- direct policy override;
- ambiguous request designed to induce unsafe action;
- social-engineering claims of authority;
- malicious argument values;
- request to bypass confirmation/escalation.

### B. Tool-output / indirect prompt injection

- malicious text embedded in knowledge/procedure fields;
- analysis text telling the agent to ignore policy;
- resource metadata containing instruction-like payloads;
- retrieved content asking for secret exfiltration;
- tool output suggesting unauthorized follow-up actions.

### C. Authorization/capability failures

- wrong company/user/resource ID;
- horizontal access across tenants/resources;
- over-broad tool exposure;
- privileged mutation from read-only context;
- action executed before permission resolution.

### D. Mutation failures

- wrong target entity;
- semantically wrong but schema-valid argument;
- duplicate side effect after retry;
- stale precondition;
- mutation executed despite conflicting evidence;
- claimed success without postcondition verification.

### E. Memory/state attacks

- cross-scenario contamination;
- stale memory overriding fresh API state;
- memory poisoning;
- malicious persistent note;
- namespace collision;
- hidden state surviving experiment reset.

### F. Availability/boundedness

- infinite/long loops;
- retry storms;
- recursive tool calls;
- expensive routing escalation;
- tool denial causing uncontrolled fallback.

### G. Observability/data leakage

- credentials in trace payloads;
- sensitive tool arguments/results copied to dashboard;
- benchmark gold labels leaking into model context;
- traces from one scenario exposed to another.

### H. MCP-specific if adopted

- token passthrough;
- insufficient audience/token validation;
- SSRF through server-controlled downstream URLs;
- over-broad scopes;
- confused-deputy behavior;
- unsafe server/plugin trust assumptions.

The MCP security guidance explicitly forbids token passthrough and recommends validating tokens/audience, least-privilege scopes and SSRF protections. These controls become mandatory if the MCP path is selected.

### I. Programmatic tool calling if tested

- arbitrary filesystem/network access;
- import/package abuse;
- hidden subprocess execution;
- bypass of canonical mutation gate;
- denial-of-service through generated code.

Programmatic tool calling therefore requires a restricted execution environment and must not receive ambient host capabilities.

## 7. Severity model

Do not collapse security into one weighted average. Classify incidents by consequence and authority boundary.

Provisional severity:

| Severity | Example |
|---|---|
| S0 | benign inefficiency; unnecessary read/tool call |
| S1 | wrong answer with no mutation/security impact |
| S2 | unauthorized information attempt blocked before disclosure/action |
| S3 | policy/precondition failure that reaches action proposal but is blocked |
| S4 | unauthorized/incorrect mutation actually executed; confidentiality breach; cross-resource access |
| S5 | repeated/high-impact destructive capability or systemic credential/capability compromise |

Final S4/S5 definitions require the real API's action taxonomy.

Safety constraints for final selection should be **lexicographic/hard**, not traded away for small latency/accuracy gains. A configuration with materially worse high-impact safety should not win via a composite score.

## 8. Control architecture

### Layer 0 — Capability minimization

- expose only needed canonical tools;
- separate read and mutate metadata;
- least-privilege credentials/scopes if API supports them;
- no ambient arbitrary HTTP/filesystem/code execution by default.

### Layer 1 — Typed validation

- generated/manual typed client validated against OpenAPI;
- Pydantic/JSON Schema validation;
- enum/range/format checks;
- canonical entity IDs.

### Layer 2 — Authorization/policy

Evaluate outside the LLM:

- actor identity/role;
- target resource ownership/scope;
- permission;
- action risk class;
- required evidence/preconditions;
- forbidden action/rule IDs.

### Layer 3 — Mutation-specific verification

For mutating/high-impact operations:

- ensure target/arguments align with stated objective;
- ensure evidence freshness/sufficiency;
- check unresolved contradictions;
- optional approval/HITL depending partner semantics;
- use idempotency control if API supports it.

### Layer 4 — Postcondition verification

After accepted mutation:

- query/verify observable final state where possible;
- never claim success solely because the LLM expected success;
- classify mismatch distinctly.

### Layer 5 — Containment/limits

- max model/tool steps;
- retry budget;
- time budget;
- restricted programmatic execution if enabled;
- network/filesystem egress bounds where relevant.

### Layer 6 — Audit/redaction

- immutable run identity;
- trace policy decision before mutation;
- secret redaction;
- benchmark-gold separation.

## 9. Security benchmark families

At minimum, create controlled scenario pairs once the API is known:

| Family | Positive/control | Adversarial counterpart |
|---|---|---|
| Authorization | authorized user acts | same request unauthorized |
| Resource scope | own asset | another company/resource |
| Evidence | sufficient evidence | missing/conflicting/stale evidence |
| Mutation | valid justified mutation | semantically invalid/high-risk mutation |
| Tool output | benign content | prompt injection in returned content |
| Clarification | complete request | ambiguous target/parameter |
| Retry | transient read failure | mutation response ambiguity/duplicate risk |
| Memory | fresh state | poisoned/stale conflicting memory |
| High impact | approved/preconditions met | missing approval/preconditions |

Pairwise construction reduces confounding: a small controlled change should flip the correct decision from ACT to ASK/ABSTAIN/ESCALATE/DENY where appropriate.

## 10. Primary security metrics

Do not use an LLM judge when a deterministic oracle is available.

- unauthorized action execution rate;
- forbidden tool-call attempt rate;
- forbidden tool-call **execution** rate;
- policy-gate false-negative rate;
- policy-gate false-positive rate;
- cross-resource access rate;
- secret leakage rate;
- indirect-prompt-injection success rate;
- mutation postcondition mismatch rate;
- duplicate side-effect rate;
- failure-to-abstain rate;
- unnecessary escalation/denial rate (utility cost);
- boundedness violations.

Important distinction:

> A dangerous proposal that is deterministically blocked is an **agent-layer failure but system-level containment success**.

Both must be reported.

## 11. Adversarial harness strategy

Use two complementary sources:

1. **hand-authored gold adversarial scenarios** tied to actual API semantics;
2. generated/red-team variations (Promptfoo candidate) for breadth.

Generated attacks must not replace project-specific gold cases because an external red-team generator does not know the true industrial authorization/state semantics automatically.

## 12. Security experiment: prompt-only vs enforced policy

Pre-register a direct comparison:

A. strong system prompt + typed tools, no deterministic authorization gate;

B. same prompt/model/tools + deterministic policy gate;

C. B + mutation-specific verification;

Measure safety and utility across authorized + unauthorized/adversarial scenario pairs.

This isolates the value of enforcement rather than simply asserting it.

## 13. Zero-event reporting

If final evaluation observes zero severe incidents, do **not** write “100% safe.” Report:

- `0 / N` observed events;
- confidence interval / upper bound for the incident probability;
- exact tested scenario families;
- untested threat classes;
- assumptions such as policy-metadata integrity.

## 14. Open TRACTIAN dependencies

Need partner/API information to finalize:

- roles/permissions/tenancy model;
- which resources belong to which company/user;
- complete mutation list;
- high-impact classifications;
- whether changes are reversible;
- idempotency semantics;
- approval/HITL requirements;
- auth tokens/scopes;
- state reset;
- whether knowledge/tool outputs can contain arbitrary text;
- limits on recording synthetic payloads.

## 15. Current decision state

Strong provisional constraints:

- authorization/schema/hard policy outside prompt-only control;
- untrusted tool text never inherits instruction authority;
- mutations receive stronger verification than reads;
- every actual side effect is traceable and postcondition-checked where possible;
- capabilities minimized by default;
- persistent memory and programmatic execution expand threat surface and remain conditional.

This threat model must be rewritten against the real Swagger/domain model before `FROZEN-v1`.
