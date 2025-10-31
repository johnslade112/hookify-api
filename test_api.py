#!/usr/bin/env python3
"""
Script de teste da Hookify API
Testa os principais endpoints e funcionalidades
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_register():
    print_section("1. Registrando novo usuário")
    
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "teste@hookify.com",
        "password": "senha12345",
        "full_name": "Usuário Teste"
    })
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Usuário criado: {data['email']}")
        return True
    else:
        print(f"✗ Erro: {response.text}")
        return False

def test_login():
    print_section("2. Fazendo login")
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "teste@hookify.com",
        "password": "senha12345"
    })
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        token = data['access_token']
        print(f"✓ Token obtido: {token[:50]}...")
        return token
    else:
        print(f"✗ Erro: {response.text}")
        return None

def test_generate_hook(token):
    print_section("3. Gerando hooks com IA")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/v2/generate/hook", 
        headers=headers,
        json={
            "niche": "fitness",
            "topic": "treino em casa",
            "tone": "motivacional",
            "platform": "tiktok",
            "variants": 3
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Hooks gerados:")
        for i, hook in enumerate(data['hooks'], 1):
            print(f"  {i}. {hook}")
        print(f"✓ Quota restante: {data['quota_remaining']}")
        return True
    else:
        print(f"✗ Erro: {response.text}")
        return False

def test_generate_complete(token):
    print_section("4. Gerando conteúdo completo")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/v2/generate/complete", 
        headers=headers,
        json={
            "niche": "marketing digital",
            "topic": "tráfego pago",
            "tone": "educativo",
            "platform": "reels",
            "call_to_action": "Salva esse post!",
            "analyze_emotion": True
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Hooks: {len(data['hooks'])} gerados")
        print(f"✓ Legendas: {len(data['captions'])} geradas")
        print(f"✓ Hashtags: {len(data['hashtags'])} geradas")
        
        if data.get('emotion_analysis'):
            emotion = data['emotion_analysis']
            print(f"✓ Emoção predominante: {emotion['primary_emotion']} ({emotion['confidence']:.2%})")
        
        print(f"✓ Quota restante: {data['quota_remaining']}")
        return True
    else:
        print(f"✗ Erro: {response.text}")
        return False

def test_subscription(token):
    print_section("5. Verificando assinatura")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/subscription/usage", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Plano atual: {data['current_plan']}")
        print(f"✓ Quota mensal: {data['monthly_quota']}")
        print(f"✓ Usado: {data['used_quota']}")
        print(f"✓ Restante: {data['remaining_quota']}")
        print(f"✓ Gerações este mês: {data['generations_this_month']}")
        return True
    else:
        print(f"✗ Erro: {response.text}")
        return False

def main():
    print("\n🚀 Iniciando testes da Hookify API v2.0\n")
    
    # Teste 1: Registro (pode falhar se usuário já existe)
    test_register()
    sleep(0.5)
    
    # Teste 2: Login
    token = test_login()
    if not token:
        print("\n❌ Falha no login. Abortando testes.")
        return
    sleep(0.5)
    
    # Teste 3: Gerar hooks
    test_generate_hook(token)
    sleep(0.5)
    
    # Teste 4: Gerar conteúdo completo
    test_generate_complete(token)
    sleep(0.5)
    
    # Teste 5: Verificar assinatura
    test_subscription(token)
    
    print("\n" + "="*60)
    print("  ✅ Testes concluídos!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
