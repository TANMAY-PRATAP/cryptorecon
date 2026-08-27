"""Direct Entity Lookup & VASP Tag Attribution Endpoints."""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.api.deps import get_filter
from app.core.bloom_filter import InvertedBloomFilter
from app.core.validators import validate_chain_address
from app.schemas.entity import TagLookupResponse, EntityTag

router = APIRouter(prefix="/entities", tags=["Entity & VASP Attribution"])


@router.get("/lookup", response_model=TagLookupResponse, status_code=status.HTTP_200_OK)
async def lookup_entity(
    address: str = Query(..., description="Target wallet/contract address"),
    blockchain: str = Query(default="ethereum", description="Target blockchain network"),
    bloom: InvertedBloomFilter = Depends(get_filter)
) -> TagLookupResponse:
    """O(1) In-Memory Tag Lookup against 100k+ known VASPs, Mixers and Exploits (<= 1ms)."""
    val_res = validate_chain_address(address, blockchain)
    if not val_res.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid address for {blockchain}: {val_res.error_message}"
        )

    matched, entity, latency_ms = bloom.lookup(blockchain, val_res.normalized_address)

    return TagLookupResponse(
        address=val_res.normalized_address,
        blockchain=blockchain.lower(),
        match_found=matched,
        lookup_latency_ms=latency_ms,
        matched_entity=entity,
        attribution_tier="TIER_0_DIRECT_BLOOM" if matched else "UNKNOWN_ENTITY"
    )


@router.post("/register", response_model=EntityTag, status_code=status.HTTP_201_CREATED)
async def register_entity_tag(
    entity: EntityTag,
    bloom: InvertedBloomFilter = Depends(get_filter)
) -> EntityTag:
    """Dynamically register a new verified VASP hot/cold wallet or mixer pool in the Bloom filter."""
    val_res = validate_chain_address(entity.address, entity.blockchain)
    if not val_res.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity address: {val_res.error_message}"
        )
    
    # Store with normalized checksum address
    entity.address = val_res.normalized_address
    bloom.add(entity)
    return entity
