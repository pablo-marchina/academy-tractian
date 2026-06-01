# Plano de Implementação — Inteli AI Hub

> Projeto unificado que integra o melhor de 10 projetos do PS n8n Academy
> em uma única solução full-stack de curadoria de notícias de IA.

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Anatomia dos Projetos Originais](#2-anatomia-dos-projetos-originais)
3. [Arquitetura do Projeto Unificado](#3-arquitetura-do-projeto-unificado)
4. [Estrutura de Diretórios](#4-estrutura-de-diretórios)
5. [Os 5 Workflows n8n](#5-os-5-workflows-n8n)
6. [Backend FastAPI](#6-backend-fastapi)
7. [Frontend React](#7-frontend-react)
8. [Infraestrutura Docker](#8-infraestrutura-docker)
9. [Fluxo de Dados](#9-fluxo-de-dados)
10. [Cronograma de Implementação](#10-cronograma-de-implementação)
11. [Comparativo: Projetos Originais vs Unificado](#11-comparativo)

---

## 1. Visão Geral

### O Problema

Existem 10 projetos independentes no workspace `ps-n8n-academy`, cada um resolvendo o mesmo problema central — curadoria automatizada de notícias de IA — mas com abordagens, tecnologias e canais de entrega diferentes. Nenhum deles é completo isoladamente:

- Alguns têm frontend mas não têm chat IA
- Outros têm multi-agente mas não têm gamificação
- Alguns integram 5 APIs mas não têm fallback de LLM
- Nenhum combina todos os canais de entrega (Email + Slack + Telegram + LinkedIn + Web)

### A Solução

Criar um **projeto unificado do zero** que extrai e integra o melhor de cada projeto:

| Projeto | Melhor Feature para Aproveitar |
|---------|-------------------------------|
| **Case_Inteli_Academy** | Dashboard web com autenticação + favoritos |
| **InteliAcedemy** | Arquitetura multi-agente (4 papéis de IA especializados) |
| **inteliIA / AI Pulse** | Gamificação (ranking/leaderboard) + 9 fontes RSS + deduplicação |
| **Mymir** | Full-stack React+FastAPI+Redis+PostgreSQL + chat IA + caching |
| **Newsletter_n8n_IA** | Fontes diversas (arXiv, Dev.to, NewsAPI) + Telegram |
| **Newsletter-IA-n8n** | Resiliência multi-LLM com fallback Groq → Gemini |
| **newsletterSemanalIA** | LinkedIn automático + imagens Pollinations + GitHub trending |
| **PS-Inteli-Academy** | Integração Airtable para dashboard visual |
| **psIa** | Frontend mobile Ionic/Angular + gestão de assinantes |
| **repositorio_inteli_academy** | 4 workflows interligados, chatbot Slack, RSS dinâmicos, previsões, error handler |

---

## 2. Anatomia dos Projetos Originais

### 2.1 Case_Inteli_Academy

| Item | Detalhe |
|------|---------|
| **Autor** | Julia Khristina |
| **Workflows n8n** | 1 workflow (`IA_Noticias.json`) — 12 nós |
| **LLM** | Google Gemini |
| **Infra** | Supabase (banco + auth), GitHub Pages (frontend) |
| **Frontend** | HTML/CSS/JS puro — dashboard, login, notícias, favoritos |
| **Trigger** | Semanal (segundas 8h) |
| **Diferencial** | Dashboard web funcional com autenticação de usuários |
| **O que copiar** | `src/app.js` (integração Supabase), `index.html` (layout dashboard), sistema de favoritos |

**Arquivos de origem:** `Case_Inteli_Academy/IA_Noticias.json`, `Case_Inteli_Academy/index.html`, `Case_Inteli_Academy/src/app.js`

### 2.2 InteliAcedemy

| Item | Detalhe |
|------|---------|
| **Autor** | Arthur Loyola |
| **Workflows n8n** | 1 workflow (`CaseIaAcademySemAPISminhas.json`) — 17 nós |
| **LLM** | Groq Llama 3.3 70B (4 chamadas) |
| **Canais** | Discord (primário), Gmail (desabilitado) |
| **Trigger** | Semanal (segundas 7h) |
| **Diferencial** | **4 agentes especializados**: Triagem → Tendências → Oportunidades → Redator-Chefe |
| **O que copiar** | Prompts dos 4 agentes (system prompt de cada), lógica de merge dos 3 outputs, formatação Markdown para relatório |

**Arquivos de origem:** `InteliAcedemy/CaseIaAcademySemAPISminhas.json`, `InteliAcedemy/relatorio_semanal.md`

### 2.3 inteliIA / AI Pulse

| Item | Detalhe |
|------|---------|
| **Autor** | Bruno Araujo |
| **Workflows n8n** | 4 workflows — principal (16 nós) + newsletter + ranking POST + ranking GET |
| **LLM** | Google Gemini (via AI Agent LangChain) |
| **Fontes** | **9 RSS feeds** em paralelo: Google News, TechCrunch, VentureBeat, MIT Tech Review, OpenAI Blog, Google AI Blog, Anthropic, Hugging Face, arXiv |
| **Frontend** | HTML/CSS/JS puro com gamificação |
| **Trigger** | Webhook (GET) — chamado pelo frontend |
| **Diferencial** | Gamificação (pontos + níveis + ranking global via static data n8n), deduplicação inteligente, controle de tokens |
| **O que copiar** | Arquitetura de merge tree para 9 RSS, `Code - Remove Duplicados` (dedup por URL + título normalizado), `Code - AI Token Control`, sistema de gamificação (localStorage + ranking n8n), design system do frontend (dark mode, glassmorphism) |

**Arquivos de origem:** `inteliIA/AI Pulse.json`, `inteliIA/AI Pulse Letter.json`, `inteliIA/AI Pulse Ranking Post.json`, `inteliIA/AI Pulse Ranking Get (2).json`, `inteliIA/index.html`

### 2.4 Mymir

| Item | Detalhe |
|------|---------|
| **Autor** | Leunam Sousa |
| **Workflows n8n** | 1 arquivo com 2 sub-workflows — **48 nós** |
| **LLM** | Groq (Llama 3.3 70B + Llama 4 Scout 17B) |
| **Infra** | **Full-stack**: React + Vite + TypeScript + Tailwind (frontend) + FastAPI + PostgreSQL + Redis (backend) + Docker Compose |
| **APIs** | Tavily, MediaStack, GNews, Resend, Supabase |
| **Diferencial** | Chat IA conversacional, caching Redis, PDF export, follow-up context, dual-agent, animações Framer Motion |
| **O que copiar** | `docker-compose.yml` inteiro, `backend/` inteiro (estrutura FastAPI), `frontend/` inteiro (estrutura React), sistema de chat com Redis, caching, export PDF |

**Arquivos de origem:** `Mymir/docker-compose.yml`, `Mymir/backend/` (todos), `Mymir/frontend/` (todos), `Mymir/assets/mymir.json`

### 2.5 Newsletter_n8n_IA

| Item | Detalhe |
|------|---------|
| **Autor** | Eduardo Totti |
| **Workflows n8n** | 1 workflow (`AI Newsletter - Inteli Academy.json`) — 19 nós |
| **LLM** | Google Gemini 2.5 Flash |
| **Fontes** | **5 fontes**: NewsAPI (PT-BR + EN), Dev.to, arXiv, Tavily |
| **Canal** | Telegram |
| **Trigger** | Semanal (segundas 6h) + manual |
| **Diferencial** | Pipeline 5 fontes paralelas + merge 5 entradas + parsing XML arXiv + Tavily |
| **O que copiar** | Nós de fonte arXiv (com parsing XML), Dev.to (com aggregate), `Code - Formatar todas notícias` (formatação de "dossiê" para LLM), template de prompt do Gemini para newsletter |

**Arquivos de origem:** `Newsletter_n8n_IA/AI Newsletter - Inteli Academy.json`

### 2.6 Newsletter-IA-n8n

| Item | Detalhe |
|------|---------|
| **Autor** | Vinicius Bonani |
| **Workflows n8n** | 1 workflow (`newsletter-ia.json`) — 24 nós |
| **LLM** | **Multi-LLM fallback**: Groq Llama 3.1 8B (primário) → Google Gemini 2.5 Flash-Lite (fallback) |
| **Fontes** | 3 RSS (TechCrunch, VentureBeat, MIT Tech Review) |
| **Canal** | Gmail |
| **Trigger** | Semanal (segundas 6h) + manual |
| **Diferencial** | Fallback automático entre LLMs, batch processing com throttling, classificação `STATUS\|CATEGORIA`, 9 categorias |
| **O que copiar** | Configuração de fallback multi-LLM no AI Agent node, SplitInBatches + Wait 15s, prompt de classificação estrita `STATUS\|CATEGORIA`, `Code in JavaScript` com `.trim()` sanitization |

**Arquivos de origem:** `Newsletter-IA-n8n/newsletter-ia.json`

### 2.7 newsletterSemanalIA

| Item | Detalhe |
|------|---------|
| **Autor** | Lucas Andrade |
| **Workflows n8n** | 1 workflow (`Newsletter IA.json`) — 24 nós |
| **LLM** | Groq (Llama 3.3 70B + GPT OSS 120B) |
| **Fontes** | TechCrunch + The Verge + GitHub Trending + Pollinations.ai |
| **Canais** | Gmail + LinkedIn (com human-in-the-loop) |
| **Trigger** | Segunda e quinta 8h |
| **Diferencial** | LinkedIn com aprovação humana, Pollinations.ai para imagens, "Hypes do Momento", dicionário visual de logos |
| **O que copiar** | Nó `Wait` com webhook para aprovação LinkedIn, `Formatar Post LinkedIn` (payload da API v2/ugcPosts), integração Pollinations.ai, `Gerar HTML da Newsletter` (template HTML beige/terracotta), lógica de "Hypes do Momento" |

**Arquivos de origem:** `newsletterSemanalIA/workflow/Newsletter IA.json`

### 2.8 PS-Inteli-Academy

| Item | Detalhe |
|------|---------|
| **Autor** | Raphaela Luvizotto |
| **Workflows n8n** | 1 workflow (`Noticias AI.json`) — 11 nós |
| **LLM** | OpenAI GPT (gpt-oss-20b) |
| **Fontes** | 2 RSS (TechCrunch, MIT) |
| **Destino** | Airtable (dashboard visual) |
| **Trigger** | Semanal (segundas 8h) + webhook |
| **Diferencial** | Integração Airtable, campo "insight" para estudantes, 5 categorias |
| **O que copiar** | Nó `Salva no Airtable`, lógica de categorias focadas em estudantes, campo `insight`, prompt com saída JSON estrita |

**Arquivos de origem:** `PS-Inteli-Academy/Noticias AI.json`

### 2.9 psIa

| Item | Detalhe |
|------|---------|
| **Autor** | Arthur DSR |
| **Workflows n8n** | 1 workflow (`Fluxo para sistema de Newsletter sobre IA.json`) — 20 nós |
| **LLM** | OpenAI GPT-4.1-mini |
| **Fontes** | 3 RSS (Google News, TechCrunch, MIT) |
| **Frontend** | Ionic 7 + Angular (PWA mobile-first) |
| **Assinantes** | Google Sheets (leitura/escrita) |
| **Canal** | Gmail |
| **Trigger** | Semanal (segunda) + webhook (dual-purpose) |
| **Diferencial** | App mobile Ionic/Angular, subscription management, structured output parser (JSON schema), dados mock, testes Karma/Jasmine |
| **O que copiar** | Nó `Verificar Se Email Existe` + `Salvar Email na Planilha` (subscription dedup), structured output parser (schema com enum de categorias), `AiNewsService` (normalização multi-formato), `ai-news-data.json` (dados mock) |

**Arquivos de origem:** `psIa/Fluxo para sistema de Newsletter sobre IA.json`, `psIa/src/` (todos)

### 2.10 repositorio_inteli_academy

| Item | Detalhe |
|------|---------|
| **Autor** | Pablo Marchina |
| **Workflows n8n** | **4 workflows interligados**: Coletor Diário (17 nós) + Sintetizador Semanal (14 nós) + Chatbot Slack (11 nós) + Error Handler (2 nós) = **44 nós** |
| **LLM** | Groq Llama 3.3 70B |
| **Fontes** | **RSS dinâmicos** (allainews_sources — centenas de fontes) |
| **Infra** | Google Sheets (ponte entre workflows), ngrok (Slack) |
| **Canais** | Slack + Gmail + arquivo local + Google Sheets |
| **Diferencial** | Arquitetura de 4 workflows interligados, RSS dinâmicos, dedup por similaridade, pré-pontuação local, análise de startup, previsões preditivas, chatbot RAG, error handler dedicado |
| **O que copiar** | **ESTE É O PROJETO MAIS COMPLETO** — 4 workflows inteiros (especialmente W1 Coletor, W2 Sintetizador, W3 Chatbot, Workflow de Erro), lógica de RSS dinâmicos, pré-pontuação local (keywords), prompt de previsões preditivas, `Alinhamento da saida` (5 caminhos de parsing de resposta LLM), workflow de erro com alertas Slack |

**Arquivos de origem:** `repositorio_inteli_academy/Workflow 1 Coletor Diario.json`, `repositorio_inteli_academy/Workflow 2 Sintetizador Semanal.json`, `repositorio_inteli_academy/Workflow 3 Chatbot Slack.json`, `repositorio_inteli_academy/Worflow de Erro.json`

---

## 3. Arquitetura do Projeto Unificado

### Diagrama de Alto Nível

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DOCKER COMPOSE                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐  │
│  │   n8n       │  │   Redis     │  │ PostgreSQL  │  │ FastAPI Backend   │  │
│  │  (5678)     │  │   (6379)    │  │   (5432)    │  │    (8000)         │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────────┬──────────┘  │
│         │                │                │                  │              │
└─────────┼────────────────┼────────────────┼──────────────────┼──────────────┘
          │                │                │                  │
          ▼                ▼                ▼                  ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                   Frontend React + Vite + Tailwind               │
    │      Dashboard │ Chat IA │ Ranking │ Trends │ Perfil            │
    └──────────────────────────────────────────────────────────────────┘
          │
          ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                      Canais de Entrega                           │
    │  ┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
    │  │  Email │ │ Slack  │ │ Telegram │ │ LinkedIn │ │   Web    │  │
    │  └────────┘ └────────┘ └──────────┘ └──────────┘ └──────────┘  │
    └──────────────────────────────────────────────────────────────────┘
```

### Tecnologias por Camada

| Camada | Tecnologia | Versão | Projeto de Origem |
|--------|-----------|--------|-------------------|
| **Orquestração** | n8n (Docker) | latest | Todos |
| **Cache/Memória** | Redis | 7-alpine | Mymir |
| **Banco de Dados** | PostgreSQL | 16-alpine | Mymir |
| **Backend** | FastAPI | Python 3.11+ | Mymir |
| **Frontend** | React + Vite + TypeScript + Tailwind | React 19 | Mymir |
| **LLM Primário** | Groq (Llama 3.3 70B) | API | InteliAcedemy |
| **LLM Fallback** | Google Gemini 2.5 Flash | API | Newsletter-IA-n8n |
| **Autenticação** | JWT (python-jose + bcrypt) | — | Mymir |
| **State Management** | Zustand | 5.x | Mymir |
| **Estilo** | Tailwind CSS 4 + Framer Motion | — | Mymir |
| **Dados Mock** | JSON estático | — | inteliIA, psIa |
| **Testes** | Vitest + Playwright | — | psIa (adaptado) |

### Portas do Ecossistema

| Serviço | Porta | Acesso |
|---------|-------|--------|
| n8n | 5678 | localhost:5678 |
| Redis | 6379 | interno (backend + n8n) |
| PostgreSQL | 5432 | interno (backend) |
| FastAPI Backend | 8000 | localhost:8000 |
| React Frontend | 5173 | localhost:5173 |

---

## 4. Estrutura de Diretórios

```
C:\Users\Inteli\Documents\Projetos\ps-n8n-academy\inteli-ai-hub\
│
├── docker-compose.yml                          ← Mymir (adaptado)
├── .env.example
├── .gitignore
├── README.md
│
├── n8n/
│   ├── workflows/
│   │   ├── 01-coletor-diario.json              ← NOVO ~25 nós
│   │   ├── 02-sintetizador-semanal.json        ← NOVO ~20 nós
│   │   ├── 03-distribuidor.json                ← NOVO ~20 nós
│   │   ├── 04-chatbot.json                     ← NOVO ~15 nós
│   │   └── 05-monitoramento.json              ← NOVO ~3 nós
│   └── README.md
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                             ← Mymir (adaptado)
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                       ← Mymir
│   │   │   ├── database.py                     ← Mymir
│   │   │   └── redis.py                        ← Mymir
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py                         ← Mymir + Case_Inteli_Academy
│   │   │   ├── article.py                      ← Mymir + Case_Inteli_Academy
│   │   │   ├── favorite.py                     ← Case_Inteli_Academy
│   │   │   ├── chat_session.py                 ← Mymir
│   │   │   ├── ranking.py                      ← inteliIA
│   │   │   └── subscriber.py                   ← psIa
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                         ← Mymir
│   │   │   ├── chat.py                         ← Mymir
│   │   │   ├── news.py                         ← Mymir + Case_Inteli_Academy
│   │   │   └── ranking.py                      ← inteliIA
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                         ← Mymir
│   │   │   ├── chat.py                         ← Mymir
│   │   │   ├── news.py                         ← Case_Inteli_Academy + Mymir webhook
│   │   │   ├── ranking.py                      ← inteliIA
│   │   │   └── subscription.py                 ← psIa
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── n8n.py                          ← Mymir (HTTP client para webhooks)
│   │   └── middleware/
│   │       ├── __init__.py
│   │       └── auth.py                         ← Mymir (JWT)
│   ├── requirements.txt                        ← Mymir (adaptado)
│   ├── Dockerfile                              ← Mymir
│   └── alembic/
│       ├── env.py
│       └── versions/
│
├── frontend/
│   ├── public/
│   │   ├── favicon.svg                         ← Mymir
│   │   └── icons.svg                           ← Mymir
│   ├── src/
│   │   ├── main.tsx                            ← Mymir
│   │   ├── App.tsx                             ← Mymir + rotas
│   │   ├── App.css                             ← Mymir
│   │   ├── index.css                           ← Mymir (Tailwind + estilos)
│   │   ├── types/
│   │   │   └── index.ts                        ← Mymir + inteliIA
│   │   ├── services/
│   │   │   ├── api.ts                          ← Mymir (axios + interceptor JWT)
│   │   │   ├── ranking.ts                      ← inteliIA
│   │   │   └── subscription.ts                 ← psIa
│   │   ├── store/
│   │   │   ├── auth.store.ts                   ← Mymir (Zustand)
│   │   │   ├── news.store.ts                   ← Case_Inteli_Academy
│   │   │   ├── chat.store.ts                   ← Mymir
│   │   │   └── ranking.store.ts                ← inteliIA
│   │   ├── hooks/
│   │   │   ├── useChat.ts                      ← Mymir
│   │   │   └── useGamification.ts              ← inteliIA
│   │   ├── pages/
│   │   │   ├── Login.tsx                       ← Mymir
│   │   │   ├── Signup.tsx                      ← Mymir
│   │   │   ├── Dashboard.tsx                   ← Case_Inteli_Academy (feed) + inteliIA (gamificaçao)
│   │   │   ├── Chat.tsx                        ← Mymir
│   │   │   ├── Ranking.tsx                     ← inteliIA
│   │   │   ├── Trends.tsx                      ← InteliAcedemy + repositorio_inteli_academy
│   │   │   ├── Profile.tsx                     ← Mymir + psIa
│   │   │   └── WeeklyReport.tsx                ← newsletterSemanalIA
│   │   └── components/
│   │       ├── common/
│   │       │   ├── Logo.tsx                    ← Mymir (órbita animada)
│   │       │   └── LoadingSpinner.tsx
│   │       ├── layout/
│   │       │   ├── DashboardLayout.tsx          ← Mymir
│   │       │   └── Sidebar.tsx                  ← Mymir
│   │       ├── news/
│   │       │   ├── NewsCard.tsx                ← Case_Inteli_Academy + inteliIA
│   │       │   ├── NewsFilters.tsx             ← inteliIA
│   │       │   ├── FavoritesButton.tsx         ← Case_Inteli_Academy
│   │       │   └── TrendingRepos.tsx           ← newsletterSemanalIA
│   │       ├── chat/
│   │       │   ├── ChatInput.tsx               ← Mymir
│   │       │   ├── MessageBubble.tsx           ← Mymir + PDF export
│   │       │   ├── PathSelector.tsx            ← Mymir
│   │       │   └── TypingIndicator.tsx         ← Mymir
│   │       ├── gamification/
│   │       │   ├── PointsBadge.tsx             ← inteliIA
│   │       │   └── Leaderboard.tsx             ← inteliIA
│   │       └── trends/
│   │           ├── TrendCard.tsx               ← InteliAcedemy
│   │           ├── WeeklySummary.tsx           ← Mymir
│   │           └── Predictions.tsx             ← repositorio_inteli_academy
│   ├── index.html                              ← Mymir
│   ├── package.json                            ← Mymir (adaptado)
│   ├── vite.config.ts                          ← Mymir
│   ├── tailwind.config.js                      ← Mymir
│   ├── tsconfig.json                           ← Mymir
│   └── tsconfig.app.json                       ← Mymir
│
├── shared/
│   ├── prompts/
│   │   ├── agente-01-triagem.md                ← InteliAcedemy
│   │   ├── agente-02-tendencias.md             ← InteliAcedemy
│   │   ├── agente-03-oportunidades.md          ← InteliAcedemy
│   │   ├── agente-04-redator-chefe.md          ← InteliAcedemy
│   │   ├── classificador-artigo.md             ← Newsletter-IA-n8n
│   │   └── newsletter-email.md                 ← Mymir
│   └── rss-sources.json                        ← inteliIA + repositorio_inteli_academy
│
└── scripts/
    ├── setup.ps1                                ← Script de inicialização Windows
    └── start-dev.ps1                            ← Script para dev environment
```

---

## 5. Os 5 Workflows n8n

### Workflow 1 — Coletor Diário

**Trigger:** Schedule diário às 08:00
**Status:** Ativo
**Workflow de erro vinculado:** Workflow 5

**Pipeline:**

```
Schedule Trigger (08:00)
  │
  ├──► Coleta RSS dinâmicos (allainews_sources do GitHub)     ← repositorio_inteli_academy
  │
  ├──► 9 RSS fixos em paralelo:                               ← inteliIA
  │     Google News AI | TechCrunch | VentureBeat |
  │     MIT Tech Review | OpenAI Blog | Google AI Blog |
  │     Anthropic | Hugging Face | arXiv
  │
  ├──► 3 APIs em paralelo:                                     ← Newsletter_n8n_IA + Mymir
  │     Tavily Search | NewsAPI (EN + PT-BR) | Dev.to
  │
  ├──► Merge consolidado (árvore de merges)                   ← inteliIA
  │
  ├──► Deduplicação (URL exata + similaridade título >75%)    ← inteliIA + repositorio_inteli_academy
  │
  ├──► Pré-pontuação local (keywords)                         ← repositorio_inteli_academy
  │     Alta: gpt, llm, openai, neural, deep learning
  │     Baixa: deal, promo, sale
  │     Bonus: arxiv (+4), github (+2)
  │
  ├──► Seleciona Top 15 mais bem pontuados
  │
  ├──► LLM classificação (AI Agent com fallback):             ← Newsletter-IA-n8n + InteliAcedemy
  │     Primário: Groq Llama 3.3 70B
  │     Fallback: Google Gemini 2.5 Flash
  │     Saída: título, resumo, categoria, relevância (1-10),
  │            sentimento, oportunidade_startup, tags
  │
  ├──► Parseia resposta LLM (5 caminhos de fallback)          ← repositorio_inteli_academy
  │
  ├──► Salva no Google Sheets (aba "Artigos")                 ← repositorio_inteli_academy
  │
  ├──► Salva no PostgreSQL (via webhook backend)              ← Mymir
  │
  └──► Envia resumo diário no Slack                           ← repositorio_inteli_academy
        Top 5 | Distribuição categorias | Oportunidades
```

**Nós estimados:** ~25
**Chamadas LLM:** 15 (1 por artigo, em lote)
**Integrações:** GitHub, RSS (9+), Tavily, NewsAPI, Dev.to, Groq, Gemini, Google Sheets, Slack, PostgreSQL

**Códigos/componentes para copiar:**
- `repositorio_inteli_academy`: Schedule trigger, RSS dinâmicos, normalização, pré-pontuação, parsing LLM, Slack
- `inteliIA`: Merge tree, deduplicação, 9 RSS
- `Newsletter_n8n_IA`: Tavily, Dev.to, NewsAPI
- `Newsletter-IA-n8n`: SplitInBatches + Wait 15s + fallback LLM

---

### Workflow 2 — Sintetizador Semanal

**Trigger:** Schedule domingo às 09:00
**Status:** Ativo
**Workflow de erro vinculado:** Workflow 5

**Pipeline:**

```
Schedule Trigger (domingo 09:00)
  │
  ├──► Lê artigos da semana (Google Sheets + PostgreSQL)
  │
  ├──► Filtra últimos 7 dias
  │
  ├──► Calcula estatísticas:                                   ← repositorio_inteli_academy
  │     Distribuição por categoria | Sentimentos |
  │     Oportunidades únicas
  │
  ├──► Multi-Agente (4 chamadas Groq Llama 3.3 70B):          ← InteliAcedemy
  │     │
  │     ├──► Agente 1: Triagem e Categorização
  │     │     Prompt: categorizar e resumir cada notícia
  │     │     max_tokens: 2500
  │     │
  │     ├──► Agente 2: Analista de Tendências
  │     │     Prompt: Identificar exatamente 4 tendências reais
  │     │     max_tokens: 3000
  │     │
  │     ├──► Agente 3: Analista de Oportunidades
  │     │     Prompt: Identificar 5 oportunidades para startups
  │     │     max_tokens: 3000
  │     │
  │     │     └──► Merge (3 entradas)
  │     │
  │     └──► Agente 4: Redator-Chefe
  │           Prompt: Montar relatório semanal completo
  │           max_tokens: 6400
  │
  ├──► Gera previsões para próxima semana                      ← repositorio_inteli_academy
  │
  ├──► Gera "Hypes do Momento" (GitHub trending)              ← newsletterSemanalIA
  │
  ├──► Cacheia no Redis (7 dias)                               ← Mymir
  │
  └──► 4 ramos paralelos:                                      ← repositorio_inteli_academy
        ├──► Prepara para Distribuidor (Workflow 3)
        ├──► Salva em Google Sheets (aba "Resumos Semanais")
        ├──► Salva em PostgreSQL
        └──► Salva arquivo local HTML
```

**Nós estimados:** ~20
**Chamadas LLM:** 4 (multi-agente) + 1 (previsões) = 5
**Integrações:** Google Sheets, PostgreSQL, Groq, Gemini, Redis, GitHub

**Códigos/componentes para copiar:**
- `InteliAcedemy`: 4 agentes (Triagem, Tendências, Oportunidades, Redator-Chefe) + Merge + Wait nodes
- `repositorio_inteli_academy`: Filtragem semanal, estatísticas, previsões, distribuição paralela
- `newsletterSemanalIA`: GitHub trending
- `Mymir`: Redis caching

---

### Workflow 3 — Distribuidor Multicanal

**Trigger:** Webhook (chamado pelo Workflow 2 + sob demanda)
**Status:** Ativo

**Pipeline:**

```
Webhook (recebe dados do relatório)
  │
  ├──► 1. Email Newsletter                                     ← psIa + newsletterSemanalIA
  │     ├──► Gera HTML profissional (beige/terracotta palette)
  │     ├──► Lê assinantes do Google Sheets
  │     ├──► Verifica duplicatas
  │     └──► Envia via Gmail (OAuth2) — um por assinante
  │
  ├──► 2. Slack                                                ← repositorio_inteli_academy
  │     ├──► Resumo executivo
  │     ├──► Top 5 artigos com links
  │     └──► Tabela de categorias
  │
  ├──► 3. Telegram                                             ← Newsletter_n8n_IA
  │     ├──► Formata para mobile (parágrafos curtos, emojis)
  │     ├──► 7 notícias mais importantes
  │     └──► Envia via Telegram Bot API
  │
  ├──► 4. LinkedIn (com human-in-the-loop)                     ← newsletterSemanalIA
  │     ├──► Gera copy via LLM (Groq GPT OSS 120B)
  │     ├──► Envia email de aprovação (Aprovar/Rejeitar)
  │     ├──► Aguarda clique (Wait webhook)
  │     └──► Se aprovado: POST LinkedIn API v2/ugcPosts
  │
  └──► 5. Webhook para Frontend                                ← Mymir
        ├──► Dados disponíveis via REST API
        └──► Cache no Redis (1 hora)
```

**Nós estimados:** ~20
**Chamadas LLM:** 1 (LinkedIn copy)
**Integrações:** Gmail, Google Sheets, Slack, Telegram, LinkedIn, Redis

**Códigos/componentes para copiar:**
- `newsletterSemanalIA`: LinkedIn approval gate, formato de post, template HTML
- `psIa`: Subscription management (Google Sheets)
- `Newsletter_n8n_IA`: Telegram node, formatação mobile
- `repositorio_inteli_academy`: Mensagens Slack
- `Mymir`: Webhook response

---

### Workflow 4 — Chatbot IA

**Trigger:** Sempre ativo (webhook)
**Status:** Ativo
**Workflow de erro vinculado:** Workflow 5

**Pipeline:**

```
Webhook (sempre ativo, via ngrok)
  │
  ├──► Aceita 2 origens:
  │     ├──► Slack Slash Command (/ia pergunta)                ← repositorio_inteli_academy
  │     └──► Web Chat (via frontend React)                     ← Mymir
  │
  ├──► Responde imediatamente (<3s para Slack)                 ← repositorio_inteli_academy
  │     "Consultando a base de IA... aguarde!"
  │
  ├──► Extrai pergunta (suporta ambos formatos)
  │
  ├──► Redis Cache Check:
  │     ├──► Cache hit → retorna resposta cacheada (TTL 1h)   ← Mymir
  │     └──► Cache miss → continua
  │
  ├──► Lê artigos do Google Sheets (últimos 7 dias, score≥6) ← repositorio_inteli_academy
  │
  ├──► Prepara contexto para IA (máx 30 artigos)
  │
  ├──► LLM responde (temperature 0.3, max 400 palavras)        ← repositorio_inteli_academy
  │     Primário: Groq Llama 3.3 70B
  │     Fallback: Google Gemini
  │
  ├──► Suporte a follow-up                                     ← Mymir
  │     Armazena contexto da conversa no Redis
  │     Permite "me fale mais sobre X"
  │
  ├──► Formata resposta (header + rodapé)
  │
  ├──► Cacheia resposta no Redis (TTL 1h)                      ← Mymir
  │
  └──► Envia resposta (Slack message ou Webhook response)
```

**Nós estimados:** ~15
**Chamadas LLM:** 1 por pergunta (mais follow-ups)
**Integrações:** Slack (webhook + message), Google Sheets, Groq, Gemini, Redis

**Códigos/componentes para copiar:**
- `repositorio_inteli_academy`: Webhook Slack, resposta dupla (sync + async), extração de pergunta, filtragem de artigos
- `Mymir`: Normalize Input, Redis cache (get/set), follow-up context, resposta padronizada

---

### Workflow 5 — Monitoramento de Erros

**Trigger:** Error Trigger (vinculado aos workflows 1, 2, 4)
**Status:** Ativo

**Pipeline:**

```
Error Trigger (automático quando qualquer nó falha)
  │
  ├──► Extrai:
  │     ├──► Nome do workflow
  │     ├──► Nó que falhou
  │     ├──► Mensagem de erro
  │     └──► Timestamp
  │
  └──► Alerta no Slack:                                        ← repositorio_inteli_academy
        "❌ ERRO no workflow [nome]
         Nó: [nome do nó]
         Erro: [mensagem]
         ⏰ [timestamp]"
```

**Nós estimados:** 3
**Integrações:** Slack

**Códigos/componentes para copiar:**
- `repositorio_inteli_academy`: Error Trigger + Slack alert + formatação

---

## 6. Backend FastAPI

### Estrutura dos Arquivos

O backend segue exatamente a estrutura do Mymir, com adições dos outros projetos.

#### `backend/app/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers import auth, chat, news, ranking, subscription

app = FastAPI(title="Inteli AI Hub", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(ranking.router, prefix="/api/ranking", tags=["ranking"])
app.include_router(subscription.router, prefix="/api/subscription", tags=["subscription"])
```

**Base:** `Mymir/backend/app/main.py`

#### `backend/app/core/config.py`
Pydantic Settings com:
- `DATABASE_URL` (PostgreSQL)
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- `JWT_SECRET`, `JWT_ALGORITHM` (HS256)
- `N8N_WEBHOOK_URL`
- `FRONTEND_URL` (CORS)

**Base:** `Mymir/backend/app/core/config.py`

#### `backend/app/core/database.py`
SQLAlchemy async engine + session + Base.

**Base:** `Mymir/backend/app/core/database.py`

#### `backend/app/core/redis.py`
Redis client connection (async).

**Base:** `Mymir/backend/app/core/redis.py`

#### `backend/app/models/`

| Modelo | Campos | Origem |
|--------|--------|--------|
| `User` | id, email, name, hashed_password, created_at | Mymir |
| `Article` | id, title, url, source, summary, category, relevance_score, sentiment, startup_opportunity, published_at, collected_at | Mymir + Case_Inteli_Academy + repositorio_inteli_academy |
| `Favorite` | id, user_id, article_id, created_at | Case_Inteli_Academy |
| `ChatSession` | id, user_id, path, created_at, updated_at | Mymir |
| `ChatMessage` | id, session_id, role (user/assistant), content, created_at | Mymir |
| `RankingEntry` | id, user_id, score, level, updated_at | inteliIA |
| `Subscriber` | id, email, name, subscribed_at, active | psIa |

#### `backend/app/schemas/`
Pydantic models para validação de entrada/saída.

| Schema | Origem |
|--------|--------|
| `SignupRequest`, `LoginRequest`, `TokenResponse` | Mymir |
| `ChatRequest`, `ChatResponse` | Mymir |
| `NewsResponse`, `NewsListResponse` | Mymir + Case_Inteli_Academy |
| `RankingResponse`, `RankingUpdateRequest` | inteliIA |
| `SubscribeRequest`, `SubscribeResponse` | psIa |

#### `backend/app/controllers/`

| Controller | Rotas | Origem |
|------------|-------|--------|
| `auth.py` | POST `/signup`, POST `/login`, GET `/me` | Mymir |
| `chat.py` | POST `/chat`, GET `/sessions`, GET `/history` | Mymir |
| `news.py` | GET `/news`, POST `/favorite`, GET `/favorites` | Mymir + Case_Inteli_Academy |
| `ranking.py` | GET `/ranking`, POST `/score` | inteliIA |
| `subscription.py` | POST `/subscribe`, DELETE `/unsubscribe` | psIa |

#### `backend/app/middleware/auth.py`
JWT Bearer token validation middleware usando `python-jose`.

**Base:** `Mymir/backend/app/middleware/auth.py`

#### `backend/app/services/n8n.py`
HTTP client (httpx) para chamar webhooks do n8n.

**Base:** `Mymir/backend/app/services/n8n.py`

#### `backend/requirements.txt`
```
fastapi==0.135.2
uvicorn==0.42.0
sqlalchemy==2.0.48
asyncpg==0.31.0
redis==7.4.0
pydantic==2.12.5
pydantic-settings==2.13.1
python-jose==3.5.0
passlib==1.7.4
bcrypt==3.2.2
httpx==0.28.1
python-dotenv==1.2.2
alembic==1.18.4
cryptography==46.0.6
```

**Base:** `Mymir/backend/requirements.txt`

---

## 7. Frontend React

### Estrutura dos Arquivos

O frontend segue a estrutura do Mymir (React + Vite + TypeScript + Tailwind), com páginas adicionais e componentes dos outros projetos.

#### Páginas

| Página | Rota | Funcionalidades | Origem |
|--------|------|----------------|--------|
| `Login.tsx` | `/login` | Formulário de login | Mymir |
| `Signup.tsx` | `/signup` | Cadastro com opt-in newsletter | Mymir + psIa |
| `Dashboard.tsx` | `/` | Feed de notícias com filtros, gamificação, favoritos, "Hypes do Momento" | Case_Inteli_Academy + inteliIA + newsletterSemanalIA |
| `Chat.tsx` | `/chat` | Chat IA com seleção de caminho, histórico, follow-up, PDF export | Mymir |
| `Ranking.tsx` | `/ranking` | Leaderboard global, pontos, níveis | inteliIA |
| `Trends.tsx` | `/trends` | Tendências da semana, oportunidades, previsões preditivas | InteliAcedemy + repositorio_inteli_academy |
| `Profile.tsx` | `/profile` | Editar perfil, gerenciar assinatura newsletter | Mymir + psIa |
| `WeeklyReport.tsx` | `/weekly` | Visualização do relatório semanal completo | newsletterSemanalIA |

#### Componentes

| Componente | Descrição | Origem |
|------------|-----------|--------|
| `Logo.tsx` | Órbita animada (SVG + Framer Motion) | Mymir |
| `DashboardLayout.tsx` | Sidebar + main area | Mymir |
| `Sidebar.tsx` | Navegação, notificações, logout | Mymir |
| `NewsCard.tsx` | Card de notícia com imagem, categoria, score, favoritar | Case_Inteli_Academy + inteliIA |
| `NewsFilters.tsx` | Filtros por categoria, data, relevância | inteliIA |
| `FavoritesButton.tsx` | Botão de favoritar/disfavoritar | Case_Inteli_Academy |
| `TrendingRepos.tsx` | "Hypes do Momento" (GitHub repos) | newsletterSemanalIA |
| `ChatInput.tsx` | Textarea com botão de envio | Mymir |
| `MessageBubble.tsx` | Mensagem com Markdown + PDF export | Mymir |
| `PathSelector.tsx` | Modal para selecionar caminho (Notícias/Tendências/Projetos) | Mymir |
| `TypingIndicator.tsx` | Indicador de digitação animado | Mymir |
| `PointsBadge.tsx` | Badge de pontos do usuário | inteliIA |
| `Leaderboard.tsx` | Tabela de ranking com posições | inteliIA |
| `TrendCard.tsx` | Card de tendência com evidências | InteliAcedemy |
| `WeeklySummary.tsx` | Resumo semanal editado | Mymir |
| `Predictions.tsx` | Previsões para próxima semana | repositorio_inteli_academy |

#### Store (Zustand)

| Store | Estado | Origem |
|-------|--------|--------|
| `auth.store.ts` | user, token, login(), logout() | Mymir |
| `news.store.ts` | articles, filters, favorites, fetchNews() | Case_Inteli_Academy |
| `chat.store.ts` | sessions, messages, sendMessage() | Mymir |
| `ranking.store.ts` | entries, myScore, fetchRanking(), updateScore() | inteliIA |

#### Services

| Service | Métodos | Origem |
|---------|---------|--------|
| `api.ts` | axios instance com interceptor JWT | Mymir |
| `ranking.ts` | getRanking(), postScore() | inteliIA |
| `subscription.ts` | subscribe(email), unsubscribe(email) | psIa |

#### `package.json` (dependências)

```json
{
  "dependencies": {
    "react": "^19.2.4",
    "react-dom": "^19.2.4",
    "react-router-dom": "^7.13.2",
    "zustand": "^5.0.12",
    "axios": "^1.14.0",
    "framer-motion": "^12.38.0",
    "lucide-react": "^1.7.0",
    "react-markdown": "^10.1.0",
    "remark-gfm": "^4.0.1",
    "jspdf": "^4.2.1",
    "react-hot-toast": "^2.6.0"
  },
  "devDependencies": {
    "typescript": "~5.9.3",
    "vite": "^8.0.1",
    "@vitejs/plugin-react": "^4.4.1",
    "tailwindcss": "^4.2.2",
    "@tailwindcss/typography": "^0.5.19",
    "@tailwindcss/vite": "^4.2.2",
    "eslint": "^9.25.1",
    "vitest": "^3.1.1",
    "@testing-library/react": "^16.3.0",
    "jsdom": "^26.0.0"
  }
}
```

**Base:** `Mymir/frontend/package.json`

---

## 8. Infraestrutura Docker

### `docker-compose.yml`

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin123
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=168
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n/workflows:/home/node/workflows
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --requirepass redis_secret
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=inteli
      - POSTGRES_PASSWORD=inteli_secret
      - POSTGRES_DB=inteli_ai_hub
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U inteli"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://inteli:inteli_secret@postgres:5432/inteli_ai_hub
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=redis_secret
      - JWT_SECRET=super-secret-jwt-key-change-in-production
      - N8N_WEBHOOK_URL=http://n8n:5678/webhook
      - FRONTEND_URL=http://localhost:5173
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

volumes:
  n8n_data:
  redis_data:
  postgres_data:
```

**Base:** `Mymir/docker-compose.yml` (adaptado, adicionando PostgreSQL)

---

## 9. Fluxo de Dados

### Entre Workflows

```
Workflow 1 (Diário 08:00)
  │
  ├──► Google Sheets (aba "Artigos") ◄───────────────────────── Workflow 4 (Chatbot lê)
  │
  ├──► PostgreSQL (via webhook backend)
  │
  └──► Slack (resumo diário)

Workflow 2 (Domingo 09:00)
  │
  ├──► Lê Google Sheets + PostgreSQL (artigos da semana)
  │
  ├──► Gera relatório via multi-agente
  │
  ├──► Cacheia no Redis (TTL 7 dias)
  │
  ├──► Salva Google Sheets (aba "Resumos Semanais")
  │
  ├──► Salva PostgreSQL
  │
  └──► Chama Workflow 3 (webhook)

Workflow 3 (Sob demanda)
  │
  ├──► Lê dados do Redis/PostgreSQL
  │
  ├──► Email (Gmail) → Assinantes do Google Sheets
  ├──► Slack → Canal #novo-canal
  ├──► Telegram → Canal @psInteliAcademy_bot
  ├──► LinkedIn → Post com aprovação humana
  └──► Webhook → Frontend (via backend)

Workflow 4 (Sempre ativo)
  │
  ├──► Slack (Slash Command) ou Web Frontend
  ├──► Lê Google Sheets (artigos recentes)
  ├──► Cache Redis (respostas + contexto)
  └──► LLM → Responde

Workflow 5 (Sempre ativo)
  └──► Vinculado aos workflows 1, 2, 4
       └──► Alerta Slack em caso de erro
```

### Entre Frontend e Backend

```
React Frontend
  │
  ├──► POST /api/auth/login → JWT token
  ├──► POST /api/auth/signup → Criar conta
  │
  ├──► GET /api/news → Listar notícias (do PostgreSQL via webhook n8n)
  ├──► POST /api/news/favorite → Favoritar notícia
  ├──► DELETE /api/news/favorite/:id → Remover favorito
  │
  ├──► POST /api/chat → Enviar pergunta (encaminha para n8n webhook)
  ├──► GET /api/chat/sessions → Listar sessões
  ├──► GET /api/chat/history/:id → Histórico da sessão
  │
  ├──► GET /api/ranking → Ranking global
  ├──► POST /api/ranking/score → Atualizar pontuação
  │
  └──► POST /api/subscription → Assinar newsletter
       └──► DELETE /api/subscription → Cancelar assinatura
```

---

## 10. Cronograma de Implementação

### Fase 1: Infraestrutura
**Dependências:** Nenhuma
**O que fazer:**
1. Criar diretório `inteli-ai-hub/`
2. Copiar `docker-compose.yml` do Mymir, adicionar PostgreSQL
3. Criar `.env.example` com todas as variáveis
4. Criar `.gitignore`
5. Testar: `docker compose up` → n8n, Redis, PostgreSQL rodando

**Origem:** `Mymir/docker-compose.yml`

---

### Fase 2: Backend Core
**Dependências:** Fase 1
**O que fazer:**
1. Copiar estrutura `backend/` do Mymir
2. Adaptar `config.py` para incluir novas variáveis
3. Adaptar `database.py` (modelos + migrations)
4. Adaptar `redis.py`
5. Criar modelos: User, Article, Favorite, ChatSession, ChatMessage, RankingEntry, Subscriber
6. Criar schemas Pydantic
7. Criar middleware JWT
8. Criar controllers: auth (signup/login/me)
9. Testar: `POST /api/auth/signup` e `POST /api/auth/login`

**Origem:** `Mymir/backend/` + `Case_Inteli_Academy` (modelos de favoritos) + `inteliIA` (modelos de ranking) + `psIa` (modelos de assinante)

---

### Fase 3: Backend APIs
**Dependências:** Fase 2
**O que fazer:**
1. Controller `news.py`: GET /news, POST /favorite, GET /favorites
2. Controller `chat.py`: POST /chat (integra com n8n webhook), GET /sessions, GET /history
3. Controller `ranking.py`: GET /ranking, POST /score
4. Controller `subscription.py`: POST /subscribe, DELETE /unsubscribe
5. Service `n8n.py`: HTTP client para webhooks do n8n
6. Testar todas as rotas

**Origem:** `Mymir/backend/controllers/` + `Case_Inteli_Academy` (favoritos) + `inteliIA` (ranking) + `psIa` (subscription)

---

### Fase 4: Frontend Core
**Dependências:** Fase 2
**O que fazer:**
1. Copiar estrutura `frontend/` do Mymir
2. Configurar Tailwind, Vite, TypeScript
3. Criar store: auth.store.ts (Zustand)
4. Criar service: api.ts (axios + interceptor JWT)
5. Criar páginas: Login.tsx, Signup.tsx
6. Criar layout: Sidebar, Header, Logo
7. Configurar React Router
8. Testar: login, signup, navegação

**Origem:** `Mymir/frontend/`

---

### Fase 5: Frontend Páginas
**Dependências:** Fase 4
**O que fazer:**
1. `Dashboard.tsx`: Feed de notícias + filtros + gamificação + favoritos + "Hypes do Momento"
2. `Chat.tsx`: Chat IA com PathSelector, MessageBubble, TypingIndicator, PDF export
3. `Ranking.tsx`: Leaderboard global com pontos e níveis
4. `Trends.tsx`: Tendências, oportunidades, previsões
5. `Profile.tsx`: Editar perfil, gerenciar assinatura
6. `WeeklyReport.tsx`: Relatório semanal visual

**Origem:** `Case_Inteli_Academy/index.html` (dashboard) + `inteliIA/index.html` (gamificação) + `Mymir/frontend/src/pages/Chat.tsx` + `newsletterSemanalIA` (trends/report)

---

### Fase 6: Workflow 1 — Coletor Diário
**Dependências:** Fase 1
**O que fazer:**
1. Criar `01-coletor-diario.json` no n8n
2. Schedule trigger (08:00 diário)
3. RSS dinâmicos (allainews_sources) — copiar de `repositorio_inteli_academy`
4. 9 RSS fixos em paralelo — copiar de `inteliIA`
5. APIs (Tavily, NewsAPI, Dev.to) — copiar de `Newsletter_n8n_IA`
6. Merge tree — copiar de `inteliIA`
7. Deduplicação — copiar de `inteliIA` + `repositorio_inteli_academy`
8. Pré-pontuação — copiar de `repositorio_inteli_academy`
9. LLM com fallback — copiar de `Newsletter-IA-n8n`
10. Parse LLM — copiar de `repositorio_inteli_academy`
11. Google Sheets — copiar de `repositorio_inteli_academy`
12. Slack — copiar de `repositorio_inteli_academy`
13. Testar execução manual

---

### Fase 7: Workflow 2 — Sintetizador Semanal
**Dependências:** Fase 6
**O que fazer:**
1. Criar `02-sintetizador-semanal.json` no n8n
2. Schedule trigger (domingo 09:00)
3. Ler Google Sheets + PostgreSQL
4. Multi-agente (4 chamadas) — copiar prompts do `InteliAcedemy`
5. Previsões — copiar de `repositorio_inteli_academy`
6. GitHub trending — copiar de `newsletterSemanalIA`
7. Redis caching — copiar de `Mymir`
8. 4 ramos paralelos — copiar de `repositorio_inteli_academy`

---

### Fase 8: Workflow 3 — Distribuidor
**Dependências:** Fase 7
**O que fazer:**
1. Criar `03-distribuidor.json` no n8n
2. Webhook trigger
3. Email (Gmail + Google Sheets) — copiar de `psIa` + `newsletterSemanalIA`
4. Slack — copiar de `repositorio_inteli_academy`
5. Telegram — copiar de `Newsletter_n8n_IA`
6. LinkedIn com aprovação — copiar de `newsletterSemanalIA`
7. Webhook para backend — copiar de `Mymir`

---

### Fase 9: Workflow 4 — Chatbot
**Dependências:** Fase 6
**O que fazer:**
1. Criar `04-chatbot.json` no n8n
2. Webhook sempre ativo
3. Resposta dupla (sync + async) — copiar de `repositorio_inteli_academy`
4. Redis cache — copiar de `Mymir`
5. Google Sheets + LLM — copiar de `repositorio_inteli_academy`
6. Follow-up context — copiar de `Mymir`

---

### Fase 10: Workflow 5 — Monitoramento
**Dependências:** Fase 6
**O que fazer:**
1. Criar `05-monitoramento.json` no n8n
2. Error trigger — copiar de `repositorio_inteli_academy`
3. Slack alert — copiar de `repositorio_inteli_academy`
4. Vincular aos workflows 1, 2, 4

---

### Fase 11: Integração Final
**Dependências:** Fases 1-10
**O que fazer:**
1. Conectar frontend ↔ backend (axios com JWT)
2. Conectar backend ↔ n8n (webhooks via service n8n.py)
3. Subir Docker Compose completo
4. Importar todos os 5 workflows no n8n
5. Configurar credenciais (Groq, Gemini, Gmail, Slack, Telegram, LinkedIn, Google Sheets)
6. Testar fluxo completo:
   - Usuário se cadastra → login → vê dashboard
   - Workflow 1 roda → artigos no banco
   - Workflow 2 roda → relatório semanal
   - Workflow 3 roda → notificações em todos os canais
   - Workflow 4 responde perguntas no chat e no Slack
   - Workflow 5 alerta se algo falhar

---

## 11. Comparativo: Projetos Originais vs Unificado

| Feature | Case | InteliAcedemy | inteliIA | Mymir | News_n8n | News-IA-n8n | NewsSemanal | PS-Inteli | psIa | Repositorio | **UNIFICADO** |
|---------|------|--------------|----------|-------|----------|-------------|-------------|-----------|------|-------------|:-------------:|
| Dashboard Web | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ (Airtable) | ✅ (Mobile) | ❌ | **✅** |
| Multi-Agente IA | ❌ | ✅ (4) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ (4)** |
| Gamificação | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** |
| Chat IA Conversacional | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (Slack) | **✅ (Web+Slack)** |
| 9+ Fontes RSS | ✅ (1) | ✅ (1) | ✅ (9) | ❌ (APIs) | ✅ (5) | ✅ (3) | ✅ (3) | ✅ (2) | ✅ (3) | ✅ (Dinâmicas) | **✅ (9+ + Dinâmicas)** |
| Fallback LLM | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | **✅** |
| LinkedIn | ❌ | ❌ | ❌ | ❌ | ❌ | ❌| ✅ | ❌ | ❌ | ❌ | **✅** |
| Telegram | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** |
| Slack | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | **✅** |
| Email Newsletter | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | **✅** |
| Cache Redis | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** |
| PostgreSQL | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** |
| Google Sheets | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | **✅** |
| Imagens Dinâmicas | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | **✅** |
| Human-in-the-Loop | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | **✅** |
| Previsões Preditivas | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | **✅** |
| Error Handler | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | **✅** |
| Docker Compose | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** |
| JWT Auth | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** |
| PDF Export | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** |
| Testes | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | **✅** |

---

## Resumo Final

O **Inteli AI Hub** será o projeto mais completo do ecossistema, combinando:

- **5 workflows n8n** interligados (vs. máximo de 4 nos projetos originais)
- **~83 nós** no total (vs. máximo de 48 no Mymir)
- **6 canais de entrega** (Email + Slack + Telegram + LinkedIn + Web + Discord-ready)
- **Full-stack moderno** (React + FastAPI + PostgreSQL + Redis + Docker)
- **LLM resiliente** (fallback automático Groq → Gemini)
- **Multi-agente** (4 papéis de IA especializados)
- **Gamificação** (pontos, níveis, ranking global)
- **Chat IA** (web + Slack, com follow-up e caching)
- **Human-in-the-loop** (LinkedIn com aprovação)
- **Monitoramento** (error handler dedicado com alertas)
- **Testes automatizados**

Tudo isso construído **do zero**, aproveitando o melhor código, prompts e configurações de cada um dos 10 projetos.

---

## Complemento A — Database Schema Detalhado

### Tabela: `users`

| Coluna | Tipo | Constraints | Origem |
|--------|------|------------|--------|
| `id` | UUID | PK, default uuid4 | Mymir |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Mymir |
| `name` | VARCHAR(255) | NOT NULL | Mymir |
| `hashed_password` | VARCHAR(255) | NOT NULL | Mymir |
| `is_active` | BOOLEAN | default true | Mymir |
| `newsletter_opt_in` | BOOLEAN | default false | psIa |
| `created_at` | TIMESTAMP | default now() | Mymir |
| `updated_at` | TIMESTAMP | onupdate now() | Mymir |

### Tabela: `articles`

| Coluna | Tipo | Constraints | Origem |
|--------|------|------------|--------|
| `id` | UUID | PK | Mymir |
| `title` | TEXT | NOT NULL | Todos |
| `url` | TEXT | UNIQUE, NOT NULL | Todos |
| `source` | VARCHAR(255) | NOT NULL | inteliIA |
| `source_type` | VARCHAR(50) | "rss_fixed", "rss_dynamic", "tavily", "newsapi", "devto", "arxiv" | Novo |
| `summary` | TEXT | | InteliAcedemy |
| `category` | VARCHAR(50) | | Newsletter-IA-n8n |
| `relevance_score` | INTEGER | 1-10 | repositorio_inteli_academy |
| `sentiment` | VARCHAR(20) | "positive", "neutral", "negative" | repositorio_inteli_academy |
| `startup_opportunity` | TEXT | | repositorio_inteli_academy |
| `insight` | TEXT | | PS-Inteli-Academy |
| `image_url` | TEXT | | newsletterSemanalIA |
| `tags` | JSONB | default [] | inteliIA |
| `published_at` | TIMESTAMP | | Todos |
| `collected_at` | TIMESTAMP | default now() | repositorio_inteli_academy |

**Índices:** `(category)`, `(source)`, `(published_at DESC)`, `(relevance_score DESC)`

### Tabela: `favorites`

| Coluna | Tipo | Constraints |
|--------|------|------------|
| `id` | UUID | PK |
| `user_id` | UUID | FK → users.id, NOT NULL |
| `article_id` | UUID | FK → articles.id, NOT NULL |
| `created_at` | TIMESTAMP | default now() |

**Unique:** `(user_id, article_id)`

### Tabela: `chat_sessions`

| Coluna | Tipo | Constraints | Origem |
|--------|------|------------|--------|
| `id` | UUID | PK | Mymir |
| `user_id` | UUID | FK → users.id, NOT NULL | Mymir |
| `path` | VARCHAR(50) | "news"/"trends"/"projects" | Mymir |
| `title` | VARCHAR(255) | auto-generated | Mymir |
| `created_at` | TIMESTAMP | default now() | Mymir |
| `updated_at` | TIMESTAMP | onupdate now() | Mymir |

### Tabela: `chat_messages`

| Coluna | Tipo | Constraints | Origem |
|--------|------|------------|--------|
| `id` | UUID | PK | Mymir |
| `session_id` | UUID | FK → chat_sessions.id, NOT NULL | Mymir |
| `role` | VARCHAR(20) | "user" / "assistant" | Mymir |
| `content` | TEXT | NOT NULL | Mymir |
| `source` | VARCHAR(20) | "cache" / "llm" | Mymir |
| `metadata` | JSONB | | Mymir |
| `created_at` | TIMESTAMP | default now() | Mymir |

**Índice:** `(session_id, created_at ASC)`

### Tabela: `ranking_entries`

| Coluna | Tipo | Constraints | Origem |
|--------|------|------------|--------|
| `id` | UUID | PK | inteliIA |
| `user_id` | UUID | FK → users.id, UNIQUE | inteliIA |
| `score` | INTEGER | default 0 | inteliIA |
| `level` | INTEGER | default 1 | inteliIA |
| `articles_read` | INTEGER | default 0 | inteliIA |
| `updated_at` | TIMESTAMP | onupdate now() | inteliIA |

### Tabela: `subscribers`

| Coluna | Tipo | Constraints | Origem |
|--------|------|------------|--------|
| `id` | UUID | PK | psIa |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | psIa |
| `name` | VARCHAR(255) | | psIa |
| `is_active` | BOOLEAN | default true | psIa |
| `source` | VARCHAR(50) | "web" / "slack" / "telegram" | psIa |
| `subscribed_at` | TIMESTAMP | default now() | psIa |
| `unsubscribed_at` | TIMESTAMP | | psIa |

---

## Complemento B — API Contracts (FastAPI)

### `POST /api/auth/signup`

**Request:**
```json
{
  "email": "user@email.com",
  "name": "User Name",
  "password": "securepassword123",
  "newsletter_opt_in": true
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "email": "user@email.com",
  "name": "User Name",
  "newsletter_opt_in": true,
  "created_at": "2026-06-01T10:00:00Z"
}
```

**Response 409:** `{ "detail": "Email already registered" }`

### `POST /api/auth/login`

**Request:**
```json
{
  "email": "user@email.com",
  "password": "securepassword123"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@email.com",
    "name": "User Name"
  }
}
```

**Response 401:** `{ "detail": "Invalid credentials" }`

### `GET /api/news`

**Params:** `?category=IA+Generativa&source=TechCrunch&limit=20&offset=0`

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Article title",
      "url": "https://...",
      "source": "TechCrunch",
      "summary": "Resumo em português...",
      "category": "IA Generativa",
      "relevance_score": 8,
      "sentiment": "positive",
      "startup_opportunity": "Oportunidade para...",
      "tags": ["gpt", "openai"],
      "image_url": "https://...",
      "published_at": "2026-05-30T14:00:00Z",
      "is_favorited": true
    }
  ],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

### `POST /api/news/favorite`

**Request:**
```json
{ "article_id": "uuid" }
```

**Response 201:** `{ "message": "Favorited" }`

### `DELETE /api/news/favorite/{article_id}`

**Response 200:** `{ "message": "Unfavorited" }`

### `POST /api/chat`

**Request:**
```json
{
  "session_id": "uuid (opcional, nova seção se omitido)",
  "path": "news",
  "message": "Quais são as principais novidades em IA esta semana?",
  "source_pref": "web"
}
```

**Response 200:**
```json
{
  "session_id": "uuid",
  "response": "Esta semana tivemos várias novidades... [texto com markdown]",
  "source": "llm",
  "path": "news",
  "follow_up_supported": true,
  "timestamp": "2026-06-01T10:00:00Z"
}
```

### `GET /api/chat/sessions`

**Response 200:**
```json
[
  {
    "id": "uuid",
    "path": "news",
    "title": "Notícias da Semana",
    "message_count": 5,
    "created_at": "2026-06-01T10:00:00Z"
  }
]
```

### `GET /api/chat/history/{session_id}`

**Response 200:**
```json
{
  "session": { "id": "uuid", "path": "news" },
  "messages": [
    { "role": "user", "content": "Quais as novidades?", "created_at": "..." },
    { "role": "assistant", "content": "Esta semana...", "created_at": "..." }
  ]
}
```

### `GET /api/ranking`

**Response 200:**
```json
{
  "my_position": 3,
  "my_score": 450,
  "my_level": 9,
  "leaderboard": [
    { "position": 1, "user_name": "João", "score": 1200, "level": 24 },
    { "position": 2, "user_name": "Maria", "score": 890, "level": 17 },
    { "position": 3, "user_name": "brun***@gmail.com", "score": 450, "level": 9 }
  ]
}
```

### `POST /api/ranking/score`

**Request:**
```json
{ "points": 10, "action": "read_article" }
```

**Response 200:**
```json
{
  "total_score": 460,
  "level": 9,
  "level_up": false
}
```

### `POST /api/subscription`

**Request:**
```json
{ "email": "user@email.com", "name": "User Name", "source": "web" }
```

**Response 201:**
```json
{ "message": "Subscribed successfully", "id": "uuid" }
```

### `DELETE /api/subscription`

**Request:**
```json
{ "email": "user@email.com" }
```

**Response 200:**
```json
{ "message": "Unsubscribed successfully" }
```

---

## Complemento C — Credenciais n8n: Passo a Passo

### 1. Groq API

| Campo | Valor |
|-------|-------|
| **Onde criar** | https://console.groq.com/keys |
| **Plano** | Free tier: 30 req/min, 14.400 req/day |
| **Modelo** | `llama-3.3-70b-versatile` |
| **Criação no n8n** | Settings → Credentials → Add → "Groq" |
| **Nome da credencial** | `Groq account` |
| **API Key** | `gsk_...` (cole a chave do console) |

### 2. Google Gemini (Fallback)

| Campo | Valor |
|-------|-------|
| **Onde criar** | https://aistudio.google.com/apikey |
| **Plano** | Free tier: 60 req/min |
| **Modelo** | `models/gemini-2.5-flash` |
| **Criação no n8n** | Settings → Credentials → Add → "Google Gemini(PaLM) API" |
| **Nome da credencial** | `Google Gemini(PaLM) Api account` |
| **API Key** | `AIza...` (cole) |

### 3. Gmail (OAuth2)

| Campo | Valor |
|-------|-------|
| **Onde criar** | https://console.cloud.google.com → APIs → Gmail API → Credentials |
| **Tipo** | OAuth 2.0 Client ID (Desktop application) |
| **Redirect URI** | `http://localhost:5678/rest/oauth2-credential/callback` |
| **Escopos** | `https://mail.google.com/` |
| **Criação no n8n** | Settings → Credentials → Add → "Gmail OAuth2 API" |
| **Client ID** | Do console Google |
| **Client Secret** | Do console Google |

### 4. Slack

| Campo | Valor |
|-------|-------|
| **Onde criar** | https://api.slack.com/apps → Create New App → From manifest |
| **Escopos (Bot Token)** | `chat:write`, `chat:write.public`, `commands`, `channels:history` |
| **Slash Command** | `/ia` → Request URL: `https://SEU-NGROK.ngrok-free.app/webhook/chatbot-ia` |
| **Criação no n8n** | Settings → Credentials → Add → "Slack API" |
| **Access Token** | `xoxb-...` (Bot User OAuth Token) |
| **Canal** | Criar canal `#novo-canal`, copiar ID (`C...`) |

### 5. Telegram

| Campo | Valor |
|-------|-------|
| **Onde criar** | https://t.me/BotFather → `/newbot` |
| **Bot username** | `@inteli_ai_hub_bot` |
| **Criação no n8n** | Settings → Credentials → Add → "Telegram API" |
| **Access Token** | `123456:ABC-DEF...` (de BotFather) |
| **Chat ID** | `@userinfobot` → enviar `/start` → copiar ID numérico |

### 6. LinkedIn

| Campo | Valor |
|-------|-------|
| **Onde criar** | https://www.linkedin.com/developers/apps → Create app |
| **Redirect URI** | `http://localhost:5678/rest/oauth2-credential/callback` |
| **Escopos** | `w_member_social`, `r_liteprofile` |
| **Criação no n8n** | Settings → Credentials → Add → "LinkedIn OAuth2 API" |
| **Client ID / Secret** | Do developer portal |
| **Person URN** | `urn:li:person:...` (obter via API) |

### 7. Google Sheets

| Campo | Valor |
|-------|-------|
| **Onde criar** | https://console.cloud.google.com → APIs → Google Sheets API → Credentials |
| **Escopos** | `https://www.googleapis.com/auth/spreadsheets` |
| **Criação no n8n** | Settings → Credentials → Add → "Google Sheets OAuth2 API" |
| **Client ID / Secret** | Do console Google |

### 8. NewsAPI

| Campo | Valor |
|-------|-------|
| **Onde criar** | https://newsapi.org/register |
| **Plano** | Free: 100 req/day |
| **API Key** | Inserir diretamente no nó HTTP Request (query param `apiKey`) |

### 9. Tavily

| Campo | Valor |
|-------|-------|
| **Onde criar** | https://app.tavily.com/sign-in |
| **Plano** | Free: 1000 req/month |
| **Criação no n8n** | Settings → Credentials → Add → "Tavily API" |

---

## Complemento D — ngrok + Slack: Setup

O Workflow 4 (Chatbot) precisa estar acessível pela internet para o Slack chamar o webhook.

### Passo 1: Baixar ngrok

```powershell
# Download
winget install ngrok

# OU
# Baixar de https://ngrok.com/download e extrair
```

### Passo 2: Autenticar

```powershell
ngrok config add-authtoken SEU_TOKEN
# Token em https://dashboard.ngrok.com/get-started/your-authtoken
```

### Passo 3: Expor o n8n

```powershell
ngrok http 5678
# Saída:
# Forwarding https://abc123.ngrok-free.app -> http://localhost:5678
```

### Passo 4: Configurar Slack

1. Ir em https://api.slack.com/apps → seu app → Slash Commands
2. Editar comando `/ia`
3. Request URL: `https://abc123.ngrok-free.app/webhook/chatbot-ia`
4. Salvar

### Passo 5: (Opcional) ngrok fixo

Para URL não mudar a cada restart:
```powershell
ngrok http 5678 --domain=seu-dominio.ngrok-free.app
```

### Script PowerShell

```powershell
# start-dev.ps1
docker compose up -d
Start-Sleep -Seconds 5
Write-Host "n8n: http://localhost:5678"
Write-Host "Iniciando ngrok..."
Start-Process -WindowStyle Hidden ngrok http 5678
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:5173"
```

---

## Complemento E — Ordem de Importação e Ativação dos Workflows

### Ordem Correta

| Ordem | Workflow | Por quê |
|-------|----------|---------|
| 1 | **05-monitoramento.json** | Deve existir ANTES dos outros para capturar erros desde o início |
| 2 | **01-coletor-diario.json** | Precisa estar ativo para popular os dados |
| 3 | **02-sintetizador-semanal.json** | Depende dos dados do Coletor |
| 4 | **03-distribuidor.json** | Depende do relatório do Sintetizador |
| 5 | **04-chatbot.json** | Independente, mas precisa dos dados do Coletor |

### Passo a Passo no n8n

```
1. Acessar http://localhost:5678
2. Login: admin / admin123
3. Settings → Credentials → criar as 7+ credenciais

4. Workflows → Add → Import from File → selecionar 05-monitoramento.json
   → Editar credential Slack no nó "Alerta de Erro"
   → Salvar → Ativar (toggle Active)

5. Repetir passo 4 para 01-coletor-diario.json
   → Configurar credenciais: Groq, Gemini, Google Sheets, Slack, Gmail
   → No nó "Todo dia as 8h": ajustar horário se necessário
   → Salvar → Ativar

6. Repetir para 02-sintetizador-semanal.json
   → Credenciais: Groq, Google Sheets, Gmail, Slack
   → Salvar → Ativar

7. Repetir para 03-distribuidor.json
   → Credenciais: Gmail, Google Sheets, Slack, Telegram, LinkedIn
   → Salvar → Ativar

8. Repetir para 04-chatbot.json
   → Configurar webhook URL (ngrok)
   → Configurar Slack Slash Command no Slack API
   → Credenciais: Groq, Google Sheets, Slack
   → Salvar → Ativar
```

### Verificação

Após ativar todos:
```
Workflow 1: aguardar schedule 08:00 OU clicar "Execute Workflow"
Workflow 2: aguardar domingo 09:00
Workflow 3: chamar webhook manualmente para testar
Workflow 4: digitar /ia no Slack → deve responder
Workflow 5: forçar erro (remover credential) → alerta no Slack
```

---

## Complemento F — Secrets Management

### No Backend (FastAPI)

Usar variáveis de ambiente no `docker-compose.yml`:

```yaml
backend:
  environment:
    - DATABASE_URL=postgresql://inteli:inteli_secret@postgres:5432/inteli_ai_hub
    - REDIS_PASSWORD=redis_secret
    - JWT_SECRET=${JWT_SECRET}  ← ler de .env
```

Arquivo `.env` (NUNCA versionar):

```env
# Database
POSTGRES_PASSWORD=inteli_secret

# Redis
REDIS_PASSWORD=redis_secret

# JWT
JWT_SECRET=your-256-bit-long-secret-key-here

# CORS
FRONTEND_URL=http://localhost:5173

# Webhook n8n
N8N_WEBHOOK_URL=http://n8n:5678/webhook
```

### No n8n (Para Tokens de API)

NUNCA colocar tokens hardcoded nos workflows. Usar o gerenciador de credenciais do n8n:

1. Settings → Credentials → Add
2. Escolher o tipo (Groq, Google, Slack, etc.)
3. Inserir token
4. Referenciar nos nós pelo nome da credencial

Para tokens de API que não têm node específico (ex: NewsAPI, Tavily), usar **n8n variables**:

```
Settings → Variables → Add
  nome: newsapi_key
  value: abc123...
```

Usar no nó HTTP Request:
```
{{ $vars.newsapi_key }}
```

### Boas Práticas

- `.env` no `.gitignore` (já incluso)
- `docker-compose.yml` usa `environment:` não `env_file:` para maior clareza
- Tokens LinkedIn NUNCA hardcoded (erro do newsletterSemanalIA que deve ser evitado)
- Chaves de API inline no workflow JSON = ❌
- Credenciais n8n + Variables = ✅

---

## Complemento G — Testes Específicos

### Backend (Vitest/Pytest)

| Teste | Descrição |
|-------|-----------|
| `test_auth_signup` | Cadastro com email válido, duplicado, inválido |
| `test_auth_login` | Login correto, senha errada, usuário inexistente |
| `test_auth_jwt` | Token expirado, token inválido, sem token |
| `test_news_list` | Listar com/sem filtros, paginação |
| `test_news_favorite` | Favoritar, disfavoritar, duplicado |
| `test_chat_send` | Enviar mensagem, session nova, follow-up |
| `test_chat_history` | Histórico de sessão vazia, com mensagens |
| `test_ranking_get` | Leaderboard vazio, com entries |
| `test_ranking_score` | Adicionar pontos, level up |
| `test_subscribe` | Assinar, duplicado, cancelar |

### Frontend (Vitest + Testing Library)

| Teste | Descrição |
|-------|-----------|
| `Login.render` | Renderiza formulário, botão submit |
| `Login.submit` | Chama API com email/senha |
| `Login.error` | Mostra erro em credenciais inválidas |
| `Dashboard.render` | Renderiza cards de notícias |
| `Dashboard.filter` | Filtra por categoria |
| `Dashboard.favorite` | Alterna favorito |
| `Chat.render` | Renderiza mensagens, input |
| `Chat.send` | Envia mensagem, recebe resposta |
| `Chat.followup` | Botão de follow-up visível |
| `Ranking.render` | Tabela de ranking, posição do usuário |
| `Ranking.gamification` | Badge de pontos/nível |

### n8n (Testes Manuais)

| Teste | Como Testar |
|-------|-------------|
| Coletor Diário | Clicar "Execute Workflow", verificar Google Sheets + Slack |
| Fallback LLM | Desabilitar credential Groq → deve cair no Gemini |
| Deduplicação | Executar 2x seguidas → artigos duplicados não devem aparecer |
| Sintetizador | Executar após coletor → relatório gerado nos 4 canais |
| Distribuidor Email | Verificar caixa de entrada |
| Distribuidor LinkedIn | Clicar "Aprovar" no email → post deve aparecer |
| Chatbot Slack | `/ia quais as principais notícias?` |
| Chatbot Follow-up | "Me fale mais sobre a primeira" |
| Error Handler | Forçar erro → Slack alerta recebido |
| Frontend | Login → Dashboard → Chat → Ranking → Profile → Logout |

---

## Complemento H — Possíveis Bloqueios e Mitigações

| Bloqueio | Risco | Mitigação |
|----------|-------|-----------|
| **Groq rate limit** | Alto (30 req/min free tier) | Usar SplitInBatches + Wait 15s (de Newsletter-IA-n8n). Fallback automático para Gemini quando exceder. |
| **Groq daily limit** | Médio (14.400 req/day) | Workflow 1 fará ~15 chamadas/dia → 450/mês → dentro do free tier. Workflow 2 fará ~5/semana |
| **Gemini rate limit** | Médio (60 req/min free tier) | Só usado como fallback, raramente será chamado |
| **NewsAPI free tier** | Alto (100 req/day) | Workflow 1 fará 2 chamadas/dia → 60/mês → dentro do limite |
| **Tavily free tier** | Alto (1000 req/month) | Workflow 1 fará ~30 chamadas/mês → dentro do limite |
| **LinkedIn token expiration** | Médio (60 dias) | OAuth2 refresh token no n8n gerencia automaticamente |
| **ngrok URL muda** | Médio (cada restart muda) | Usar `ngrok --domain` com subdomínio fixo (gratuito via ngrok.yml) |
| **Slack webhook timeout** | Baixo (3s limite) | Implementado resposta imediata + processamento async |
| **Google Sheets rate limit** | Baixo (60 req/min) | Workflows fazem no máximo 5 req/execução |
| **PostgreSQL connection pool** | Baixo | SQLAlchemy pool_size=5, max_overflow=10 |
| **Docker no Windows** | Médio (WSL2 necessário) | Documentar instalação do Docker Desktop + WSL2 |
| **Porta 5678 ocupada** | Baixo | Configurar porta alternativa via env |
| **RSS feed muda formato** | Médio | Parsing regex flexível + fallback silencioso (`onError: continueRegularOutput`) |

---

## Complemento I — Arquivos Específicos com Trechos para Copiar

Para cada seção do plano, aqui estão os trechos de código EXATOS a copiar de cada projeto:

### Do `repositorio_inteli_academy`

| O que copiar | Arquivo de origem | Linhas/Função |
|---|---|---|
| RSS dinâmicos (allainews_sources) | `Workflow 1 Coletor Diario.json` | Nó "Coleta fontes" (httpRequest para raw.githubusercontent.com) |
| Organização de links RSS | `Workflow 1 Coletor Diario.json` | Nó "Organiza links" (code com regex) |
| Normalização de dados RSS | `Workflow 1 Coletor Diario.json` | Nó "Normaliza os dados" (code com parsing XML + limpeza) |
| Pré-pontuação local | `Workflow 1 Coletor Diario.json` | Nó "Prepara os dados para a IA" (code com keywords + scores) |
| Alinhamento da saída (5 caminhos) | `Workflow 1 Coletor Diario.json` | Nó "Alinhamento da saida" (code com 5 tentativas de parse) |
| Agregação de dados do dia | `Workflow 1 Coletor Diario.json` | Nó "Agrega dados do dia" (code com estatísticas) |
| Filtragem semanal | `Workflow 2 Sintetizador Semanal.json` | Nó "Filtra e Prepara" (code) |
| Previsões preditivas | `Workflow 2 Sintetizador Semanal.json` | Prompt do nó "Sintetiza a Semana" (IA) |
| HTML relatório semanal | `Workflow 2 Sintetizador Semanal.json` | Nó "Monta HTML" (code) |
| Extração de pergunta Slack | `Workflow 3 Chatbot Slack.json` | Nó "Extrai pergunta do slack" (code) |
| Filtragem para chatbot | `Workflow 3 Chatbot Slack.json` | Nó "Filtra e prepara para a IA" (code) |
| Formata resposta Slack | `Workflow 3 Chatbot Slack.json` | Nó "Formata a resposta da IA" (code) |
| Error trigger + alerta | `Worflow de Erro.json` | Nós "Error Trigger" + "Alerta de Erro" |

### Do `InteliAcedemy`

| O que copiar | Arquivo de origem | Linhas/Função |
|---|---|---|
| Prompt Agente 1 - Triagem | `CaseIaAcademySemAPISminhas.json` | System message do nó "API Triagem e Categorizacao" |
| Prompt Agente 2 - Tendências | `CaseIaAcademySemAPISminhas.json` | System message do nó "API Analista de Tendencias" |
| Prompt Agente 3 - Oportunidades | `CaseIaAcademySemAPISminhas.json` | System message do nó "API Analista de Oportunidades" |
| Prompt Agente 4 - Redator-Chefe | `CaseIaAcademySemAPISminhas.json` | System message do nó "API Redator Chefe" |
| Code de formatação inicial | `CaseIaAcademySemAPISminhas.json` | Nó "Pegar as informacoes e deixar em bom formato" |
| Code de merge dos 3 agentes | `CaseIaAcademySemAPISminhas.json` | Nó "Code in JavaScript" (após Merge) |
| Code de extração de relatório | `CaseIaAcademySemAPISminhas.json` | Nó "Pegar Relatorio" |
| Code de conversão Markdown | `CaseIaAcademySemAPISminhas.json` | Nó "Produzir MarkDownDoRelatorio" (conversão para Buffer) |

### Do `inteliIA`

| O que copiar | Arquivo de origem | Linhas/Função |
|---|---|---|
| 9 RSS em paralelo | `AI Pulse.json` | Nós RSS Read 0-8 |
| Merge tree (6 merges) | `AI Pulse.json` | Nós Merge + Merge1-6 |
| Code - Padroniza e Resume | `AI Pulse.json` | stripHtml, extrai source, normaliza campos |
| Code - Remove Duplicados | `AI Pulse.json` | Dedup por URL + título normalizado (acentos) |
| Code - Filtro de Notícias | `AI Pulse.json` | Bloqueio de spam (podcast, webinar, sponsored) |
| Code - AI Token Control | `AI Pulse.json` | Ordenação + limite de 15 |
| Ranking POST (static data) | `AI Pulse Ranking Post.json` | Nó "Code in JavaScript" |
| Ranking GET (static data) | `AI Pulse Ranking Get (2).json` | Nó "Code in JavaScript" |
| Frontend - Gamificação | `index.html` | Sistema de pontos + níveis (localStorage) |
| Frontend - Ranking | `index.html` | Tabela de ranking com emails mascarados |
| Frontend - CSS dark mode | `index.html` | Design system completo (variáveis CSS, glassmorphism) |

### Do `Mymir`

| O que copiar | Arquivo de origem | Caminho |
|---|---|---|
| Docker Compose (base) | `Mymir/docker-compose.yml` | Serviços n8n + redis |
| Backend - main.py | `Mymir/backend/app/main.py` | FastAPI app setup |
| Backend - config.py | `Mymir/backend/app/core/config.py` | Pydantic Settings |
| Backend - database.py | `Mymir/backend/app/core/database.py` | SQLAlchemy engine |
| Backend - redis.py | `Mymir/backend/app/core/redis.py` | Redis client |
| Backend - auth middleware | `Mymir/backend/app/middleware/auth.py` | JWT validation |
| Backend - auth controller | `Mymir/backend/app/controllers/auth.py` | Signup/Login/Me |
| Backend - chat controller | `Mymir/backend/app/controllers/chat.py` | Chat endpoints |
| Backend - n8n service | `Mymir/backend/app/services/n8n.py` | Webhook client |
| Backend - requirements.txt | `Mymir/backend/requirements.txt` | Dependências Python |
| Backend - User model | `Mymir/backend/app/models/models.py` | SQLAlchemy User |
| Backend - Auth schemas | `Mymir/backend/app/schemas/auth.py` | Pydantic auth |
| Frontend - package.json | `Mymir/frontend/package.json` | Dependências React |
| Frontend - vite.config.ts | `Mymir/frontend/vite.config.ts` | Vite config |
| Frontend - tailwind.config.js | `Mymir/frontend/tailwind.config.js` | Tailwind config |
| Frontend - App.tsx | `Mymir/frontend/src/App.tsx` | Router + auth guard |
| Frontend - api.ts | `Mymir/frontend/src/services/api.ts` | Axios + JWT interceptor |
| Frontend - auth.store.ts | `Mymir/frontend/src/store/auth.store.ts` | Zustand auth state |
| Frontend - chat.store.ts | `Mymir/frontend/src/store/chat.store.ts` | Zustand chat state |
| Frontend - useChat.ts | `Mymir/frontend/src/hooks/useChat.ts` | Chat logic |
| Frontend - Login.tsx | `Mymir/frontend/src/pages/Login.tsx` | Login page |
| Frontend - Signup.tsx | `Mymir/frontend/src/pages/Signup.tsx` | Signup page |
| Frontend - Chat.tsx | `Mymir/frontend/src/pages/Chat.tsx` | Chat page |
| Frontend - Profile.tsx | `Mymir/frontend/src/pages/Profile.tsx` | Profile page |
| Frontend - Sidebar.tsx | `Mymir/frontend/src/components/layout/Sidebar.tsx` | Sidebar |
| Frontend - Logo.tsx | `Mymir/frontend/src/components/common/Logo.tsx` | Animated logo |
| Frontend - ChatInput.tsx | `Mymir/frontend/src/components/chat/ChatInput.tsx` | Chat input |
| Frontend - MessageBubble.tsx | `Mymir/frontend/src/components/chat/MessageBubble.tsx` | Message + PDF |
| Frontend - PDF export | `Mymir/frontend/src/utils/exportPdf.ts` | jsPDF generator |

### Do `Newsletter_n8n_IA`

| O que copiar | Nó no workflow |
|---|---|
| arXiv XML request | Nó "arXiv" (httpRequest com query params) |
| Tavily request | Nó "Tavily Search" (httpRequest POST com body) |
| Dev.to request | Nó "Dev.to" (httpRequest GET) |
| NewsAPI EN request | Nó "NewsAPI-Geral" (httpRequest GET) |
| NewsAPI PT-BR request | Nó "NewsAPI-PtBr" (httpRequest GET) |
| arXiv XML parsing | Nó "padroniza arXiv" (xml node) |
| Dev.to aggregation | Nó "arrumar itens dev.to" (aggregate node) |
| 5-input Merge | Nó "Juntar tudo" (merge v3, 5 inputs) |
| Code - Formatador de Dossiê | Nó "Formatar todas notícias" |
| Prompt Gemini para newsletter | System + User messages do nó "Message a model" |
| Telegram node | Nó "Telegram - mandar a newsletter" |

### Do `Newsletter-IA-n8n`

| O que copiar | Nó no workflow |
|---|---|
| Multi-LLM fallback setup | Nós "AI Agent" + "Groq Chat Model" + "Google Gemini Chat Model" |
| SplitInBatches (batch=5) | Nó "Loop Over Items" |
| Wait 15s throttling | Nó "Wait" |
| Edit Fields parsing | Nó "Edit Fields" |
| Filter RELEVANTE | Nó "Filter" |
| Code - Category Count | Nó "Code in JavaScript" |
| Prompt classificação STATUS\|CATEGORIA | System message do nó "AI Agent" |
| 9 categorias | System message do nó "AI Agent" |
| Fallback prompt | System + User messages do nó "Basic LLM Chain" |

### Do `newsletterSemanalIA`

| O que copiar | Nó no workflow |
|---|---|
| GitHub Trending | Nó "Buscar GitHub Trending AI" (httpRequest GitHub API) |
| GitHub data extraction | Nó "Extrair dados GitHub" (code) |
| TechCrunch RSS com Pollinations | Nó "Filtrar Artigos da Semana" (code com fallback Pollinations) |
| The Verge RSS com filtro de keywords | Nó "Extrair Dados The Verge" (code) |
| LLM Categorização + Resumo | Nó "Categorizar e resumir com IA" (chainLlm) |
| Parse resposta IA | Nó "Parsear resposta da IA" (code com fallback) |
| Agrupar por categoria + GitHub | Nó "Agrupar por categoria" (code) |
| Gerar HTML Newsletter | Nó "Gerar HTML da Newsletter" (code com template beige) |
| LinkedIn - Juntar artigos | Nó "Juntar Artigos" (code) |
| LinkedIn - IA copywriter | Nó "IA copywritter" (chainLlm com prompt LinkedIn) |
| LinkedIn - Wait webhook approval | Nó "Wait" (webhook mode) |
| LinkedIn - Formatar post | Nó "Formatar Post LinkedIn" (code com payload API) |
| LinkedIn - POST API | Nó "Postar no Linkedin" (httpRequest para v2/ugcPosts) |

### Do `PS-Inteli-Academy`

| O que copiar | Nó no workflow |
|---|---|
| Prompt LLM com saída JSON estrita | System message do nó "Message a model" |
| Code parse JSON | Nó "Formato Json Output" |
| Airtable insert | Nó "Salva no Airtable" |

### Do `psIa`

| O que copiar | Arquivo de origem | Caminho/Função |
|---|---|---|
| Subscription dedup | Workflow | Nós "Verificar Se Email Existe" + "Email Ja Existe?" |
| Google Sheets subscriber write | Workflow | Nós "Preparar Dados para Planilha" + "Salvar Email na Planilha" |
| Structured output parser | Workflow | Nó "estruturar json para o front" (outputParserStructured) |
| Frontend - AiNewsService | `src/services/ai-news.service.ts` | Normalização multi-formato |
| Frontend - AiNews model | `src/models/ai-news.model.ts` | Interface AiNewsItem |
| Frontend - Home page | `src/app/home/home.page.ts` | News list + subscription form |
| Frontend - Mock data | `src/assets/ai-news-data.json` | 15 notícias mock |
| Testes - Service | `src/services/ai-news.service.spec.ts` | Testes de filtro/subscription |
| Testes - Page | `src/app/home/home.page.spec.ts` | Testes de init/erro/email |

### Do `Case_Inteli_Academy`

| O que copiar | Arquivo | Função |
|---|---|---|
| Supabase integration | `src/app.js` | Auth + banco |
| Login system | `index.html` | Formulário + validação |
| Dashboard layout | `index.html` | Feed de notícias |
| Favorites system | `index.html` + `src/app.js` | Favoritar/disfavoritar |
| Download HTML | `index.html` | Exportar relatório |
