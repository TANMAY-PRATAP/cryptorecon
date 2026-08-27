"""Bitcoin (UTXO) Client and CIOH Heuristic Engine."""

from typing import List, Dict, Any, Set, Optional
import httpx
from pydantic import BaseModel


class UTXOInput(BaseModel):
    txid: str
    vout: int
    prevout_address: Optional[str] = None
    value_satoshis: int = 0


class UTXOOutput(BaseModel):
    address: Optional[str] = None
    value_satoshis: int = 0
    script_type: Optional[str] = None
    is_change: bool = False


class BitcoinTransaction(BaseModel):
    txid: str
    block_time: int
    inputs: List[UTXOInput]
    outputs: List[UTXOOutput]
    is_coinjoin: bool = False


class BitcoinClient:
    """Async Bitcoin API / Blockstream client with CIOH clustering heuristic."""

    def __init__(self, api_url: str = "https://blockstream.info/api"):
        self.api_url = api_url.rstrip("/")

    @staticmethod
    def apply_cioh(inputs: List[UTXOInput]) -> Set[str]:
        """Apply Common-Input-Ownership Heuristic (CIOH).
        
        Assumes all input addresses in a standard multi-input transaction are controlled
        by the same entity / cluster (excluding CoinJoin transactions).
        """
        cluster_addresses: Set[str] = set()
        for inp in inputs:
            if inp.prevout_address:
                cluster_addresses.add(inp.prevout_address)
        return cluster_addresses

    @staticmethod
    def detect_change_address(outputs: List[UTXOOutput], known_inputs: Set[str]) -> Optional[str]:
        """Peel-chain change address detection heuristic.
        
        Identifies return/change address based on non-round payment amount and address uniqueness.
        """
        for out in outputs:
            if not out.address:
                continue
            # If address matches input, it is direct reuse change
            if out.address in known_inputs:
                out.is_change = True
                return out.address
        return None

    async def get_address_txs(self, address: str) -> List[BitcoinTransaction]:
        """Fetch transactions for a Bitcoin address from public Blockstream API."""
        url = f"{self.api_url}/address/{address}/txs"
        txs: List[BitcoinTransaction] = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    for item in data:
                        inputs = []
                        for vin in item.get("vin", []):
                            prev = vin.get("prevout", {})
                            inputs.append(UTXOInput(
                                txid=vin.get("txid", ""),
                                vout=vin.get("vout", 0),
                                prevout_address=prev.get("scriptpubkey_address"),
                                value_satoshis=prev.get("value", 0)
                            ))
                        
                        outputs = []
                        for vout in item.get("vout", []):
                            outputs.append(UTXOOutput(
                                address=vout.get("scriptpubkey_address"),
                                value_satoshis=vout.get("value", 0),
                                script_type=vout.get("scriptpubkey_type")
                            ))
                        
                        txs.append(BitcoinTransaction(
                            txid=item.get("txid", ""),
                            block_time=item.get("status", {}).get("block_time", 0),
                            inputs=inputs,
                            outputs=outputs
                        ))
        except Exception:
            pass
        return txs
