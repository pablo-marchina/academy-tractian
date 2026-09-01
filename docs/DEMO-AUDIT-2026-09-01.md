# Final Demo Audit — 2026-09-01

**Baseline:** `main@3e0dbac5af413859b53011f6e43e8c0107b2fae3`  
**Acceptance source:** `docs/DELIVERY-ACCEPTANCE.md` §9  
**Current integrated provider-free demo:** `provider-free-final-delivery-reproduction-v1`

## Executive finding

The current five-scenario demo is valuable integration evidence, but it is not sufficient by itself for the final demonstration claim because its decision source is explicitly scripted/provider-free.

It does exercise the real `ProductionRuntime`, `HarnessRunner`, policy/tool boundaries, structured `RunTrace`, controlled-action runtime and evaluators. Therefore it is not a fake trace fixture. However, the agent decisions themselves are supplied by `_ScriptedDecisionSource`, so the final-delivery requirement `real integrated path, not a scripted mock-only path` remains only partially satisfied until D01 resolves and the selected/bounded provider path is integrated.

## Current five-scenario population

```text
DEMO-01  read/investigate → ORIENT
DEMO-02  clarify          → ASK_CLARIFICATION
DEMO-03  abstain          → ABSTAIN
DEMO-04  escalate         → ESCALATE_HUMAN
DEMO-05  controlled action→ ACT_REPROCESS
```

The reproduction validator requires exactly five traces, five evaluator passes, five contract passes, zero provider calls, zero credential probes, zero real-customer mutations, zero semantic-private access, zero automatic retries and zero replays.

## Acceptance matrix

| Required demo behavior | Status now | Evidence | Final closure needed |
|---|---|---|---|
| 1. Contextualize | PARTIAL | DEMO-01 reads asset evidence and returns orientation | repeat through final non-scripted provider path |
| 2. Investigate | PARTIAL | DEMO-01 performs one typed read through the real execution boundary | final provider must select/use tools correctly on representative cases |
| 3. Execute | PARTIAL | DEMO-05 performs one controlled accepted supplied/test action with durable claim | retain controlled safety semantics; no need for unsafe real-customer mutation, but final agent decision path must be demonstrated |
| 4. Clarify / insufficient evidence | PARTIAL | DEMO-02 + DEMO-03 | final provider path must demonstrate safe clarify/abstain behavior |
| 5. Escalate | PARTIAL + PFG-01 | DEMO-04 terminal escalation | handoff completeness evaluator must be strengthened; final provider path must pass it |
| 6. Conflict / uncertainty | PARTIAL | EV-007/EV-011 cover partial/unavailable/uncertain behavior | currently not an integrated demo trace; final demo should include or visibly link a trace/campaign case |
| 7. Failure / robustness | PARTIAL | EV-007 covers 11 deterministic failure families | final demonstration should surface at least one fault trace directly, not only a separate report |
| 8. Customer-safe response | PARTIAL | EV-011 validates 10 cases / 60 applicable predicates | final non-scripted agent output must pass the same safety expectations |
| 9. Per-run evaluation | PARTIAL | all five scripted integrated traces are evaluated | final non-scripted provider trace must be evaluated by the same separated evaluator plane |
| 10. Reliability view | PROVED_BOUNDED | EV-007 + EV-008 provide aggregate provider-free failure/stability evidence | provider-specific stability/latency remains post-D01 evidence if a provider is selected |

## Demo design decision before D01

Do **not** rewrite the frozen five-scenario campaign. It remains useful immutable provider-free integration evidence.

Do **not** create a fake sixth scripted scenario and call that the final real demo.

The prospective final demo should instead be additive after D01:

```text
frozen provider-free demo evidence (preserved)
+
selected/bounded real DecisionSource path
+
representative runtime traces
+
per-run production evaluator
+
at least one visible failure/uncertainty path
+
PFG-01-complete escalation handoff when escalation is demonstrated
+
aggregate reliability evidence
```

## Provider-free work allowed now

1. close PFG-01 escalation-handoff evaluator completeness;
2. ensure the final demo checklist/runbook explicitly references one conflict/failure trace rather than hiding it in an aggregate JSON;
3. preserve existing five-scenario hashes/results unchanged;
4. prepare post-D01 demo acceptance hooks without invoking a provider.

## D01 dependency

A final `PROVED` status for the real integrated agent demo cannot be issued before one of these is frozen:

```text
selected Cloudflare candidate
OR
NO_SELECTION
OR
LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED
```

If D01 is externally blocked, the final delivery must state that the provider-free integrated path is reproducible but the real hosted-model demonstration is bounded by that external blocker; it must not relabel scripted evidence as live evidence.