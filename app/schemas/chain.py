"""Blockchain, Token and Address Schema Definitions."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Blockchain(str, Enum):
    ETHEREUM = "ethereum"
    TRON = "tron"
    BITCOIN = "bitcoin"
    POLYGON = "polygon"
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"

    @classmethod
    def from_string(cls, value: str) -> "Blockchain":
        clean_val = value.strip().lower()
        for member in cls:
            if member.value == clean_val:
                return member
        raise ValueError(f"Unsupported blockchain network: '{value}'")


class TokenContract(BaseModel):
    symbol: str = Field(..., description="Token ticker symbol (e.g. USDT, USDC)")
    address: str = Field(..., description="Contract address on target blockchain")
    decimals: int = Field(default=6, ge=0, le=18, description="Token decimals")
    name: Optional[str] = Field(default=None, description="Descriptive token name")


class AddressValidationResult(BaseModel):
    is_valid: bool = Field(..., description="Whether address conforms to chain standard")
    blockchain: Blockchain = Field(..., description="Target blockchain")
    normalized_address: str = Field(..., description="Checksummed or canonical address")
    format_type: str = Field(..., description="Address subtype: EIP-55, Base58Check, Bech32, P2SH, etc.")
    error_message: Optional[str] = Field(default=None, description="Validation failure details if invalid")
