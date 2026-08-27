"""API Endpoints for Multi-Hop Forensic Traversal and Dual-Stack Attribution."""

from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.traversal import (
    TraversalRequest,
    CytoscapeGraphResponse,
    AttributionInspectRequest,
    AttributionInspectResponse,
)
from app.traversal.traversal_service import TraversalService
from app.attribution import get_attributor, DualStackAttributor

router = APIRouter(tags=["Forensic Traversal & Attribution"])


@router.post(
    "/traversal/trace",
    response_model=CytoscapeGraphResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute multi-hop traversal with CFR dynamic pruning"
)
async def trace_fund_flow(
    request: TraversalRequest
) -> CytoscapeGraphResponse:
    """Execute multi-hop on-chain forensic traversal.
    
    1. Traverses up to max_hops from suspect address.
    2. Applies Dynamic CFR Pruning Formula: Branch Flow >= min(50, Total/(N_branches * 1.5)).
    3. Collapses >= 5 intermediate mule splits into a compound MuleCluster node.
    4. Applies Dual-Stack VASP Attribution at each hop.
    5. Returns Cytoscape.js compatible graph elements.
    """
    service = TraversalService()
    try:
        return await service.trace_case(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forensic traversal failed: {str(e)}"
        )


@router.post(
    "/attribution/inspect",
    response_model=AttributionInspectResponse,
    status_code=status.HTTP_200_OK,
    summary="Inspect wallet using Dual-Stack VASP Attribution"
)
async def inspect_vasp_attribution(
    request: AttributionInspectRequest,
    attributor: DualStackAttributor = Depends(get_attributor)
) -> AttributionInspectResponse:
    """Run Dual-Stack Attribution against a specific address.
    
    - EVM / TRON: Tier 1 Gas Ancestry -> Tier 2 Contract Factory -> Tier 3 Omnibus Sweep.
    - Bitcoin: Tier 1 CIOH Cluster Match -> Tier 2 HD Derivation -> Tier 3 Subpoena Escalation.
    """
    try:
        return attributor.inspect_address(
            address=request.address,
            blockchain=request.blockchain
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attribution inspection failed: {str(e)}"
        )
