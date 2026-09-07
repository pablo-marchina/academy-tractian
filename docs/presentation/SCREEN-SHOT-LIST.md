# Technical Presentation — Screen Shot List

This is the exact capture plan for the 5-minute technical video.

Use together with [`05-MIN-TECHNICAL-SCREENPLAY.md`](05-MIN-TECHNICAL-SCREENPLAY.md).

## Capture rule

Every shot must answer at least one technical question:

1. Who owns authority?
2. Who owns control flow?
3. Who can execute a tool?
4. Where does external I/O happen?
5. How does evidence become auditable?
6. How is failure/uncertainty represented?
7. How is the run evaluated independently?
8. Where is durable truth stored?

If a screen answers none of these, cut it.

---

## Shot 01 — Full architecture

**Duration:** 20–25 s  
**Source:** architecture overlay, not raw code.

### Must show

```text
Browser / React
→ FastAPI production-api
→ AgentController
→ DecisionSource
→ HarnessRunner / ToolSpec
→ supplied TRACTIAN API

RunTrace
→ ProductionEvaluator
→ Neon PostgreSQL
→ SSE / Frontend
```

### Highlight in order

1. identity/tenant boundary;
2. runtime/control-flow boundary;
3. tool/network boundary;
4. evaluator/persistence boundary.

### Do not show

- every internal class;
- every provider experiment;
- all deployment metadata.

---

## Shot 02 — Authenticated product + tenant context

**Duration:** 20–25 s  
**UI depth:** Results.

### Must show

- application is signed in;
- current user/org context if safely visible;
- no developer/local environment;
- public hosted product UI.

### Overlay

```text
managed session
→ server validation
→ AuthenticatedRuntimeContext
→ PostgreSQL org scope
→ RLS
```

### Avoid

- cookies;
- devtools Network headers;
- auth tokens;
- secret environment variables.

---

## Shot 03 — Submit primary run

**Duration:** 25–35 s  
**UI depth:** Results.

### Primary run requirements

Choose one scenario that:

- is already known to complete reliably;
- requires 2–3 meaningful read operations;
- returns evidence understandable on-screen;
- terminates in a clear `FINAL` if possible;
- has evaluation artifacts available after completion;
- does not require consequential external action execution.

### Must show

- request text;
- click/submit;
- run created;
- human-readable progress.

### Architecture highlights

```text
Browser
→ FastAPI
→ persist run
→ AgentController
→ DecisionSource
```

---

## Shot 04 — Structured decision + tool proposal

**Duration:** 15–20 s  
**UI depth:** Investigation.

### Must show

One real operation with:

- canonical tool name;
- arguments;
- validation/execution state;
- associated result/evidence reference.

### Good examples

Prefer a read that is semantically obvious to the reviewer, such as an asset, analysis, model/data-state or related industrial resource lookup.

### Overlay

```text
DecisionSource
→ structured TOOL_CALL
→ ToolSpec registry
→ B1/B2 deterministic checks
→ HarnessRunner
```

### Narration anchor

“The model proposes; the execution boundary decides whether and how the call can run.”

---

## Shot 05 — Remote TRACTIAN API result

**Duration:** 15–20 s  
**UI depth:** Investigation or Evidence.

### Must show

- successful remote read;
- returned industrial information;
- conversion into evidence/observation;
- timing/status if already exposed safely.

### Overlay

```text
HarnessRunner
→ ProductionTractianTransport
→ typed HTTPS
→ supplied TRACTIAN API
→ normalized evidence
```

### Required claim discipline

Say **“API fornecida pela TRACTIAN, hospedada remotamente para o projeto”** or equivalent.

Do not call it TRACTIAN customer/corporate production infrastructure.

---

## Shot 06 — Evidence lineage

**Duration:** 20–25 s  
**UI depth:** Evidence.

### Must show

At least one visible chain:

```text
terminal/claim or observation
→ evidence
→ tool result
→ tool name + arguments
→ timestamp/resource/provenance
```

### Technical point

The final answer is not the only artifact; its supporting observable evidence is separately inspectable.

---

## Shot 07 — Trace / dynamic investigation

**Duration:** 15–20 s  
**UI depth:** Investigation.

### Must show

A timeline or graph containing multiple stages, ideally:

```text
decision
→ validation
→ tool execution
→ observation
→ next decision
→ terminal
```

### Explicitly say

`RunTrace` stores observable execution behavior. It does not expose hidden chain-of-thought.

---

## Shot 08 — Main terminal result

**Duration:** 15–20 s  
**UI depth:** Results.

### Must show

- `FINAL` or actual terminal status;
- concise conclusion;
- next step;
- evidence status/coverage if rendered.

### Technical point

Terminal state is structured, not just free-form text.

---

## Shot 09 — Secondary safe-degradation run

**Duration:** 15–20 s  
**UI depth:** Results/Evidence.

Use an already persisted run. Do not wait for a second live run.

### Preferred

`ESCALATE` with visible:

- escalation reason;
- evidence already collected;
- unresolved condition;
- human next step.

### Alternative

`ABSTAIN` or `CLARIFY` if it demonstrates the failure/uncertainty policy more clearly.

### Technical point

Insufficient/conflicting evidence changes the terminal policy instead of forcing a fabricated conclusion.

---

## Shot 10 — Evaluation pipeline

**Duration:** 15–20 s  
**UI depth:** Engineering.

### Must show

```text
completed RunTrace
→ ProductionEvaluator
→ deterministic checks
→ persisted safe evaluation
```

### Technical point

Evaluation is post-runtime and evaluator-private reference material is outside the agent context.

---

## Shot 11 — Expected vs Observed / metrics

**Duration:** 20–25 s  
**UI depth:** Engineering / Eval.

### Prioritize visible metrics in this order

1. function/tool selection;
2. arguments/validation;
3. expected trajectory or read coverage;
4. evidence correctness/coverage;
5. terminal/decision correctness;
6. action/escalation correctness;
7. safety/failure behavior;
8. stability.

### Must not do

- invent a metric that is not currently rendered/evidenced;
- describe a semantic judge as authoritative if it is not human-calibrated;
- show private gold text.

### Visual comparison

Prefer a compact table:

```text
Expected              Observed
get_asset             get_asset       ✓
get_analysis          get_analysis    ✓
get_model_state       get_model_state ✓
terminal: FINAL       FINAL           ✓
```

---

## Shot 12 — Action boundary

**Duration:** 20–25 s  
**UI depth:** Investigation / Engineering.

### Must show

- action capability exists;
- proposal state;
- explicit limitation.

### Overlay

```text
LLM proposes
→ deterministic schema/policy boundary
→ action proposal
→ confirmation/authorization architecture
→ external execution
```

Place a strong visual label on the final step:

```text
RELEASE 0
EXTERNAL CONSEQUENTIAL EXECUTION DISABLED
```

### Technical point

Proposal visibility does not imply execution authority.

---

## Shot 13 — Deployment architecture

**Duration:** 20–25 s  
**Source:** overlay diagram.

### Must show

```text
Browser
→ Railway production-web
→ Railway production-api
   ├→ Neon Auth
   ├→ Cloudflare Workers AI
   ├→ supplied TRACTIAN API
   └→ Neon PostgreSQL
```

### Then show realtime path

```text
PostgreSQL event row
→ commit
→ LISTEN/NOTIFY wake-up
→ durable catch-up by cursor
→ authenticated SSE
→ React state
```

### Technical point

Rows/cursors are truth; notification is only wake-up.

---

## Shot 14 — Final numbered architecture

**Duration:** 15–20 s

Reveal one number at a time:

```text
1 Auth/session validation
2 Tenant/run ownership
3 AgentController + DecisionSource
4 ToolSpec validation
5 HarnessRunner + TRACTIAN HTTPS
6 Evidence + RunTrace
7 Terminal policy
8 ProductionEvaluator
9 PostgreSQL + SSE
```

End here. No extra outro animation is needed.

---

# UI preparation before recording

## Results

Have available:

- empty/ready state before primary run;
- primary run after completion;
- one secondary `ESCALATE`/`ABSTAIN` persisted run.

## Evidence

Ensure the primary run has:

- multiple evidence records;
- provenance/tool information visible;
- no sensitive/private data.

## Investigation

Ensure the primary run has:

- multiple events;
- at least one tool call with arguments;
- trace/timeline graph readable at 1080p.

## Engineering

Ensure there is a view that can show:

- architecture/capabilities;
- evaluator result;
- expected-vs-observed or closest promoted equivalent;
- action boundary/capability state.

---

# What should never appear on screen

- `.env` files;
- terminal with secrets;
- provider/API keys;
- session cookies or authorization headers;
- raw evaluator-private oracle/gold;
- hidden chain-of-thought;
- private benchmark paths containing protected material;
- localhost as evidence of the production system;
- unsupported “all actions live” wording;
- unsupported “final best provider” wording.
