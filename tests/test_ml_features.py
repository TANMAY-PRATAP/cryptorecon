"""Unit tests for 14-Dimensional Feature Extraction & Node2Vec Embeddings."""

import pytest
import numpy as np
from app.ml.features import (
    calculate_gini_coefficient,
    calculate_degree_entropy,
    generate_node2vec_embedding,
    FeatureExtractor,
)


def test_calculate_gini_coefficient():
    """Verify Gini coefficient calculation on transaction splits."""
    # Perfect equality: all transfers are identical 100 USDT -> Gini is 0.0
    equal_splits = [100.0, 100.0, 100.0, 100.0, 100.0]
    gini_eq = calculate_gini_coefficient(equal_splits)
    assert gini_eq == 0.0

    # High inequality: 1 transfer has 9,990 USDT, 9 transfers have 1 USDT -> Gini > 0.8
    unequal_splits = [1.0] * 9 + [9990.0]
    gini_uneq = calculate_gini_coefficient(unequal_splits)
    assert gini_uneq > 0.80

    # Single transfer / empty
    assert calculate_gini_coefficient([500.0]) == 0.0
    assert calculate_gini_coefficient([]) == 0.0


def test_calculate_degree_entropy():
    """Verify Shannon entropy of degree distribution."""
    # Equal 50/50 fan-in and fan-out -> maximum entropy 1.0
    ent_max = calculate_degree_entropy(in_degree=10, out_degree=10)
    assert round(ent_max, 2) == 1.0

    # Highly skewed degree: 1 in, 99 out -> low entropy
    ent_skew = calculate_degree_entropy(in_degree=1, out_degree=99)
    assert ent_skew < 0.20

    # Edge cases
    assert calculate_degree_entropy(in_degree=0, out_degree=5) == 0.0
    assert calculate_degree_entropy(in_degree=0, out_degree=0) == 0.0


def test_generate_node2vec_embedding():
    """Verify topological Node2Vec embedding generation."""
    emb = generate_node2vec_embedding(
        node_id="0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        degree=12,
        dimension=16
    )
    assert len(emb) == 16
    # Verify L2 norm is approximately 1.0
    norm = np.linalg.norm(emb)
    assert round(norm, 2) == 1.0

    # Verify determinism
    emb_repeat = generate_node2vec_embedding(
        node_id="0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        degree=12,
        dimension=16
    )
    assert emb == emb_repeat


def test_feature_extractor_pipeline():
    """Verify end-to-end 14-dimensional feature extraction from transaction records."""
    target = "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976"
    mock_txs = [
        # Inbound transfer
        {
            "from_address": "0xVictim1",
            "to_address": target,
            "amount": 10000.0,
            "timestamp": 1700000000,
            "gas_funder": "0xBinanceHotWallet"
        },
        # 5 Rapid Outbound Mule Splits (within 10 minutes)
        *[
            {
                "from_address": target,
                "to_address": f"0xMule_{i}",
                "amount": 1900.0,
                "timestamp": 1700000600 + (i * 60)
            }
            for i in range(5)
        ]
    ]

    features = FeatureExtractor.extract_from_transactions(
        target_address=target,
        transactions=mock_txs
    )

    assert features.fan_in_degree == 1
    assert features.fan_out_degree == 5
    assert features.native_gas_dispenser_diversity == 1
    assert features.rapid_dispersion_ratio == 1.0  # All drained within 10 mins (< 1 hr)
    assert features.gini_coefficient_amounts == pytest.approx(0.35, rel=0.1)  # Low inequality smurfing
    assert features.exchange_hop_distance == 2
