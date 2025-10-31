# Arquitetura Hookify API - Sistema Completo

## Análise do Código Existente

O repositório atual possui uma base funcional com:

- **Framework**: FastAPI com SQLAlchemy
- **Funcionalidades atuais**:
  - Geração de hooks, legendas e hashtags (templates estáticos)
  - Encurtador de links com UTM tracking
  - Analytics básico de cliques
  - Autenticação via API Key simples
  
- **Limitações identificadas**:
  - Geração baseada em templates aleatórios, não usa IA real
  - Sem sistema de usuários e planos
  - Sem análise de emoção
  - Sem rate limiting por plano
  - Sem integração com modelos de linguagem
  - Sem sistema de pagamento/monetização

## Nova Arquitetura Proposta

### 1. Camada de Dados (Database Layer)

**Modelos a serem criados:**

- `User`: usuários da plataforma
  - id, email, password_hash, created_at, is_active
  
- `Subscription`: assinaturas e planos
  - id, user_id, plan_type (FREE, BASIC, PRO, PREMIUM)
  - start_date, end_date, is_active
  - monthly_quota, used_quota
  
- `Generation`: histórico de gerações
  - id, user_id, type (hook/caption/hashtag/emotion)
  - input_data, output_data, created_at
  
- `ApiKey`: chaves de API por usuário
  - id, user_id, key, name, created_at, last_used

### 2. Sistema de Planos Mensais

| Plano | Preço/mês | Gerações/mês | Features |
|-------|-----------|--------------|----------|
| **FREE** | R$ 0 | 10 | Hooks + Legendas básicas |
| **BASIC** | R$ 29 | 100 | + Hashtags + Análise de emoção |
| **PRO** | R$ 79 | 500 | + Múltiplas variantes + Prioridade |
| **PREMIUM** | R$ 199 | 2000 | + API ilimitada + Suporte dedicado |

### 3. Integração com IA

**Modelos disponíveis (via OpenAI API):**
- `gpt-4.1-mini`: geração de hooks, legendas e hashtags
- `gemini-2.5-flash`: análise de emoção e sentimento

**Prompts especializados:**
- Hook Generator: criar ganchos virais baseados em nicho e tom
- Caption Writer: legendas persuasivas com CTA
- Hashtag Optimizer: hashtags relevantes e trending
- Emotion Analyzer: detectar emoção predominante (alegria, surpresa, medo, raiva, tristeza, neutro)

### 4. Endpoints da API

**Autenticação:**
- `POST /auth/register`: criar conta
- `POST /auth/login`: login (retorna JWT)
- `POST /auth/refresh`: renovar token
- `GET /auth/me`: dados do usuário

**Geração de Conteúdo:**
- `POST /v2/generate/hook`: gerar hooks com IA
- `POST /v2/generate/caption`: gerar legendas com IA
- `POST /v2/generate/hashtags`: gerar hashtags com IA
- `POST /v2/generate/complete`: gerar tudo de uma vez
- `POST /v2/analyze/emotion`: analisar emoção do texto/vídeo

**Gestão de Conta:**
- `GET /subscription/current`: plano atual
- `POST /subscription/upgrade`: upgrade de plano
- `GET /subscription/usage`: uso mensal
- `GET /history`: histórico de gerações

**Admin:**
- `GET /admin/users`: listar usuários
- `GET /admin/stats`: estatísticas da plataforma

### 5. Rate Limiting e Quotas

- Middleware customizado para verificar quota mensal
- Redis para cache de contadores (opcional, usar SQLite primeiro)
- Resposta 429 quando quota excedida
- Header `X-Quota-Remaining` em todas as respostas

### 6. Sistema de Pagamento (Futuro)

- Integração com Stripe ou Mercado Pago
- Webhooks para renovação automática
- Gerenciamento de ciclo de vida da assinatura

## Stack Tecnológica Final

- **Backend**: FastAPI + Python 3.11
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **ORM**: SQLAlchemy 2.0
- **Auth**: JWT (python-jose + passlib)
- **IA**: OpenAI SDK (modelos pré-configurados)
- **Deploy**: Docker + Render/Railway
- **Docs**: Swagger UI automático (FastAPI)

## Próximos Passos

1. ✅ Análise do código existente
2. ⏳ Criar novos modelos de banco de dados
3. ⏳ Implementar sistema de autenticação JWT
4. ⏳ Integrar OpenAI para geração real com IA
5. ⏳ Criar endpoints v2 com análise de emoção
6. ⏳ Implementar rate limiting por plano
7. ⏳ Documentar API e criar guia de monetização
