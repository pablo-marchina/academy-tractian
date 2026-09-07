# Technical Presentation — Recording Checklist

Use immediately before the 5-minute technical video. Goal: eliminate improvisation and avoid claims stronger than live evidence.

## 1. Product preflight

- [ ] public hosted product opens;
- [ ] sign-in works without `managed_session_unavailable`;
- [ ] **Home**, **Analyses**, **Technical** load;
- [ ] selected result/evidence detail opens;
- [ ] PRIMARY `run_97b91f6e0feb91184283` is accessible;
- [ ] R420 unavailable `run_547b2a62d84ef56a3d3d` is accessible;
- [ ] optional data-quality `run_21813cb7b4ad9adbdc5e` is accessible;
- [ ] Technical Current analysis trace is readable;
- [ ] Technical Quality evaluation is visible;
- [ ] Technical Actions governed boundary is visible;
- [ ] no recorded screen contains secrets/private evaluator/action material.

If a required live component is unavailable, use persisted real hosted evidence; do not substitute local/mock evidence while calling it production.

## 2. Identity check

Before speaking exact deployment claims verify current active status. Expected at this documentation checkpoint:

```text
backend source  3545d75c00ca30419e0f47e8b1950aa50cbbf462
frontend        1bc124a8d4dbd029178ff8129b25452129445de7
supplied API    47561c1175181b508139e23e6e39b555c1347d57
```

If hosted identities have advanced, use real current values and update active docs before final recording.

## 3. Primary read run

Recommended: `run_97b91f6e0feb91184283`.

Required:

- [ ] R310 discovered through identity/company/fleet;
- [ ] condition evidence exists;
- [ ] spectrum asset→point progression is visible/explainable;
- [ ] terminal `partial` is visible;
- [ ] evaluation exists;
- [ ] no claim that this read run proves action readiness.

Do not describe all same-name spectrum calls as redundancy; verify argument/resource progression.

## 4. Secondary read run

Use `run_547b2a62d84ef56a3d3d` to demonstrate **authorized missing-resource fail-closed**.

Say: R420 was not found in the authorized fleet.

Do not say R420 is in another tenant/plant, the API failed, or a true bilateral comparison occurred.

## 5. Current action evidence

Know these facts before recording:

```text
PR #211 merge       1a1e7139bfa0361416120b3f21937c4048b5bb1f
PR #213 merge       3545d75c00ca30419e0f47e8b1950aa50cbbf462
required gate       34164123263 — SUCCESS
healthy #213 deploy 2cbc4215-f59a-4947-8691-0d4776458445 — SUCCESS
fresh write gate    5ba36471-776c-4e15-919b-56e2da216b74 — FAILED SAFE
live blocker        update_asset_config → HTTP 403 / accepted=false
```

Allowed explanation:

- local governed action architecture is implemented and CI-qualified;
- production composition can enable five governed actions;
- fresh smoke correctly blocked promotion when vendor acceptance failed;
- supplied runtime investigation found separate upstream users for low versus high/escalation permissions;
- corrective actor routing will keep local user as authorization/audit principal and select vendor actor server-side by company+permission;
- corrective routing is not yet merged/proven at this checkpoint.

Do not widen the claim beyond this.

## 6. Browser prep

- [ ] clean browser window;
- [ ] no personal/bookmark clutter if avoidable;
- [ ] notifications closed;
- [ ] readable 1080p zoom;
- [ ] no credential-manager overlays;
- [ ] stable viewport;
- [ ] no devtools containing auth/session headers.

## 7. Architecture assets

Have open:

- [ ] runtime overview;
- [ ] identity/session overlay;
- [ ] V13 asset-grounding overlay;
- [ ] tool execution/drill-down overlay;
- [ ] terminal + response-mode overlay;
- [ ] evaluator isolation;
- [ ] governed action boundary;
- [ ] local requester vs vendor actor overlay;
- [ ] failed-validation containment overlay;
- [ ] production deployment/realtime;
- [ ] final recap.

## 8. Timing rehearsal

```text
00:28 architecture complete
00:55 identity/Home complete
01:25 grounding complete
02:05 tool/drill-down complete
02:40 result/response-mode complete
03:05 missing-resource case complete
03:38 evaluator complete
04:15 action boundary complete
04:40 deployment complete
05:00 stop
```

Tolerance: ±5s. Cut examples before speed-reading safety semantics.

## 9. Allowed current claims

- [ ] hosted product is remote;
- [ ] Railway hosts production web/API;
- [ ] Neon provides durable PostgreSQL and managed auth;
- [ ] Cloudflare GLM-4.7-Flash is provisional Release 0 provider;
- [ ] supplied TRACTIAN API is remotely hosted for the project;
- [ ] 18 canonical operations exist: 13 reads + 5 governed actions;
- [ ] V13 resolves explicit asset labels through authorized fleet discovery;
- [ ] relevant diagnostics require condition evidence;
- [ ] response modes are complete/partial/inconclusive/conflict/unavailable;
- [ ] post-runtime deterministic evaluation is promoted;
- [ ] current auth boundary distinguishes invalid session from temporary identity-service unavailability;
- [ ] same-name read calls can be legitimate point drill-down;
- [ ] governed action proposal/custody/confirmation/grants/idempotency/lease architecture is implemented and CI-qualified;
- [ ] five-action vendor acceptance is not yet proven;
- [ ] the live write gate surfaced `update_asset_config` HTTP 403 and failed safely;
- [ ] vendor actor selection must be server-owned, not model/browser-controlled.

## 10. Unsupported wording

- [ ] do not say Cloudflare is final/best provider;
- [ ] do not say all 18 operations have been exercised successfully live;
- [ ] do not say all 13 reads have already been exercised by recent V13 prompts;
- [ ] do not say external actions remain globally disabled/read-only;
- [ ] do not say all five actions work or are 100% reliable;
- [ ] do not say the upstream actor routing fix is already production-proven;
- [ ] do not call supplied API TRACTIAN corporate production infrastructure;
- [ ] do not say semantic confidence/usability is human-calibrated;
- [ ] do not say every repeated tool name is a loop;
- [ ] do not claim final SLO/HA/RTO/RPO/security/value evidence;
- [ ] do not claim access to chain-of-thought.

## 11. Secret/privacy checklist

Never record `.env`, API/provider/database keys, cookies/session tokens, authorization headers, private action custody, action grants, idempotency material, vendor actor mappings, evaluator-private oracle/gold, protected benchmark material or hidden model reasoning.

## 12. Failure fallback

### Provider unavailable

Use a prepared persisted real V13 run and state that you are inspecting persisted hosted evidence.

### TRACTIAN read API unavailable

Use persisted remote evidence. Do not substitute local/mock.

### Managed auth unavailable

Do not repeatedly enter credentials. Show/state temporary unavailable/retry truthfully.

### Action surface differs

Do not execute a fresh consequential action merely for the video. Use the documented Technical Actions state and current hosted/progress evidence. Never turn a 403 into a success claim.

### UI navigation differs

Stop and verify current hosted frontend identity. Do not follow obsolete navigation.

## 13. Final 60-second check

- [ ] recorder resolution correct;
- [ ] microphone stable;
- [ ] signed in;
- [ ] primary/secondary runs known;
- [ ] overlays open;
- [ ] action limitation wording memorized;
- [ ] no secret-bearing terminal visible;
- [ ] stopwatch ready off-screen;
- [ ] first frame architecture;
- [ ] last frame final recap.