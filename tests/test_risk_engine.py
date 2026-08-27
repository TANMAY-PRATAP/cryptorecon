"""Unit tests for LightGBM Classifier, Composite Risk Scorer & HITL Retraining."""

import pytest
from app.schemas.ml import TypologyType, StructuralFeatures, HITLFeedbackRequest
from app.ml.classifier import LightGBMTypologyClassifier, CompositeRiskScorer
from app.ml.bootstrap_loader import BootstrapLoader, HITLFeedbackBuffer
from app.ml import RiskEngine


def test_mule_ring_typology_prediction():
    """Verify Mule-Ring pattern detection (fan-out >= 5, rapid dispersion)."""
    classifier = LightGBMTypologyClassifier()
    features = StructuralFeatures(
        fan_in_degree=1,
        fan_out_degree=6,
        rapid_dispersion_ratio=0.8,
        gini_coefficient_amounts=0.15,
        median_holding_duration_seconds=300
    )

    probs = classifier.predict_probabilities(features)
    assert probs[TypologyType.MULE_RING.value] > 0.40
    assert max(probs, key=probs.get) == TypologyType.MULE_RING.value


def test_ransomware_typology_prediction():
    """Verify Ransomware pattern detection (long holding duration, low fan-out)."""
    classifier = LightGBMTypologyClassifier()
    features = StructuralFeatures(
        fan_in_degree=1,
        fan_out_degree=2,
        median_holding_duration_seconds=172800,  # 48 hours holding
        rapid_dispersion_ratio=0.0
    )

    probs = classifier.predict_probabilities(features)
    assert probs[TypologyType.RANSOMWARE.value] > 0.35


def test_darknet_market_typology_prediction():
    """Verify Darknet Market pattern detection (high address reuse, fan-in)."""
    classifier = LightGBMTypologyClassifier()
    features = StructuralFeatures(
        fan_in_degree=15,
        fan_out_degree=3,
        historical_address_reuse_count=8,
        transaction_burst_velocity=12.0
    )

    probs = classifier.predict_probabilities(features)
    assert probs[TypologyType.DARKNET_MARKET.value] > 0.40


def test_composite_risk_scorer_tiers():
    """Verify 0-100 composite risk scoring and tiers."""
    # 1. High risk mule case
    features_high = StructuralFeatures(
        fan_in_degree=1,
        fan_out_degree=6,
        rapid_dispersion_ratio=0.9
    )
    probs_high = {
        TypologyType.MULE_RING.value: 0.85,
        TypologyType.UNFLAGGED.value: 0.15
    }
    score_h, tier_h, factors_h = CompositeRiskScorer.calculate_score(features_high, probs_high)
    assert score_h >= 71
    assert tier_h == "HIGH"
    assert any("Mule-Ring" in f for f in factors_h)

    # 2. Critical Obfuscation Breakpoint
    score_c, tier_c, _ = CompositeRiskScorer.calculate_score(features_high, probs_high, is_mixer_direct=True)
    assert score_c == 100
    assert tier_c == "CRITICAL_OBFUSCATION"

    # 3. Clean wallet
    features_clean = StructuralFeatures(fan_in_degree=1, fan_out_degree=1)
    probs_clean = {TypologyType.UNFLAGGED.value: 0.90}
    score_l, tier_l, _ = CompositeRiskScorer.calculate_score(features_clean, probs_clean)
    assert score_l <= 30
    assert tier_l == "LOW"


def test_hitl_feedback_and_retraining():
    """Verify recording investigator feedback and updating model weights."""
    engine = RiskEngine()

    feedback_req = HITLFeedbackRequest(
        complaint_id="NCRP-2026-HITL-01",
        suspect_address="0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        blockchain="ethereum",
        confirmed_typology=TypologyType.MULE_RING,
        investigator_badge_id="POLICE_DL_8841",
        notes="Confirmed cyber fraud smurfing mule ring in NCRP investigation."
    )

    res = engine.record_hitl_feedback(feedback_req)
    assert res.status == "FEEDBACK_RECORDED"
    assert res.total_retained_samples >= 1
    assert res.model_retrained is True
    assert engine.classifier.class_weights[TypologyType.MULE_RING] > 1.0


def test_bootstrap_loaders():
    """Verify loading bootstrap datasets."""
    elliptic_data = BootstrapLoader.load_elliptic_samples()
    assert len(elliptic_data) >= 3
    assert elliptic_data[0]["label"] == "illicit"

    ransom_data = BootstrapLoader.load_ransomwhere_clusters()
    assert len(ransom_data) >= 2
    assert "LockBit" in ransom_data[0]["family"]
