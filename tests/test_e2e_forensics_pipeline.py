"""End-to-End System Integration Test for Complete CryptoRecon Pipeline (Modules 1-7)."""

import pytest  # pyrefly: ignore # type: ignore
from datetime import datetime, timezone
from starlette.testclient import TestClient  # pyrefly: ignore # type: ignore
from app.main import app  # pyrefly: ignore # type: ignore

client = TestClient(app)


def test_full_e2e_forensics_pipeline():
    """Execute end-to-end multi-chain forensic reconnaissance lifecycle."""
    complaint_id = "NCRP-2026-SIH26183-FINAL"
    suspect_address = "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976"
    blockchain = "ethereum"
    token_contract = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    stolen_usdt = 18500.0

    # -------------------------------------------------------------
    # Step 1: Ingestion & Time-Lock Pre-Processor (Module 1)
    # -------------------------------------------------------------
    ingest_payload = {
        "complaint_id": complaint_id,
        "suspect_address": suspect_address,
        "blockchain": blockchain,
        "token_contract": token_contract,
        "incident_timestamp_utc": "2026-08-27T10:00:00Z",
        "stolen_amount": stolen_usdt,
        "victim_bank_ref": "HDFC/2026/CYBER/9981"
    }

    res_ingest = client.post("/api/v1/cases/ingest", json=ingest_payload)
    assert res_ingest.status_code == 201
    ingest_data = res_ingest.json()
    assert ingest_data["complaint_id"] == complaint_id
    assert ingest_data["lookup_latency_ms"] < 2.0

    # -------------------------------------------------------------
    # Step 2: Multi-Hop Traversal with CFR Dynamic Pruning (Module 2 & 3)
    # -------------------------------------------------------------
    trace_payload = {
        "suspect_address": suspect_address,
        "blockchain": blockchain,
        "token_contract": token_contract,
        "incident_timestamp_utc": "2026-08-27T10:00:00Z",
        "total_stolen_amount": stolen_usdt,
        "max_hops": 3,
        "cfr_min_floor_usdt": 50.0,
        "cfr_dilution_factor": 1.5,
        "mule_split_threshold": 5
    }

    res_trace = client.post("/api/v1/traversal/trace", json=trace_payload)
    assert res_trace.status_code == 200
    trace_data = res_trace.json()
    assert trace_data["total_nodes"] >= 3
    assert trace_data["cfr_pruned_branches_count"] >= 1
    assert any("CoinDCX" in vasp for vasp in trace_data["attributed_vasps"])

    # -------------------------------------------------------------
    # Step 3: Dual-Stack VASP Attribution (Module 5)
    # -------------------------------------------------------------
    attr_payload = {
        "address": "0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf",
        "blockchain": blockchain
    }
    res_attr = client.post("/api/v1/attribution/inspect", json=attr_payload)
    assert res_attr.status_code == 200
    attr_data = res_attr.json()
    assert "CoinDCX" in attr_data["attributed_vasp"]
    assert attr_data["recommended_action"] == "DISPATCH_SEC_94_BNSS_NOTICE"

    # -------------------------------------------------------------
    # Step 4: Graph AI/ML Risk Scoring & Typology (Module 4)
    # -------------------------------------------------------------
    ml_payload = {
        "address": suspect_address,
        "blockchain": blockchain,
        "complaint_id": complaint_id,
        "historical_transactions": [
            {"from_address": "0xVictim", "to_address": suspect_address, "amount": stolen_usdt, "timestamp": 1700000000},
            {"from_address": suspect_address, "to_address": "0xMule1", "amount": 3000.0, "timestamp": 1700000300},
            {"from_address": suspect_address, "to_address": "0xMule2", "amount": 3000.0, "timestamp": 1700000320},
            {"from_address": suspect_address, "to_address": "0xMule3", "amount": 3000.0, "timestamp": 1700000340},
            {"from_address": suspect_address, "to_address": "0xMule4", "amount": 3000.0, "timestamp": 1700000360},
            {"from_address": suspect_address, "to_address": "0xMule5", "amount": 3000.0, "timestamp": 1700000380}
        ]
    }
    res_ml = client.post("/api/v1/ml/risk-score", json=ml_payload)
    assert res_ml.status_code == 200
    ml_data = res_ml.json()
    assert ml_data["risk_score"] >= 65
    assert ml_data["primary_typology"] == "Mule Ring"
    assert ml_data["inference_latency_ms"] < 50.0

    # -------------------------------------------------------------
    # Step 5: Mixer Obfuscation Breakpoint Detection (Module 6)
    # -------------------------------------------------------------
    res_mix = client.get("/api/v1/mixer/inspect", params={"address": "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b"})
    assert res_mix.status_code == 200
    assert res_mix.json()["risk_score"] == 100
    assert res_mix.json()["status"] == "CRYPTOGRAPHIC_BREAKPOINT"

    # -------------------------------------------------------------
    # Step 6: P2P INR Re-Stitching & 1930 CFCFRMS Freeze (Module 7)
    # -------------------------------------------------------------
    res_freeze = client.post(
        "/api/v1/legal/cfcfrms-freeze",
        params={
            "complaint_id": complaint_id,
            "vasp_uid": "UID_CDX_99214",
            "tx_hash": "0xfinal_sweep_hash_99182",
            "victim_bank_ref": "HDFC/2026/CYBER/9981"
        }
    )
    assert res_freeze.status_code == 201
    freeze_data = res_freeze.json()
    assert freeze_data["target_bank_name"] == "HDFC Bank Ltd"
    assert freeze_data["target_account_number"] == "50100492817291"
    assert freeze_data["freeze_amount_inr"] > 0

    # -------------------------------------------------------------
    # Step 7: Statutory Legal Notice & Section 65B BSA Certificate
    # -------------------------------------------------------------
    bnss_payload = {
        "complaint_id": complaint_id,
        "suspect_address": suspect_address,
        "blockchain": blockchain,
        "vasp_name": "CoinDCX",
        "compliance_email": "nodal.officer@coindcx.com",
        "stolen_amount_usdt": stolen_usdt,
        "statutory_deadline_hours": 24
    }
    res_bnss = client.post("/api/v1/legal/export-sec94-bnss", json=bnss_payload)
    assert res_bnss.status_code == 200
    assert "SECTION 94 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA" in res_bnss.json()["html_content"]

    bsa_payload = {
        "complaint_id": complaint_id,
        "suspect_address": suspect_address,
        "blockchain": blockchain
    }
    res_bsa = client.post("/api/v1/legal/export-sec65b-bsa", json=bsa_payload)
    assert res_bsa.status_code == 200
    assert "BHARATIYA SAKSHYA ADHINIYAM" in res_bsa.json()["html_content"]

    # -------------------------------------------------------------
    # Step 8: Dashboard Visualizer Delivery
    # -------------------------------------------------------------
    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200
    assert "CryptoRecon" in res_dash.text
    assert "cytoscape" in res_dash.text
