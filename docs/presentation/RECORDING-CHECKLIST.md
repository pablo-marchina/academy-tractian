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
- [ ] Technical Actions boundary is visible;
- [ ] no recorded screen contains secrets/private evaluator material.

If a required live component is unavailable, use persisted real hosted evidence; do not substitute local/mock evidence while calling it production.

## 2. Identity check

Before speaking exact deployment claims verify current active status. Expected at this documentation checkpoint:

```text
backend   08866da60245f58f217981b7ae668b10be45cc67
frontend  1bc124a8d4dbd029178ff8129b25452129445de7
API       47561c1175181b508139e23e6e39b555c1347d57
```

If hosted identities have advanced, use real current values and update active docs before final recording.

## 3. Primary run

Recommended: `run_97b91f6e0feb91184283`.

Required:

- [ ] R310 was discovered through identity/company/fleet;
- [ ] condition evidence exists;
- [ ] spectrum asset→point progression is visible or explainable;
- [ ] terminal `partial` is visible;
- [ ] evaluation exists;
- [ ] no consequential external action required.

Do not describe all same-name spectrum calls as redundancy; verify argument/resource progression.

## 4. Secondary run

Use `run_547b2a62d84ef56a3d3d` to demonstrate **authorized missing-resource fail-closed**.

Say: R420 was not found in the authorized fleet.

Do not say:

- R420 is in another tenant/plant;
- API failed;
- a true R310-vs-R420 technical comparison occurred.

## 5. Browser prep

- [ ] clean browser window;
- [ ] no personal/bookmark clutter if avoidable;
- [ ] notifications closed;
- [ ] readable 1080p zoom;
- [ ] no credential-manager overlays;
- [ ] stable viewport;
- [ ] no devtools containing auth/session headers.

## 6. Architecture assets

Have open:

- [ ] runtime overview;
- [ ] identity/session overlay;
- [ ] V13 asset-grounding overlay;
- [ ] tool execution/drill-down overlay;
- [ ] terminal + response-mode overlay;
- [ ] evaluator isolation;
- [ ] action boundary;
- [ ] production deployment/realtime;
- [ ] final recap.

## 7. Timing rehearsal

```text
00:28 architecture complete
00:55 identity/Home complete
01:25 grounding complete
02:05 tool/drill-down complete
02:40 result/response-mode complete
03:05 missing-resource case complete
03:42 evaluator complete
04:08 action boundary complete
04:38 deployment complete
05:00 stop
```

Tolerance: ±5s. Cut examples before speed-reading safety semantics.

## 8. Allowed current claims

- [ ] hosted product is remote;
- [ ] Railway hosts production web/API;
- [ ] Neon provides durable PostgreSQL and managed auth;
- [ ] Cloudflare GLM-4.7-Flash is provisional Release 0 provider;
- [ ] supplied TRACTIAN API is remotely hosted for the project;
- [ ] 18 canonical operations exist;
- [ ] 13 are read operations available to Release 0; 5 are action operations with external execution disabled;
- [ ] V13 resolves explicit asset labels through authorized fleet discovery;
- [ ] relevant diagnostics require condition evidence;
- [ ] response modes are complete/partial/inconclusive/conflict/unavailable;
- [ ] post-runtime deterministic evaluation is promoted;
- [ ] current auth boundary distinguishes invalid session from temporary identity-service unavailability;
- [ ] same-name read calls can be legitimate point drill-down.

## 9. Unsupported wording

- [ ] do not say Cloudflare is final/best provider;
- [ ] do not say all 18 operations execute live;
- [ ] do not say all 13 reads have already been exercised by recent V13 user prompts;
- [ ] do not say external actions are enabled;
- [ ] do not call supplied API TRACTIAN corporate production infrastructure;
- [ ] do not say semantic confidence is human-calibrated;
- [ ] do not say every repeated tool name is a loop;
- [ ] do not claim final SLO/HA/RTO/RPO/security/value evidence;
- [ ] do not claim access to chain-of-thought.

## 10. Secret/privacy checklist

Never record `.env`, API/provider/database keys, cookies/session tokens, authorization headers, private action custody, evaluator-private oracle/gold, protected benchmark material or hidden model reasoning.

## 11. Failure fallback

### Provider unavailable

Use the prepared persisted real V13 run and say that you are inspecting already-persisted hosted evidence rather than claiming a fresh model call.

### TRACTIAN API unavailable

Use persisted remote evidence. Do not substitute local/mock.

### Managed auth unavailable

Do not repeatedly enter credentials. The correct UI state is temporary unavailable/retry; use persisted recording/evidence only if needed and state the live auth condition truthfully.

### Evaluation panel unavailable

Use a persisted evaluation surface/artifact tied to the same run where possible.

### UI navigation differs

Stop and verify current hosted frontend identity. Do not follow the obsolete four-tab script.

## 12. Final 60-second check

- [ ] recorder resolution correct;
- [ ] microphone stable;
- [ ] signed in;
- [ ] primary/secondary runs known;
- [ ] overlays open;
- [ ] no secret-bearing terminal visible;
- [ ] stopwatch ready off-screen;
- [ ] first frame architecture;
- [ ] last frame final nine-step recap.