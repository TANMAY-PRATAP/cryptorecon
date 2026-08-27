"""Unit tests for Cumulative Flow Ratio (CFR) Dynamic Pruning and Mule Detection."""

import pytest
from app.traversal.cfr_engine import CFRPruner, MuleClusterDetector


def test_cfr_pruner_threshold_calculation():
    """Verify CFR dynamic threshold calculation: min(50 USDT, Total / (N_branches * 1.5))."""
    pruner = CFRPruner(min_floor_usdt=50.0, dilution_factor=1.5)

    # Case 1: 10,000 USDT stolen, 5 branches -> 10000 / (5 * 1.5) = 1333.33 -> capped at 50.0 USDT
    t1 = pruner.calculate_threshold(total_stolen_usdt=10000.0, branch_fan_out_count=5)
    assert t1 == 50.0

    # Case 2: 100 USDT stolen, 4 branches -> 100 / (4 * 1.5) = 16.67 USDT -> below floor, returns 16.67 USDT
    t2 = pruner.calculate_threshold(total_stolen_usdt=100.0, branch_fan_out_count=4)
    assert round(t2, 2) == 16.67

    # Case 3: 500 USDT stolen, 10 branches -> 500 / 15 = 33.33 USDT
    t3 = pruner.calculate_threshold(total_stolen_usdt=500.0, branch_fan_out_count=10)
    assert round(t3, 2) == 33.33


def test_cfr_should_traverse():
    """Verify branch flow filtering against threshold."""
    pruner = CFRPruner(min_floor_usdt=50.0, dilution_factor=1.5)

    # 10,000 USDT total, 4 branches -> threshold is 50.0 USDT
    # Branch with 1500.0 USDT should pass
    passes, thresh = pruner.should_traverse(
        branch_amount=1500.0,
        total_stolen_usdt=10000.0,
        branch_fan_out_count=4
    )
    assert passes is True
    assert thresh == 50.0

    # Dust branch with 5.0 USDT should be dropped
    passes_dust, _ = pruner.should_traverse(
        branch_amount=5.0,
        total_stolen_usdt=10000.0,
        branch_fan_out_count=4
    )
    assert passes_dust is False


def test_mule_cluster_detector():
    """Verify smurfing mule cluster identification and aggregation."""
    detector = MuleClusterDetector(split_threshold=5)

    # Less than 5 splits: not a mule cluster
    assert detector.is_mule_cluster(4) is False
    # 5 or more splits: is a mule cluster
    assert detector.is_mule_cluster(5) is True
    assert detector.is_mule_cluster(12) is True

    # Test creating compound MuleClusterDetail
    parent_addr = "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976"
    outflows = [
        {"to_address": f"0xmule_{i}", "amount": 200.0, "current_balance": 180.0, "gas_funder": "0xbinance"}
        for i in range(6)
    ]

    cluster = detector.create_mule_cluster(
        parent_address=parent_addr,
        outflows=outflows,
        parent_total_volume=1200.0
    )

    assert cluster.total_wallets == 6
    assert cluster.total_volume_usdt == 1200.0
    assert len(cluster.members) == 6
    assert cluster.members[0].percentage_of_parent == pytest.approx(16.67, 0.1)
    assert cluster.members[0].gas_funder == "0xbinance"
