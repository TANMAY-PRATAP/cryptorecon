"""Unit and Performance Tests for Inverted Bloom Filter."""

import time
import pytest  # pyrefly: ignore # type: ignore
from app.core.bloom_filter import InvertedBloomFilter  # pyrefly: ignore # type: ignore
from app.schemas.entity import EntityTag, EntityType  # pyrefly: ignore # type: ignore


def test_bloom_filter_pre_seeded_entities():
    """Verify pre-seeded entities are properly indexed."""
    bloom = InvertedBloomFilter()
    assert bloom.total_entities >= 10

    # Test Binance EVM hot wallet lookup
    matched, entity, latency_ms = bloom.lookup("ethereum", "0x28c6c06298d514db089934071355e5743bf21d60")
    assert matched is True
    assert entity is not None
    assert "Binance" in entity.entity_name
    assert latency_ms < 1.0  # Engineering benchmark: <= 1ms

    # Test Tornado Cash Router lookup (Mixer pool 100% risk)
    matched_tc, entity_tc, lat_tc = bloom.lookup("ethereum", "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b")
    assert matched_tc is True
    assert entity_tc.entity_type == EntityType.MIXER_POOL
    assert entity_tc.risk_rating == 100

    # Test CoinDCX FIU-IND registered entity
    matched_cdx, entity_cdx, _ = bloom.lookup("ethereum", "0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf")
    assert matched_cdx is True
    assert entity_cdx.fiu_registered is True
    assert entity_cdx.jurisdiction == "IN"


def test_bloom_filter_unknown_entity():
    """Verify unknown entity returns False and None."""
    bloom = InvertedBloomFilter()
    matched, entity, latency_ms = bloom.lookup("ethereum", "0x000000000000000000000000000000000000dead")
    assert matched is False
    assert entity is None
    assert latency_ms < 1.0


def test_bloom_filter_dynamic_registration():
    """Verify dynamic runtime registration and retrieval."""
    bloom = InvertedBloomFilter()
    new_tag = EntityTag(
        address="0x1111111254fb6c44bac0bed2854e76f90643097d",
        blockchain="ethereum",
        entity_name="1inch Aggregator V5",
        entity_type=EntityType.DEX_ROUTER,
        jurisdiction="GLOBAL_P2P",
        risk_rating=5
    )
    bloom.add(new_tag)

    matched, entity, latency_ms = bloom.lookup("ethereum", "0x1111111254fb6c44bac0bed2854e76f90643097d")
    assert matched is True
    assert entity is not None
    assert entity.entity_name == "1inch Aggregator V5"
    assert latency_ms < 1.0


def test_bloom_filter_latency_benchmark():
    """Benchmark 1,000 lookups to ensure average latency is well under 1ms."""
    bloom = InvertedBloomFilter()
    iterations = 1000
    addresses = [
        ("ethereum", "0x28c6c06298d514db089934071355e5743bf21d60"),
        ("ethereum", "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b"),
        ("tron", "TYDzsYUE2UtZZ3z66o7kULg43H4tKq7rK6"),
        ("bitcoin", "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s"),
        ("ethereum", "0x9999999999999999999999999999999999999999"),
    ]

    t_start = time.perf_counter()
    for i in range(iterations):
        chain, addr = addresses[i % len(addresses)]
        bloom.lookup(chain, addr)
    t_end = time.perf_counter()

    avg_latency_ms = ((t_end - t_start) / iterations) * 1000.0
    # Average lookup must be sub-millisecond (typically <= 0.05 ms in pure python)
    assert avg_latency_ms < 0.5
