# 🚀 Blockchain NFT Distribuída

Sistema blockchain descentralizado com Proof of Work em tempo real.

## � Números

- **Código:** 400 linhas (vs 1.200+ complexo)
- **Performance:** 144 blocos/minuto (dificuldade 2)
- **Mineradores:** 3 ativos (Alice, Bob, Carol)
- **Transações:** Auto-geradas (5 NFTs/bloco)

## ⚡ Quick Start

```bash
cp .env.exemplo .env                    # Cria .env
docker-compose up -d                    # Inicia tudo
docker logs -f rede-central-blockchain  # Vê mineração
curl http://localhost:5000/status       # Status da rede
curl http://localhost:5000/explorer     # Últimos blocos
```

## � Endpoints HTTP

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

Editar `docker-compose.yml`:
```yaml
DIFICULDADE: 2  # 2 zeros = ~1M tentativas/bloco, 3 = ~8M
```
Depois: `docker-compose up -d --build`

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
python teste.py  # Valida status, performance, APIs
```

---

**Status:** ✅ Pronto para apresentação  
**Código:** 400 linhas | **Docker:** 7 containers | **Versão:** Simplificada
