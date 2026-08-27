"""Module 1: Ingestion & Time-Lock Pre-Processor Endpoints."""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_filter, get_redis, get_case_store
from app.core.bloom_filter import InvertedBloomFilter
from app.core.validators import (
    validate_chain_address,
    validate_incident_timelock,
)
from app.schemas.case import (
    CaseIngestRequest,
    CaseIngestResponse,
    CaseStatus,
    CaseDetail,
    CFRPruningConfig,
)
from app.schemas.chain import Blockchain
from app.storage.redis_client import RedisManager
from app.storage.memory_store import MemoryCaseStore

router = APIRouter(prefix="/cases", tags=["Case Ingestion & Validation"])


@router.post("/ingest", response_model=CaseIngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_case(
    request: CaseIngestRequest,
    bloom: InvertedBloomFilter = Depends(get_filter),
    redis_mgr: RedisManager = Depends(get_redis),
    case_store: MemoryCaseStore = Depends(get_case_store)
) -> CaseIngestResponse:
    """Ingest suspect wallet from 1930 / NCRP / SAHYOG Gateway.
    
    1. Address format verification (EIP-55 for EVM, Base58Check for TRON/BTC).
    2. Enforces Time-Lock boundary (T_incident).
    3. Executes O(1) Inverted Bloom Filter lookup (<= 1ms).
    4. Routes to Direct Tag Attribution OR Queues for Multi-Chain RPC Engine.
    """
    # 1. Address Format Verification
    validation_result = validate_chain_address(request.suspect_address, request.blockchain)
    if not validation_result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "ADDRESS_VALIDATION_FAILED",
                "blockchain": request.blockchain,
                "address": request.suspect_address,
                "message": validation_result.error_message
            }
        )

    # 2. Time-Lock Pre-Processor Rule
    is_valid_time, time_err = validate_incident_timelock(request.incident_timestamp_utc)
    if not is_valid_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "TIMELOCK_VALIDATION_FAILED",
                "incident_timestamp_utc": request.incident_timestamp_utc.isoformat(),
                "message": time_err
            }
        )

    normalized_address = validation_result.normalized_address
    chain_name = validation_result.blockchain.value

    # 3. Query In-Memory Inverted Bloom Filter (<= 1ms)
    matched, entity, latency_ms = bloom.lookup(chain_name, normalized_address)

    # 4. Route Attribution or Queue for Multi-Chain RPC Traversal
    task_id: Optional[str] = None
    if matched and entity is not None:
        case_status = CaseStatus.TAGGED_DIRECT
        message = f"Immediate VASP/Entity Tag Attribution: Matched '{entity.entity_name}' ({entity.entity_type.value}) in {latency_ms:.3f} ms."
        risk_score = entity.risk_rating
        attributed_vasp = entity.entity_name
    else:
        case_status = CaseStatus.QUEUED_FOR_TRAVERSAL
        message = f"Unknown entity. Case successfully validated and queued for Multi-Chain Micro-Batch RPC Traversal."
        risk_score = 0
        attributed_vasp = None
        
        # Enqueue for asynchronous traversal engine
        queue_payload = {
            "complaint_id": request.complaint_id,
            "suspect_address": normalized_address,
            "blockchain": chain_name,
            "token_contract": request.token_contract,
            "incident_timestamp_utc": request.incident_timestamp_utc.isoformat(),
            "stolen_amount": request.stolen_amount,
            "time_lock_enforced_from": request.incident_timestamp_utc.isoformat(),
        }
        task_id = await redis_mgr.enqueue_case("traversal_pipeline_queue", queue_payload)

    # 5. Persist Case Record
    now_utc = datetime.now(timezone.utc)
    case_record = CaseDetail(
        complaint_id=request.complaint_id,
        suspect_address=request.suspect_address,
        normalized_address=normalized_address,
        blockchain=validation_result.blockchain,
        token_contract=request.token_contract,
        incident_timestamp_utc=request.incident_timestamp_utc,
        status=case_status,
        risk_score=risk_score,
        typology=entity.entity_type.value if (entity and matched) else "UNFLAGGED",
        direct_tag_matched=matched,
        attributed_vasp=attributed_vasp,
        cfr_pruning_config=CFRPruningConfig(),
        created_at_utc=now_utc,
        updated_at_utc=now_utc,
        metadata={
            "format_type": validation_result.format_type,
            "victim_bank_ref": request.victim_bank_ref,
            "stolen_amount": request.stolen_amount,
            "lookup_latency_ms": latency_ms,
            "queued_task_id": task_id
        }
    )
    await case_store.save_case(case_record)

    return CaseIngestResponse(
        complaint_id=request.complaint_id,
        suspect_address=request.suspect_address,
        blockchain=chain_name,
        normalized_address=normalized_address,
        incident_timestamp_utc=request.incident_timestamp_utc,
        status=case_status,
        direct_tag_matched=matched,
        attributed_entity=entity,
        lookup_latency_ms=latency_ms,
        time_lock_enforced_from_utc=request.incident_timestamp_utc,
        message=message,
        queued_task_id=task_id,
        created_at_utc=now_utc
    )


@router.get("/{complaint_id}", response_model=CaseDetail, status_code=status.HTTP_200_OK)
async def get_case_detail(
    complaint_id: str,
    case_store: MemoryCaseStore = Depends(get_case_store)
) -> CaseDetail:
    """Fetch forensic state and details for an ingested complaint."""
    case = await case_store.get_case(complaint_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation case with complaint_id '{complaint_id}' not found."
        )
    return case


@router.get("", response_model=List[CaseDetail], status_code=status.HTTP_200_OK)
async def list_cases(
    limit: int = 50,
    case_store: MemoryCaseStore = Depends(get_case_store)
) -> List[CaseDetail]:
    """List recent ingested cases."""
    return await case_store.list_cases(limit=limit)
