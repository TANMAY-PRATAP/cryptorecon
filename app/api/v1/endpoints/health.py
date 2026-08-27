"""Health and Readiness Monitoring Endpoints."""

from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from app.config import Settings
from app.api.deps import get_app_settings, get_filter, get_redis, get_case_store
from app.core.bloom_filter import InvertedBloomFilter
from app.storage.redis_client import RedisManager
from app.storage.memory_store import MemoryCaseStore

router = APIRouter(tags=["Health & Diagnostics"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(
    settings: Settings = Depends(get_app_settings)
) -> Dict[str, Any]:
    """Liveness probe: returns 200 OK when service is running."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.APP_ENV,
        "timestamp_utc": datetime.now(timezone.utc).isoformat()
    }


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness_check(
    settings: Settings = Depends(get_app_settings),
    bloom: InvertedBloomFilter = Depends(get_filter),
    redis_mgr: RedisManager = Depends(get_redis),
    case_store: MemoryCaseStore = Depends(get_case_store)
) -> Dict[str, Any]:
    """Readiness probe: validates critical subsystems and Bloom filter status."""
    total_cases = await case_store.total_count()
    
    return {
        "status": "ready",
        "version": settings.VERSION,
        "bloom_filter": {
            "ready": True,
            "indexed_entities": bloom.total_entities,
            "bit_array_bytes": bloom.memory_usage_bytes,
            "expected_capacity": settings.BLOOM_FILTER_EXPECTED_ELEMENTS,
            "target_fpr": settings.BLOOM_FILTER_FALSE_POSITIVE_RATE
        },
        "redis": {
            "connected": redis_mgr.is_connected,
            "redis_url": settings.REDIS_URL if settings.DEBUG else "[REDACTED]"
        },
        "state_store": {
            "active_cases_in_memory": total_cases
        },
        "timestamp_utc": datetime.now(timezone.utc).isoformat()
    }
