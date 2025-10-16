# Hookify API

Gera **hooks, legendas e hashtags** para TikTok/Reels/Shorts e oferece **encurtador com UTM + métricas**.

## Endpoints
- `GET /templates`
- `POST /generate`
- `POST /links/shorten`
- `GET /r/{code}`
- `GET /analytics/links`

### Auth
Envie o header: `X-API-Key: <sua-chave>`

### Rodar localmente
```bash
pip install -r requirements.txt
$env:API_KEY="minha-chave"  # PowerShell
uvicorn app:app --reload
```

### Testes (cURL)
```bash
curl -H "X-API-Key: minha-chave" http://localhost:8000/templates

curl -X POST -H "Content-Type: application/json"  -H "X-API-Key: minha-chave"  -d '{"niche":"ganhar dinheiro com IA","platform":"tiktok","tone":"direto","language":"pt","product_name":"Mentoria IA","problems":["falta de clareza"],"call_to_action":"Link na bio ⬆️","variants":3,"hashtags_count":5}'  http://localhost:8000/generate
```
