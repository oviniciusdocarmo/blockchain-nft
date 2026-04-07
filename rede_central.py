"""
Rede Central - Coordinador e Blockchain
- Recebe blocos dos mineradores
- Gerencia mempool de NFTs
- Valida e adiciona blocos
- Publica eventos no Kafka
- Gera NFTs automaticamente
"""

import threading
import time
import os
import random
import json
from datetime import datetime
from flask import Flask, request, jsonify
from kafka import KafkaProducer
from nft_models import TransacaoNFT, Bloco, Blockchain

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================
DIFICULDADE = int(os.environ.get('DIFICULDADE', '2'))
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'localhost:9092')

# Estado global
blockchain = Blockchain(dificuldade=DIFICULDADE)
mempool = []  # Transações pendentes
trava = threading.Lock()
kafka_producer = None


# ============================================================================
# KAFKA
# ============================================================================
def inicializar_kafka():
    """Conecta ao Kafka"""
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
            print("✅ Kafka conectado")
            return
        except:
            print(f"⏳ Tentando Kafka ({tentativa + 1}/{max_tentativas})...")
            time.sleep(2)
    
    print("⚠️ Kafka não disponível, continuando sem publicação")


def publicar_evento(topico: str, evento: dict):
    """Publica evento no Kafka"""
    if not kafka_producer:
        return
    try:
        kafka_producer.send(topico, value=evento)
    except Exception as e:
        print(f"⚠️ Erro ao publicar: {e}")


# ============================================================================
# FLASK ROUTES
# ============================================================================
app = Flask(__name__)


@app.route('/status', methods=['GET'])
def status_rede():
    """Retorna status da rede"""
    with trava:
        return jsonify({
            'status': 'ok',
            'blockchain': blockchain.obter_status(),
            'mempool': len(mempool),
            'timestamp': datetime.now().isoformat()
        })


@app.route('/bloco', methods=['POST'])
def receber_bloco():
    """Recebe e valida um bloco do minerador"""
    try:
        bloco_dict = request.json
        
        # Reconstrói o objeto Bloco
        transacoes = [
            TransacaoNFT(
                tipo=tx['tipo'],
                origem=tx['origem'],
                destino=tx['destino'],
                nft_id=tx['nft_id'],
                metadados=tx['metadados']
            ) for tx in bloco_dict['transacoes']
        ]
        
        bloco = Bloco(
            index=bloco_dict['index'],
            transacoes=transacoes,
            previous_hash=bloco_dict['previous_hash'],
            minerador=bloco_dict['minerador']
        )
        bloco.hash = bloco_dict['hash']
        bloco.nonce = int(bloco_dict['nonce'])
        bloco.timestamp = bloco_dict['timestamp']
        
        with trava:
            if blockchain.adicionar_bloco(bloco):
                # Remove transações do mempool
                for tx in bloco.transacoes:
                    mempool[:] = [m for m in mempool if m.id != tx.id]
                
                # Publica evento
                publicar_evento('blocos-minerados', {
                    'evento': 'bloco-aceito',
                    'bloco': bloco.index,
                    'minerador': bloco.minerador,
                    'hash': bloco.hash,
                    'transacoes': len(bloco.transacoes),
                    'timestamp': datetime.now().isoformat()
                })
                
                return jsonify({'aceito': True, 'mensagem': f'Bloco #{bloco.index} aceito'}), 200
            else:
                return jsonify({'aceito': False, 'mensagem': 'Bloco inválido'}), 400
    
    except Exception as e:
        return jsonify({'aceito': False, 'mensagem': str(e)}), 400


@app.route('/minerador/status', methods=['GET'])
def status_minerador():
    """Info que minerador precisa para começar a minerar"""
    with trava:
        ultimo_bloco = blockchain.cadeia[-1]
        return jsonify({
            'altura': blockchain.obter_status()['altura'],
            'ultimo_bloco': ultimo_bloco.para_dict(),
            'dificuldade': blockchain.dificuldade,
            'mempool': [tx.para_dict() for tx in mempool[:10]]  # Primeiras 10
        })


@app.route('/explorer', methods=['GET'])
def explorer():
    """Últimos blocos para visualização"""
    with trava:
        return jsonify({
            'altura': blockchain.obter_status()['altura'],
            'blocos': blockchain.obter_blocos_recentes(5),
            'mempool_pendentes': len(mempool),
            'dificuldade': blockchain.dificuldade
        })


# ============================================================================
# GERADORES DE TRANSAÇÕES (Background)
# ============================================================================
def gerador_nfts():
    """Gera MINTs de NFT automaticamente a cada 5 segundos"""
    contador = 1
    while True:
        time.sleep(5)
        with trava:
            # Gera 3-5 MINTs
            for _ in range(random.randint(3, 5)):
                dono = f"User_{random.randint(1, 100)}"
                nome_nft = f"NFT-Arte#{contador}"
                
                tx = TransacaoNFT(
                    tipo='MINT',
                    origem='Sistema',
                    destino=dono,
                    metadados=f"Nome: {nome_nft}, Criado: {datetime.now().isoformat()}"
                )
                mempool.append(tx)
                contador += 1
                print(f"💎 [{datetime.now().strftime('%H:%M:%S')}] MINT: {nome_nft} → {dono}")


def visualizador():
    """Mostra status em tempo real"""
    ultima_altura = 0
    while True:
        with trava:
            altura = blockchain.obter_status()['altura']
            mempool_size = len(mempool)
        
        if altura > ultima_altura:
            os.system('clear' if os.name == 'posix' else 'cls')
            print("=" * 70)
            print(f"🌐 BLOCKCHAIN NFT EXPLORER | Altura: {altura} blocos | Mempool: {mempool_size}")
            print("=" * 70)
            
            with trava:
                para_mostrar = blockchain.cadeia[-5:]
                for bloco in para_mostrar:
                    print(f"\n📦 BLOCO #{bloco.index}")
                    print(f"   ⛏️  Minerador: {bloco.minerador}")
                    print(f"   📄 Transações: {len(bloco.transacoes)}")
                    print(f"   🔢 Nonce: {bloco.nonce}")
                    print(f"   🔐 Hash: \033[92m{bloco.hash}\033[0m")
                    
                    if bloco.transacoes:
                        print(f"   Detalhes:")
                        for tx in bloco.transacoes:
                            print(f"      • {tx.tipo}: {tx.origem} → {tx.destino} ({tx.nft_id[:8]}...)")
            
            ultima_altura = altura
        
        time.sleep(1)


# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🚀 REDE CENTRAL NFT BLOCKCHAIN")
    print("=" * 70)
    print(f"   Dificuldade: {DIFICULDADE} zeros")
    print(f"   Kafka: {KAFKA_BROKER}")
    print("=" * 70 + "\n")
    
    # Inicializa Kafka
    inicializar_kafka()
    
    # Inicia threads
    threading.Thread(target=gerador_nfts, daemon=True).start()
    threading.Thread(target=visualizador, daemon=True).start()
    
    # Flexiona Flask
    print("🌐 Iniciando servidor HTTP na porta 5000...\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
