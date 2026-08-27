"""Thread-safe In-Memory Storage for Cases and Forensic Records."""

import asyncio
from typing import Dict, Optional, List
from app.schemas.case import CaseDetail


class MemoryCaseStore:
    """In-memory state store for active investigation cases."""

    def __init__(self):
        self._cases: Dict[str, CaseDetail] = {}
        self._lock = asyncio.Lock()

    async def save_case(self, case: CaseDetail) -> None:
        async with self._lock:
            self._cases[case.complaint_id] = case

    async def get_case(self, complaint_id: str) -> Optional[CaseDetail]:
        async with self._lock:
            return self._cases.get(complaint_id)

    async def list_cases(self, limit: int = 50) -> List[CaseDetail]:
        async with self._lock:
            return list(self._cases.values())[:limit]

    async def exists(self, complaint_id: str) -> bool:
        async with self._lock:
            return complaint_id in self._cases

    async def total_count(self) -> int:
        async with self._lock:
            return len(self._cases)


_memory_store_instance: Optional[MemoryCaseStore] = None


def get_memory_store() -> MemoryCaseStore:
    global _memory_store_instance
    if _memory_store_instance is None:
        _memory_store_instance = MemoryCaseStore()
    return _memory_store_instance
