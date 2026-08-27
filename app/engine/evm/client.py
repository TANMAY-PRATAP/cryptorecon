"""EVM Client and ERC-20 Event Log Decoder."""

from typing import List, Dict, Any, Optional
import httpx
from pydantic import BaseModel

# Transfer(address,address,uint256) topic
ERC20_TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


class DecodedERC20Transfer(BaseModel):
    tx_hash: str
    from_address: str
    to_address: str
    amount_raw: int
    amount_normalized: float
    token_address: str
    block_number: int


class EVMClient:
    """Async EVM client for log extraction and RPC interaction."""

    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url

    @staticmethod
    def parse_transfer_log(log: Dict[str, Any], decimals: int = 6) -> Optional[DecodedERC20Transfer]:
        """Decode raw eth_getLogs entry for ERC-20 Transfer event."""
        topics = log.get("topics", [])
        if not topics or topics[0].lower() != ERC20_TRANSFER_TOPIC.lower():
            return None

        try:
            # Topic 1: from address (32 bytes padded)
            from_raw = topics[1]
            from_addr = "0x" + from_raw[-40:]

            # Topic 2: to address (32 bytes padded)
            to_raw = topics[2]
            to_addr = "0x" + to_raw[-40:]

            # Data: value (uint256 hex)
            data_hex = log.get("data", "0x0")
            if data_hex.startswith("0x"):
                data_hex = data_hex[2:]
            val_raw = int(data_hex, 16) if data_hex else 0
            val_norm = val_raw / (10 ** decimals)

            return DecodedERC20Transfer(
                tx_hash=log.get("transactionHash", ""),
                from_address=from_addr,
                to_address=to_addr,
                amount_raw=val_raw,
                amount_normalized=val_norm,
                token_address=log.get("address", ""),
                block_number=int(log.get("blockNumber", "0x0"), 16) if isinstance(log.get("blockNumber"), str) else 0
            )
        except Exception:
            return None

    async def get_erc20_transfers(
        self,
        token_address: str,
        wallet_address: str,
        from_block: int = 0,
        to_block: str = "latest"
    ) -> List[DecodedERC20Transfer]:
        """Fetch and decode ERC-20 transfer logs for a suspect wallet."""
        padded_addr = "0x" + wallet_address.lower().replace("0x", "").zfill(64)
        
        # Outflow transfers
        payload_out = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getLogs",
            "params": [{
                "address": token_address,
                "fromBlock": hex(from_block) if isinstance(from_block, int) else from_block,
                "toBlock": to_block,
                "topics": [ERC20_TRANSFER_TOPIC, padded_addr]
            }]
        }

        transfers = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(self.rpc_url, json=payload_out)
                data = res.json()
                if "result" in data and isinstance(data["result"], list):
                    for raw_log in data["result"]:
                        decoded = self.parse_transfer_log(raw_log)
                        if decoded:
                            transfers.append(decoded)
        except Exception:
            pass

        return transfers
