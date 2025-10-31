#!/usr/bin/env python3
"""
Exemplo de integração com a Hookify API em Python
Demonstra como usar a API em suas aplicações
"""

import requests
from typing import List, Dict, Optional

class HookifyClient:
    """Cliente Python para a Hookify API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, token: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.token = token
        
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        elif self.api_key:
            return {"X-API-Key": self.api_key}
        return {}
    
    def register(self, email: str, password: str, full_name: Optional[str] = None) -> Dict:
        """Registra um novo usuário"""
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={"email": email, "password": password, "full_name": full_name}
        )
        response.raise_for_status()
        return response.json()
    
    def login(self, email: str, password: str) -> str:
        """Faz login e retorna o token"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["access_token"]
        return self.token
    
    def generate_hooks(
        self,
        niche: str,
        topic: str,
        tone: str = "direto",
        platform: str = "tiktok",
        variants: int = 3
    ) -> Dict:
        """Gera hooks virais"""
        response = requests.post(
            f"{self.base_url}/v2/generate/hook",
            headers=self._get_headers(),
            json={
                "niche": niche,
                "topic": topic,
                "tone": tone,
                "platform": platform,
                "variants": variants
            }
        )
        response.raise_for_status()
        return response.json()
    
    def generate_captions(
        self,
        niche: str,
        topic: str,
        tone: str = "direto",
        product_name: Optional[str] = None,
        call_to_action: Optional[str] = None,
        max_length: int = 150,
        variants: int = 3
    ) -> Dict:
        """Gera legendas persuasivas"""
        response = requests.post(
            f"{self.base_url}/v2/generate/caption",
            headers=self._get_headers(),
            json={
                "niche": niche,
                "topic": topic,
                "tone": tone,
                "product_name": product_name,
                "call_to_action": call_to_action,
                "max_length": max_length,
                "variants": variants
            }
        )
        response.raise_for_status()
        return response.json()
    
    def generate_hashtags(
        self,
        niche: str,
        topic: str,
        platform: str = "tiktok",
        count: int = 10,
        include_trending: bool = True
    ) -> Dict:
        """Gera hashtags relevantes"""
        response = requests.post(
            f"{self.base_url}/v2/generate/hashtags",
            headers=self._get_headers(),
            json={
                "niche": niche,
                "topic": topic,
                "platform": platform,
                "count": count,
                "include_trending": include_trending
            }
        )
        response.raise_for_status()
        return response.json()
    
    def analyze_emotion(self, text: str, context: Optional[str] = None) -> Dict:
        """Analisa a emoção de um texto"""
        response = requests.post(
            f"{self.base_url}/v2/analyze/emotion",
            headers=self._get_headers(),
            json={"text": text, "context": context}
        )
        response.raise_for_status()
        return response.json()
    
    def generate_complete(
        self,
        niche: str,
        topic: str,
        tone: str = "direto",
        platform: str = "tiktok",
        product_name: Optional[str] = None,
        call_to_action: Optional[str] = None,
        analyze_emotion: bool = False
    ) -> Dict:
        """Gera hooks, legendas, hashtags e opcionalmente analisa emoção"""
        response = requests.post(
            f"{self.base_url}/v2/generate/complete",
            headers=self._get_headers(),
            json={
                "niche": niche,
                "topic": topic,
                "tone": tone,
                "platform": platform,
                "product_name": product_name,
                "call_to_action": call_to_action,
                "analyze_emotion": analyze_emotion
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_subscription(self) -> Dict:
        """Retorna informações da assinatura"""
        response = requests.get(
            f"{self.base_url}/subscription",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_usage(self) -> Dict:
        """Retorna estatísticas de uso"""
        response = requests.get(
            f"{self.base_url}/subscription/usage",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()


# ==================== EXEMPLO DE USO ====================

def main():
    # Inicializar cliente
    client = HookifyClient(base_url="http://localhost:8000")
    
    # 1. Fazer login
    print("🔐 Fazendo login...")
    token = client.login(email="teste@hookify.com", password="senha12345")
    print(f"✓ Token obtido: {token[:50]}...\n")
    
    # 2. Gerar conteúdo completo
    print("🚀 Gerando conteúdo completo...")
    result = client.generate_complete(
        niche="fitness",
        topic="perder barriga rápido",
        tone="motivacional",
        platform="reels",
        call_to_action="Salva esse post e me segue para mais dicas!",
        analyze_emotion=True
    )
    
    print("\n📌 HOOKS GERADOS:")
    for i, hook in enumerate(result['hooks'], 1):
        print(f"  {i}. {hook}")
    
    print("\n📝 LEGENDAS GERADAS:")
    for i, caption in enumerate(result['captions'], 1):
        print(f"  {i}. {caption[:100]}...")
    
    print("\n#️⃣ HASHTAGS GERADAS:")
    print(f"  {' '.join(result['hashtags'])}")
    
    if result.get('emotion_analysis'):
        emotion = result['emotion_analysis']
        print(f"\n😊 ANÁLISE DE EMOÇÃO:")
        print(f"  Emoção predominante: {emotion['primary_emotion']}")
        print(f"  Confiança: {emotion['confidence']:.2%}")
        print(f"  Sugestões: {emotion['suggestions'][0]}")
    
    print(f"\n💡 Quota restante: {result['quota_remaining']}")
    
    # 3. Verificar uso
    print("\n📊 Verificando estatísticas de uso...")
    usage = client.get_usage()
    print(f"  Plano: {usage['current_plan']}")
    print(f"  Usado: {usage['used_quota']}/{usage['monthly_quota']}")
    print(f"  Gerações este mês: {usage['generations_this_month']}")


if __name__ == "__main__":
    main()
