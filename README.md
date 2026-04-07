# 🚀 Blockchain NFT Distribuída

Sistema blockchain descentralizado com Proof of Work em tempo real.

## ⚡ Quick Start

```bash
cp .env.exemplo .env                    # Cria .env
docker-compose up -d                    # Inicia tudo
docker logs -f rede-central-blockchain  # Vê mineração em tempo real
curl http://localhost:5000/status       # Status blockchain
curl http://localhost:5000/explorer     # Últimos 5 blocos
```

## 📡 Endpoints HTTP

- `GET /status` → Status blockchain + mempool
- `GET /explorer` → Últimos 5 blocos
- `GET /minerador/status` → Info para mineradores
- `POST /bloco` → Recebe blocos (interno)
- `http://localhost:8080` → Kafka UI (eventos)

## ⛏️ Fluxo de Mineração

1. Sistema gera NFTs (MINT automático)
2. Mineradores buscam status
3. PoW: encontra nonce com N zeros
4. POST /bloco → validação
5. Publica Kafka → disseminação

## ⚙️ Configuração

Editar `.env`:
```bash
DIFICULDADE=2              # 2 zeros = ~1M tentativas/bloco, 3 = ~8M tentativas
KAFKA_BROKER=kafka:9092    # Broker interno do Docker
REDE_CENTRAL_URL=http://rede-central:5000  # URL da central
```
Depois reconstruir: `docker-compose down && docker-compose up -d --build`

## ✅ Requisitos

- ✓ Blocos encadeados por hash
- ✓ Proof of Work (dificuldade configurável)
- ✓ 3 mineradores em competição
- ✓ Mempool + validação
- ✓ Consenso (maior trabalho)
- ✓ Kafka + HTTP disseminação
- ✓ Visualização tempo real
- ✓ NFT (MINT auto-gerado)

## 🧪 Teste Rápido

```bash
python teste.py  # Valida altura, mempool, taxa de mineração
```

## 📁 Arquivos Principais

- `nft_models.py` - Classes Blockchain, Bloco, TransacaoNFT
- `rede_central.py` - API Flask central
- `minerador.py` - PoW distribuído (Alice, Bob, Carol)
- `.env` - Configuração (DIFICULDADE, KAFKA_BROKER, etc)
- `docker-compose.yml` - Orquestração de 7 containers

