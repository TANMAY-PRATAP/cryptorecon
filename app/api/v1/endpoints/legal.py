"""API Endpoints for Asset Recovery, P2P Re-Stitching & Legal Notice PDF Generation."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import HTMLResponse
from app.schemas.legal import (
    P2PCounterpartyRecord,
    CFCFRMSFreezePayload,
    Section94BNSSRequest,
    Section65BBSARequest,
    LegalExportResponse,
)
from app.legal import P2PRestitcher, LegalNoticeGenerator, get_legal_generator

router = APIRouter(prefix="/legal", tags=["Asset Recovery & Legal Dispatch"])


@router.post(
    "/p2p-restitch",
    response_model=P2PCounterpartyRecord,
    status_code=status.HTTP_200_OK,
    summary="Re-stitch VASP cashout UID to P2P Bank Account and UPI VPA"
)
async def restitch_p2p_details(
    complaint_id: str = Query(..., description="NCRP Complaint ID"),
    vasp_uid: str = Query(..., description="VASP internal deposit UID or Tag"),
    tx_hash: str = Query(..., description="Blockchain sweep transaction hash")
) -> P2PCounterpartyRecord:
    """Extract counterparty Bank Account, IFSC, and UPI VPA linked to exchange cashout."""
    return P2PRestitcher.restitch_p2p_order(
        complaint_id=complaint_id,
        vasp_uid=vasp_uid,
        tx_hash=tx_hash
    )


@router.post(
    "/cfcfrms-freeze",
    response_model=CFCFRMSFreezePayload,
    status_code=status.HTTP_201_CREATED,
    summary="Generate 1930 / I4C CFCFRMS Banking Freeze Injection Payload"
)
async def generate_cfcfrms_freeze(
    complaint_id: str = Query(..., description="NCRP Complaint ID"),
    vasp_uid: str = Query(..., description="VASP deposit UID"),
    tx_hash: str = Query(..., description="Blockchain sweep tx hash"),
    victim_bank_ref: Optional[str] = Query(default=None)
) -> CFCFRMSFreezePayload:
    """Generate structured payload for direct 1930 / I4C CFCFRMS banking lien injection."""
    record = P2PRestitcher.restitch_p2p_order(complaint_id, vasp_uid, tx_hash)
    return P2PRestitcher.generate_cfcfrms_payload(record, tx_hash, victim_bank_ref)


@router.post(
    "/export-sec94-bnss",
    response_model=LegalExportResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Section 94 BNSS Statutory Freezing Notice"
)
async def export_section_94_bnss(
    request: Section94BNSSRequest,
    generator: LegalNoticeGenerator = Depends(get_legal_generator)
) -> LegalExportResponse:
    """Compile and export court-admissible Section 94 BNSS Notice with 24-hr compliance deadline."""
    return generator.generate_sec_94_bnss(request)


@router.post(
    "/export-sec65b-bsa",
    response_model=LegalExportResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Section 65B BSA Electronic Evidence Certificate"
)
async def export_section_65b_bsa(
    request: Section65BBSARequest,
    generator: LegalNoticeGenerator = Depends(get_legal_generator)
) -> LegalExportResponse:
    """Compile Section 65B BSA Certificate with SHA-256 RPC digests and Merkle proofs."""
    return generator.generate_sec_65b_bsa(request)


@router.get(
    "/section94-bnss",
    response_class=HTMLResponse,
    summary="Download Section 94 BNSS Statutory Notice (GET)"
)
async def download_section_94_bnss(
    complaint_id: str = Query("NCRP-2026-98124", description="Complaint ID"),
    suspect_address: str = Query(..., description="Suspect or VASP address"),
    blockchain: str = Query("ethereum", description="Blockchain network"),
    vasp_name: str = Query("CoinDCX", description="VASP Name"),
    compliance_email: str = Query("nodal.officer@coindcx.com", description="Compliance Email"),
    stolen_amount_usdt: float = Query(15000.0, description="Stolen amount in USDT"),
    generator: LegalNoticeGenerator = Depends(get_legal_generator)
) -> HTMLResponse:
    """Return direct rendered HTML of Section 94 BNSS Freezing Notice."""
    req = Section94BNSSRequest(
        complaint_id=complaint_id,
        suspect_address=suspectAddress if (suspectAddress := suspect_address) else "0x00",
        blockchain=blockchain,
        vasp_name=vasp_name,
        compliance_email=compliance_email,
        stolen_amount_usdt=stolen_amount_usdt
    )
    result = generator.generate_sec_94_bnss(req)
    return HTMLResponse(
        content=result.html_content,
        headers={"Content-Disposition": f'inline; filename="Sec94_BNSS_{complaint_id}.html"'}
    )


@router.get(
    "/section65b-bsa",
    response_class=HTMLResponse,
    summary="Download Section 65B BSA Evidence Certificate (GET)"
)
async def download_section_65b_bsa(
    case_id: Optional[str] = Query(None, description="Complaint / Case ID"),
    complaint_id: Optional[str] = Query(None, description="Complaint ID"),
    suspect_address: Optional[str] = Query("0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976"),
    blockchain: str = Query("ethereum"),
    investigator_name: str = Query("Cyber Crime Cell Forensic Unit", description="Investigator Name"),
    generator: LegalNoticeGenerator = Depends(get_legal_generator)
) -> HTMLResponse:
    """Return direct rendered HTML of Section 65B BSA Evidence Certificate."""
    cid = case_id or complaint_id or "NCRP-2026-98124"
    req = Section65BBSARequest(
        complaint_id=cid,
        suspect_address=suspect_address or "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        blockchain=blockchain,
        investigator_name=investigator_name
    )
    result = generator.generate_sec_65b_bsa(req)
    return HTMLResponse(
        content=result.html_content,
        headers={"Content-Disposition": f'inline; filename="Sec65B_BSA_{cid}.html"'}
    )
