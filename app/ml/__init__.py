"""Module 4: Graph-AI/ML Risk & Typology Engine."""

import time
from typing import Dict, Any, Optional, List
from app.schemas.ml import (
    RiskScoringRequest,
    RiskScoringResponse,
    TypologyType,
    StructuralFeatures,
    HITLFeedbackRequest,
    HITLFeedbackResponse,
)
from app.ml.features import FeatureExtractor
from app.ml.classifier import LightGBMTypologyClassifier, CompositeRiskScorer
from app.ml.bootstrap_loader import BootstrapLoader, HITLFeedbackBuffer


class RiskEngine:
    """Unified Graph AI/ML Risk Scoring & Typology Engine."""

    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.classifier = LightGBMTypologyClassifier()
        self.scorer = CompositeRiskScorer()
        self.feedback_buffer = HITLFeedbackBuffer()

    def analyze_wallet(
        self,
        address: str,
        blockchain: str = "ethereum",
        transactions: Optional[List[Dict[str, Any]]] = None,
        is_mixer_direct: bool = False
    ) -> RiskScoringResponse:
        """Run complete AI/ML inference pipeline on suspect wallet."""
        t0 = time.perf_counter()

        # 1. Feature Extraction (14 Dimensions)
        features = self.feature_extractor.extract_from_transactions(
            target_address=address,
            transactions=transactions
        )

        # 2. Classifier Inference
        typology_probs = self.classifier.predict_probabilities(features)

        # 3. Determine Primary Typology
        primary_typology_str = max(typology_probs, key=typology_probs.get)
        primary_typology = TypologyType(primary_typology_str)

        # 4. Composite Risk Score
        risk_score, risk_tier, top_factors = self.scorer.calculate_score(
            features=features,
            typology_probs=typology_probs,
            is_mixer_direct=is_mixer_direct
        )

        latency_ms = (time.perf_counter() - t0) * 1000.0

        # Recommended action
        if is_mixer_direct or risk_score >= 85:
            rec_action = "CRITICAL_FREEZE_AND_SUBPOENA"
        elif risk_score >= 60:
            rec_action = "EXPAND_TRAVERSAL_AND_FLAG"
        elif risk_score >= 30:
            rec_action = "MONITOR_MEMPOOL_OUTFLOWS"
        else:
            rec_action = "NO_IMMEDIATE_ACTION"

        return RiskScoringResponse(
            address=address,
            blockchain=blockchain,
            risk_score=risk_score,
            risk_tier=risk_tier,
            primary_typology=primary_typology,
            typology_probabilities=typology_probs,
            extracted_features=features,
            top_risk_factors=top_factors,
            inference_latency_ms=round(latency_ms, 3),
            is_breakpoint=is_mixer_direct,
            recommended_action=rec_action
        )

    def record_hitl_feedback(self, request: HITLFeedbackRequest) -> HITLFeedbackResponse:
        """Record Human-in-the-Loop investigation outcome and adapt classifier weights."""
        count = self.feedback_buffer.record_feedback(request)
        self.classifier.update_weights(request.confirmed_typology, count)

        return HITLFeedbackResponse(
            status="FEEDBACK_RECORDED",
            feedback_id=f"HITL_{request.complaint_id}_{count}",
            complaint_id=request.complaint_id,
            total_retained_samples=count,
            model_retrained=True,
            message=f"Investigation ground truth logged. Classifier weights updated for {request.confirmed_typology.value}."
        )


_risk_engine_instance: Optional[RiskEngine] = None


def get_risk_engine() -> RiskEngine:
    global _risk_engine_instance
    if _risk_engine_instance is None:
        _risk_engine_instance = RiskEngine()
    return _risk_engine_instance


__all__ = [
    "RiskEngine",
    "get_risk_engine",
    "FeatureExtractor",
    "LightGBMTypologyClassifier",
    "CompositeRiskScorer",
    "BootstrapLoader",
    "HITLFeedbackBuffer",
]
