# Academy × TRACTIAN — Final Handoff Runbook

**Status:** ACTIVE operational runbook  
**Authority:** subordinate to [`CURRENT-PROJECT-STATUS.md`](CURRENT-PROJECT-STATUS.md), accepted ADRs and frozen experiment evidence.  
**Plan:** [`DELIVERY-PLAN.md`](DELIVERY-PLAN.md)

This runbook separates **what works now** from **what becomes the final handoff once the realtime observability/frontend P0 work is merged**.

## 1. Current supported provider-free path

```text
request
→ ProductionRuntime
→ DecisionSource
→ AgentController
→ HarnessRunner
→ typed TRACTIAN tools
→ B1/B2/B3 safety boundaries as applicable
→ RunTrace
→ deterministic evaluator
```

The default production runtime is action-disabled. The controlled supplied/test action profile is separately governed and does not authorize real-customer mutation.

## 2. Backend prerequisites

- Python 3.11+
- `pydantic>=2.6,<3`
- `pytest>=8` for development/test

From repository root:

```bash
python --version
python -m pip install -e ".[dev]" -e "research/e2[dev]"
```

No provider secret is needed for provider-free reproduction.

## 3. Current clean provider-free reproduction

```bash
python -m pytest -q tests
python -m pytest -q research/e2/tests/test_controller.py
python scripts/validate_ev007_failure_campaign.py
python scripts/validate_ev008_stability_campaign.py
python scripts/validate_ev011_communication_campaign.py
python scripts/validate_delivery_reproduction.py
python scripts/validate_final_handoff_audit.py
```

Do not change frozen expected identities to make a regression pass. Diagnose the implementation/evidence change instead.

Historical frozen campaign identities include:

```text
EV-007  7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9
EV-008  1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8
EV-011  cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e
DEMO    43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445
```

## 4. Provider-free demonstration

`python scripts/validate_delivery_reproduction.py` exercises representative integrated paths including:

- investigate/read → orient/final;
- missing context → clarification;
- no safe path → abstention;
- human review → escalation;
- controlled supplied/test action with local transport/idempotency custody.

This is synthetic/provider-free delivery evidence and performs no real customer mutation.

## 5. D01 historical live evidence

D01 has already executed:

```text
Cloudflare Workers AI
GLM 4.7 Flash + Nemotron 3 120B A12B
32 / 32 completed attempts
USD 0.00
2813.628464 observed Neurons
NO_SELECTION
24 / 24 CLIENT_FAILURE at exact 512 output-token ceiling
```

Do not rerun D01 or alter its frozen semantics.

## 6. D02 governed live boundary

D02 is a prospective diagnostic with:

```text
same providers/probes/repeats/prompt/schema/evaluator
completion cap 1024
sanitized failure subtype
worst-case packet 9352.805376 Neurons
USD0 / no retries / no fallbacks
```

Operational rule:

1. start from exact current `main`;
2. provider credentials absent;
3. wait for an eligible Workers AI UTC reset;
4. make a fresh truthful zero-use operator attestation;
5. capture fresh evidence (<=600 s);
6. issue fresh receipt (<=300 s) bound to exact custody root;
7. only then provision token/account ID in environment;
8. execute the governed D02 launcher once;
9. clear credentials immediately;
10. inspect custody/ledger/result;
11. if any attempt is `CLAIMED`/`UNCERTAIN`, never blind-rerun it;
12. analyze D02 vs D01 and apply frozen hard-gate/Pareto rules.

Never paste tokens/account identifiers into documentation or chat logs.

## 7. Failure behavior

### Invalid arguments

B1 blocks before transport. Preserve the failure; do not convert it into success.

### Policy/authorization denial

Denied actions stop before transport and remain visible as contained policy events.

### Tool boundary failure

Fail closed to a safe terminal path where implemented. Do not invent successful external state.

### Decision-source/provider failure

Malformed/unusable provider output must not become an invented action or answer. Sanitized failure/provenance metadata may be recorded; raw material remains private.

### Missing/conflicting evidence

Clarify, abstain or escalate; do not fabricate certainty.

### Consequential action uncertainty

Once a durable idempotency/attempt claim is consumed, do not delete/reuse it to manufacture retry eligibility.

## 8. Realtime observability/frontend handoff contract

Once #121/#124/#122/#125/#123 are merged, the final clean setup must additionally document exact commands for:

```text
backend/observability install
frontend install from lockfile
frontend build
observability API start
React control-room start
provider-independent live demo
frontend/unit/E2E test suite
```

Do not add placeholder commands before the actual package/scripts exist. This runbook must be updated from committed executable commands, not from planned names.

Final realtime behavior must show:

- `LIVE / RECONNECTING / CAUGHT_UP / HISTORICAL` state;
- real event-driven timeline/trace graph updates;
- reconnect/cursor catch-up;
- safe drill-down;
- architecture/output lineage;
- no raw/private telemetry in browser.

## 9. Observability diagnosis

For any run, diagnose the earliest failing boundary:

```text
request/context
→ decision source
→ controller decision
→ tool proposal
→ B1 validation
→ B2/B3 policy
→ tool transport
→ observation
→ terminal outcome
→ trace validation
→ evaluator
→ safe projection
→ persistence
→ SSE transport
→ browser reducer/render
```

Do not mask one boundary with retry/fallback from another.

## 10. Security/privacy

Never persist or expose through handoff/frontend/API/SSE:

- provider secrets/tokens;
- account/auth identifiers/headers;
- identity binding/user ID/seed;
- raw provider prompt/response material;
- forbidden raw tool/observation bodies;
- hidden chain-of-thought;
- evaluator-private gold/oracles/blind outcomes.

## 11. Rollback/reversal

- code/runtime regression: return to last validated Git commit and rerun clean reproduction;
- frontend/observability regression: revert to last validated frozen frontend/backend build and rerun affected tests;
- controlled action uncertainty: reconcile external state, never auto-replay consumed claim;
- provider experiment: preserve custody/ledger; no alternate root to reset attempts;
- scientific evidence: frozen artifacts remain immutable;
- privacy/evaluation leak: treat as evidence-integrity incident, not a documentation cleanup opportunity.

A documented code/config reversal path is not equivalent to proof of infrastructure rollback in a horizontally deployed production environment.

## 12. Final presentation sequence

The target final demo flow is:

```text
1. Mission Control / system state
2. submit representative industrial request
3. run appears LIVE
4. architecture path activates from real events
5. model/decision metadata
6. typed tool proposal
7. validation/policy result
8. TRACTIAN tool/API metadata
9. safe observation/evidence
10. terminal response
11. runtime trace completes
12. evaluator appears after runtime completion
13. Explain This Run / output lineage
14. dynamic data explorer
15. Tools & Policy / failure behavior
16. D01 vs D02 / provider quality/resource evidence
17. one clarification/abstain/escalation/blocked/failure case
```

Maintain a provider-independent fallback demo so live provider availability is not a single presentation point of failure.

## 13. Final completion checklist

Before delivery:

- clean backend install/reproduction passes;
- frontend/observability clean install/build/start passes once implemented;
- all P0 acceptance rows in `DELIVERY-ACCEPTANCE.md` pass or are explicitly bounded;
- D02 is resolved or its blocker is explicitly documented;
- no open P0 frontend/observability defect;
- documentation links/commands match committed code;
- no secrets/private evaluator material are present;
- hard visual/feature freeze respected;
- exact final demo rehearsed on the presentation environment.

If any item fails, report the exact boundary and limitation rather than broadening claims.