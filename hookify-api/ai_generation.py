"""
Módulo de geração de conteúdo usando IA (OpenAI API)
Suporta: hooks, legendas, hashtags e análise de emoção
"""

from openai import OpenAI
from typing import List, Dict, Tuple
import json
import os

# Cliente OpenAI já configurado via variáveis de ambiente
client = OpenAI()

# Modelo padrão (pode ser alterado via env)
DEFAULT_MODEL = os.getenv("AI_MODEL", "gpt-4.1-mini")

# ==================== PROMPTS ESPECIALIZADOS ====================

HOOK_SYSTEM_PROMPT = """Você é um especialista em criar hooks virais para vídeos curtos (TikTok, Reels, Shorts).
Seu objetivo é criar ganchos que:
- Capturam atenção nos primeiros 3 segundos
- Geram curiosidade e vontade de assistir até o fim
- São diretos, impactantes e relevantes para o nicho
- Usam gatilhos mentais (escassez, urgência, exclusividade, prova social)
- Têm entre 5-15 palavras

Retorne APENAS um array JSON com os hooks, sem explicações."""

CAPTION_SYSTEM_PROMPT = """Você é um copywriter especializado em legendas para vídeos de redes sociais.
Suas legendas devem:
- Complementar o vídeo e reforçar a mensagem
- Incluir call-to-action quando solicitado
- Ser persuasivas e engajadoras
- Usar linguagem natural e conversacional
- Ter entre 50-150 palavras (ajustável)

Retorne APENAS um array JSON com as legendas, sem explicações."""

HASHTAG_SYSTEM_PROMPT = """Você é um especialista em hashtags para redes sociais.
Suas hashtags devem:
- Ser relevantes para o nicho e tópico
- Misturar hashtags populares e de nicho
- Incluir hashtags em português (quando aplicável)
- Evitar hashtags genéricas demais
- Priorizar hashtags com potencial de alcance

Retorne APENAS um array JSON com as hashtags (com #), sem explicações."""

EMOTION_SYSTEM_PROMPT = """Você é um analista de emoções especializado em conteúdo de vídeo.
Analise o texto/descrição e identifique:
- Emoção predominante (alegria, surpresa, medo, raiva, tristeza, neutro)
- Nível de confiança da análise (0-1)
- Distribuição de todas as emoções detectadas
- Sugestões para aumentar engajamento emocional

Retorne APENAS um JSON com: primary_emotion, confidence, emotions_breakdown (dict), suggestions (array)."""

# ==================== FUNÇÕES DE GERAÇÃO ====================

def generate_hooks(
    niche: str,
    topic: str,
    tone: str,
    platform: str,
    variants: int = 3
) -> List[str]:
    """Gera hooks virais usando IA"""
    
    tone_map = {
        "direto": "direto e objetivo",
        "motivacional": "inspirador e motivacional",
        "educativo": "educativo e informativo",
        "storytelling": "narrativo e envolvente"
    }
    
    user_prompt = f"""Crie {variants} hooks virais para um vídeo de {platform} sobre:
Nicho: {niche}
Tópico: {topic}
Tom: {tone_map.get(tone, tone)}

Retorne um array JSON: ["hook 1", "hook 2", ...]"""

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": HOOK_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.9,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        # Tenta parsear JSON
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        hooks = json.loads(content)
        return hooks if isinstance(hooks, list) else [content]
    
    except Exception as e:
        print(f"Erro ao gerar hooks: {e}")
        # Fallback para templates
        return [
            f"Ninguém te conta isso sobre {topic}…",
            f"Pare de errar em {topic} — faça isso 👇",
            f"Se eu começasse do zero em {niche} hoje, faria isso:"
        ][:variants]

def generate_captions(
    niche: str,
    topic: str,
    tone: str,
    product_name: str = None,
    call_to_action: str = None,
    max_length: int = 150,
    variants: int = 3
) -> List[str]:
    """Gera legendas persuasivas usando IA"""
    
    user_prompt = f"""Crie {variants} legendas para um vídeo sobre:
Nicho: {niche}
Tópico: {topic}
Tom: {tone}
{f'Produto: {product_name}' if product_name else ''}
{f'CTA: {call_to_action}' if call_to_action else ''}
Tamanho máximo: {max_length} palavras

Retorne um array JSON: ["legenda 1", "legenda 2", ...]"""

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": CAPTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=800
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        captions = json.loads(content)
        return captions if isinstance(captions, list) else [content]
    
    except Exception as e:
        print(f"Erro ao gerar legendas: {e}")
        return [
            f"Aprenda sobre {topic} de forma simples e prática. {call_to_action or 'Salva esse vídeo!'}",
            f"Se você quer resultados em {niche}, precisa saber isso. {call_to_action or 'Comenta aqui embaixo!'}",
            f"O segredo para {topic} que ninguém te conta. {call_to_action or 'Compartilha com quem precisa!'}"
        ][:variants]

def generate_hashtags(
    niche: str,
    topic: str,
    platform: str,
    count: int = 10,
    include_trending: bool = True
) -> List[str]:
    """Gera hashtags relevantes usando IA"""
    
    user_prompt = f"""Crie {count} hashtags para um vídeo de {platform} sobre:
Nicho: {niche}
Tópico: {topic}
{'Incluir hashtags em alta/trending' if include_trending else 'Focar em hashtags de nicho'}

Retorne um array JSON: ["#hashtag1", "#hashtag2", ...]"""

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": HASHTAG_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        hashtags = json.loads(content)
        # Garante que todas tenham #
        hashtags = [h if h.startswith("#") else f"#{h}" for h in hashtags]
        return hashtags if isinstance(hashtags, list) else [content]
    
    except Exception as e:
        print(f"Erro ao gerar hashtags: {e}")
        niche_tag = niche.replace(" ", "").lower()
        topic_tag = topic.replace(" ", "").lower()
        return [
            f"#{niche_tag}", f"#{topic_tag}", "#viral", "#fyp", "#foryou",
            "#dicas", "#aprendizado", "#conteudo", "#trending", "#explorepage"
        ][:count]

def analyze_emotion(text: str, context: str = None) -> Dict:
    """Analisa a emoção predominante no texto usando IA"""
    
    user_prompt = f"""Analise a emoção predominante neste texto/descrição de vídeo:

Texto: {text}
{f'Contexto: {context}' if context else ''}

Retorne um JSON com:
{{
  "primary_emotion": "alegria|surpresa|medo|raiva|tristeza|neutro",
  "confidence": 0.0-1.0,
  "emotions_breakdown": {{"alegria": 0.5, "surpresa": 0.3, ...}},
  "suggestions": ["sugestão 1", "sugestão 2", ...]
}}"""

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": EMOTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=600
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        result = json.loads(content)
        return result
    
    except Exception as e:
        print(f"Erro ao analisar emoção: {e}")
        return {
            "primary_emotion": "neutro",
            "confidence": 0.5,
            "emotions_breakdown": {"neutro": 1.0},
            "suggestions": ["Adicione mais elementos emocionais ao conteúdo"]
        }

def generate_complete(
    niche: str,
    topic: str,
    tone: str,
    platform: str,
    product_name: str = None,
    call_to_action: str = None,
    analyze_emotion_flag: bool = False
) -> Tuple[List[str], List[str], List[str], Dict]:
    """Gera hooks, legendas, hashtags e opcionalmente analisa emoção"""
    
    hooks = generate_hooks(niche, topic, tone, platform, variants=3)
    captions = generate_captions(niche, topic, tone, product_name, call_to_action, variants=3)
    hashtags = generate_hashtags(niche, topic, platform, count=10)
    
    emotion_result = None
    if analyze_emotion_flag:
        # Analisa a emoção do primeiro hook + primeira legenda
        combined_text = f"{hooks[0]} {captions[0]}"
        emotion_result = analyze_emotion(combined_text, context=f"Vídeo sobre {topic} em {niche}")
    
    return hooks, captions, hashtags, emotion_result
