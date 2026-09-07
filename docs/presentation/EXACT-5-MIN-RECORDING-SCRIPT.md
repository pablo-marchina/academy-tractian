# Exact 5-Minute Technical Recording Script

**Use this file literally while recording.**  
**Target duration:** 5:00  
**Language:** Portuguese  
**Style:** architecture walkthrough, no business pitch, no generic AI explanation.  
**Primary artifact:** one already-persisted hosted production run that completed successfully and contains tool calls, evidence, a terminal decision and an evaluation.

> Do not improvise claims. If a value shown in the UI differs from the examples below, point to the real value and keep the spoken claim qualitative.

---

# Recording setup before 00:00

Prepare the hosted product in a browser at the public production URL.

Have these two persisted runs ready:

- **PRIMARY RUN:** completed run, preferably `ORIENT` / customer-visible `Conclusion ready`, with at least 2 meaningful TRACTIAN read calls, evidence references and a persisted evaluation.
- **SAFE-DEGRADATION RUN:** completed `ESCALATE_HUMAN`, `ABSTAIN` or `ASK_CLARIFICATION` run.

Do not expose:

- cookies, bearer tokens or secrets;
- evaluator-private gold;
- `.env` or provider keys;
- hidden chain-of-thought;
- localhost windows.

Use the architecture diagrams from [`ARCHITECTURE-OVERLAYS.md`](ARCHITECTURE-OVERLAYS.md) as full-screen overlays where indicated.

---

# 00:00–00:32 — Full promoted architecture

## EXACT SCREEN

Full-screen architecture overlay. No browser chrome and no title slide.

Show only:

```text
Browser / React
      ↓
production-web / Caddy
      ↓
production-api / FastAPI
      ↓
AuthenticatedRuntimeContext
      ↓
AgentController
      ↕
DecisionSource / hosted model
      ↓
HarnessRunner + ToolSpec
      ↓
ProductionTractianTransport
      ↓
supplied TRACTIAN API

RunTrace
   ↓
ProductionEvaluator
   ↓
Neon PostgreSQL
   ↓
REST / authenticated SSE
```

Animate/highlight, in this order:

1. `AuthenticatedRuntimeContext`
2. `AgentController`
3. `HarnessRunner + ToolSpec`
4. `RunTrace → ProductionEvaluator`

## EXACT WORDS

> “Vou começar direto pela arquitetura promovida. O sistema foi dividido em quatro boundaries principais. Identidade e tenant ficam fora da LLM. O `AgentController` é dono do control flow. Toda execução de ferramenta passa pelo `HarnessRunner` e pelo contrato canônico de `ToolSpec`. E a avaliação acontece somente depois do runtime, a partir do `RunTrace` persistido. O princípio central é que o modelo pode propor uma decisão, mas ele não recebe autoridade sobre identidade, permissões ou acesso direto à rede.”

At **00:32**, hard cut to the hosted product.

---

# 00:32–00:55 — Hosted product and identity boundary

## EXACT SCREEN

Hosted browser, **01 Results** selected.

Keep visible:

- top bar: `ACADEMY × TRACTIAN`;
- title: `Industrial Agent Operations`;
- service state: `API healthy`;
- depth navigation:
  - `01 Results — Answer & next step`
  - `02 Evidence — Why this answer`
  - `03 Investigation — Runtime & operations`
  - `04 Engineering — Architecture & evals`

Do **not** open developer tools.

Place a small overlay on the right:

```text
managed session
→ server validation
→ AuthenticatedRuntimeContext
→ PostgreSQL tenant scope
→ RLS
```

## EXACT WORDS

> “Este é o produto hospedado. A sessão do navegador é validada no servidor, e o backend deriva o usuário e o tenant efetivos. O browser não pode escolher organization, role ou permission por header. O mesmo escopo é aplicado ao PostgreSQL, com RLS como uma boundary independente. Isso mantém identidade e autorização determinísticas e externas ao comportamento do modelo.”

At **00:55**, click **03 Investigation**.

---

# 00:55–01:38 — Runtime, controller and tool execution

## EXACT SCREEN

**03 Investigation — Runtime & operations**.

Select the prepared **PRIMARY RUN** in `Run Explorer` if it is not already selected.

Keep visible, in this order:

1. `View: HISTORICAL` or the actual persisted-view state;
2. `Selected safe run ID`;
3. metric cards: `Events`, `Model calls`, `Tool calls`, `Policy blocks`, `Evidence refs`, `Errors`;
4. `Trace Graph`.

Zoom/pan the Trace Graph until one complete path is readable:

```text
model decision
→ tool call
→ observation/tool result
→ next decision
→ terminal
```

Then point to one real tool call from the selected run.

Small overlay:

```text
DecisionSource
→ structured TOOL_CALL
→ ToolSpec lookup
→ deterministic validation
→ HarnessRunner
→ typed HTTPS
→ supplied TRACTIAN API
```

## EXACT WORDS

> “Aqui está uma execução real já persistida. O `AgentController` mantém um loop bounded e chama uma interface `DecisionSource` desacoplada do provider. A saída do modelo não é código executável: é uma decisão estruturada. Quando essa decisão é uma tool call, ela precisa resolver contra o registry de `ToolSpec`, passar pelas validações determinísticas e somente então o `HarnessRunner` pode executar o transporte.”

> “Então a separação é explícita: o modelo seleciona e parametriza; o runtime valida; o `HarnessRunner` executa. O contrato possui dezoito operações canônicas. Na Release 0, treze reads estão habilitadas no caminho remoto e cinco actions permanecem proposal-only.”

At **01:38**, click **02 Evidence**.

---

# 01:38–02:14 — Evidence lineage and observable trace

## EXACT SCREEN

**02 Evidence — Why this answer**.

Keep visible:

- heading `See why the answer is supported`;
- panel `Canonical event timeline`;
- panel `Terminal outcome`;
- panel `Safe references`.

Scroll the canonical timeline only enough to show at least one event containing:

- `tool`;
- `evidence`;
- `status` and/or `latency` if present;
- event sequence number.

If possible, keep the tool event and its corresponding evidence event on screen together.

Place this small overlay:

```text
tool call + args
→ remote result
→ normalized observation
→ evidence ID
→ RunTrace event
→ terminal output
```

## EXACT WORDS

> “Cada retorno externo é normalizado em uma observação e pode gerar uma referência de evidência persistida. A timeline canônica mantém sequence, origem, tool, status, latência e evidence ID quando esses campos existem.”

> “Esse é também o limite da observabilidade: nós persistimos comportamento externo verificável — decisões, chamadas, resultados, políticas, falhas e terminais. Não expomos chain-of-thought privado. Assim, uma conclusão pode ser auditada até a chamada que produziu a evidência, sem depender de raciocínio interno não verificável.”

At **02:14**, click **01 Results**.

---

# 02:14–02:42 — Structured terminal policy

## EXACT SCREEN

**01 Results — Answer & next step**, with PRIMARY RUN still selected.

Show the completed outcome card:

- `WHAT YOU NEED TO KNOW`;
- actual heading, preferably `Conclusion ready`;
- persisted customer-safe message;
- `What to do next`;
- `SUPPORTING EVIDENCE`.

After ~15 seconds, switch to the prepared **SAFE-DEGRADATION RUN** using persisted history, then return to `Results` if the UI changes tab automatically.

Show its actual state, preferably:

- `Human review recommended`, or
- `Not enough evidence`, or
- `More context needed`.

## EXACT WORDS

> “O terminal também é estruturado. Uma conclusão normal é `ORIENT`, apresentada aqui como `Conclusion ready`. Mas o controller não é obrigado a produzir uma resposta final. Ele pode pedir contexto adicional, se abster ou escalar.”

> “Neste segundo run persistido, o comportamento seguro é diferente. Quando a evidência é insuficiente ou a incerteza não pode ser resolvida pelo runtime, a política terminal muda em vez de fabricar uma conclusão. Essa decisão também fica persistida e entra na avaliação.”

At **02:42**, reselect the **PRIMARY RUN**, then click **04 Engineering**.

---

# 02:42–03:34 — Post-runtime evaluator

## EXACT SCREEN

**04 Engineering — Architecture & evals**.

Keep the layer intro visible briefly:

- `ENGINEERING & EVALUATION`;
- `Open the full observability surface`;
- `POST-RUNTIME ONLY` if visible.

Then move to the evaluation panel for the PRIMARY RUN.

Show, if present:

- persisted evaluation score/check count;
- blocking checks / pass-fail status;
- expected-versus-observed or closest trajectory/evaluation surface;
- tool/function correctness;
- argument validity/correctness;
- trajectory/read coverage;
- evidence checks;
- terminal/decision checks;
- safety/failure checks.

Do not expose private expected answer text or evaluator-only gold.

Architecture inset:

```text
completed RunTrace
        ↓
ProductionEvaluator
        ↓
deterministic checks
        ↓
safe persisted projection

private reference ─X→ AgentController
```

## EXACT WORDS

> “A segunda metade do sistema é o evaluator. Ele é pós-runtime: primeiro a execução termina e produz um `RunTrace`; só depois o `ProductionEvaluator` recebe esse artefato. Qualquer referência privada usada para scoring fica fora do contexto do agente.”

> “A avaliação é decomposta por comportamento. Nós conseguimos inspecionar seleção de função, validade dos argumentos, trajetória, cobertura de evidência, decisão terminal, segurança e comportamento sob falha, dentro do que cada cenário consegue medir deterministicamente.”

> “Isso é mais útil do que avaliar apenas o texto final. Se uma mudança introduzir regressão, conseguimos distinguir se o problema começou na escolha da tool, nos argumentos, na evidência recuperada ou somente na decisão final.”

At **03:34**, click **03 Investigation** and scroll to `Action Control`.

---

# 03:34–04:04 — Consequential action safety boundary

## EXACT SCREEN

**03 Investigation — Runtime & operations**, `Action Control` visible.

Show the capability/proposal state. If no action proposal exists for the selected run, use the capability surface in Engineering, but do not fabricate one.

Overlay:

```text
model proposal
→ schema/policy validation
→ action proposal
→ confirmation architecture
→ authorization/custody/idempotency/lease
→ external execution
```

Put a prominent red/amber label over the final arrow:

```text
RELEASE 0
EXTERNAL CONSEQUENTIAL EXECUTION DISABLED
```

## EXACT WORDS

> “Reads e ações consequenciais têm authorities diferentes. A LLM pode propor uma action, mas proposal não é autorização. O código já separa validação, confirmação, custody, idempotência e lease de execução.”

> “A fronteira promovida hoje é deliberadamente mais restrita: as cinco actions existem no contrato, porém a Release 0 mantém execução consequencial externa desabilitada. Então o que está sendo mostrado aqui é a boundary real, sem transformar uma capacidade ainda bloqueada em claim de produção.”

At **04:04**, hard cut to deployment overlay.

---

# 04:04–04:37 — Deployment and realtime consistency

## EXACT SCREEN

Full-screen deployment overlay:

```text
Browser
  ↓ HTTPS
Railway production-web
  ↓ /api + SSE
Railway production-api
  ├→ Neon Auth
  ├→ Cloudflare Workers AI
  ├→ supplied TRACTIAN API
  └→ Neon PostgreSQL
```

After ~15 seconds morph/transition the lower half into:

```text
runtime transition
→ PostgreSQL event row
→ commit
→ LISTEN / NOTIFY wake-up
→ durable catch-up by cursor
→ authenticated SSE
→ React state
```

## EXACT WORDS

> “No deployment atual, frontend e backend estão hospedados no Railway. A API valida sessão com Neon Auth, chama o provider hospedado, acessa remotamente a API fornecida pela TRACTIAN para o projeto e persiste estado em Neon PostgreSQL.”

> “Para realtime, PostgreSQL continua sendo a fonte de verdade. `LISTEN/NOTIFY` é apenas um mecanismo de wake-up. O cliente recupera eventos persistidos por cursor e recebe atualização por SSE autenticado. Portanto, perder uma notification não significa perder o estado autoritativo da execução.”

At **04:37**, transition to the final numbered architecture.

---

# 04:37–05:00 — Final technical recap

## EXACT SCREEN

Full-screen architecture. Reveal one numbered label every ~2 seconds:

```text
1  Server-validated identity / tenant
2  Durable run ownership
3  AgentController + structured DecisionSource
4  ToolSpec deterministic validation
5  HarnessRunner + remote TRACTIAN I/O
6  Evidence + RunTrace
7  Explicit terminal policy
8  Post-runtime ProductionEvaluator
9  PostgreSQL + authenticated SSE
```

Do not show an outro/logo animation after the final sentence.

## EXACT WORDS

> “Então o sistema fecha um caminho agentic auditável de ponta a ponta: identidade e autoridade ficam fora do modelo; decisões são estruturadas; execução externa passa por uma boundary tipada; evidências e traces são persistidos; incerteza vira um estado terminal explícito; e a avaliação é independente do runtime.”

> “O resultado técnico é que não medimos apenas se o agente chegou a uma resposta. Conseguimos medir e inspecionar como ele chegou nela e localizar exatamente em qual boundary uma regressão foi introduzida.”

**STOP RECORDING immediately.**

---

# Exact click sequence

Use this as the operator cheat sheet during recording:

```text
00:00  architecture overlay
00:32  hosted product / Results
00:55  click 03 Investigation
        select PRIMARY RUN
        show metrics + Trace Graph + one tool call
01:38  click 02 Evidence
        show canonical event timeline + safe references
02:14  click 01 Results
        show PRIMARY terminal
        select SAFE-DEGRADATION RUN
        show its Results terminal
02:42  reselect PRIMARY RUN
        click 04 Engineering
        show evaluator
03:34  click 03 Investigation
        scroll Action Control
04:04  deployment overlay
04:37  final numbered architecture
05:00  stop
```

---

# Exact visual hierarchy

At any moment, only one concept should be visually dominant:

| Time | Dominant visual |
|---:|---|
| 00:00–00:32 | architecture boundaries |
| 00:32–00:55 | identity / tenant boundary |
| 00:55–01:38 | runtime + tool execution |
| 01:38–02:14 | evidence + trace lineage |
| 02:14–02:42 | terminal state semantics |
| 02:42–03:34 | evaluator isolation + metrics |
| 03:34–04:04 | action safety boundary |
| 04:04–04:37 | hosted deployment + realtime |
| 04:37–05:00 | end-to-end recap |

---

# Claims that must be spoken exactly or equivalently

Use:

- “API fornecida pela TRACTIAN para o projeto, hospedada remotamente.”
- “Cloudflare é o provider provisório da Release 0.”
- “13 reads live e 5 actions proposal-only.”
- “Execução consequencial externa está desabilitada na Release 0.”
- “O evaluator é pós-runtime.”
- “O browser não é autoridade de tenant ou permissions.”
- “O `HarnessRunner` é a boundary canônica de execução.”

Never say:

- “API de produção corporativa da TRACTIAN”;
- “todas as actions estão funcionando em produção”;
- “Cloudflare foi provado como o melhor modelo”;
- “vemos o raciocínio interno da LLM”;
- “LISTEN/NOTIFY é a fonte de verdade”;
- “um merge na main significa que todos os componentes foram redeployados.”
