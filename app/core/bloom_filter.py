"""High-Performance In-Memory Inverted Bloom Filter & Tag Attribution Engine.

Implements sub-millisecond O(1) membership testing and tag lookup for 100k+
known VASP hot/cold wallets, mixer pools, and sanctioned entities.
"""

import math
import hashlib
import time
from typing import Optional, Dict, List, Tuple
from app.schemas.entity import EntityTag
from app.core.seed_entities import SEED_ENTITIES


class InvertedBloomFilter:
    """High-performance in-memory Bloom filter with exact attribution hash map."""

    def __init__(
        self,
        expected_elements: int = 150000,
        false_positive_rate: float = 0.001
    ):
        self.expected_elements = max(1000, expected_elements)
        self.false_positive_rate = false_positive_rate

        # Calculate optimal size (m) and hash count (k)
        # m = - (n * ln(p)) / (ln(2)^2)
        # k = (m / n) * ln(2)
        self.bit_size = int(
            - (self.expected_elements * math.log(self.false_positive_rate)) / (math.log(2) ** 2)
        )
        self.hash_count = int((self.bit_size / self.expected_elements) * math.log(2))
        self.hash_count = max(1, self.hash_count)

        # Allocate bytearray for bits (8 bits per byte)
        self.byte_count = (self.bit_size + 7) // 8
        self.bit_array = bytearray(self.byte_count)

        # Exact attribution dictionary: (blockchain.lower(), address.lower()) -> EntityTag
        self._entity_store: Dict[Tuple[str, str], EntityTag] = {}
        self._item_count = 0

        # Pre-seed with default entities
        self._seed_default_entities()

    def _seed_default_entities(self) -> None:
        """Populate filter with curated seed entities."""
        for entity in SEED_ENTITIES:
            self.add(entity)

    def _get_hashes(self, key: str) -> List[int]:
        """Generate k hash indices using double hashing (Kirsch-Mitzenmacher optimization).
        
        g_i(x) = (h1(x) + i * h2(x)) % m
        """
        # Compute two 64-bit independent hashes using SHA-256
        digest = hashlib.sha256(key.encode("utf-8")).digest()
        h1 = int.from_bytes(digest[:8], byteorder="big")
        h2 = int.from_bytes(digest[8:16], byteorder="big")
        if h2 == 0:
            h2 = 1

        indices = []
        for i in range(self.hash_count):
            combined = (h1 + i * h2) % self.bit_size
            indices.append(combined)
        return indices

    def _normalize_address(self, blockchain: str, address: str) -> str:
        """Normalize address per blockchain rules (lowercase for EVM, Base58 for TRON)."""
        chain = blockchain.strip().lower()
        addr = address.strip()
        if chain in ("ethereum", "polygon", "bsc", "arbitrum", "optimism"):
            return addr.lower()
        elif chain == "tron":
            if (addr.startswith("41") and len(addr) == 42) or (addr.startswith("0x41") and len(addr) == 44):
                from app.core.validators import tron_hex_to_base58
                return tron_hex_to_base58(addr)
            return addr
        return addr

    def _make_key(self, blockchain: str, address: str) -> str:
        """Create normalized composite key."""
        norm_addr = self._normalize_address(blockchain, address)
        return f"{blockchain.strip().lower()}:{norm_addr.lower()}"

    def add(self, entity: EntityTag) -> None:
        """Add an entity to both the Bloom filter bit array and attribution store."""
        key = self._make_key(entity.blockchain, entity.address)
        
        # Set bits in bitarray
        for index in self._get_hashes(key):
            byte_idx = index // 8
            bit_idx = index % 8
            self.bit_array[byte_idx] |= (1 << bit_idx)

        # Store exact entity metadata
        norm_addr = self._normalize_address(entity.blockchain, entity.address)
        dict_key = (entity.blockchain.strip().lower(), norm_addr.lower())
        self._entity_store[dict_key] = entity
        self._item_count += 1

    def contains(self, blockchain: str, address: str) -> bool:
        """Check if an address is possibly in the set (Bloom filter pass)."""
        key = self._make_key(blockchain, address)
        for index in self._get_hashes(key):
            byte_idx = index // 8
            bit_idx = index % 8
            if not (self.bit_array[byte_idx] & (1 << bit_idx)):
                return False
        return True

    def lookup(self, blockchain: str, address: str) -> Tuple[bool, Optional[EntityTag], float]:
        """Perform O(1) lookup returning (match_found, entity_tag, latency_ms)."""
        t0 = time.perf_counter()
        
        # Step 1: Bloom filter screening (<= 0.05 ms)
        in_bloom = self.contains(blockchain, address)
        
        if not in_bloom:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return False, None, round(latency_ms, 4)

        # Step 2: Exact dictionary retrieval to confirm and eliminate false positives
        norm_addr = self._normalize_address(blockchain, address)
        dict_key = (blockchain.strip().lower(), norm_addr.lower())
        matched_entity = self._entity_store.get(dict_key)
        
        latency_ms = (time.perf_counter() - t0) * 1000.0
        return matched_entity is not None, matched_entity, round(latency_ms, 4)

    @property
    def total_entities(self) -> int:
        """Total number of unique indexed entity tags."""
        return len(self._entity_store)

    @property
    def memory_usage_bytes(self) -> int:
        """Memory size of bit array in bytes."""
        return len(self.bit_array)


# Global singleton instance
_bloom_filter_instance: Optional[InvertedBloomFilter] = None


def get_bloom_filter() -> InvertedBloomFilter:
    """Retrieve or initialize the global InvertedBloomFilter instance."""
    global _bloom_filter_instance
    if _bloom_filter_instance is None:
        _bloom_filter_instance = InvertedBloomFilter()
    return _bloom_filter_instance
