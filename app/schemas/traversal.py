"""Schemas for Traversal, Graph Visualization, Mule Clusters, and Attribution."""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field
from app.schemas.chain import Blockchain
from app.schemas.entity import EntityType, EntityTag


class NodeCategory(str, Enum):
    SUSPECT = "SUSPECT"
    WALLET = "WALLET"
    VASP = "VASP"
    MULE_CLUSTER = "MULE_CLUSTER"
    MIXER_POOL = "MIXER_POOL"
    BRIDGE = "BRIDGE"


class AttributionTier(str, Enum):
    TIER_0_DIRECT_BLOOM = "TIER_0_DIRECT_BLOOM"
    TIER_1_GAS_PARENT = "TIER_1_GAS_PARENT"
    TIER_2_CONTRACT_FACTORY = "TIER_2_CONTRACT_FACTORY"
    TIER_3_OMNIBUS_SWEEP = "TIER_3_OMNIBUS_SWEEP"
    UTXO_TIER_1_CIOH = "UTXO_TIER_1_CIOH"
    UTXO_TIER_2_HD_DERIVATION = "UTXO_TIER_2_HD_DERIVATION"
    UTXO_TIER_3_SUBPOENA_CANDIDATE = "UTXO_TIER_3_SUBPOENA_CANDIDATE"
    UNATTRIBUTED = "UNATTRIBUTED"


class MuleMember(BaseModel):
    address: str
    split_amount: float
    percentage_of_parent: float
    current_balance: float
    gas_funder: Optional[str] = None
    tx_hash: Optional[str] = None


class MuleClusterDetail(BaseModel):
    cluster_id: str
    parent_address: str
    total_wallets: int
    total_volume_usdt: float
    members: List[MuleMember] = Field(default_factory=list)
    created_at_utc: datetime = Field(default_factory=datetime.utcnow)


class CytoscapeNodeData(BaseModel):
    id: str
    label: str
    category: NodeCategory
    address: Optional[str] = None
    blockchain: str
    risk_score: int = Field(default=0, ge=0, le=100)
    color_code: str = Field(default="#22c55e")  # Green by default
    is_breakpoint: bool = False
    is_mule_cluster: bool = False
    cluster_data: Optional[MuleClusterDetail] = None
    attribution: Optional[Dict[str, Any]] = None
    hop_level: int = 0


class CytoscapeEdgeData(BaseModel):
    id: str
    source: str
    target: str
    amount: float
    token: str
    tx_hash: str
    timestamp_utc: Optional[str] = None
    flow_ratio: float = 1.0
    label: Optional[str] = None


class CytoscapeElement(BaseModel):
    data: Dict[str, Any]
    classes: Optional[str] = None


class CytoscapeGraphResponse(BaseModel):
    elements: List[Dict[str, Any]]
    total_nodes: int
    total_edges: int
    mule_clusters_count: int
    attributed_vasps: List[str] = Field(default_factory=list)
    max_hops_traversed: int
    cfr_pruned_branches_count: int


class TraversalRequest(BaseModel):
    suspect_address: str
    blockchain: str = "ethereum"
    token_contract: str = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    incident_timestamp_utc: datetime = Field(default_factory=datetime.utcnow)
    total_stolen_amount: float = 10000.0
    max_hops: int = Field(default=4, ge=1, le=8)
    cfr_min_floor_usdt: float = 50.0
    cfr_dilution_factor: float = 1.5
    mule_split_threshold: int = 5


class AttributionInspectRequest(BaseModel):
    address: str
    blockchain: str = "ethereum"
    token_contract: Optional[str] = None
    incident_timestamp_utc: Optional[datetime] = None


class AttributionInspectResponse(BaseModel):
    address: str
    blockchain: str
    attributed_vasp: Optional[str] = None
    entity_type: Optional[str] = None
    attribution_tier: AttributionTier
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: float
    recommended_action: str
