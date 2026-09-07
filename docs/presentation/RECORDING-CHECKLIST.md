# Technical Presentation — Recording Checklist

Use this immediately before recording the 5-minute technical video.

The goal is to eliminate improvisation and avoid making claims stronger than the live evidence.

---

## 1. Product preflight

Before opening the recorder, verify:

- [ ] public hosted product opens successfully;
- [ ] sign-in works;
- [ ] the expected authenticated user/org context is available;
- [ ] `Results`, `Evidence`, `Investigation` and `Engineering` load;
- [ ] primary prepared run can be started;
- [ ] at least one remote TRACTIAN read completes;
- [ ] evidence is persisted and visible;
- [ ] evaluation for the selected primary run is visible after completion;
- [ ] one persisted `ESCALATE`, `ABSTAIN` or `CLARIFY` run is ready as secondary example;
- [ ] action capability/proposal view is visible;
- [ ] no screen that will be recorded contains secrets or private evaluator material.

If any required live component is unavailable, do not improvise a false live claim. Use the fallback section below.

---

## 2. Primary run selection

The primary run should maximize technical density per second.

### Required characteristics

- [ ] 2–3 meaningful read calls;
- [ ] readable tool names;
- [ ] understandable arguments;
- [ ] useful evidence returned;
- [ ] clear terminal state, preferably `FINAL`;
- [ ] trace/timeline is non-trivial but readable;
- [ ] deterministic evaluation data is available;
- [ ] no consequential external action is required;
- [ ] completion time is predictable enough for recording.

### Reject a candidate run if

- it frequently times out;
- it requires too many repetitive reads;
- its evidence is impossible to explain visually;
- the final answer is semantically unclear;
- the evaluator surface is empty;
- it depends on unpromoted functionality.

---

## 3. Secondary run selection

Prepare exactly one persisted secondary run.

Preferred order:

1. `ESCALATE`;
2. `ABSTAIN`;
3. `CLARIFY`.

The secondary run should visibly demonstrate:

- [ ] why the main agent cannot safely finish;
- [ ] evidence already collected;
- [ ] unresolved/ambiguous condition;
- [ ] human/user next step.

Do not execute a second live run during the recording unless the main run is exceptionally fast and deterministic.

---

## 4. Browser preparation

- [ ] use a clean browser window;
- [ ] hide bookmarks/personal tabs if not needed;
- [ ] close notifications;
- [ ] zoom so tool names, args and evaluator metrics are readable at 1080p;
- [ ] keep only the product and architecture asset tabs open;
- [ ] disable extensions/popups that can alter the screen;
- [ ] ensure no credential manager overlays appear;
- [ ] keep product UI in a stable width/layout throughout the capture.

Recommended: record at 1080p or higher, then crop in editing rather than zooming unpredictably during the run.

---

## 5. Architecture asset preparation

Have these overlays ready before recording:

- [ ] runtime boundary overview;
- [ ] identity/tenant boundary;
- [ ] tool execution boundary;
- [ ] evaluator isolation;
- [ ] consequential action boundary;
- [ ] production deployment;
- [ ] final 9-step recap.

Source: [`ARCHITECTURE-OVERLAYS.md`](ARCHITECTURE-OVERLAYS.md).

Do not switch to the full canonical architecture diagram if it becomes unreadable. Presentation overlays exist to preserve the same truth at a lower visual density.

---

## 6. Timing rehearsal

Run one rehearsal with a stopwatch.

Target checkpoints:

```text
00:25 architecture overview complete
00:50 identity boundary complete
01:25 primary run started / controller explained
02:00 tool execution explained
02:30 evidence/trace explained
03:00 terminal policy complete
03:40 evaluator complete
04:10 action boundary complete
04:40 deployment complete
05:00 stop
```

Tolerance: ±5 seconds per checkpoint.

If over time, cut examples — never speed-read architecture semantics.

---

## 7. Claim discipline checklist

### Allowed current claims

- [ ] hosted product is remote;
- [ ] frontend/backend use Railway serving path;
- [ ] durable state uses Neon PostgreSQL;
- [ ] managed auth is server validated;
- [ ] model provider in Release 0 is Cloudflare GLM-4.7-Flash and is provisional;
- [ ] supplied TRACTIAN API is remotely hosted for the project;
- [ ] 18 canonical operations exist;
- [ ] 13 reads are live in Release 0;
- [ ] 5 consequential actions are proposal-only in Release 0;
- [ ] `FINAL`, `CLARIFY`, `ABSTAIN`, `ESCALATE` are promoted terminal behaviors;
- [ ] post-runtime deterministic evaluation is promoted;
- [ ] evidence/history/evaluation persistence and authenticated SSE are promoted.

### Forbidden/unsupported wording

- [ ] do **not** say Cloudflare is the final/best provider;
- [ ] do **not** say all 18 operations execute live;
- [ ] do **not** say consequential external actions are enabled;
- [ ] do **not** say supplied API is TRACTIAN corporate production infrastructure;
- [ ] do **not** say semantic judge is authoritative if not human-calibrated;
- [ ] do **not** say a source merge proves an identical hosted deployment;
- [ ] do **not** expose or claim access to chain-of-thought.

---

## 8. Secret / privacy checklist

Never record:

- [ ] `.env` contents;
- [ ] API/provider keys;
- [ ] database credentials;
- [ ] cookies/session tokens;
- [ ] authorization headers;
- [ ] private action custody payloads;
- [ ] evaluator-private oracle/gold text;
- [ ] protected benchmark artifacts containing private expected answers;
- [ ] raw hidden model reasoning.

If a browser/devtools view could expose any of these, do not use it in the video.

---

## 9. Audio checklist

- [ ] narration is technical, not promotional;
- [ ] class/function names are pronounced consistently;
- [ ] explain responsibility before implementation detail;
- [ ] use “proposes” for model decisions and “executes” only for actual execution boundary;
- [ ] explicitly distinguish runtime and evaluator;
- [ ] explicitly distinguish proposal and authorization;
- [ ] explicitly state the current action limitation;
- [ ] avoid generic phrases like “AI analyzes everything”.

Useful sentence structure:

```text
<Component A> owns <responsibility>.
<Component B> can only <bounded operation>.
The boundary exists so <failure/safety/evaluation reason>.
```

---

## 10. Failure fallback plan

### If the provider is temporarily unavailable

Do not claim a live provider call occurred.

Use a previously persisted real hosted run and say:

> “Vou inspecionar uma execução hospedada já persistida para mostrar o mesmo runtime path sem depender da disponibilidade do provider durante a gravação.”

### If the supplied TRACTIAN API is temporarily unavailable

Use a previously persisted run with remote evidence already recorded. Do not substitute a local/mock request while calling it production.

### If the evaluation panel fails to load

Use the persisted evaluation artifact/surface that already exists, but keep it tied to the same run identity if possible.

### If the primary run ends in a different safe terminal

Do not restart repeatedly just to obtain `FINAL` unless time permits. Explain the observed terminal if technically defensible, then use the prepared persisted `FINAL` only if needed for the evaluator walkthrough.

### If a UI tab is broken

Use the closest truthful promoted visualization or architecture overlay. Never invent screenshots.

---

## 11. Final 60-second pre-record checklist

- [ ] recorder is running at correct resolution;
- [ ] microphone level is stable;
- [ ] hosted product is already signed in;
- [ ] primary request text is copied and ready;
- [ ] secondary run is bookmarked/known in history;
- [ ] architecture overlays are open;
- [ ] no secret-bearing terminal is visible;
- [ ] stopwatch/timeline is available off-screen;
- [ ] first frame is architecture, not desktop clutter;
- [ ] last frame is the 9-step architecture recap.

Then record in one pass if possible.