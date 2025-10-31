# Hookify API v2.0

API com Inteligência Artificial para geração de hooks, legendas, hashtags e análise de emoção para vídeos. Ideal para influenciadores, agências e criadores de conteúdo que buscam otimizar sua produção e engajamento.

## Visão Geral

A Hookify API evoluiu de um simples gerador de templates para uma plataforma completa de criação de conteúdo com IA. A versão 2.0 introduz um sistema de usuários, planos de assinatura, geração de conteúdo via `gpt-4.1-mini` e análise de emoção com `gemini-2.5-flash`.

## Funcionalidades Principais

- **Geração com IA**: Crie hooks, legendas e hashtags de alta qualidade, adaptados ao seu nicho e tom.
- **Análise de Emoção**: Entenda o impacto emocional do seu conteúdo antes de postar.
- **Sistema de Planos**: Modelo freemium com múltiplos tiers (Free, Basic, Pro, Premium) para monetização.
- **Autenticação Segura**: Suporte para JWT (usuários de painel) e API Keys (integrações diretas).
- **Gestão de Quota**: Rate limiting automático baseado no plano do usuário.
- **Histórico de Gerações**: Acompanhe todo o conteúdo gerado pela plataforma.

## Arquitetura

Para uma visão detalhada da arquitetura, consulte o arquivo [ARCHITECTURE.md](./ARCHITECTURE.md).

## Como Começar

### Pré-requisitos

- Python 3.11+
- Docker (opcional, para deploy)
- Chave da API da OpenAI (configurada como variável de ambiente `OPENAI_API_KEY`)

### Instalação Local

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/johnslade112/hookify-api.git
   cd hookify-api/hookify-api
   ```

2. **Crie um ambiente virtual e instale as dependências:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente:**
   Crie um arquivo `.env` a partir do `.env.example` e preencha os valores:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas chaves
   ```

4. **Inicie o servidor:**
   ```bash
   uvicorn app:app --reload
   ```

5. **Acesse a documentação interativa:**
   - **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Deploy com Docker

O projeto inclui um `Dockerfile` otimizado para produção.

1. **Construa a imagem:**
   ```bash
   docker build -t hookify-api:latest .
   ```

2. **Execute o container:**
   ```bash
   docker run -d -p 8000:8000 --env-file .env hookify-api:latest
   ```

## Endpoints da API (v2)

A documentação completa e interativa está disponível em `/docs`.

- `POST /auth/register`: Cria um novo usuário.
- `POST /auth/login`: Autentica e retorna um token JWT.
- `GET /auth/me`: Retorna informações do usuário logado.
- `POST /v2/generate/hook`: Gera hooks com IA.
- `POST /v2/generate/caption`: Gera legendas com IA.
- `POST /v2/generate/hashtags`: Gera hashtags com IA.
- `POST /v2/analyze/emotion`: Analisa a emoção de um texto.
- `POST /v2/generate/complete`: Gera todo o conteúdo (hooks, legendas, hashtags) em uma única chamada.
- `GET /subscription`: Consulta o plano e o uso da quota.
- `POST /subscription/upgrade`: Altera o plano do usuário.

## Monetização

Para detalhes sobre como configurar e gerenciar os planos de assinatura, consulte o [GUIA_DE_MONETIZACAO.md](./GUIA_DE_MONETIZACAO.md).
