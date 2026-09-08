# Exact 5-Minute Technical Recording Script

**Use this file literally while recording.**  
**Target:** 5:00  
**Language:** Portuguese  
**Provider claim checkpoint:** 2026-09-08 — Groq GPT-OSS-120B 85/85 = `NO_SELECTION`; production provider unchanged.

> Se algum valor visual ou hosted identity diferir, fale o valor real exibido e consulte `../ACTIVE-PROJECT-STATUS.md`. Não improvise uma claim.

## Antes de 00:00

Abra o produto hospedado e deixe a sessão autenticada. Prepare:

- PRIMARY: `run_97b91f6e0feb91184283`;
- DATA QUALITY opcional: `run_21813cb7b4ad9adbdc5e`;
- BOUNDED UNAVAILABLE: `run_547b2a62d84ef56a3d3d`.

Não exponha cookies, tokens, secrets, gold privado, `.env`, chain-of-thought ou localhost.

---

## 00:00–00:28 — Arquitetura

**Tela:** overlay completo.

```text
Browser / React
→ production-web / Railway
→ production-api / FastAPI
→ AuthenticatedRuntimeContext
→ V13 DecisionSource ↔ AgentController
→ HarnessRunner + ToolSpec
→ supplied TRACTIAN API
→ Evidence + RunTrace
→ ProductionEvaluator
→ Neon PostgreSQL
→ SSE / UI
```

**Fala:**

> “Vou começar pela arquitetura realmente promovida. Identidade e tenant ficam fora da LLM. O `AgentController` controla o loop, o `DecisionSource` só pode propor decisões estruturadas, toda execução externa passa pelo `HarnessRunner` e pelo contrato canônico de `ToolSpec`, e o evaluator roda depois do runtime. O modelo nunca recebe autoridade para escolher tenant, permissions ou fazer I/O de rede diretamente.”

---

## 00:28–00:55 — Home e sessão

**Tela:** produto hospedado, **Home**, usuário autenticado.

Overlay:

```text
managed session
→ server validation
→ AuthenticatedRuntimeContext
→ PostgreSQL tenant scope
→ RLS
```

**Fala:**

> “O fluxo começa em Home com uma pergunta normal sobre o equipamento. A sessão é validada no servidor e o backend deriva usuário, organização e permissões. Reads podem reutilizar brevemente um contexto já validado; criação de run continua exigindo validação fresca. Sessão inválida é 401 e indisponibilidade temporária de identidade é 503. Isso reduz fan-out sem criar stale auth.”

---

## 00:55–01:25 — Grounding de R310

**Tela:** selecione o PRIMARY em Analyses ou use Home para abrir a pergunta equivalente.

**Fala:**

> “O usuário pode falar em R310 sem conhecer IDs internos. O runtime começa pela identidade, extrai o company ID apenas de observação estruturada autorizada, lista a frota e só então resolve R310. Se o label não existir na frota autorizada, o agente não inventa outro tenant nem transfere para o usuário a obrigação de descobrir um asset ID interno.”

Overlay:

```text
R310
→ get_current_user
→ list_assets_by_company
→ asset_R310
→ evidence reads
```

---

## 01:25–02:05 — Technical / Current analysis

**Clique:** **Technical → Current analysis**.

Mostre a sequência do PRIMARY e uma chamada de spectrum.

**Fala:**

> “Aqui aparece a execução observável. A saída do provider não é código: é uma decisão tipada. Para uma tool call, nome e argumentos precisam resolver contra o registry, passar pela validação determinística e somente o `HarnessRunner` pode chamar o transporte TRACTIAN.”

> “Chamadas sucessivas de spectrum não são automaticamente loop: este run progride do ativo para um `point_id`. Redundância é avaliada por operação, argumentos, recurso e contribuição de evidência.”

---

## 02:05–02:40 — Resultado + response_mode

**Tela:** volte ao resultado do PRIMARY e mantenha a evidência contextual visível.

**Fala:**

> “O terminal e o `response_mode` são contratos diferentes. O terminal diz o que o controller faz; o `response_mode` diz quão completamente a evidência sustenta a mensagem. Aqui o modo é `partial`: existe evidência direcional compatível com mecanismo de rolamento, mas a causa raiz continua probabilística.”

> “Os modos são `complete`, `partial`, `inconclusive`, `conflict` e `unavailable`. A auditabilidade vem de calls, argumentos, status, evidence IDs e eventos persistidos — não de expor chain-of-thought.”

---

## 02:40–03:05 — Analyses / R420 ausente

**Clique:** **Analyses** → `run_547b2a62d84ef56a3d3d` → resultado.

**Fala:**

> “Este caso testa fail-closed. O pedido compara R310 e R420, mas R420 não apareceu na frota autorizada. O correto foi `unavailable`: não inventou o ativo, não mudou de tenant e não pediu um ID sem origem autorizada. Isso prova recurso ausente, não uma comparação bilateral real.”

---

## 03:05–03:42 — Technical / Quality

**Clique:** PRIMARY → **Technical → Quality**.

**Fala:**

> “Depois do runtime entra o `ProductionEvaluator`. Ele recebe o `RunTrace` concluído; referências privadas de avaliação não entram no contexto do agente. Os checks estruturais localizam regressões no processo, não só no texto final.”

> “Essa mesma disciplina rejeitou uma configuração de provider que parecia atraente: Groq com GPT-OSS-120B completou 85 de 85 casos, mas ficou em 81,18% de rubric pass, 82,35% de reliability e nove contract failures. O resultado oficial foi `NO_SELECTION`; então não promovemos o provider nem reduzimos a régua.”

Overlay:

```text
RunTrace complete
→ deterministic evaluation
→ hard gates
→ PASS | NO_SELECTION
```

---

## 03:42–04:08 — Technical / Actions

**Clique:** **Technical → Actions**.

**Fala:**

> “Reads e ações consequenciais não compartilham autoridade. A LLM pode propor uma action, mas proposal não é autorização. Existem boundaries para validação, confirmação, custody, idempotência e leases, porém a Release 0 mantém execução externa consequencial em deny-all.”

---

## 04:08–04:38 — Deployment e realtime

**Tela:** overlay de deployment.

```text
Browser
→ production-web / Railway
→ production-api / Railway
   ├→ Neon Auth
   ├→ provider provisório
   ├→ supplied TRACTIAN API
   └→ Neon PostgreSQL
```

**Fala:**

> “Frontend e backend estão no Railway, estado durável e RLS ficam no Neon, o provider de produção continua provisório e as reads usam remotamente a API fornecida da TRACTIAN. A pesquisa de provider roda separada: o `NO_SELECTION` do Groq não alterou production-api nem production-web.”

> “No realtime, a linha persistida no PostgreSQL é a verdade. `LISTEN/NOTIFY` só acorda o consumidor; catch-up por cursor e SSE autenticado recuperam o estado durável.”

---

## 04:38–05:00 — Recap

**Tela:** nove passos numerados.

**Fala:**

> “O sistema fecha um caminho auditável: identidade server-owned, ownership persistido, decisão groundeada, validação tipada, I/O apenas pelo `HarnessRunner`, evidência e `RunTrace`, terminal com semântica explícita, evaluator pós-runtime e projeção durável para a UI.”

> “Já provamos um produto read-only hospedado e um framework que inclusive rejeita candidatos que não passam os gates. Ainda não afirmamos provider final, actions consequenciais, SLO final ou calibração humana completa.”

**STOP.**

## Sequência exata de cliques

```text
00:00 architecture overlay
00:28 hosted product / Home
00:55 Analyses → PRIMARY
01:25 Technical → Current analysis
02:05 selected Result / evidence
02:40 Analyses → unavailable run
03:05 PRIMARY → Technical → Quality
03:42 Technical → Actions
04:08 deployment overlay
04:38 final recap
05:00 stop
```

## Claims proibidas

Nunca diga:

- “Cloudflare é o melhor/final provider”;
- “Groq venceu o provider tournament”;
- “o tournament Cloudflare-vs-Groq final foi concluído”;
- “strict structured output já está aprovado/promovido”;
- “todas as 18 operações executam em produção”;
- “actions externas estão habilitadas”;
- “R420 existe em outro tenant/planta” sem observação autorizada;
- “mesma tool duas vezes é necessariamente loop”;
- “o agente expõe raciocínio interno”;
- “já provamos SLO/segurança/capacidade final”.
