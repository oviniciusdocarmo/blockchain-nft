"""
Modelos simples para Blockchain NFT
- TransacaoNFT: MINT, TRANSFER, BURN
- Bloco: com PoW
- Blockchain: com consenso
"""

import hashlib
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any


class TransacaoNFT:
    """Transação de NFT: MINT (criar), TRANSFER (transferir), BURN (destruir)"""
    
    def __init__(self, tipo: str, origem: str, destino: str, nft_id: str = None, metadados: str = ""):
        self.id = str(uuid.uuid4())
        self.tipo = tipo  # MINT, TRANSFER, BURN
        self.origem = origem
        self.destino = destino
        self.nft_id = nft_id or str(uuid.uuid4())
        self.metadados = metadados
        self.timestamp = datetime.now().isoformat()
    
    def para_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'tipo': self.tipo,
            'origem': self.origem,
            'destino': self.destino,
            'nft_id': self.nft_id,
            'metadados': self.metadados,
            'timestamp': self.timestamp
        }


class Bloco:
    """Um bloco na blockchain"""
    
    def __init__(self, index: int, transacoes: List[TransacaoNFT], previous_hash: str, minerador: str):
        self.index = index
        self.transacoes = transacoes
        self.previous_hash = previous_hash
        self.minerador = minerador
        self.timestamp = datetime.now().isoformat()
        self.nonce = 0
        self.hash = self.calcular_hash()
    
    def calcular_hash(self, nonce: int = None) -> str:
        """Calcula SHA256 do bloco"""
        if nonce is not None:
            self.nonce = nonce
        
        dados = {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'minerador': self.minerador,
            'nonce': self.nonce,
            'transacoes': [tx.para_dict() for tx in self.transacoes]
        }
        
        string = json.dumps(dados, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(string.encode()).hexdigest()
    
    def para_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'hash': self.hash,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'minerador': self.minerador,
            'nonce': str(self.nonce),  # Convertido para string (XML-RPC safe)
            'transacoes': [tx.para_dict() for tx in self.transacoes],
            'num_transacoes': len(self.transacoes)
        }


class Blockchain:
    """A blockchain com consenso por maior trabalho acumulado"""
    
    def __init__(self, dificuldade: int = 2):
        self.dificuldade = dificuldade
        self.cadeia = [self._bloco_genesis()]
    
    def _bloco_genesis(self) -> Bloco:
        """Cria o bloco gênesis"""
        bloco = Bloco(0, [], '0' * 64, 'Sistema')
        bloco.hash = bloco.calcular_hash()
        return bloco
    
    def adicionar_bloco(self, bloco: Bloco) -> bool:
        """Valida e adiciona bloco à cadeia"""
        ultimo = self.cadeia[-1]
        
        # Validação básica
        if bloco.index != ultimo.index + 1:
            return False
        if bloco.previous_hash != ultimo.hash:
            return False
        if not bloco.hash.startswith('0' * self.dificuldade):
            return False
        
        self.cadeia.append(bloco)
        return True
    
    def obter_status(self) -> Dict[str, Any]:
        """Status atual da blockchain"""
        ultimo = self.cadeia[-1]
        return {
            'altura': len(self.cadeia) - 1,
            'ultimo_bloco': ultimo.para_dict(),
            'dificuldade': self.dificuldade,
            'trabalho_total': len(self.cadeia)  # Simples: quantidade de blocos
        }
    
    def obter_blocos_recentes(self, quantidade: int = 5) -> List[Dict[str, Any]]:
        """Retorna últimos N blocos"""
        return [bloco.para_dict() for bloco in self.cadeia[-quantidade:]]
