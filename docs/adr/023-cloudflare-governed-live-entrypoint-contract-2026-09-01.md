# ADR-023 — Cloudflare governed live entrypoint audit and launcher contract

**Status:** ACCEPTED  
**Decision state:** `SUBSTANTIVE_COMPOSITION_SUFFICIENT / OPERATIONAL_ENTRYPOINT_MISSING / MINIMAL_LAUNCHER_ONLY / LIVE_NOT_AUTHORIZED`  
**Implementation validation:** `PROVIDER_FREE_VALIDATED / LIVE_NOT_AUTHORIZED`  
**Date:** 2026-09-01  
**Base audited:** `main@0a7d093c87c3c746eb45bbfa1e7e82e4de7f8502`  
**Provider/model inference calls in this audit:** 0  
**Credential/account probes in this audit:** 0  
**Live network validation in this audit:** 0  
**Comparison attempts consumed:** 0 / 32  
**Production provider/model selected:** NO

## Decision question

Before any new code is created, does the current repository already contain sufficient substantive composition for the ADR-022 authorization path to invoke the frozen ADR-020 Cloudflare executor/custody path, or is new executor, custody, client or authorization behavior required?

## Decision

The repository already contains sufficient substantive composition.

The only demonstrated material gap is the absence of one canonical operational entrypoint that composes the already-frozen authorization and live-task APIs without requiring ad-hoc Python during the short-lived authorization window.

Freeze the audit conclusion as:

```text
substantive composition sufficient
operational entrypoint missing
no executor changes authorized
no custody changes authorized
no client changes authorized
no authorization-policy changes authorized
no comparison/scoring changes authorized
no project-wide CLI/framework work authorized
minimal gate-specific launcher only
```

This ADR authorizes only implementation and provider-free validation of that minimal launcher. It does **not** authorize provider inference or comparison attempt 1.

## Evidence supporting sufficiency

The current path already provides all substantive responsibilities:

```text
ADR-022 reset-window evidence + receipt
      ↓
reset_window_authorization_to_adr020_pre_live_evidence(...)
      ↓
ADR-020 CloudflarePreLiveEvidence
      ↓
CloudflareLiveSecrets
      ↓
build_cloudflare_one_shot_transport_v2()
      ↓
GovernedCloudflareLiveTaskV2.prepare(...)
      ↓
existing custody reservation + fixed run/ + write-ahead ledger
      ↓
execute_all()
      ↓
existing resource guards / no-replay / sanitized result
```

The authorization adapter already validates the receipt against the exact evidence, custody root and current UTC time before returning ADR-020 pre-live evidence. ADR-020 already owns provider client construction, resource accounting, custody, attempt claiming, no replay, execution and sanitized result handling.

Therefore a new wrapper carrying any of those semantics would be duplication rather than a justified capability.

## Frozen launcher contract

The prospective launcher is gate-specific research/operations composition code under:

```text
scripts/research/execute_cloudflare_live_comparison_v2.py
```

It is not a new production runtime and must not be added to `[project.scripts]`.

### Command-line inputs

Exactly these operator inputs are permitted:

```text
--evidence <reset-window-evidence.json>
--receipt <reset-window-receipt.json>
--custody-root <canonical-custody-root>
```

No provider, model, route, retry, fallback, budget, fixture, account, token or output-policy option is permitted.

`fixture_result` is not operator-configurable. The launcher must pass:

```text
fixture_result=False
```

### Secret inputs

Only after the receipt has already been issued may the launcher consume these environment variables:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

The launcher must not accept secrets on the command line, read a dotenv file, discover credentials, probe an account or serialize the values.

### Allowed project API surface

The launcher may call only the following existing Academy × TRACTIAN project APIs for substantive behavior:

```text
academy_tractian.cloudflare_live_authorization_reset_v2.CloudflareResetWindowEvidenceV1
academy_tractian.cloudflare_live_authorization_reset_v2.CloudflareResetWindowReceiptV1
academy_tractian.cloudflare_live_authorization_reset_v2.validate_frozen_reset_window_amendment
academy_tractian.cloudflare_live_authorization_reset_v2.reset_window_authorization_to_adr020_pre_live_evidence

academy_tractian.cloudflare_provider_live_v2.CloudflareLiveSecrets
academy_tractian.cloudflare_provider_live_v2.build_cloudflare_one_shot_transport_v2
academy_tractian.cloudflare_provider_live_v2.GovernedCloudflareLiveTaskV2.prepare
academy_tractian.cloudflare_provider_live_v2.GovernedCloudflareLiveTaskV2.execute_all
```

Standard-library parsing, path handling, environment access, UTC clock access and JSON serialization are infrastructure only and do not expand this API allowlist.

No direct construction of Cloudflare provider clients is allowed in the launcher; that remains owned by ADR-020 `GovernedCloudflareLiveTaskV2.prepare(...)`.

## Required launcher sequence

The launcher must perform only this sequence:

```text
1. parse evidence / receipt / custody-root paths
2. validate the frozen ADR-022 amendment
3. deserialize evidence as CloudflareResetWindowEvidenceV1
4. deserialize receipt as CloudflareResetWindowReceiptV1
5. call reset_window_authorization_to_adr020_pre_live_evidence(..., now_utc=current UTC)
6. read CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID from the environment
7. construct CloudflareLiveSecrets
8. construct the existing one-shot transport
9. call GovernedCloudflareLiveTaskV2.prepare(
       custody_root=...,
       secrets=...,
       pre_live_evidence=...,
       transport=...,
       fixture_result=False,
   )
10. call execute_all()
11. emit only the returned sanitized governed result
```

The receipt/evidence/custody validation therefore occurs before any network-capable live task is prepared or executed.

## Explicitly forbidden launcher behavior

The launcher must not implement or duplicate:

- provider/model selection;
- provider client request formatting;
- authorization rules;
- evidence derivation;
- receipt issuance;
- custody marker logic;
- ledger creation or state transitions;
- resource/Neuron accounting;
- H8/H9/H10 checks;
- retry, fallback, warm-up or parallelism;
- replay/resume behavior;
- exception sanitization owned by ADR-020;
- result scoring or adjudication;
- mutation of any frozen packet identity;
- alternate custody-root derivation;
- secret persistence or logging;
- a generic CLI/application framework.

## Files outside launcher scope

This implementation task is not authorized to modify substantive frozen implementation files, including:

```text
src/academy_tractian/cloudflare_provider_live_v2.py
src/academy_tractian/cloudflare_provider_client.py
src/academy_tractian/cloudflare_live_authorization_v1.py
src/academy_tractian/cloudflare_live_authorization_reset_v2.py
src/academy_tractian/cloudflare_provider_comparison_v2.py
src/academy_tractian/cloudflare_provider_provenance_v2.py
```

Historical ADR-018 through ADR-022 bytes must remain unchanged.

## Provider-free acceptance test

Exactly one new composition-focused test is justified for the launcher.

It must:

1. construct valid synthetic reset-window evidence;
2. issue a synthetic receipt using the existing authorization API;
3. invoke the launcher composition path with synthetic environment secrets;
4. exercise the real ADR-022 adapter;
5. reach the real `GovernedCloudflareLiveTaskV2` using an injected provider-free transport;
6. complete the frozen 32-attempt fixture geometry without network;
7. prove the launcher did not implement a second custody, client, executor or authorization mechanism.

The production launcher itself remains hard-pinned to `fixture_result=False`; the test may inject/monkeypatch the existing transport/task boundary only to keep provider calls at zero.

## Operational documentation reconciliation

The first CI run exposed an additional historical immutability constraint: `docs/FINAL-HANDOFF-RUNBOOK.md` is a direct byte-pinned artifact of the ADR-017 freeze (`c7df131f555e3b07161fd1d518965958d245555c`). Editing that file causes the canonical final-handoff audit and ADR-017 freeze regressions to fail.

Therefore the correct reconciliation preserves the historical bytes and uses a prospective addendum:

- `docs/NEXT-STEPS.md` names the exact launcher command after receipt issuance and secret provisioning;
- `docs/FINAL-HANDOFF-RUNBOOK.md` remains byte-for-byte unchanged as ADR-017 evidence;
- `docs/FINAL-HANDOFF-RUNBOOK-CLOUDFLARE-ADDENDUM-2026-09-01.md` prospectively supersedes only the provider-comparison guidance in that frozen runbook;
- historical OpenAI/Gemini issue #44 remains preserved as historical evidence, not current execution guidance;
- ADR-018 through ADR-022 remain immutable.

This is a governance-preserving resolution of the apparent conflict between “update the operational guidance” and “do not rewrite historical frozen artifacts.”

## Validation history

The first PR-associated `production-runtime` execution reached the complete production test suite and reported:

```text
307 passed
3 failed
```

All three failures were caused solely by modifying the ADR-017-pinned `docs/FINAL-HANDOFF-RUNBOOK.md` blob. No launcher/test failure was reported in that run. The frozen runbook was restored byte-for-byte and the prospective Cloudflare addendum was introduced instead.

The corrected candidate:

```text
fbdac76f885902f2d4f06d623957fd4e377aab00
```

then completed all 17 PR-associated workflows successfully, including:

```text
production-runtime
final-handoff-acceptance-audit
final-delivery-provider-free-reproduction
cloudflare-live-authorization-v1-provider-free
cloudflare-reset-window-amendment-provider-free
cloudflare-reset-window-evidence-capture-provider-free
provider-model-comparison-design-v2
```

The corrected `production-runtime` run reported:

```text
310 passed   python -m pytest -q tests
12 passed    python -m pytest -q research/e2/tests/test_controller.py
```

The final-handoff acceptance workflow passed its production tests, ADR-004 regression, EV-007, EV-008, EV-011, ADR-016 clean reproduction and final handoff audit.

All provider-free validation runs, including the initial documentation failure and the corrected success, consumed:

```text
provider inference        0
credential/account probes 0
live network validation   0
comparison attempts       0 / 32
```

Provider-free launcher acceptance is therefore complete. Live authorization remains a separate future gate.

## Live gate remains separate

Nothing in this audit, launcher implementation or provider-free test authorizes a live model request.

The live sequence remains:

```text
admissible reset-window evidence
→ short-lived receipt
→ only then provision Cloudflare secrets
→ explicit live execution decision
→ canonical launcher
→ frozen ADR-020 packet
```

Any evidence/exclusivity failure must terminate as:

```text
LIVE_PROVIDER_COMPARISON_EXTERNALLY_BLOCKED
```

The protocol must not be weakened to obtain a result.

## Post-D01 boundary

Only after provider D01 resolves or is explicitly bounded may the project return to the macro architecture plan:

```text
provider D01 result/bounded blocker
→ agent-topology materiality audit
→ minimum controlled topology comparison only if it can still change P0/P1
→ runtime/orchestration materiality one gate later
```

No LangGraph, multi-agent, RAG/vector/reranking, persistent-memory or generic runtime work is authorized by this ADR.
