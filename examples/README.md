# Exemplos de Integração - Hookify API

Esta pasta contém exemplos práticos de como integrar a Hookify API em diferentes linguagens de programação.

## Python

O arquivo `python_integration.py` demonstra como criar um cliente Python para a API.

### Instalação

```bash
pip install requests
```

### Uso

```python
from python_integration import HookifyClient

# Inicializar cliente
client = HookifyClient(base_url="http://localhost:8000")

# Fazer login
token = client.login("seu@email.com", "suasenha")

# Gerar conteúdo completo
result = client.generate_complete(
    niche="fitness",
    topic="perder peso",
    tone="motivacional",
    platform="tiktok",
    analyze_emotion=True
)

print(result['hooks'])
print(result['captions'])
print(result['hashtags'])
```

## JavaScript/Node.js

O arquivo `javascript_integration.js` demonstra como usar a API em aplicações Node.js.

### Instalação

```bash
npm install axios
```

### Uso

```javascript
const HookifyClient = require('./javascript_integration');

const client = new HookifyClient('http://localhost:8000');

// Fazer login
const token = await client.login('seu@email.com', 'suasenha');

// Gerar hooks
const result = await client.generateHooks({
  niche: 'marketing digital',
  topic: 'tráfego pago',
  tone: 'educativo',
  variants: 5
});

console.log(result.hooks);
```

## Outros Exemplos

Você pode adaptar esses exemplos para outras linguagens seguindo a mesma lógica:

1. Fazer autenticação (login ou API key)
2. Incluir o token/key nos headers das requisições
3. Fazer chamadas POST/GET para os endpoints desejados
4. Processar as respostas JSON

## Documentação Completa

Para ver todos os endpoints disponíveis e seus parâmetros, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
