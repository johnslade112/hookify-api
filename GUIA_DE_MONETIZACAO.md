# Guia de Monetização da Hookify API

Este guia detalha a estratégia de monetização da Hookify API, o sistema de planos, e como integrar um gateway de pagamento para gerenciar assinaturas.

## 1. Planos de Assinatura

A API opera em um modelo freemium, projetado para atrair usuários com um plano gratuito funcional e incentivá-los a fazer upgrade para planos pagos com mais recursos e limites mais altos.

### Tabela de Planos

| Plano | Preço (R$/mês) | Gerações/mês | Recursos Principais |
|---|---|---|---|
| **FREE** | R$ 0 | 10 | Geração de hooks e legendas (base) |
| **BASIC** | R$ 29 | 100 | + Geração de hashtags e análise de emoção |
| **PRO** | R$ 79 | 500 | + Múltiplas variantes por geração, suporte prioritário |
| **PREMIUM** | R$ 199 | 2.000 | + Acesso ilimitado à API, suporte dedicado |

### Justificativa dos Planos

- **FREE**: Permite que novos usuários testem a funcionalidade principal sem compromisso, servindo como uma ferramenta de aquisição.
- **BASIC**: Ideal para criadores de conteúdo individuais que precisam de um volume moderado de gerações e acesso a todas as ferramentas de IA.
- **PRO**: Voltado para freelancers, agências pequenas e influenciadores que gerenciam múltiplas contas e necessitam de maior volume e flexibilidade.
- **PREMIUM**: Desenhado para agências de marketing, grandes influenciadores e empresas que precisam de integração via API em larga escala e suporte personalizado.

## 2. Integração com Gateway de Pagamento (Stripe)

Recomendamos o uso do **Stripe** devido à sua documentação robusta, APIs amigáveis para desenvolvedores e suporte global. A integração seguirá os seguintes passos:

### Passo 1: Configurar Produtos e Preços no Stripe

1.  **Crie os Produtos**: No painel do Stripe, crie quatro produtos: `Hookify FREE`, `Hookify BASIC`, `Hookify PRO` e `Hookify PREMIUM`.
2.  **Defina os Preços**: Para cada produto, crie um preço recorrente (mensal) correspondente aos valores da tabela acima. Guarde os IDs dos preços (ex: `price_...`).

### Passo 2: Implementar o Checkout

Crie um endpoint no backend (ex: `/subscription/create-checkout-session`) que, ao ser chamado, redireciona o usuário para uma página de checkout do Stripe.

```python
# Exemplo de endpoint para criar a sessão de checkout

import stripe

stripe.api_key = 'sk_test_...' # Sua chave secreta do Stripe

@app.post("/subscription/create-checkout-session")
def create_checkout_session(request: UpgradeRequest, user: User = Depends(get_current_user)):
    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=user.id,
            success_url="https://your-frontend.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://your-frontend.com/cancel",
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": get_stripe_price_id(request.plan_type), # Função que mapeia seu plano ao ID do Stripe
                    "quantity": 1,
                }
            ],
        )
        return {"redirect_url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Passo 3: Gerenciar o Ciclo de Vida com Webhooks

Webhooks são essenciais para manter seu banco de dados sincronizado com o status das assinaturas no Stripe.

Crie um endpoint público (ex: `/webhooks/stripe`) para receber eventos do Stripe.

**Eventos importantes a serem tratados:**

-   `checkout.session.completed`: Ocorre quando um usuário completa o pagamento. Use este evento para ativar a assinatura no seu banco de dados. Extraia o `client_reference_id` para identificar o usuário.
-   `invoice.payment_succeeded`: Ocorre a cada renovação mensal bem-sucedida. Use para garantir que a assinatura continue ativa e para resetar a quota de geração do usuário.
-   `customer.subscription.deleted`: Ocorre quando uma assinatura é cancelada. Use para fazer o downgrade do usuário para o plano FREE no final do ciclo de billing.
-   `invoice.payment_failed`: Ocorre quando a renovação falha. Você pode notificar o usuário e, após algumas tentativas, cancelar a assinatura.

```python
# Exemplo de endpoint de webhook

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = 'whsec_...' # Seu segredo de webhook

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Tratar o evento
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id')
        # Ative a assinatura para o user_id

    elif event['type'] == 'invoice.payment_succeeded':
        # Resete a quota do usuário

    elif event['type'] == 'customer.subscription.deleted':
        # Faça o downgrade do plano do usuário

    return {"status": "success"}
```

## 3. Experiência do Usuário (Painel de Controle)

É crucial que o usuário tenha uma área em seu painel de controle para gerenciar sua assinatura.

**Funcionalidades recomendadas:**

-   **Visualização do Plano Atual**: Mostrar o plano atual, quota usada/total e a data da próxima renovação.
-   **Opções de Upgrade/Downgrade**: Botões que iniciam o fluxo de checkout para alterar o plano.
-   **Gerenciamento de Pagamento**: Um link para o portal do cliente do Stripe, onde o usuário pode atualizar seu cartão de crédito, ver faturas e cancelar a assinatura.

```python
# Endpoint para criar um link para o portal do cliente Stripe

@app.post("/subscription/create-portal-session")
def create_portal_session(user: User = Depends(get_current_user)):
    # Obtenha o stripe_customer_id do seu banco de dados (armazenado após o primeiro pagamento)
    stripe_customer_id = get_stripe_customer_id(user.id)

    portal_session = stripe.billing_portal.Session.create(
        customer=stripe_customer_id,
        return_url="https://your-frontend.com/account",
    )
    return {"redirect_url": portal_session.url}
```

## Conclusão

Ao seguir este guia, você terá um sistema de monetização robusto e escalável para a Hookify API. A chave para o sucesso é uma integração cuidadosa com o gateway de pagamento e uma experiência de usuário clara e transparente no gerenciamento de assinaturas.
