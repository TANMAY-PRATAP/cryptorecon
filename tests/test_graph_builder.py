"""Unit and Integration tests for Forensic Graph Builder & Traversal API."""

import pytest  # pyrefly: ignore # type: ignore
from starlette.testclient import TestClient  # pyrefly: ignore # type: ignore
from app.main import app  # pyrefly: ignore # type: ignore
from app.traversal.graph_builder import ForensicGraphBuilder, get_risk_color  # pyrefly: ignore # type: ignore
from app.traversal.cfr_engine import MuleClusterDetector  # pyrefly: ignore # type: ignore
from app.schemas.traversal import NodeCategory  # pyrefly: ignore # type: ignore

client = TestClient(app)


def test_risk_color_coding():
    """Verify color coding matches PRD requirements."""
    # Green (<= 35)
    assert get_risk_color(15) == "#10b981"
    assert get_risk_color(35) == "#10b981"

    # Yellow / Amber (36-70)
    assert get_risk_color(40) == "#f59e0b"
    assert get_risk_color(70) == "#f59e0b"

    # Red (>= 71)
    assert get_risk_color(75) == "#ef4444"
    assert get_risk_color(100) == "#ef4444"

    # Purple (Breakpoints / Mixers)
    assert get_risk_color(0, is_breakpoint=True) == "#a855f7"

    # Blue (VASPs)
    assert get_risk_color(0, is_vasp=True) == "#3b82f6"


def test_graph_builder_topology_and_export():
    """Verify multi-hop graph generation, mule cluster embedding and Cytoscape export."""
    builder = ForensicGraphBuilder()

    # Add Root Suspect
    builder.add_wallet_node(
        address="0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        blockchain="ethereum",
        risk_score=90,
        is_suspect=True,
        hop_level=0
    )

    # Add VASP Node
    builder.add_vasp_node(
        address="0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf",
        vasp_name="CoinDCX",
        blockchain="ethereum",
        hop_level=1
    )

    # Add Transfer Edge
    builder.add_transfer_edge(
        source_id="0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        target_id="0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf",
        amount=4500.0,
        token="USDT",
        tx_hash="0xsample_tx_hash_12345678"
    )

    # Add Mule Cluster
    detector = MuleClusterDetector()
    mule_cluster = detector.create_mule_cluster(
        parent_address="0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        outflows=[
            {"to_address": f"0xmule_{i}", "amount": 100.0} for i in range(5)
        ],
        parent_total_volume=500.0
    )
    builder.add_mule_cluster_node(mule_cluster, "ethereum", hop_level=1)

    # Export to Cytoscape JSON
    cyto = builder.to_cytoscape_json()
    assert cyto.total_nodes == 3  # Root, VASP, MuleCluster
    assert cyto.total_edges == 1
    assert cyto.mule_clusters_count == 1
    assert "CoinDCX" in cyto.attributed_vasps

    # Verify Cypher export
    cypher_queries = builder.to_cypher_queries()
    assert len(cypher_queries) >= 4
    assert any("MuleCluster" in q for q in cypher_queries)
    assert any("CoinDCX" in q for q in cypher_queries)


def test_traversal_api_endpoint():
    """Verify POST /api/v1/traversal/trace executes end-to-end multi-hop traversal."""
    payload = {
        "suspect_address": "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        "blockchain": "ethereum",
        "token_contract": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "incident_timestamp_utc": "2026-08-27T10:00:00Z",
        "total_stolen_amount": 15000.0,
        "max_hops": 3,
        "cfr_min_floor_usdt": 50.0,
        "cfr_dilution_factor": 1.5,
        "mule_split_threshold": 5
    }

    response = client.post("/api/v1/traversal/trace", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "elements" in data
    assert data["total_nodes"] >= 2
    assert data["total_edges"] >= 1
    assert data["cfr_pruned_branches_count"] >= 1  # Verify dust was pruned by CFR


def test_attribution_inspect_api_endpoint():
    """Verify POST /api/v1/attribution/inspect endpoint."""
    # Test CoinDCX
    payload_cdx = {
        "address": "0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf",
        "blockchain": "ethereum"
    }
    res_cdx = client.post("/api/v1/attribution/inspect", json=payload_cdx)
    assert res_cdx.status_code == 200
    data_cdx = res_cdx.json()
    assert "CoinDCX" in data_cdx["attributed_vasp"]
    assert data_cdx["attribution_tier"] == "TIER_0_DIRECT_BLOOM"

    # Test Bitcoin Binance Cold Storage
    payload_btc = {
        "address": "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s",
        "blockchain": "bitcoin"
    }
    res_btc = client.post("/api/v1/attribution/inspect", json=payload_btc)
    assert res_btc.status_code == 200
    data_btc = res_btc.json()
    assert "Binance" in data_btc["attributed_vasp"]
    assert data_btc["attribution_tier"] == "TIER_0_DIRECT_BLOOM"


def test_traversal_custom_wallet_dynamic():
    """Verify custom address traversal returns accurate root node without hardcoded fake counterparties."""
    custom_addr = "0x1234567890abcdef1234567890abcdef12345678"
    payload = {
        "suspect_address": custom_addr,
        "blockchain": "ethereum",
        "total_stolen_amount": 5000.0,
        "max_hops": 2
    }
    response = client.post("/api/v1/traversal/trace", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "elements" in data
    # Root node must represent the custom address
    root = [el for el in data["elements"] if el.get("data", {}).get("is_suspect")]
    assert len(root) == 1
    assert root[0]["data"]["address"].lower() == custom_addr.lower()
