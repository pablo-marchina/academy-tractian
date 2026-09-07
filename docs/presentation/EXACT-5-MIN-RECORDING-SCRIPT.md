# Exact 5-Minute Technical Recording Script

**Use this file literally while recording.**  
**Target:** 5:00  
**Language:** Portuguese  
**Hosted backend:** `08866da60245f58f217981b7ae668b10be45cc67`  
**Hosted frontend:** `1bc124a8d4dbd029178ff8129b25452129445de7`

> Se algum valor visual diferir, fale o valor real exibido. Não improvise uma claim.

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

> “Vou começar pela arquitetura realmente promovida. Identidade e tenant ficam fora da LLM. O `AgentController` controla o loop, a V13 do `DecisionSource` só pode propor decisões estruturadas, toda execução externa passa pelo `HarnessRunner` e pelo contrato canônico de `ToolSpec`, e o evaluator roda apenas depois do runtime. O modelo nunca recebe autoridade para escolher tenant, permissions ou fazer I/O de rede diretamente.”

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

> “Este é o produto hospedado atual. O fluxo começa em Home com uma pergunta normal sobre o equipamento. A sessão é validada no servidor e o backend deriva usuário, organização e permissões. Para bursts de leitura, o servidor pode reutilizar por no máximo dois segundos um contexto já validado; uma criação de run continua exigindo validação fresca. Sessão inválida é 401 e indisponibilidade temporária do serviço de identidade é 503. Isso reduz fan-out sem criar stale auth.”

---

## 00:55–01:25 — Grounding de R310

**Tela:** selecione o PRIMARY em Analyses ou use Home para abrir a pergunta equivalente.

**Fala:**

> “O usuário pode falar em R310 sem conhecer IDs internos. A V13 força primeiro `get_current_user`, extrai o company ID apenas de uma observação estruturada autorizada, lista a frota da empresa e só então resolve R310 para o recurso interno. Se o label não existir na frota autorizada, o agente não pode inventar outro tenant nem pedir que o usuário descubra o asset ID por fora.”

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

> “Aqui aparece a execução observável. A saída do provider não é código: é uma decisão tipada. Para uma tool call, o nome e os argumentos precisam resolver contra o registry, passar pela validação determinística e somente o `HarnessRunner` pode chamar o transporte TRACTIAN.”

> “Neste run existem chamadas sucessivas de spectrum, mas isso não é automaticamente um loop. O acesso progride do ativo para um `point_id` específico. Então nossa métrica de redundância compara tool, argumentos e recurso alvo; não apenas o nome da tool.”

Overlay:

```text
DecisionSource
→ ToolSpec
→ validation
→ HarnessRunner
→ typed HTTPS
→ TRACTIAN
→ observation/evidence
```

---

## 02:05–02:40 — Resultado + response_mode

**Tela:** volte ao resultado do PRIMARY e mantenha a evidência contextual visível.

**Fala:**

> “O terminal e o `response_mode` são contratos diferentes. O terminal diz o que o controller faz; o `response_mode` diz quão completamente a evidência sustenta a mensagem. Aqui o modo é `partial`: existe evidência direcional compatível com mecanismo de rolamento, mas a causa raiz continua probabilística.”

> “Os modos são `complete`, `partial`, `inconclusive`, `conflict` e `unavailable`. A regra importante é não chamar uma resposta útil de inconclusiva só porque a explicação causal ainda tem incerteza.”

Aponte uma evidence reference. Diga:

> “A auditabilidade vem de calls, args, status, evidence IDs e eventos persistidos — não de expor chain-of-thought.”

---

## 02:40–03:05 — Analyses / R420 ausente

**Clique:** **Analyses** → `run_547b2a62d84ef56a3d3d` → resultado.

**Fala:**

> “Este segundo caso testa fail-closed. O pedido compara R310 e R420, mas R420 não apareceu na frota autorizada da empresa. O resultado correto foi `unavailable`: ele não inventou o ativo, não mudou de tenant e não pediu um ID interno impossível de justificar. Isso prova o comportamento de recurso ausente; não é uma claim de que já validamos uma comparação bilateral com dois ativos reais.”

---

## 03:05–03:42 — Technical / Quality

**Clique:** PRIMARY → **Technical → Quality**.

**Fala:**

> “Depois do runtime entra o `ProductionEvaluator`. Ele recebe o `RunTrace` concluído; referências privadas de avaliação não entram no contexto do agente.”

> “Nos runs V13 finais, os checks blocking persistidos passaram, incluindo integridade da cadeia de execução, proveniência das chamadas do modelo, identidade do trace de produção, validade das propostas, segurança read-only e consistência terminal. Isso permite localizar regressões no processo, não só no texto final.”

Overlay:

```text
RunTrace complete
→ ProductionEvaluator
→ deterministic checks
→ safe persisted projection
```

---

## 03:42–04:08 — Technical / Actions

**Clique:** **Technical → Actions**.

**Fala:**

> “Reads e ações consequenciais não compartilham autoridade. A LLM pode propor uma action, mas proposal não é autorização. O código contém boundaries para validação, confirmação, custody, idempotência e leases, porém a Release 0 mantém execução externa consequencial em deny-all. Portanto, nenhum teste desta apresentação deve executar uma mudança real.”

Overlay com último passo marcado `DISABLED`.

---

## 04:08–04:38 — Deployment e realtime

**Tela:** overlay de deployment.

```text
Browser
→ production-web 1bc124a...
→ production-api 08866da...
   ├→ Neon Auth
   ├→ Cloudflare Workers AI
   ├→ supplied TRACTIAN API 47561c...
   └→ Neon PostgreSQL
```

**Fala:**

> “Frontend e backend estão no Railway, estado durável e RLS ficam no Neon, o provider provisório é Cloudflare e as reads usam remotamente a API fornecida pela TRACTIAN para o projeto. Os três componentes têm identidades de deployment separadas.”

> “No realtime, a linha persistida no PostgreSQL é a verdade. `LISTEN/NOTIFY` só acorda o consumidor; o catch-up por cursor e o SSE autenticado recuperam o estado durável.”

---

## 04:38–05:00 — Recap

**Tela:** nove passos numerados.

**Fala:**

> “O sistema fecha um caminho auditável: identidade server-owned, ownership persistido, decisão V13 groundeada, validação tipada, I/O apenas pelo `HarnessRunner`, evidência e `RunTrace`, terminal com semântica explícita de evidência, evaluator pós-runtime e projeção durável para a UI.”

> “O que nós já provamos é um produto read-only hospedado e progressivamente hardenado. Ainda não afirmamos provider final, cobertura live de todas as reads, actions consequenciais, SLO final ou calibração humana completa.”

**STOP.**

## Sequência exata de cliques

```text
00:00 architecture overlay
00:28 hosted product / Home
00:55 Analyses → PRIMARY (ou Home → pergunta)
01:25 Technical → Current analysis
02:05 selected Result / evidence detail
02:40 Analyses → run_547b2...
03:05 PRIMARY → Technical → Quality
03:42 Technical → Actions
04:08 deployment overlay
04:38 final recap
05:00 stop
```

## Claims proibidas

Nunca diga:

- “Cloudflare é o melhor/final provider”;
- “todas as 18 operações executam em produção”;
- “actions externas estão habilitadas”;
- “R420 existe em outro tenant/planta” sem observação autorizada;
- “mesma tool duas vezes é necessariamente loop”;
- “API corporativa de produção da TRACTIAN”;
- “o agente expõe seu raciocínio interno”;
- “V13 já provou SLO/segurança/capacidade final”.