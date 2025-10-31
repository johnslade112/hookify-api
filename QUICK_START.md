# Guia de Início Rápido - Hookify API

Este guia ajudará você a começar a usar a Hookify API em poucos minutos.

## 1. Registrar um Usuário

Primeiro, crie uma conta na API:

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seu@email.com",
    "password": "suasenha123",
    "full_name": "Seu Nome"
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "email": "seu@email.com",
  "full_name": "Seu Nome",
  "is_active": true,
  "created_at": "2025-10-31T12:00:00"
}
```

## 2. Fazer Login

Obtenha seu token de acesso:

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seu@email.com",
    "password": "suasenha123"
  }'
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Guarde o `access_token` - você vai usá-lo em todas as requisições.

## 3. Gerar Hooks com IA

Agora você pode gerar hooks virais:

```bash
curl -X POST "http://localhost:8000/v2/generate/hook" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "niche": "fitness",
    "topic": "perder barriga",
    "tone": "motivacional",
    "platform": "tiktok",
    "variants": 3
  }'
```

**Resposta:**
```json
{
  "hooks": [
    "Você é capaz. Ninguém te conta isso sobre perder barriga…",
    "Você é capaz. Pare de errar em perder barriga — faça isso 👇",
    "Você é capaz. Se eu começasse do zero em fitness hoje, faria isso:"
  ],
  "quota_remaining": 9
}
```

## 4. Gerar Conteúdo Completo

Para gerar hooks, legendas e hashtags de uma vez:

```bash
curl -X POST "http://localhost:8000/v2/generate/complete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "niche": "finanças",
    "topic": "investir em ações",
    "tone": "educativo",
    "platform": "reels",
    "call_to_action": "Salva esse post!",
    "analyze_emotion": true
  }'
```

**Resposta:**
```json
{
  "hooks": ["...", "...", "..."],
  "captions": ["...", "...", "..."],
  "hashtags": ["#financas", "#investimentos", "..."],
  "emotion_analysis": {
    "primary_emotion": "confiança",
    "confidence": 0.85,
    "emotions_breakdown": {"confiança": 0.7, "curiosidade": 0.3},
    "suggestions": ["Adicione um senso de urgência para aumentar engajamento"]
  },
  "quota_remaining": 8
}
```

## 5. Verificar Seu Plano e Uso

```bash
curl -X GET "http://localhost:8000/subscription/usage" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

**Resposta:**
```json
{
  "current_plan": "FREE",
  "monthly_quota": 10,
  "used_quota": 2,
  "remaining_quota": 8,
  "generations_this_month": 2,
  "most_used_type": "complete"
}
```

## 6. Fazer Upgrade do Plano

```bash
curl -X POST "http://localhost:8000/subscription/upgrade" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "plan_type": "BASIC"
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "plan_type": "BASIC",
  "monthly_quota": 100,
  "used_quota": 2,
  "remaining_quota": 98,
  "is_active": true,
  "start_date": "2025-10-31T12:00:00",
  "end_date": null
}
```

## Próximos Passos

- Explore a documentação completa em `/docs`
- Leia o [GUIA_DE_MONETIZACAO.md](./GUIA_DE_MONETIZACAO.md) para integrar pagamentos
- Consulte [ARCHITECTURE.md](./ARCHITECTURE.md) para entender a estrutura do projeto

## Suporte

Para dúvidas ou problemas, abra uma issue no GitHub ou entre em contato.
