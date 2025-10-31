/**
 * Exemplo de integração com a Hookify API em JavaScript/Node.js
 * Demonstra como usar a API em aplicações web e Node.js
 */

const axios = require('axios');

class HookifyClient {
  constructor(baseUrl = 'http://localhost:8000', apiKey = null, token = null) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
    this.token = token;
    this.client = axios.create({ baseURL: baseUrl });
  }

  _getHeaders() {
    if (this.token) {
      return { Authorization: `Bearer ${this.token}` };
    } else if (this.apiKey) {
      return { 'X-API-Key': this.apiKey };
    }
    return {};
  }

  async register(email, password, fullName = null) {
    const response = await this.client.post('/auth/register', {
      email,
      password,
      full_name: fullName
    });
    return response.data;
  }

  async login(email, password) {
    const response = await this.client.post('/auth/login', {
      email,
      password
    });
    this.token = response.data.access_token;
    return this.token;
  }

  async generateHooks({ niche, topic, tone = 'direto', platform = 'tiktok', variants = 3 }) {
    const response = await this.client.post(
      '/v2/generate/hook',
      { niche, topic, tone, platform, variants },
      { headers: this._getHeaders() }
    );
    return response.data;
  }

  async generateCaptions({
    niche,
    topic,
    tone = 'direto',
    productName = null,
    callToAction = null,
    maxLength = 150,
    variants = 3
  }) {
    const response = await this.client.post(
      '/v2/generate/caption',
      {
        niche,
        topic,
        tone,
        product_name: productName,
        call_to_action: callToAction,
        max_length: maxLength,
        variants
      },
      { headers: this._getHeaders() }
    );
    return response.data;
  }

  async generateHashtags({
    niche,
    topic,
    platform = 'tiktok',
    count = 10,
    includeTrending = true
  }) {
    const response = await this.client.post(
      '/v2/generate/hashtags',
      {
        niche,
        topic,
        platform,
        count,
        include_trending: includeTrending
      },
      { headers: this._getHeaders() }
    );
    return response.data;
  }

  async analyzeEmotion(text, context = null) {
    const response = await this.client.post(
      '/v2/analyze/emotion',
      { text, context },
      { headers: this._getHeaders() }
    );
    return response.data;
  }

  async generateComplete({
    niche,
    topic,
    tone = 'direto',
    platform = 'tiktok',
    productName = null,
    callToAction = null,
    analyzeEmotion = false
  }) {
    const response = await this.client.post(
      '/v2/generate/complete',
      {
        niche,
        topic,
        tone,
        platform,
        product_name: productName,
        call_to_action: callToAction,
        analyze_emotion: analyzeEmotion
      },
      { headers: this._getHeaders() }
    );
    return response.data;
  }

  async getSubscription() {
    const response = await this.client.get('/subscription', {
      headers: this._getHeaders()
    });
    return response.data;
  }

  async getUsage() {
    const response = await this.client.get('/subscription/usage', {
      headers: this._getHeaders()
    });
    return response.data;
  }
}

// ==================== EXEMPLO DE USO ====================

async function main() {
  const client = new HookifyClient('http://localhost:8000');

  try {
    // 1. Fazer login
    console.log('🔐 Fazendo login...');
    const token = await client.login('teste@hookify.com', 'senha12345');
    console.log(`✓ Token obtido: ${token.substring(0, 50)}...\n`);

    // 2. Gerar conteúdo completo
    console.log('🚀 Gerando conteúdo completo...');
    const result = await client.generateComplete({
      niche: 'marketing digital',
      topic: 'como vender no Instagram',
      tone: 'educativo',
      platform: 'reels',
      callToAction: 'Comenta "QUERO" para receber o guia completo!',
      analyzeEmotion: true
    });

    console.log('\n📌 HOOKS GERADOS:');
    result.hooks.forEach((hook, i) => {
      console.log(`  ${i + 1}. ${hook}`);
    });

    console.log('\n📝 LEGENDAS GERADAS:');
    result.captions.forEach((caption, i) => {
      console.log(`  ${i + 1}. ${caption.substring(0, 100)}...`);
    });

    console.log('\n#️⃣ HASHTAGS GERADAS:');
    console.log(`  ${result.hashtags.join(' ')}`);

    if (result.emotion_analysis) {
      const emotion = result.emotion_analysis;
      console.log('\n😊 ANÁLISE DE EMOÇÃO:');
      console.log(`  Emoção predominante: ${emotion.primary_emotion}`);
      console.log(`  Confiança: ${(emotion.confidence * 100).toFixed(1)}%`);
      console.log(`  Sugestões: ${emotion.suggestions[0]}`);
    }

    console.log(`\n💡 Quota restante: ${result.quota_remaining}`);

    // 3. Verificar uso
    console.log('\n📊 Verificando estatísticas de uso...');
    const usage = await client.getUsage();
    console.log(`  Plano: ${usage.current_plan}`);
    console.log(`  Usado: ${usage.used_quota}/${usage.monthly_quota}`);
    console.log(`  Gerações este mês: ${usage.generations_this_month}`);

  } catch (error) {
    console.error('❌ Erro:', error.response?.data || error.message);
  }
}

// Executar se for o arquivo principal
if (require.main === module) {
  main();
}

module.exports = HookifyClient;
