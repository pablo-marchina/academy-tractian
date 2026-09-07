# 2026-09-05 — Required agent modes source gate

## Objective

Advance the consolidated plan through deterministic offline/source acceptance for Contextualize, Investigate, Clarify, Abstain and Escalate while preserving the accepted controller/provider protocol and all frozen historical evidence.

## Implementation

Added `production-required-agent-modes-gate-v1` as an additive post-hoc `RunTrace` consumer. The gate does not mutate `HarnessRunner`, `AgentController`, `ProductionRuntime`, `ProductionEvaluator`, provider request v1 or frozen EV-* artifacts.

The gate maps the canonical terminal decisions to the required product modes:

```text
ORIENT             -> CONTEXTUALIZE
INVESTIGATE        -> INVESTIGATE
ASK_CLARIFICATION  -> CLARIFY
ABSTAIN            -> ABSTAIN
ESCALATE_HUMAN     -> ESCALATE
action decisions   -> EXECUTION_DEFERRED
```

Deterministic invariants include valid trace lifecycle, known terminal Decision/ResponseMode, canonical tool-result identity, read-semantics contract integrity, at least one canonical read for INVESTIGATE, non-empty message/reason for control terminals, no `complete` claim by Clarify/Abstain/Escalate, and exact sanitized escalation-handoff binding.

The output report deliberately excludes raw upstream bodies, terminal message text, user request, identity id, user id and seed. Only structural counts, terminal enum values, read-mode distribution, handoff status and stable violation codes are retained.

## Evidence-driven correction during implementation

The initial design assumed Clarify/Abstain/Escalate should all emit `inconclusive`. Inspection of the accepted controller contract showed the real deterministic behavior is:

```text
CLARIFY   -> partial
ESCALATE  -> partial
ABSTAIN   -> unavailable
```

The proposed invariant was therefore corrected before promotion. The final gate does not force one uncertainty mode; it only prevents these control terminals from falsely claiming `complete`, preserving the controller's existing semantics.

## Regression coverage

`tests/test_mode_acceptance_gate.py` covers:

- Contextualize without an unnecessary forced tool call;
- Investigate with a canonical structured read;
- controller-generated Clarify and Abstain modes;
- Escalate after conflicting evidence with exact handoff validation;
- explicit deferral of all canonical consequential-action decisions;
- unknown terminal decision/response mode;
- false `complete` control terminal;
- missing terminal message/reason;
- Investigate without a read;
- malformed read semantics;
- blocked action attempting to substitute for read evidence;
- sanitized report boundaries;
- forged unknown `tool_result`;
- invalid trace lifecycle;
- sanitized gate exception output.

## Validation

Functional implementation head:

`d72b33830a98152530f9d98f4547131dca22de42`

At that head, all 11 pull-request workflows completed successfully, including:

- `production-runtime`;
- standalone production wheel smoke;
- production image smoke;
- clean-clone full-product reproduction;
- frozen EV-007 / EV-008 / EV-011 reproduction;
- full-product Playwright;
- EDD, observability, frontend, Railway IaC and runtime handoff;
- `final-ci-required / required-gate`.

## Non-claims

This milestone performed zero live provider calls, zero real TRACTIAN requests and zero consequential production actions. It does not prove hosted correctness of any agent mode, provider quality, real TRACTIAN reachability or action authorization. Those remain dependency-gated.

## Next dependency-independent work

Prepare the real action-authorization boundary while keeping production DENY-ALL. The current action runtime accepts an injected resolver keyed only by `user_id`; source hardening must ensure any future principal is bound to trusted server-owned organization/resource/permission facts rather than browser claims or ambiguous cross-organization user state.
