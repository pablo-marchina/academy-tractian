# Exact 5-Minute Technical Recording Script

**Use this file literally while recording.**  
**Target:** 5:00  
**Language:** Portuguese  
**Current backend source:** `3545d75c00ca30419e0f47e8b1950aa50cbbf462`  
**Hosted frontend:** `1bc124a8d4dbd029178ff8129b25452129445de7`

> Se algum valor visual/deployment diferir, fale o valor real exibido. Não improvise uma claim.

## Antes de 00:00

Abra o produto hospedado e deixe a sessão autenticada. Prepare:

- PRIMARY: `run_97b91f6e0feb91184283`;
- DATA QUALITY opcional: `run_21813cb7b4ad9adbdc5e`;
- BOUNDED UNAVAILABLE: `run_547b2a62d84ef56a3d3d`.

Não exponha cookies, tokens, secrets, grants, actor mappings, gold privado, `.env`, chain-of-thought ou localhost.

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

Actions:
proposal → custody → confirmation → grant/resource scope
→ idempotency + lease → server-owned vendor actor → one typed write
```

**Fala:**

> “Vou começar pela arquitetura realmente promovida. Identidade e tenant ficam fora da LLM. O `AgentController` controla o loop, a V13 só propõe decisões estruturadas, toda execução externa passa pelo `HarnessRunner` e pelo contrato canônico de `ToolSpec`, e o evaluator roda depois do runtime. Ações consequenciais têm um boundary separado de custody, confirmação, autorização server-owned, idempotência e lease. O modelo nunca recebe autoridade para escolher tenant, permissions, vendor actor ou fazer I/O de rede diretamente.”

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

> “Este é o produto hospedado atual. O fluxo começa em Home com uma pergunta normal sobre o equipamento. A sessão é validada no servidor e o backend deriva usuário, organização e permissões. Para bursts de leitura, o servidor pode reutilizar por no máximo dois segundos um contexto já validado; uma criação de run ou outra mutation continua exigindo validação fresca. Sessão inválida é 401 e indisponibilidade temporária do serviço de identidade é 503.”

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

**Fala:**

> “Aqui aparece a execução observável. A saída do provider não é código: é uma decisão tipada. Para uma tool call, nome e argumentos precisam resolver contra o registry, passar pela validação determinística e somente o `HarnessRunner` pode chamar o transporte TRACTIAN.”

> “Neste run existem chamadas sucessivas de spectrum, mas isso não é automaticamente um loop. O acesso progride do ativo para um `point_id` específico. A métrica de redundância compara tool, argumentos, recurso alvo e contribuição de evidência.”

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

> “Os modos são `complete`, `partial`, `inconclusive`, `conflict` e `unavailable`. A auditabilidade vem de calls, argumentos, status, evidence IDs e eventos persistidos — não de expor chain-of-thought.”

---

## 02:40–03:05 — Analyses / R420 ausente

**Clique:** **Analyses** → `run_547b2a62d84ef56a3d3d` → resultado.

**Fala:**

> “Este segundo caso testa fail-closed. O pedido compara R310 e R420, mas R420 não apareceu na frota autorizada. O resultado correto foi `unavailable`: ele não inventou o ativo, não mudou de tenant e não pediu um ID interno impossível de justificar. Isso prova recurso ausente seguro; não prova ainda uma comparação bilateral com dois ativos reais.”

---

## 03:05–03:38 — Technical / Quality

**Clique:** PRIMARY → **Technical → Quality**.

**Fala:**

> “Depois do runtime entra o `ProductionEvaluator`. Ele recebe o `RunTrace` concluído; referências privadas de avaliação não entram no contexto do agente.”

> “A matriz obrigatória mais recente também passou produção wheel/image, action lease e fencing, horizontal runtime, clean clone e Chromium. Isso prova o contrato de source e runtime testado, mas não substitui aceitação live do fornecedor.”

Overlay:

```text
RunTrace complete
→ ProductionEvaluator
→ deterministic checks
→ safe persisted projection
```

---

## 03:38–04:15 — Technical / Actions

**Clique:** **Technical → Actions**.

**Fala:**

> “Aqui está a mudança importante em relação ao Release 0 original: actions consequenciais não estão mais simplesmente em deny-all. O caminho governado foi promovido. A LLM pode propor, mas proposal não é execução. O backend faz custody do payload exato, exige confirmação explícita, resolve grant e resource scope server-side, adquire idempotência e lease e só então pode fazer uma tentativa remota.”

Overlay:

```text
proposal
→ private custody
→ exact confirmation
→ server-owned grant + resource scope
→ persistent idempotency
→ lease/fencing
→ server-owned vendor actor
→ one remote attempt
→ ACCEPTED | NOT_ACCEPTED | BLOCKED | UNCERTAIN
```

**Fala:**

> “Mas eu não vou dizer que as cinco actions já estão prontas. O smoke live de produção falhou corretamente em `update_asset_config` com HTTP 403 e `accepted=false`, abortando o deployment antes de substituir a versão saudável. Investigando a API fornecida, vimos que o mesmo company tem atores upstream diferentes para `action_low` e para `action_high` mais `escalate`. A correção é manter o usuário local como principal de autorização e auditoria e escolher o ator TRACTIAN server-side por company e permissão no último boundary. Essa correção ainda precisa ser mergeada e validada 5 de 5.”

---

## 04:15–04:40 — Deployment e realtime

**Tela:** overlay de deployment.

```text
Browser
→ production-web 1bc124a...
→ production-api source 3545d75...
   ├→ Neon Auth
   ├→ Cloudflare Workers AI
   ├→ supplied TRACTIAN API 47561c...
   └→ Neon PostgreSQL
```

**Fala:**

> “Frontend e backend estão no Railway, estado durável e RLS ficam no Neon, o provider provisório é Cloudflare e a integração TRACTIAN é remota. O required gate do source 3545d75 passou, mas usamos aceitação hospedada separada para claims externas.”

> “Também descobrimos uma nuance operacional: `redeploy` do Railway pode reutilizar um snapshot antigo. Para provar uma mudança de configuração ou pre-deploy, forçamos um snapshot novo. Foi esse snapshot que realmente executou o smoke de writes e revelou o 403.”

---

## 04:40–05:00 — Recap

**Tela:** recap.

**Fala:**

> “O sistema fecha um caminho auditável: identidade server-owned, ownership persistido, decisão V13 groundeada, validação tipada, I/O apenas pelo `HarnessRunner`, evidência e `RunTrace`, terminal com semântica explícita, evaluator pós-runtime e ações com custody, confirmação, idempotência e lease.”

> “O que nós já provamos é o produto hospedado e a arquitetura governada local. Ainda não afirmamos provider final, cobertura live de todas as reads, aceitação 5 de 5 das actions, SLO final, segurança completa, usabilidade humana ou calibração humana final.”

**STOP.**

## Sequência exata de cliques

```text
00:00 architecture overlay
00:28 hosted product / Home
00:55 Analyses → PRIMARY
01:25 Technical → Current analysis
02:05 selected Result / evidence detail
02:40 Analyses → run_547b2...
03:05 PRIMARY → Technical → Quality
03:38 Technical → Actions
04:15 deployment overlay
04:40 final recap
05:00 stop
```

## Claims proibidas

Nunca diga:

- “Cloudflare é o melhor/final provider”;
- “todas as 18 operações já foram exercitadas live”;
- “as cinco actions já funcionam 100%”;
- “actions continuam desabilitadas/deny-all” como descrição do estado atual;
- “a correção de vendor actor já está em produção” antes de merge/deploy/5-of-5;
- “R420 existe em outro tenant/planta” sem observação autorizada;
- “mesma tool duas vezes é necessariamente loop”;
- “API corporativa de produção da TRACTIAN”;
- “o agente expõe seu raciocínio interno”;
- “já provamos SLO/segurança/capacidade/usabilidade humana final”.