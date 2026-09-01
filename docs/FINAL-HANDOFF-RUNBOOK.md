# Academy × TRACTIAN — Final Handoff Runbook

**Scope:** provider-free final handoff for the actually evidenced runtime/evaluator path, plus the separately governed current Cloudflare comparison boundary.  
**Authority:** subordinate to `CURRENT-PROJECT-STATUS.md`, frozen ADRs and frozen experiment artifacts.  
**Does not authorize:** live provider calls, credential probing, real customer mutation, C4 reconstruction/rescoring, semantic/private/blind evaluation, global architecture freeze or unconditional production-readiness claims.

## 1. Supported handoff path

The reviewer-facing path is intentionally small:

```text
request
→ AgentController
→ DecisionSource
→ HarnessRunner.execute_tool()
→ strict B1 argument validation
→ B2 action/resource safety
→ RunTrace
→ deterministic evaluator
```

The default `ProductionRuntime` is action-disabled. The separately governed `ControlledActionRuntime` is used only for explicitly authorized supplied/test action demonstrations and preserves durable idempotency custody before action transport.

The current provider-comparison path is separate from this provider-free handoff and is governed by ADR-018 through ADR-023. It must not be invoked merely to reproduce the handoff.

## 2. Environment prerequisites

Use Python 3.11 or newer. The production and E2 packages require `pydantic>=2.6,<3`; test extras require `pytest>=8`.

From a clean checkout at the repository root:

```bash
python --version
python -m pip install -e ".[dev]" -e "research/e2[dev]"
```

No provider secret is required for the canonical provider-free reproduction. Do not add dummy provider secrets, probe accounts or invoke the governed Cloudflare comparison merely to test setup.

## 3. Canonical clean reproduction

Execute in this exact order:

```bash
python -m pytest -q tests
python -m pytest -q research/e2/tests/test_controller.py
python scripts/validate_ev007_failure_campaign.py
python scripts/validate_ev008_stability_campaign.py
python scripts/validate_ev011_communication_campaign.py
python scripts/validate_delivery_reproduction.py
python scripts/validate_final_handoff_audit.py
```

Interpretation:

- test/validator failure means the handoff is not reproduced at that checkout;
- do not change frozen expected SHAs to make a failing regression green;
- diagnose the changed implementation/evidence instead;
- no failed provider-free validator permits a live-provider fallback.

Frozen identities that must remain unchanged:

```text
EV-007  7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9
EV-008  1542a7cbb69e64e72e78e24e28163d22372eb70aa2438b062845a1ab6b181dd8
EV-011  cfa811da3af43a9577e0512c8da1fb8423bdf1d2b55a80023c18199033f65a2e
DEMO    43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445
```

## 4. Demonstration sequence

`python scripts/validate_delivery_reproduction.py` reruns the five frozen integrated scenarios and validates the static result/evidence index:

1. `DEMO-01` — supplied/local `get_asset`, investigate/read, supported `ORIENT`;
2. `DEMO-02` — `ASK_CLARIFICATION / MISSING_CONTEXT`;
3. `DEMO-03` — `ABSTAIN / NO_SAFE_PATH`;
4. `DEMO-04` — `ESCALATE_HUMAN / HUMAN_REVIEW_REQUIRED`;
5. `DEMO-05` — authorized supplied/test `reprocess_analysis`, one deterministic local action transport and one fresh durable local claim.

Expected campaign SHA: `43903731c34573df259461596e9659e11c55699450d2bbd1cb4b617acde32445`.

This demonstrates integrated runtime + evaluator behavior without provider calls or real customer mutations. It is not a live customer deployment demonstration.

## 5. Evidence and monitoring surfaces

For a run, inspect `RunTrace` rather than relying only on final text. The normalized trace records lifecycle events such as proposal, policy check, tool call/result, observation, final response and run finish. Production evaluator/campaign outputs add deterministic classifications and reason codes.

Reviewer-level evidence surfaces:

- `research/results/final-delivery-evidence-index-2026-08-28.json` — exact repository evidence identities;
- `research/results/provider-free-final-delivery-demo-result-2026-08-28.json` — five demo result identities;
- EV-007 result/freeze — deterministic failure containment;
- EV-008 result/freeze — repeated-run stability;
- EV-011 result/freeze — customer-safe communication;
- `docs/BENCHMARK-INTEGRITY-GATE.md` — evaluation contamination/independence boundaries;
- `docs/RUBRIC-TO-EVIDENCE.md` — reviewer navigation.

For operational diagnosis, classify the failure at the earliest failing boundary instead of masking it with retries.

## 6. Failure and fallback behavior

### Invalid tool arguments

Strict B1 validation blocks malformed/incomplete arguments before transport. Treat the run as evaluator-invalid where applicable; do not rewrite it into a successful execution.

### Read/tool transport failure

The production path fails closed to `ABSTAIN / TOOL_BOUNDARY_FAILURE` without exposing raw exception material. Do not retry automatically unless a separately frozen policy explicitly authorizes a replacement class; the current delivery campaigns report zero automatic retries.

### Decision-source/provider payload failure

Malformed/unusable decision material fails safely rather than being converted into an invented action or answer. Provider execution is not required for the provider-free handoff.

### Missing/ambiguous evidence

Use clarification, abstention or escalation according to the trace decision. Do not fabricate certainty.

### Consequential action denied

The default `ProductionRuntime` has actions permanently disabled by its frozen config type and grants zero production action permissions. A denied action must stop before transport.

### Post-claim action transport uncertainty

In the controlled action profile the durable idempotency claim is acquired before transport. If transport then fails, the attempt is consumed/uncertain and must **not** be automatically replayed or described as successful. Human/operator reconciliation is required before any future action decision.

### Customer-facing communication

Do not expose credentials, raw exception/provider material, evaluator-private/gold information or unnecessary internal implementation details. Success claims must be supported by the trace; uncertain/failed actions must not be phrased as completed.

## 7. Current governed provider comparison boundary

There is currently no selected live provider and no automatic cross-provider fallback.

The current frozen candidate packet is the ADR-018→023 Cloudflare path:

```text
@cf/zai-org/glm-4.7-flash                    16 maximum attempts
@cf/nvidia/nemotron-3-120b-a12b              16 maximum attempts
total                                          32 maximum attempts
consumed                                        0 / 32 at current baseline
automatic retries                               0
fallbacks                                       0
warm-ups                                        0
parallel provider calls                         0
packet worst-case                               7937.522688 Neurons
Workers Paid / prepaid spillover                forbidden
```

The historical issue #44 OpenAI/Gemini packet remains repository evidence for its original scope. It is **not** the current live execution instruction and must not be substituted for the ADR-018→023 Cloudflare path.

### Current governance layers

```text
ADR-018   Cloudflare comparison preregistration
ADR-019   direct Workers AI client
ADR-020   executor/custody/resource accounting
ADR-021   original live authorization protocol
ADR-022   reset-window evidence fallback
ADR-023   entrypoint sufficiency audit + minimal launcher contract
```

ADR-023 freezes the conclusion that substantive composition is sufficient. No executor, custody, client or authorization rewrite is authorized for launcher convenience.

### Preconditions for any live invocation

Provider execution is separate from provider-free reproduction and requires all of the following:

```text
admissible reset-window evidence
valid short-lived receipt bound to exact custody root
exclusive Workers AI account window still intact
CLOUDFLARE_API_TOKEN provisioned only after receipt
CLOUDFLARE_ACCOUNT_ID provisioned only after receipt
explicit operator execution decision
0 consumed comparison attempts before attempt 1
```

If any prerequisite is absent or uncertain, remain at attempt 0 and use `LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED` where applicable. Do not probe credentials/accounts to infer readiness.

After all gates are true, the only current operational command is:

```text
python scripts/research/execute_cloudflare_live_comparison_v2.py --evidence <evidence.json> --receipt <receipt.json> --custody-root <canonical-root>
```

The launcher delegates to the frozen ADR-022 adapter and ADR-020 governed task with `fixture_result=False`. It does not expose provider/model/retry/fallback/budget options.

A provider-free regression failure is never a reason to execute the live comparison.

## 8. Rollback / reversal

No deployment platform is frozen by this handoff, so there is no evidence-backed claim of an exercised infrastructure deployment rollback. The implemented reversal controls are narrower and deterministic:

1. **Runtime behavior change:** revert the release/commit to the last frozen validated Git head and rerun the canonical clean reproduction.
2. **Consequential actions:** keep default `ProductionRuntime` action-disabled; do not enable actions as a recovery shortcut.
3. **Controlled action uncertainty:** never delete/reuse an idempotency claim to manufacture replay eligibility; reconcile the external state first.
4. **Provider comparison:** preserve custody/attempt ledgers; never reset a consumed/uncertain attempt by switching roots. A recovery needs a prospective governance decision.
5. **Scientific evidence:** frozen artifacts remain immutable. Do not reconstruct or replace the missing C4 artifact; retain the external blocker.
6. **Benchmark/blind breach:** reclassify consumed evidence according to the benchmark-integrity rules; do not erase the breach.

Thus the delivery has a documented **code/config/fail-closed reversal path**, not proof of a production deployment rollback exercise.

## 9. Security/privacy boundaries

Never persist or print provider secrets, bearer tokens, raw idempotency secrets, evaluator-private gold, blind outcomes or customer-sensitive payloads in handoff artifacts. Synthetic sentinels are used by fault campaigns to prove leakage detection without real credentials.

Identity and evaluation seed are runner/runtime-owned and outside model/provider control. API permission enforcement and project/system safety policy are distinct checks.

For the current Cloudflare comparison specifically, the launcher accepts no secret CLI argument. `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` are consumed from the runtime environment only after receipt issuance, and ADR-020 custody/result artifacts remain sanitized.

## 10. Known limitations and non-claims

The final handoff must state these rather than hiding them:

- live Cloudflare provider comparison remains unexecuted at 0/32 calls; no model/provider is selected;
- provider latency, live reliability and live cost/resource behavior are not measured yet;
- no credential/account probe has occurred;
- no real customer mutation has occurred;
- the integrated demo is provider-free/supplied-test evidence;
- the default production runtime remains action-disabled;
- C4 per-group/slice reporting is blocked on the exact evaluator-side artifact SHA `b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c` (177350 bytes, 144 rows);
- `FRESH_BLIND`, `LEGACY_LOCKED_TEST` and semantic/private evaluation are not authorized;
- no independent fresh-blind generalization claim is available;
- global final architecture and unconditional production readiness are not frozen/authorized.

## 11. Reviewer completion checklist

A provider-free handoff is reproducible only if:

- dependency installation succeeds from a clean checkout;
- complete production tests and ADR-004 regression pass;
- EV-007, EV-008 and EV-011 reproduce their frozen SHAs;
- ADR-016 demo reproduces `43903731…` and the evidence index resolves with zero violations;
- the final acceptance-audit validator passes;
- provider calls remain 0/32 unless a separately authorized ADR-018→023 governed Cloudflare execution records consumed attempts;
- credential probes and real customer mutations remain zero;
- scientific/C4 authorization state is unchanged unless separately reconciled.

If any item fails, report the exact failed boundary and preserve the failure; do not broaden claims.
