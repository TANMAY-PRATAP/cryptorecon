"""Unit and Integration tests for Asset Recovery & Legal Dispatch Engine."""

import pytest  # pyrefly: ignore # type: ignore
from starlette.testclient import TestClient  # pyrefly: ignore # type: ignore
from app.main import app  # pyrefly: ignore # type: ignore
from app.legal.p2p_restitcher import P2PRestitcher  # pyrefly: ignore # type: ignore
from app.legal.pdf_generator import LegalNoticeGenerator  # pyrefly: ignore # type: ignore
from app.schemas.legal import Section94BNSSRequest, Section65BBSARequest  # pyrefly: ignore # type: ignore

client = TestClient(app)


def test_p2p_restitch_known_uid():
    """Verify P2P order re-stitching for known CoinDCX UID."""
    record = P2PRestitcher.restitch_p2p_order(
        complaint_id="NCRP-2026-98124",
        vasp_uid="UID_CDX_99214",
        tx_hash="0xsample_sweep_tx_123456"
    )

    assert record.complaint_id == "NCRP-2026-98124"
    assert record.vasp_name == "CoinDCX"
    assert record.bank_name == "HDFC Bank Ltd"
    assert record.bank_ifsc == "HDFC0001234"
    assert record.bank_account_number == "50100492817291"
    assert record.upi_vpa == "mule.cashout99@okhdfcbank"
    assert record.inr_fiat_amount == 472500.0


def test_cfcfrms_freeze_payload_generation():
    """Verify generation of structured 1930 / I4C CFCFRMS banking freeze payload."""
    record = P2PRestitcher.restitch_p2p_order(
        complaint_id="NCRP-2026-98124",
        vasp_uid="UID_CDX_99214",
        tx_hash="0xsample_sweep_tx_123456"
    )

    payload = P2PRestitcher.generate_cfcfrms_payload(
        p2p_record=record,
        linked_tx_hash="0xsample_sweep_tx_123456",
        victim_bank_ref="AXIS/2026/UPI/88921"
    )

    assert "CFCFRMS" in payload.portal_name
    assert payload.complaint_id == "NCRP-2026-98124"
    assert payload.target_bank_name == "HDFC Bank Ltd"
    assert payload.target_account_number == "50100492817291"
    assert payload.freeze_amount_inr == 472500.0
    assert payload.urgency_level == "EMERGENCY_CRIME_LIEN"
    assert payload.evidence_cert_ref.startswith("BSA-65B-CERT-")


def test_generate_section_94_bnss_notice():
    """Verify rendering of statutory Section 94 BNSS freezing notice."""
    generator = LegalNoticeGenerator()
    req = Section94BNSSRequest(
        complaint_id="NCRP-2026-98124",
        suspect_address="0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        blockchain="ethereum",
        vasp_name="CoinDCX",
        compliance_email="nodal.officer@coindcx.com",
        exchange_uid="UID_CDX_99214",
        stolen_amount_usdt=15000.0,
        statutory_deadline_hours=24
    )

    res = generator.generate_sec_94_bnss(req)
    assert res.document_type == "SECTION_94_BNSS_STATUTORY_NOTICE"
    assert "SECTION 94 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA" in res.html_content
    assert "CoinDCX" in res.html_content
    assert "nodal.officer@coindcx.com" in res.html_content
    assert "24 HOURS (URGENT)" in res.html_content
    assert len(res.sha256_digest) == 64


def test_generate_section_65b_bsa_certificate():
    """Verify compilation of court-admissible Section 65B BSA electronic evidence certificate."""
    generator = LegalNoticeGenerator()
    req = Section65BBSARequest(
        complaint_id="NCRP-2026-98124",
        suspect_address="0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        blockchain="ethereum",
        rpc_endpoint_used="https://eth.llamarpc.com"
    )

    res = generator.generate_sec_65b_bsa(req)
    assert res.document_type == "SECTION_65B_BSA_EVIDENCE_CERTIFICATE"
    assert "BHARATIYA SAKSHYA ADHINIYAM (BSA), 2023" in res.html_content
    assert "SHA-256 RPC Response Digest" in res.html_content
    assert len(res.sha256_digest) == 64


def test_legal_endpoints():
    """Verify REST API legal endpoints."""
    # 1. P2P Restitch Endpoint
    res_p2p = client.post(
        "/api/v1/legal/p2p-restitch",
        params={
            "complaint_id": "NCRP-2026-98124",
            "vasp_uid": "UID_CDX_99214",
            "tx_hash": "0xsample_tx"
        }
    )
    assert res_p2p.status_code == 200
    assert res_p2p.json()["bank_account_number"] == "50100492817291"

    # 2. CFCFRMS Freeze Endpoint
    res_frz = client.post(
        "/api/v1/legal/cfcfrms-freeze",
        params={
            "complaint_id": "NCRP-2026-98124",
            "vasp_uid": "UID_CDX_99214",
            "tx_hash": "0xsample_tx"
        }
    )
    assert res_frz.status_code == 201
    assert res_frz.json()["target_bank_name"] == "HDFC Bank Ltd"

    # 3. Export Section 94 BNSS
    req_bnss = {
        "complaint_id": "NCRP-2026-98124",
        "suspect_address": "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        "blockchain": "ethereum",
        "vasp_name": "CoinDCX",
        "compliance_email": "nodal.officer@coindcx.com"
    }
    res_b = client.post("/api/v1/legal/export-sec94-bnss", json=req_bnss)
    assert res_b.status_code == 200
    assert "SECTION 94" in res_b.json()["html_content"]
