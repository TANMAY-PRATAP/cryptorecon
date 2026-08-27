"""Pydantic Schemas for AI/ML Risk Scoring, Typology Classification, and Mixer Obfuscation."""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TypologyType(str, Enum):
    MULE_RING = "Mule Ring"
    RANSOMWARE = "Ransomware"
    DARKNET_MARKET = "Darknet Market"
    TERROR_FINANCING = "Terror Financing"
    UNFLAGGED = "Unflagged"


class StructuralFeatures(BaseModel):
    fan_in_degree: int = Field(default=0, description="Count of distinct inbound senders")
    fan_out_degree: int = Field(default=0, description="Count of distinct outbound recipients")
    degree_entropy: float = Field(default=0.0, description="Shannon entropy of transaction degree")
    transaction_burst_velocity: float = Field(default=0.0, description="Peak transactions per hour")
    median_holding_duration_seconds: float = Field(default=0.0, description="Median time funds remain in wallet")
    native_gas_dispenser_diversity: int = Field(default=0, description="Count of distinct native gas dispensers")
    historical_address_reuse_count: int = Field(default=0, description="Frequency of recurring address reuse")
    gini_coefficient_amounts: float = Field(default=0.0, ge=0.0, le=1.0, description="Gini inequality of transfer amounts")
    rapid_dispersion_ratio: float = Field(default=0.0, ge=0.0, le=1.0, description="Fraction of funds drained in < 1 hour")
    privacy_mixer_interaction_ratio: float = Field(default=0.0, ge=0.0, le=1.0, description="Ratio of mixer/privacy pool hops")
    volume_in_out_ratio: float = Field(default=1.0, description="Inflow to Outflow volume ratio")
    inter_tx_variance: float = Field(default=0.0, description="Variance in time interval between transactions")
    exchange_hop_distance: int = Field(default=99, description="Shortest hop distance to known VASP")
    node2vec_embedding_dim: int = Field(default=16, description="Dimension of topological embedding vector")


class RiskScoringRequest(BaseModel):
    address: str
    blockchain: str = "ethereum"
    complaint_id: Optional[str] = None
    historical_transactions: Optional[List[Dict[str, Any]]] = None
    subgraph_nodes: Optional[List[str]] = None


class RiskScoringResponse(BaseModel):
    address: str
    blockchain: str
    risk_score: int = Field(..., ge=0, le=100, description="Composite Risk Score (0-100)")
    risk_tier: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL_OBFUSCATION")
    primary_typology: TypologyType
    typology_probabilities: Dict[str, float]
    extracted_features: StructuralFeatures
    top_risk_factors: List[str] = Field(default_factory=list)
    inference_latency_ms: float
    is_breakpoint: bool = False
    recommended_action: str


class HITLFeedbackRequest(BaseModel):
    complaint_id: str
    suspect_address: str
    blockchain: str
    confirmed_typology: TypologyType
    investigator_badge_id: str
    notes: Optional[str] = None
    timestamp_utc: datetime = Field(default_factory=datetime.utcnow)


class HITLFeedbackResponse(BaseModel):
    status: str = "FEEDBACK_RECORDED"
    feedback_id: str
    complaint_id: str
    total_retained_samples: int
    model_retrained: bool
    message: str


class MixerInspectionResponse(BaseModel):
    address: str
    blockchain: str
    is_mixer: bool
    protocol_name: Optional[str] = None
    risk_score: int = Field(default=0, ge=0, le=100)
    status: str = "STANDARD_WALLET"
    break_point_flag: bool = False
    evidence: Dict[str, Any] = Field(default_factory=dict)
    compliance_advisory: str


class WatchdogSubscriptionRequest(BaseModel):
    target_address: str
    blockchain: str = "ethereum"
    complaint_id: Optional[str] = None
    webhook_url: Optional[str] = None
    monitoring_duration_days: int = Field(default=30, ge=1, le=90)


class WatchdogSubscriptionResponse(BaseModel):
    subscription_id: str
    target_address: str
    blockchain: str
    active: bool
    expires_at_utc: datetime
    message: str


class WatchdogAlert(BaseModel):
    alert_id: str
    subscription_id: str
    target_address: str
    blockchain: str
    event_type: str  # "MIXER_EXIT", "BALANCE_SWEEP", "MEMPOOL_OUTFLOW"
    detected_tx_hash: str
    amount: float
    token: str
    counterparty: str
    timestamp_utc: datetime
