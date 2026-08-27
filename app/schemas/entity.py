"""Known Entity and VASP Attribution Schema Definitions."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    VASP_HOT = "VASP_HOT_WALLET"
    VASP_COLD = "VASP_COLD_WALLET"
    VASP_DEPOSIT = "VASP_DEPOSIT_SWEEPER"
    MIXER_POOL = "MIXER_POOL"
    MIXER_RELAYER = "MIXER_RELAYER"
    RANSOMWARE = "RANSOMWARE_AFFILIATE"
    DARKNET_MARKET = "DARKNET_MARKET"
    TERROR_FINANCING = "TERROR_FINANCING"
    OFAC_SANCTIONED = "OFAC_SANCTIONED"
    MULE_WALLET = "MULE_WALLET"
    DEX_ROUTER = "DEX_ROUTER"
    BRIDGE = "CROSS_CHAIN_BRIDGE"
    UNKNOWN = "UNKNOWN"


class EntityTag(BaseModel):
    address: str = Field(..., description="Canonical entity blockchain address")
    blockchain: str = Field(..., description="Target network: ethereum, tron, bitcoin, etc.")
    entity_name: str = Field(..., description="Name of VASP or Protocol (e.g., Binance, Tornado Cash, CoinDCX)")
    entity_type: EntityType = Field(..., description="Classified category")
    jurisdiction: Optional[str] = Field(default=None, description="Country or operational jurisdiction (e.g. IN, US, OFFSHORE)")
    compliance_email: Optional[str] = Field(default=None, description="Law Enforcement / Nodal officer contact email")
    fiu_registered: bool = Field(default=False, description="Whether entity is registered with FIU-IND")
    risk_rating: int = Field(default=0, ge=0, le=100, description="Base entity risk rating (0-100)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context tags")


class TagLookupResponse(BaseModel):
    address: str
    blockchain: str
    match_found: bool
    lookup_latency_ms: float = Field(..., description="Measured lookup latency in milliseconds")
    matched_entity: Optional[EntityTag] = None
    attribution_tier: str = Field(default="TIER_0_DIRECT_BLOOM", description="Attribution pipeline tier")
