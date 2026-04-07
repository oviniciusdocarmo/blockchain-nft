#!/usr/bin/env python3
"""
Script de teste rápido da Blockchain NFT Simplificada
Verifica status, API endpoints, e performance
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def teste_api():
    """Testa todos os endpoints"""
    
    print("\n" + "="*70)
    print("🧪 TESTE DA BLOCKCHAIN NFT SIMPLIFICADA")
    print("="*70 + "\n")
    
    try:
        # 1. Status
        print("1️⃣  Testando /status...")
        resp = requests.get(f"{BASE_URL}/status", timeout=5)
        status = resp.json()
        
        print(f"   ✅ Status: {status['status']}")
        print(f"   📊 Altura blockchain: {status['blockchain']['altura']} blocos")
        print(f"   💾 Mempool: {status['mempool']} transações pendentes")
        print(f"   ⚙️  Dificuldade: {status['blockchain']['dificuldade']} zeros")
        
        # 2. Explorer
        print("\n2️⃣  Testando /explorer...")
        resp = requests.get(f"{BASE_URL}/explorer", timeout=5)
        explorer = resp.json()
        
        print(f"   ✅ Últimos {len(explorer['blocos'])} blocos:")
        for bloco in explorer['blocos'][-3:]:
            print(f"      • Bloco #{bloco['index']}: {len(bloco['transacoes'])} NFTs | Minerador: {bloco['minerador']}")
        
        # 3. Status Minerador
        print("\n3️⃣  Testando /minerador/status...")
        resp = requests.get(f"{BASE_URL}/minerador/status", timeout=5)
        minerador = resp.json()
        
        print(f"   ✅ Altura para próximo bloco: {minerador['altura'] + 1}")
        print(f"   📦 Mempool com {len(minerador['mempool'])} NFTs disponíveis:")
        for tx in minerador['mempool'][:3]:
            print(f"      • {tx['tipo']}: {tx['origem']} → {tx['destino']}")
        
        # 4. Performance
        print("\n4️⃣  PERFORMANCE")
        altura_inicial = status['blockchain']['altura']
        
        print(f"   ⏳ Aguardando 10 segundos...")
        import time
        time.sleep(10)
        
        resp = requests.get(f"{BASE_URL}/status", timeout=5)
        status_novo = resp.json()
        altura_final = status_novo['blockchain']['altura']
        
        blocos_minerados = altura_final - altura_inicial
        tempo_meio_bloco = 10 / blocos_minerados if blocos_minerados > 0 else float('inf')
        
        print(f"   ✅ Blocos minerados em 10s: {blocos_minerados}")
        print(f"   ⌛ Tempo médio/bloco: {tempo_meio_bloco:.2f}s")
        print(f"   📈 Taxa: ~{blocos_minerados * 6}/minuto")
        
        # 5. Blockchain
        print("\n5️⃣  BLOCKCHAIN stats")
        print(f"   ✅ Total de blocos: {status_novo['blockchain']['trabalho_total']}")
        print(f"   💾 Trabalho acumulado: {status_novo['blockchain']['trabalho_total']} PoW")
        
        print("\n" + "="*70)
        print("✅ TODOS OS TESTES PASSOU!")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("   Certifique-se de que o Docker está rodando:")
        print("   docker-compose -f docker-compose-simple.yml up -d")
        return False

if __name__ == '__main__':
    teste_api()
