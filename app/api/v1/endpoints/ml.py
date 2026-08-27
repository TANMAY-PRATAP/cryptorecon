"""FastAPI Endpoints for Graph-AI/ML Risk Engine and Mixer Breakpoint Resolver."""

from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.schemas.ml import (
    RiskScoringRequest,
    RiskScoringResponse,
    HITLFeedbackRequest,
    HITLFeedbackResponse,
    MixerInspectionResponse,
    WatchdogSubscriptionRequest,
    WatchdogSubscriptionResponse,
    WatchdogAlert,
)
from app.ml import RiskEngine, get_risk_engine
from app.mixer import MixerResolver, MempoolMixerWatchdog, get_watchdog

router = APIRouter(tags=["Graph AI/ML Risk & Mixer Breakpoints"])


@router.post(
    "/ml/risk-score",
    response_model=RiskScoringResponse,
    status_code=status.HTTP_200_OK,
    summary="Compute 0-100 Risk Score & Typology Classification"
)
async def compute_risk_score(
    request: RiskScoringRequest,
    risk_engine: RiskEngine = Depends(get_risk_engine)
) -> RiskScoringResponse:
    """Extract 14 structural features and predict 0-100 risk score & typology."""
    mixer_inspection = MixerResolver.inspect(request.address, request.blockchain)

    return risk_engine.analyze_wallet(
        address=request.address,
        blockchain=request.blockchain,
        transactions=request.historical_transactions,
        is_mixer_direct=mixer_inspection.is_mixer
    )


@router.post(
    "/ml/feedback",
    response_model=HITLFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Human-in-the-Loop verified investigation outcome"
)
async def submit_hitl_feedback(
    request: HITLFeedbackRequest,
    risk_engine: RiskEngine = Depends(get_risk_engine)
) -> HITLFeedbackResponse:
    """Record 1930 / I4C verified investigation ground truth and adapt model weights."""
    return risk_engine.record_hitl_feedback(request)


@router.get(
    "/mixer/inspect",
    response_model=MixerInspectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Inspect address for Mixer & Cryptographic Breakpoint status"
)
async def inspect_mixer_address(
    address: str = Query(..., description="Target wallet/contract address"),
    blockchain: str = Query(default="ethereum", description="Target blockchain network")
) -> MixerInspectionResponse:
    """Check if address is a known privacy mixer (Tornado, Railgun, CoinJoin)."""
    return MixerResolver.inspect(address, blockchain)


@router.post(
    "/mixer/watchdog/subscribe",
    response_model=WatchdogSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subscribe dormant wallet to 30-day Mempool Watchdog"
)
async def subscribe_watchdog(
    request: WatchdogSubscriptionRequest,
    watchdog: MempoolMixerWatchdog = Depends(get_watchdog)
) -> WatchdogSubscriptionResponse:
    """Register wallet address for active mempool listening and mixer exit alerts."""
    return await watchdog.subscribe(request)


@router.get(
    "/mixer/watchdog/alerts",
    response_model=List[WatchdogAlert],
    status_code=status.HTTP_200_OK,
    summary="List recent Mempool Watchdog alerts"
)
async def list_watchdog_alerts(
    limit: int = Query(default=50, ge=1, le=100),
    watchdog: MempoolMixerWatchdog = Depends(get_watchdog)
) -> List[WatchdogAlert]:
    """Retrieve recent mempool movements and mixer withdrawal alerts."""
    return await watchdog.list_alerts(limit=limit)
