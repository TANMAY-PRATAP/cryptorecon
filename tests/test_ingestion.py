"""Integration tests for Module 1 FastAPI Ingestion Pipeline."""

import pytest  # pyrefly: ignore # type: ignore
from starlette.testclient import TestClient  # pyrefly: ignore # type: ignore
from app.main import app  # pyrefly: ignore # type: ignore

client = TestClient(app)


def test_health_and_readiness_endpoints():
    """Verify health and readiness endpoints."""
    # Health check
    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200
    data_h = res_health.json()
    assert data_h["status"] == "healthy"
    assert data_h["service"] == "CryptoRecon"

    # Readiness check
    res_ready = client.get("/api/v1/readiness")
    assert res_ready.status_code == 200
    data_r = res_ready.json()
    assert data_r["status"] == "ready"
    assert data_r["bloom_filter"]["ready"] is True
    assert data_r["bloom_filter"]["indexed_entities"] >= 10


def test_ingest_unknown_suspect_address(sample_valid_evm_case_payload):
    """Test ingestion of unflagged suspect address queued for traversal."""
    response = client.post("/api/v1/cases/ingest", json=sample_valid_evm_case_payload)
    assert response.status_code == 201
    data = response.json()

    assert data["complaint_id"] == sample_valid_evm_case_payload["complaint_id"]
    assert data["status"] in ("QUEUED_FOR_TRAVERSAL", "TAGGED_DIRECT")
    assert data["lookup_latency_ms"] < 2.0
    assert "time_lock_enforced_from_utc" in data

    # Verify retrieval via GET /api/v1/cases/{complaint_id}
    res_get = client.get(f"/api/v1/cases/{sample_valid_evm_case_payload['complaint_id']}")
    assert res_get.status_code == 200
    case_data = res_get.json()
    assert case_data["complaint_id"] == sample_valid_evm_case_payload["complaint_id"]


def test_ingest_known_vasp_direct_tag(sample_known_vasp_payload):
    """Test ingestion of suspect address matching known VASP (CoinDCX) in Bloom filter."""
    response = client.post("/api/v1/cases/ingest", json=sample_known_vasp_payload)
    assert response.status_code == 201
    data = response.json()

    assert data["complaint_id"] == sample_known_vasp_payload["complaint_id"]
    assert data["status"] == "TAGGED_DIRECT"
    assert data["direct_tag_matched"] is True
    assert data["attributed_entity"] is not None
    assert "CoinDCX" in data["attributed_entity"]["entity_name"]
    assert data["attributed_entity"]["compliance_email"] == "nodal.officer@coindcx.com"
    assert data["attributed_entity"]["fiu_registered"] is True
    assert data["lookup_latency_ms"] < 1.0


def test_ingest_invalid_address():
    """Test rejection of malformed EVM address."""
    invalid_payload = {
        "complaint_id": "NCRP-2026-ERR-01",
        "suspect_address": "0xinvalidEthereumAddress123",
        "blockchain": "ethereum",
        "token_contract": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "incident_timestamp_utc": "2026-08-27T10:00:00Z"
    }
    response = client.post("/api/v1/cases/ingest", json=invalid_payload)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_ingest_tron_case(sample_tron_payload):
    """Test TRON address ingestion with Base58Check normalization."""
    response = client.post("/api/v1/cases/ingest", json=sample_tron_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["blockchain"] == "tron"
    assert data["normalized_address"] == sample_tron_payload["suspect_address"]


def test_ingest_bitcoin_case(sample_bitcoin_payload):
    """Test Bitcoin Bech32 address ingestion."""
    response = client.post("/api/v1/cases/ingest", json=sample_bitcoin_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["blockchain"] == "bitcoin"
    assert data["normalized_address"] == sample_bitcoin_payload["suspect_address"].lower()


def test_entity_lookup_endpoint():
    """Test standalone entity lookup endpoint."""
    # Lookup Binance Hot Wallet
    res = client.get(
        "/api/v1/entities/lookup",
        params={
            "address": "0x28c6c06298d514db089934071355e5743bf21d60",
            "blockchain": "ethereum"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["match_found"] is True
    assert data["matched_entity"]["entity_name"] == "Binance 14"
    assert data["lookup_latency_ms"] < 1.0

    # Lookup Unknown Wallet
    res_unk = client.get(
        "/api/v1/entities/lookup",
        params={
            "address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
            "blockchain": "ethereum"
        }
    )
    assert res_unk.status_code == 200
    data_unk = res_unk.json()
    assert data_unk["match_found"] is False
    assert data_unk["matched_entity"] is None
