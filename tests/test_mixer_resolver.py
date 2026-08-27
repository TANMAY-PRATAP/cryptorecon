"""Unit and Integration tests for Mixer Resolver, Mempool Watchdog & ML API Endpoints."""

import pytest
from starlette.testclient import TestClient
from app.main import app
from app.mixer.resolver import MixerResolver
from app.mixer.watchdog import MempoolMixerWatchdog
from app.schemas.ml import WatchdogSubscriptionRequest

client = TestClient(app)


def test_mixer_resolver_tornado_cash():
    """Verify detection of Tornado Cash router and pool addresses."""
    # Tornado Cash Router
    res_router = MixerResolver.inspect("0xd90e2f925da726b50c4ed8d0fb90ad053324f31b", "ethereum")
    assert res_router.is_mixer is True
    assert res_router.risk_score == 100
    assert res_router.status == "CRYPTOGRAPHIC_BREAKPOINT"
    assert res_router.break_point_flag is True
    assert "Tornado Cash" in res_router.protocol_name

    # Tornado Cash 1 ETH Pool
    res_pool = MixerResolver.inspect("0x47ce0c6ed5b0ce3d3a51fdb1c52dc66a7c3c2936", "ethereum")
    assert res_pool.is_mixer is True
    assert res_pool.risk_score == 100
    assert res_pool.break_point_flag is True


def test_mixer_resolver_railgun():
    """Verify detection of Railgun privacy contract."""
    res_railgun = MixerResolver.inspect("0xfa8449189744799aed7cb7bb47470f4f107d706b", "ethereum")
    assert res_railgun.is_mixer is True
    assert res_railgun.risk_score == 100
    assert "Railgun" in res_railgun.protocol_name


def test_mixer_resolver_clean_wallet():
    """Verify clean wallet does not trigger mixer flag."""
    res_clean = MixerResolver.inspect("0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976", "ethereum")
    assert res_clean.is_mixer is False
    assert res_clean.risk_score == 0
    assert res_clean.break_point_flag is False


@pytest.mark.asyncio
async def test_mempool_watchdog_subscription_and_alerts():
    """Verify Mempool Watchdog subscription and real-time alert emission."""
    watchdog = MempoolMixerWatchdog()
    req = WatchdogSubscriptionRequest(
        target_address="0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        blockchain="ethereum",
        complaint_id="NCRP-2026-98124",
        monitoring_duration_days=30
    )

    sub_res = await watchdog.subscribe(req)
    assert sub_res.active is True
    assert sub_res.subscription_id.startswith("SUB_ETHEREUM_")

    # Emit exit alert
    alert = await watchdog.emit_alert(
        subscription_id=sub_res.subscription_id,
        event_type="MIXER_EXIT",
        detected_tx_hash="0xexit_tx_9988776655",
        amount=5.0,
        token="ETH",
        counterparty="0xRelayerGasStation"
    )
    assert alert.event_type == "MIXER_EXIT"
    assert alert.amount == 5.0

    alerts_list = await watchdog.list_alerts()
    assert len(alerts_list) == 1
    assert alerts_list[0].alert_id == alert.alert_id


def test_ml_risk_score_api_endpoint():
    """Verify POST /api/v1/ml/risk-score endpoint."""
    payload = {
        "address": "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        "blockchain": "ethereum",
        "historical_transactions": [
            {
                "from_address": "0xVictim1",
                "to_address": "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
                "amount": 25000.0,
                "timestamp": 1700000000
            },
            *[
                {
                    "from_address": "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
                    "to_address": f"0xMule_{i}",
                    "amount": 4000.0,
                    "timestamp": 1700000300 + (i * 30)
                }
                for i in range(6)
            ]
        ]
    }

    res = client.post("/api/v1/ml/risk-score", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["risk_score"] >= 60
    assert data["primary_typology"] == "Mule Ring"
    assert "extracted_features" in data
    assert data["extracted_features"]["fan_out_degree"] == 6
    assert data["inference_latency_ms"] < 50.0  # Engineering benchmark: <= 45 ms


def test_mixer_inspect_api_endpoint():
    """Verify GET /api/v1/mixer/inspect endpoint."""
    # Test Tornado Cash
    res_tc = client.get("/api/v1/mixer/inspect", params={"address": "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b"})
    assert res_tc.status_code == 200
    data_tc = res_tc.json()
    assert data_tc["is_mixer"] is True
    assert data_tc["risk_score"] == 100
    assert data_tc["break_point_flag"] is True

    # Test clean address
    res_clean = client.get("/api/v1/mixer/inspect", params={"address": "0x5555555555555555555555555555555555555555"})
    assert res_clean.status_code == 200
    data_clean = res_clean.json()
    assert data_clean["is_mixer"] is False
    assert data_clean["risk_score"] == 0


def test_watchdog_subscription_api_endpoint():
    """Verify POST /api/v1/mixer/watchdog/subscribe and alert retrieval."""
    req_payload = {
        "target_address": "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        "blockchain": "ethereum",
        "complaint_id": "NCRP-2026-98124",
        "monitoring_duration_days": 30
    }
    res_sub = client.post("/api/v1/mixer/watchdog/subscribe", json=req_payload)
    assert res_sub.status_code == 201
    data_sub = res_sub.json()
    assert data_sub["active"] is True
    assert data_sub["subscription_id"].startswith("SUB_")

    # List alerts
    res_alerts = client.get("/api/v1/mixer/watchdog/alerts")
    assert res_alerts.status_code == 200
    assert isinstance(res_alerts.json(), list)
