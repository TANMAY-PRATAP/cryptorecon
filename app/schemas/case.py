"""Case Ingestion and Forensic State Models."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from app.schemas.chain import Blockchain
from app.schemas.entity import EntityTag


class CaseStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    TAGGED_DIRECT = "TAGGED_DIRECT"
    QUEUED_FOR_TRAVERSAL = "QUEUED_FOR_TRAVERSAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class CFRPruningConfig(BaseModel):
    min_absolute_flow_usdt: float = Field(default=50.0, description="Minimum USDT floor per branch")
    dilution_factor: float = Field(default=1.5, description="Dilution divisor: Total/(N_branches * 1.5)")
    mule_cluster_split_threshold: int = Field(default=5, description="Fan-out split threshold to collapse into MuleCluster")


class CaseIngestRequest(BaseModel):
    complaint_id: str = Field(
        ...,
        examples=["NCRP-2026-98124"],
        description="Official NCRP/1930 Cyber Crime Complaint identifier"
    )
    suspect_address: str = Field(
        ...,
        examples=["0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976"],
        description="Suspect wallet address on target blockchain"
    )
    blockchain: str = Field(
        ...,
        examples=["ethereum"],
        description="Target network: ethereum, tron, bitcoin, polygon, bsc, arbitrum, optimism"
    )
    token_contract: str = Field(
        default="0xdAC17F958D2ee523a2206206994597C13D831ec7",
        examples=["0xdAC17F958D2ee523a2206206994597C13D831ec7"],
        description="Token contract address (e.g., USDT ERC-20 / TRC-20, or 'NATIVE')"
    )
    incident_timestamp_utc: datetime = Field(
        ...,
        examples=["2026-08-27T10:00:00Z"],
        description="UTC incident timestamp (T_0) for time-lock boundary enforcement"
    )
    stolen_amount: Optional[float] = Field(
        default=None,
        ge=0,
        description="Reported stolen token/fiat amount if known"
    )
    victim_bank_ref: Optional[str] = Field(
        default=None,
        description="1930 / CFCFRMS banking transaction reference"
    )

    @field_validator("complaint_id")
    @classmethod
    def validate_complaint_id(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("complaint_id cannot be empty")
        return clean

    @field_validator("suspect_address")
    @classmethod
    def validate_address_not_empty(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("suspect_address cannot be empty")
        return clean


class CaseIngestResponse(BaseModel):
    complaint_id: str
    suspect_address: str
    blockchain: str
    normalized_address: str
    incident_timestamp_utc: datetime
    status: CaseStatus
    direct_tag_matched: bool
    attributed_entity: Optional[EntityTag] = None
    lookup_latency_ms: float
    time_lock_enforced_from_utc: datetime
    message: str
    queued_task_id: Optional[str] = None
    created_at_utc: datetime = Field(default_factory=datetime.utcnow)


class CaseDetail(BaseModel):
    complaint_id: str
    suspect_address: str
    normalized_address: str
    blockchain: Blockchain
    token_contract: str
    incident_timestamp_utc: datetime
    status: CaseStatus
    risk_score: int = Field(default=0, ge=0, le=100)
    typology: str = Field(default="UNFLAGGED")
    direct_tag_matched: bool = False
    attributed_vasp: Optional[str] = None
    cfr_pruning_config: CFRPruningConfig = Field(default_factory=CFRPruningConfig)
    created_at_utc: datetime
    updated_at_utc: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
