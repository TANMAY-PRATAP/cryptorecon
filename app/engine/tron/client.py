"""TRON Network Client and TRC-20 Log Parser."""

from typing import List, Dict, Any, Optional
import httpx
from pydantic import BaseModel
from app.core.validators import _b58decode, BASE58_ALPHABET
import hashlib


def hex_to_tron_base58(hex_addr: str) -> str:
    """Convert a 41-prefixed hex address into TRON Base58Check format."""
    clean = hex_addr.lower().replace("0x", "")
    if len(clean) == 40:
        clean = "41" + clean
    
    raw = bytes.fromhex(clean)
    h1 = hashlib.sha256(raw).digest()
    h2 = hashlib.sha256(h1).digest()
    checksum = h2[:4]
    
    full_payload = raw + checksum
    # Base58 encode
    val = int.from_bytes(full_payload, byteorder="big")
    res = []
    while val > 0:
        val, mod = divmod(val, 58)
        res.append(BASE58_ALPHABET[mod])
    res.reverse()
    
    # Handle leading zeros
    num_zeros = 0
    for b in full_payload:
        if b == 0:
            num_zeros += 1
        else:
            break
    return "1" * num_zeros + "".join(res)


class TRC20Transfer(BaseModel):
    tx_id: str
    from_address: str
    to_address: str
    amount_normalized: float
    token_symbol: str
    block_timestamp_ms: int


class TronGridClient:
    """Async TronGrid REST API client for TRC-20 event parsing and balance retrieval."""

    def __init__(self, api_url: str = "https://api.trongrid.io", api_key: Optional[str] = None):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["TRON-PRO-API-KEY"] = self.api_key
        return headers

    async def get_trc20_transfers(
        self,
        wallet_address: str,
        limit: int = 50,
        min_timestamp_ms: int = 0
    ) -> List[TRC20Transfer]:
        """Fetch TRC-20 transfer events for a wallet using TronGrid REST API."""
        url = f"{self.api_url}/v1/accounts/{wallet_address}/transactions/trc20"
        params = {
            "limit": limit,
            "min_timestamp": min_timestamp_ms,
            "order_by": "block_timestamp,asc"
        }
        
        results: List[TRC20Transfer] = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, params=params, headers=self._headers())
                if res.status_code == 200:
                    data = res.json()
                    for item in data.get("data", []):
                        dec = item.get("token_info", {}).get("decimals")
                        if dec is None or dec == 0:
                            dec = 6
                        raw_val = float(item.get("value", 0))
                        norm_val = raw_val / (10 ** dec)
                        
                        results.append(TRC20Transfer(
                            tx_id=item.get("transaction_id", ""),
                            from_address=item.get("from", ""),
                            to_address=item.get("to", ""),
                            amount_normalized=norm_val,
                            token_symbol=item.get("token_info", {}).get("symbol", "USDT"),
                            block_timestamp_ms=item.get("block_timestamp", 0)
                        ))
        except Exception:
            pass

        return results
