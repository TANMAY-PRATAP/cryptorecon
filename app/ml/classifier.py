"""LightGBM-Compatible Typology Classifier & Composite Risk Scorer.

Predicts 0-100 composite risk score and classifies wallet typology into:
- Mule Ring
- Ransomware
- Darknet Market
- Terror Financing
- Unflagged
"""

import time
import math
from typing import Dict, Any, Tuple, List, Optional
from app.schemas.ml import TypologyType, StructuralFeatures, RiskScoringResponse


class LightGBMTypologyClassifier:
    """Ensemble Decision Tree / Gradient-Boosted Classifier for Typology Prediction."""

    def __init__(self):
        # Base class priors / initial bias
        self.class_weights: Dict[TypologyType, float] = {
            TypologyType.MULE_RING: 1.0,
            TypologyType.RANSOMWARE: 1.0,
            TypologyType.DARKNET_MARKET: 1.0,
            TypologyType.TERROR_FINANCING: 1.0,
            TypologyType.UNFLAGGED: 1.0,
        }

    def predict_probabilities(self, features: StructuralFeatures) -> Dict[str, float]:
        """Compute softmax probability distribution across fraud typologies using structural features."""
        scores: Dict[TypologyType, float] = {
            TypologyType.MULE_RING: 0.0,
            TypologyType.RANSOMWARE: 0.0,
            TypologyType.DARKNET_MARKET: 0.0,
            TypologyType.TERROR_FINANCING: 0.0,
            TypologyType.UNFLAGGED: 0.5,
        }

        # 1. Mule Ring Rule Trees: High fan-out, rapid dispersion, low Gini (equal splits)
        if features.fan_out_degree >= 5:
            scores[TypologyType.MULE_RING] += 2.5
        if features.rapid_dispersion_ratio >= 0.4:
            scores[TypologyType.MULE_RING] += 1.8
        if features.gini_coefficient_amounts < 0.35 and features.fan_out_degree >= 3:
            scores[TypologyType.MULE_RING] += 1.5

        # 2. Ransomware Rule Trees: Long holding duration, large volume, Bitcoin peel-chains
        if features.median_holding_duration_seconds >= 86400:  # > 24 hours
            scores[TypologyType.RANSOMWARE] += 1.8
        if features.fan_in_degree == 1 and features.fan_out_degree in (1, 2):
            scores[TypologyType.RANSOMWARE] += 1.2

        # 3. Darknet Market Rule Trees: High address reuse, continuous burst velocity, multi-input fan-in
        if features.historical_address_reuse_count >= 3:
            scores[TypologyType.DARKNET_MARKET] += 2.2
        if features.fan_in_degree >= 8:
            scores[TypologyType.DARKNET_MARKET] += 1.6

        # 4. Terror Financing Rule Trees: High degree entropy, privacy mix interaction, burst velocity
        if features.privacy_mixer_interaction_ratio > 0.1:
            scores[TypologyType.TERROR_FINANCING] += 2.0
            scores[TypologyType.DARKNET_MARKET] += 1.0
        if features.degree_entropy > 0.8:
            scores[TypologyType.TERROR_FINANCING] += 1.2

        # Apply custom dynamic class weights (from HITL retraining)
        for c in scores:
            scores[c] *= self.class_weights.get(c, 1.0)

        # Softmax normalization
        max_score = max(scores.values())
        exp_scores = {c: math.exp(s - max_score) for c, s in scores.items()}
        sum_exp = sum(exp_scores.values())

        return {c.value: round(exp_scores[c] / sum_exp, 4) for c in scores}

    def update_weights(self, confirmed_typology: TypologyType, feedback_count: int) -> None:
        """Human-in-the-Loop weight adaptation."""
        boost = 1.0 + min(0.5, feedback_count * 0.05)
        self.class_weights[confirmed_typology] = boost


class CompositeRiskScorer:
    """Calculates 0-100 Composite Risk Score and Top Risk Factors."""

    @staticmethod
    def calculate_score(
        features: StructuralFeatures,
        typology_probs: Dict[str, float],
        is_mixer_direct: bool = False
    ) -> Tuple[int, str, List[str]]:
        """Calculate score in [0, 100], risk tier, and human-readable risk factors."""
        if is_mixer_direct:
            return 100, "CRITICAL_OBFUSCATION", ["Direct interaction with sanctioned Privacy Mixer / Breakpoint pool."]

        base_score = 0.0
        risk_factors: List[str] = []

        # 1. Typology Probability Impact (up to 40 pts)
        mule_prob = typology_probs.get(TypologyType.MULE_RING.value, 0.0)
        ransom_prob = typology_probs.get(TypologyType.RANSOMWARE.value, 0.0)
        darknet_prob = typology_probs.get(TypologyType.DARKNET_MARKET.value, 0.0)
        terror_prob = typology_probs.get(TypologyType.TERROR_FINANCING.value, 0.0)

        max_fraud_prob = max(mule_prob, ransom_prob, darknet_prob, terror_prob)
        base_score += max_fraud_prob * 45.0

        if mule_prob >= 0.4:
            risk_factors.append(f"Smurfing Mule-Ring signature detected ({mule_prob * 100:.1f}% confidence).")
        if ransom_prob >= 0.4:
            risk_factors.append(f"Ransomware deposit / peel-chain pattern detected ({ransom_prob * 100:.1f}% confidence).")
        if darknet_prob >= 0.4:
            risk_factors.append(f"Darknet vendor multi-counterparty reuse pattern ({darknet_prob * 100:.1f}% confidence).")
        if terror_prob >= 0.4:
            risk_factors.append(f"High-entropy obfuscation / terror funding signature ({terror_prob * 100:.1f}% confidence).")

        # 2. Rapid Dispersion Penalty (up to 20 pts)
        if features.rapid_dispersion_ratio >= 0.5:
            base_score += features.rapid_dispersion_ratio * 20.0
            risk_factors.append(f"Rapid fund dispersion: {features.rapid_dispersion_ratio * 100:.0f}% of funds drained in <1 hour.")

        # 3. Privacy Mixer Intermediary Penalty (up to 25 pts)
        if features.privacy_mixer_interaction_ratio > 0.0:
            base_score += features.privacy_mixer_interaction_ratio * 30.0
            risk_factors.append("Downstream interaction with privacy mixing protocol.")

        # 4. Burst Velocity & Fan-out (up to 15 pts)
        if features.fan_out_degree >= 5:
            base_score += 15.0
            risk_factors.append(f"High fan-out degree ({features.fan_out_degree} distinct recipient addresses).")
        elif features.transaction_burst_velocity > 10.0:
            base_score += 10.0
            risk_factors.append(f"High transaction burst velocity ({features.transaction_burst_velocity:.1f} tx/hr).")

        final_score = int(min(100, max(0, round(base_score))))

        if final_score >= 71:
            tier = "HIGH"
        elif final_score >= 31:
            tier = "MEDIUM"
        else:
            tier = "LOW"

        if not risk_factors:
            risk_factors.append("No significant illicit behavioral heuristics triggered.")

        return final_score, tier, risk_factors
