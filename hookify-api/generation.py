import random

HOOK_TEMPLATES_PT = [
    "Ninguém te conta isso sobre {niche}…",
    "Pare de {pain} — faça isso em {timeframe} 👇",
    "Se eu começasse do zero em {niche} hoje, faria isso:",
    "Erro que te impede de {benefit} (e a correção em 10s)",
    "3 passos simples para {benefit} sem {objection}"
]

CAPTION_TEMPLATES_PT = [
    "Esse é o método que eu usaria para {benefit} sem {objection}. Salva esse vídeo e aplica hoje.",
    "Aprendi do jeito difícil. Aqui vai o atalho para {benefit}. Comenta 'quero' que te mando o checklist.",
    "{product} + {niche}: o combo que me fez sair de {pain} para {benefit}. Você pode copiar.",
    "Se você luta com {pain}, tenta isso por 7 dias. Depois me conta nos comentários."
]

HASHTAGS_PT = [
    "#{niche}", "#dicas", "#aprendizado", "#passoapasso", "#resultados",
    "#marketingdigital", "#negocios", "#foco", "#metas", "#conteudodevalor"
]

TONE_PREFIX = {
    "direto": "",
    "motivacional": "Você é capaz. ",
    "educativo": "Anota aí: ",
    "storytelling": "Deixa eu te contar: "
}

def _pick(lst, k):
    return random.sample(lst, min(k, len(lst)))

def _fmt(text, vars):
    for k, v in vars.items():
        text = text.replace("{"+k+"}", v)
    return text

def generate_pt(niche, tone, product, problems, cta, variants, hashtags_count):
    pain = (problems or ["não ter resultado"])[0]
    mapping = {
        "niche": niche,
        "pain": pain,
        "benefit": f"evoluir em {niche}",
        "objection": "gastar muito" if "dinheiro" in niche else "complicar sua rotina",
        "timeframe": "7 dias",
        "product": product or "este método",
    }

    prefix = TONE_PREFIX.get(tone, "")
    hooks = [prefix + _fmt(t, mapping) for t in _pick(HOOK_TEMPLATES_PT, variants)]
    captions_core = [_fmt(t, mapping) for t in _pick(CAPTION_TEMPLATES_PT, variants)]
    captions = [c + (f" {cta}" if cta else "") for c in captions_core]

    hashtags_base = [h.replace("{niche}", niche.replace(" ", "")) for h in HASHTAGS_PT]
    hashtags = _pick(hashtags_base, hashtags_count)
    return hooks, captions, hashtags

def generate_content(language, **kwargs):
    if language == "pt":
        return generate_pt(**kwargs)
    # Default para PT por enquanto
    return generate_pt(**kwargs)
