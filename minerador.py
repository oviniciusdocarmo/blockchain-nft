"""
Minerador NFT - Mining descentralizado
- Poll da rede central
- Seleciona transações do mempool
- Executa Proof of Work
- Submete blocos e publica em Kafka
"""

import sys
import time
import random
import string
import requests
import json
from datetime import datetime
from kafka import KafkaProducer
from nft_models import Bloco, TransacaoNFT
import os


# ============================================================================
# CONFIG
# ============================================================================
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'localhost:9092')
REDE_CENTRAL_URL = os.environ.get('REDE_CENTRAL_URL', 'http://localhost:5000')
INTERVALO_POLL = 2  # segundos

meu_id = sys.argv[1] if len(sys.argv) > 1 else 'Minerador'
kafka_producer = None


# ============================================================================
# KAFKA
# ============================================================================
def conectar_kafka():
    """Inicializa Kafka producer"""
    global kafka_producer
    max_tentativas = 10
    
    for tentativa in range(max_tentativas):
        try:
            kafka_producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
                acks='all',
                retries=3
            )
            print(f"✅ Kafka conectado")
            return
        except:
            print(f"⏳ Kafka ({tentativa + 1}/{max_tentativas})...")
            time.sleep(2)
    
    print("⚠️ Kafka offline, mas continuando")


def publicar(topico: str, evento: dict):
    """Publica no Kafka"""
    if not kafka_producer:
        return
    try:
        kafka_producer.send(topico, value=evento)
    except:
        pass


# ============================================================================
# HTTP API
# ============================================================================
def conectar_rede(url: str):
    """Aguarda conexão com rede central"""
    max_tentativas = 60
    
    for tentativa in range(max_tentativas):
        try:
            resp = requests.get(f'{url}/minerador/status', timeout=5)
            if resp.status_code == 200:
                print(f"✅ Rede Central conectada!")
                return True
        except:
            pass
        
        print(f"⏳ Aguardando Rede Central ({tentativa + 1}/{max_tentativas})...")
        time.sleep(3)
    
    print("❌ Não foi possível conectar à Rede Central")
    sys.exit(1)


def obter_status():
    """Pega status da rede"""
    try:
        resp = requests.get(f'{REDE_CENTRAL_URL}/minerador/status', timeout=5)
        return resp.json()
    except:
        return None


def submeter_bloco(bloco_dict: dict):
    """Submete bloco à rede central"""
    try:
        resp = requests.post(
            f'{REDE_CENTRAL_URL}/bloco',
            json=bloco_dict,
            timeout=5
        )
        return resp.json()
    except Exception as e:
        return {'aceito': False, 'mensagem': str(e)}


# ============================================================================
# PROOF OF WORK
# ============================================================================
def proof_of_work(bloco: Bloco, dificuldade: int) -> tuple:
    """Mining: encontra nonce que faz hash começar com N zeros"""
    tentativas = 0
    
    while True:
        nonce = int(''.join(random.choices(string.digits, k=10)))
        hash_gerado = bloco.calcular_hash(nonce)
        tentativas += 1
        
        if hash_gerado.startswith('0' * dificuldade):
            return hash_gerado, nonce, tentativas
        
        if tentativas % 1_000_000 == 0:
            print(f"   ⏳ {tentativas:,} tentativas...")


# ============================================================================
# MINERADOR PRINCIPAL
# ============================================================================
def minerador_principal():
    """Loop de mineração"""
    print(f"\n{'='*70}")
    print(f"⛏️  MINERADOR [{meu_id}] iniciado")
    print(f"{'='*70}\n")
    
    ultima_altura = 0
    
    while True:
        try:
            status = obter_status()
            if not status:
                print("⚠️ Rede offline")
                time.sleep(INTERVALO_POLL)
                continue
            
            altura = status['altura']
            dificuldade = status['dificuldade']
            mempool = status['mempool']
            
            # Detecta novo bloco
            if altura > ultima_altura:
                print(f"\n🔔 [Bloco #{altura}] adicionado à rede!")
                ultima_altura = altura
            
            # Valida mempool
            if len(mempool) < 3:
                print(f"⏳ Mempool ({len(mempool)}/3 NFTs)")
                time.sleep(INTERVALO_POLL)
                continue
            
            # Seleciona transações
            txs = mempool[:5]  # Primeiras 5
            print(f"\n🔍 Validando {len(txs)} transações...")
            
            transacoes_obj = []
            for tx_dict in txs:
                tx = TransacaoNFT(
                    tipo=tx_dict['tipo'],
                    origem=tx_dict['origem'],
                    destino=tx_dict['destino'],
                    nft_id=tx_dict['nft_id'],
                    metadados=tx_dict['metadados']
                )
                transacoes_obj.append(tx)
                print(f"   ✅ {tx.tipo}: {tx.origem[:10]}... → {tx.destino[:10]}...")
            
            # Monta bloco
            ultimo_bloco = status['ultimo_bloco']
            prox_index = ultimo_bloco['index'] + 1
            
            bloco = Bloco(
                index=prox_index,
                transacoes=transacoes_obj,
                previous_hash=ultimo_bloco['hash'],
                minerador=meu_id
            )
            
            print(f"\n⛏️  MINERANDO BLOCO #{prox_index}...")
            print(f"   📄 Transações: {len(transacoes_obj)}")
            print(f"   🔗 Hash anterior: {ultimo_bloco['hash'][:16]}...")
            print(f"   🔒 Dificuldade: {dificuldade} zeros")
            
            tempo_inicio = time.time()
            
            # PoW
            hash_encontrado, nonce, tentativas = proof_of_work(bloco, dificuldade)
            
            tempo_decorrido = time.time() - tempo_inicio
            bloco.hash = hash_encontrado
            bloco.nonce = nonce
            
            print(f"\n✨ HASH ENCONTRADO!")
            print(f"   🔢 Nonce: {nonce}")
            print(f"   🔐 Hash: \033[92m{hash_encontrado}\033[0m")
            print(f"   📊 Tentativas: {tentativas:,}")
            print(f"   ⏱️  Tempo: {tempo_decorrido:.2f}s")
            print(f"   📈 Taxa: {tentativas/tempo_decorrido/1_000_000:.2f}M try/s")
            
            # Publica progresso
            publicar('eventos-rede', {
                'fase': 'pow-concluido',
                'minerador': meu_id,
                'bloco': prox_index,
                'tentativas': tentativas,
                'tempo_segundos': tempo_decorrido,
                'timestamp': datetime.now().isoformat()
            })
            
            # Submete bloco
            print(f"\n📤 Submetendo bloco à rede...")
            
            resultado = submeter_bloco(bloco.para_dict())
            
            if resultado['aceito']:
                print(f"✅ {resultado['mensagem']}")
                
                publicar('blocos-minerados', {
                    'evento': 'bloco-aceito',
                    'minerador': meu_id,
                    'bloco': prox_index,
                    'hash': hash_encontrado,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                print(f"❌ Rejeitado: {resultado['mensagem']}")
            
            time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Minerador parado")
            break
        except Exception as e:
            print(f"💥 Erro: {e}")
            time.sleep(INTERVALO_POLL)


# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    conectar_kafka()
    conectar_rede(REDE_CENTRAL_URL)
    minerador_principal()
