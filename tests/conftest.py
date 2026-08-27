"""Pytest configuration, fixtures and test setup."""

import pytest
from datetime import datetime, timezone
from app.main import app
from app.core.bloom_filter import InvertedBloomFilter, get_bloom_filter
from app.storage.memory_store import MemoryCaseStore


@pytest.fixture
def bloom_filter_fixture() -> InvertedBloomFilter:
    """Provide freshly initialized bloom filter instance for tests."""
    return get_bloom_filter()


@pytest.fixture
def sample_valid_evm_case_payload():
    """Valid EVM case payload for 1930 / NCRP ingestion."""
    return {
        "complaint_id": "NCRP-2026-98124",
        "suspect_address": "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976",
        "blockchain": "ethereum",
        "token_contract": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "incident_timestamp_utc": "2026-08-27T10:00:00Z",
        "stolen_amount": 5400.0,
        "victim_bank_ref": "AXIS/2026/UPI/88921"
    }


@pytest.fixture
def sample_known_vasp_payload():
    """Payload targeting a known CoinDCX Hot Wallet address."""
    return {
        "complaint_id": "NCRP-2026-11002",
        "suspect_address": "0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf",
        "blockchain": "ethereum",
        "token_contract": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "incident_timestamp_utc": "2026-08-27T12:00:00Z"
    }


@pytest.fixture
def sample_tron_payload():
    """Payload with TRON TRC-20 USDT suspect address."""
    return {
        "complaint_id": "NCRP-2026-TRON-4412",
        "suspect_address": "TYDzsYUE2UtZZ3z66o7kULg43H4tKq7rK6",
        "blockchain": "tron",
        "token_contract": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        "incident_timestamp_utc": "2026-08-27T08:30:00Z"
    }


@pytest.fixture
def sample_bitcoin_payload():
    """Payload with Bitcoin Bech32 suspect address."""
    return {
        "complaint_id": "NCRP-2026-BTC-7781",
        "suspect_address": "bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97",
        "blockchain": "bitcoin",
        "token_contract": "NATIVE",
        "incident_timestamp_utc": "2026-08-27T09:15:00Z"
    }
