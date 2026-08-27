"""Pydantic Schemas for Legal Dispatch, P2P Re-Stitching, and CFCFRMS Portal Injection."""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class FreezePortalStatus(str, Enum):
    PENDING = "PENDING"
    SUBMITTED_TO_1930 = "SUBMITTED_TO_1930"
    ACCOUNT_FROZEN = "ACCOUNT_FROZEN"
    REJECTED = "REJECTED"


class P2PCounterpartyRecord(BaseModel):
    complaint_id: str
    vasp_name: str
    exchange_uid: str
    p2p_order_id: str
    crypto_amount: float
    token_symbol: str
    inr_fiat_amount: float
    bank_account_number: str
    bank_ifsc: str
    bank_name: str
    upi_vpa: Optional[str] = None
    account_holder_name: str
    counterparty_pan_kyc: Optional[str] = None
    counterparty_phone: Optional[str] = None
    trade_timestamp_utc: datetime


class CFCFRMSFreezePayload(BaseModel):
    portal_name: str = "1930 / I4C CFCFRMS Banking Freeze Gateway"
    complaint_id: str
    victim_bank_ref: Optional[str] = None
    target_bank_name: str
    target_account_number: str
    target_ifsc: str
    target_upi_vpa: Optional[str] = None
    account_holder_name: str
    freeze_amount_inr: float
    linked_crypto_tx_hash: str
    linked_vasp_uid: str
    urgency_level: str = "EMERGENCY_CRIME_LIEN"
    timestamp_utc: datetime = Field(default_factory=datetime.utcnow)
    evidence_cert_ref: str


class Section94BNSSRequest(BaseModel):
    complaint_id: str
    suspect_address: str
    blockchain: str
    vasp_name: str
    compliance_email: str
    exchange_uid: Optional[str] = None
    investigating_officer_name: str = "Inspector R. K. Sharma"
    police_unit: str = "Cyber Crime Police Station, Cyberabad"
    state_jurisdiction: str = "Telangana Police / I4C Gateway"
    stolen_amount_usdt: float = 10000.0
    statutory_deadline_hours: int = 24


class Section65BBSARequest(BaseModel):
    complaint_id: str
    suspect_address: str
    blockchain: str
    rpc_endpoint_used: str = "https://eth.llamarpc.com"
    rpc_response_sha256_hash: Optional[str] = None
    merkle_root_proof: Optional[str] = None
    certifying_examiner_name: str = "Cyber Forensic Examiner #774"
    lab_accreditation: str = "CERT-In / I4C Accredited Digital Forensics Unit"
    system_hostname: str = "CYBER-RECON-V4-NODE-01"


class LegalExportResponse(BaseModel):
    document_type: str
    complaint_id: str
    rendered_filename: str
    html_content: str
    sha256_digest: str
    generated_at_utc: datetime = Field(default_factory=datetime.utcnow)
    statutory_reference: str
