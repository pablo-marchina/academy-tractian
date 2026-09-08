# Technical Presentation — Recording Checklist

Use immediately before the 5-minute technical video. Goal: eliminate improvisation and avoid claims stronger than live evidence.

**Provider claim checkpoint:** 2026-09-08 — Groq GPT-OSS-120B completed 85/85 and returned `NO_SELECTION`; no production provider promotion followed.

## 1. Product preflight

- [ ] public hosted product opens;
- [ ] sign-in works without `managed_session_unavailable`;
- [ ] Home, Analyses and Technical load;
- [ ] selected result/evidence detail opens;
- [ ] primary R310 run is accessible;
- [ ] R420 unavailable run is accessible;
- [ ] optional data-quality run is accessible;
- [ ] Technical Current analysis trace is readable;
- [ ] Technical Quality evaluation is visible;
- [ ] Technical Actions boundary is visible;
- [ ] no recorded screen contains secrets/private evaluator material.

If a live component is unavailable, use persisted real hosted evidence; do not substitute local/mock evidence while calling it production.

## 2. Identity check

Before exact deployment claims, verify [`../ACTIVE-PROJECT-STATUS.md`](../ACTIVE-PROJECT-STATUS.md). Source/docs/provider-research branch identities are separate from hosted backend/frontend/supplied-API identities.

If hosted identities have advanced, use the real current values and update the active status before recording.

## 3. Provider evidence check

Before mentioning provider selection, verify [`../PROVIDER-QUALIFICATION-STATUS-2026-09-08.md`](../PROVIDER-QUALIFICATION-STATUS-2026-09-08.md).

Current claim-safe facts:

```text
Groq openai/gpt-oss-120b
attempts           85/85
rubric pass        69/85 = 81.18%
reliability        70/85 = 82.35%
contract failures  9
repeat stability   11/17 = 64.71%
selection          NO_SELECTION
```

- [ ] say this is a **single-provider qualification**, not a completed Cloudflare-vs-Groq tournament;
- [ ] say Cloudflare GPT-OSS was quota-blocked in non-scored preflight and later removed from the requested path only if relevant;
- [ ] say production provider remained unchanged by this research;
- [ ] do not claim strict output has passed; it remains a challenger direction;
- [ ] do not claim the causal 21/21 is complete;
- [ ] do not show contaminated partial causal runs as final evidence.

## 4. Primary run

Required:

- [ ] R310 discovered through identity/company/fleet;
- [ ] condition evidence exists;
- [ ] spectrum asset→point progression is visible/explainable;
- [ ] terminal `partial` is visible;
- [ ] evaluation exists;
- [ ] no consequential external action required.

Do not describe same-name spectrum calls as redundancy without checking target/arguments.

## 5. Secondary run

Use the R420 unavailable run to demonstrate **authorized missing-resource fail-closed**.

Say: R420 was not found in the authorized fleet.

Do not say it is in another tenant/plant, that the API failed, or that a true bilateral comparison occurred.

## 6. Browser prep

- [ ] clean browser window;
- [ ] notifications closed;
- [ ] readable viewport;
- [ ] no credential-manager overlays;
- [ ] no devtools containing auth/session headers.

## 7. Architecture assets

Have open:

- [ ] runtime overview;
- [ ] identity/session overlay;
- [ ] asset-grounding overlay;
- [ ] tool execution/drill-down overlay;
- [ ] terminal + response-mode overlay;
- [ ] evaluator isolation;
- [ ] action boundary;
- [ ] production deployment/realtime;
- [ ] provider research/promotion boundary if used;
- [ ] final recap.

## 8. Timing rehearsal

```text
00:28 architecture complete
00:55 identity/Home complete
01:25 grounding complete
02:05 tool/drill-down complete
02:40 result/response-mode complete
03:05 missing-resource case complete
03:42 evaluator/provider qualification complete
04:08 action boundary complete
04:38 deployment complete
05:00 stop
```

Tolerance: ±5s. Cut examples before speed-reading safety semantics.

## 9. Allowed current claims

- [ ] hosted product is remote;
- [ ] Railway hosts production web/API;
- [ ] Neon provides durable PostgreSQL and managed auth;
- [ ] production provider remains provisional;
- [ ] supplied TRACTIAN API is remotely hosted for the project;
- [ ] 18 canonical operations exist: 13 reads + 5 action operations represented, with external execution disabled;
- [ ] explicit labels resolve through authorized fleet discovery;
- [ ] relevant diagnostics require appropriate evidence;
- [ ] response modes are complete/partial/inconclusive/conflict/unavailable;
- [ ] post-runtime deterministic evaluation is promoted;
- [ ] Groq GPT-OSS-120B 85/85 was rejected as `NO_SELECTION` under unchanged gates;
- [ ] provider experiments do not automatically change production;
- [ ] same-name reads can be legitimate point drill-down.

## 10. Unsupported wording

- [ ] do not say Cloudflare is final/best provider;
- [ ] do not say Groq is the final/best provider;
- [ ] do not say Groq won a Cloudflare comparison;
- [ ] do not say the final paired tournament completed;
- [ ] do not say 2048 tokens fix the failure;
- [ ] do not say low reasoning is globally superior;
- [ ] do not say strict structured output is production-ready;
- [ ] do not say all 18 operations execute live;
- [ ] do not say all 13 reads were recently exercised by user prompts;
- [ ] do not say external actions are enabled;
- [ ] do not say semantic confidence is human-calibrated;
- [ ] do not claim final SLO/HA/RTO/RPO/security/value evidence;
- [ ] do not claim access to chain-of-thought.

## 11. Secret/privacy checklist

Never record `.env`, provider/API/database keys, cookies/session tokens, authorization headers, private action custody, evaluator-private oracle/gold, protected benchmark material, raw sensitive provider payloads or hidden model reasoning.

## 12. Failure fallback

### Provider unavailable

Use prepared persisted production evidence and say you are inspecting persisted hosted evidence rather than claiming a fresh call.

### TRACTIAN API unavailable

Use persisted remote evidence. Do not substitute local/mock.

### Managed auth unavailable

Do not repeatedly enter credentials. Use truthful unavailable/retry semantics.

### Evaluation panel unavailable

Use persisted evaluation tied to the same run where possible.

### UI navigation differs

Verify current hosted frontend identity. Do not follow obsolete navigation.

## 13. Final 60-second check

- [ ] current active status open;
- [ ] current provider status open;
- [ ] recorder/microphone stable;
- [ ] signed in;
- [ ] primary/secondary runs known;
- [ ] overlays open;
- [ ] no secret-bearing terminal visible;
- [ ] first frame architecture;
- [ ] last frame final recap;
- [ ] provider wording says `NO_SELECTION`, not winner.
