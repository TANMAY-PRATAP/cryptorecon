"""Unit tests for Address & Time-Lock Validators."""

from datetime import datetime, timezone, timedelta
import pytest  # pyrefly: ignore # type: ignore
from app.core.validators import (  # pyrefly: ignore # type: ignore
    validate_chain_address,
    validate_evm_address,
    validate_tron_address,
    validate_bitcoin_address,
    validate_incident_timelock,
    to_eip55_checksum,
)
from app.schemas.chain import Blockchain  # pyrefly: ignore # type: ignore


def test_evm_eip55_checksum():
    """Verify EIP-55 checksumming logic."""
    raw = "0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed"
    checksummed = to_eip55_checksum(raw)
    assert checksummed == "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"

    # Valid EIP-55 address validation
    res = validate_evm_address(checksummed, Blockchain.ETHEREUM)
    assert res.is_valid is True
    assert res.normalized_address == checksummed
    assert res.format_type == "EIP-55"


def test_evm_invalid_format():
    """Verify detection of invalid EVM address structures."""
    # Too short
    res_short = validate_evm_address("0x12345", Blockchain.ETHEREUM)
    assert res_short.is_valid is False

    # Invalid non-hex characters
    res_invalid_chars = validate_evm_address("0xZZZ2e36675B8B1Fc2ffDa6112dE9C1C90D218976", Blockchain.ETHEREUM)
    assert res_invalid_chars.is_valid is False

    # Missing 0x prefix
    res_no_prefix = validate_evm_address("71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976", Blockchain.ETHEREUM)
    assert res_no_prefix.is_valid is False


def test_tron_address_validation():
    """Verify TRON Base58Check validation."""
    valid_tron = "TYDzsYUE2UtZZ3z66o7kULg43H4tKq7rK6"
    res = validate_tron_address(valid_tron)
    assert res.is_valid is True
    assert res.blockchain == Blockchain.TRON
    assert res.format_type == "Base58Check"

    # Invalid TRON - does not start with T
    res_bad_start = validate_tron_address("AYDzsYUE2UtZZ3z66o7kULg43H4tKq7rK6")
    assert res_bad_start.is_valid is False

    # Invalid length
    res_bad_len = validate_tron_address("TYDzsYUE2UtZZ3z66o7kULg43H4tKq")
    assert res_bad_len.is_valid is False


def test_bitcoin_address_validation():
    """Verify Bitcoin Legacy, P2SH and Bech32 validation."""
    # 1. Bech32 SegWit
    bech32_addr = "bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97"
    res_b32 = validate_bitcoin_address(bech32_addr)
    assert res_b32.is_valid is True
    assert res_b32.format_type == "Bech32/SegWit"

    # 2. Legacy P2PKH
    legacy_addr = "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s"
    res_p2pkh = validate_bitcoin_address(legacy_addr)
    assert res_p2pkh.is_valid is True
    assert res_p2pkh.format_type == "P2PKH_Base58Check"

    # 3. P2SH
    p2sh_addr = "34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo"
    res_p2sh = validate_bitcoin_address(p2sh_addr)
    assert res_p2sh.is_valid is True
    assert res_p2sh.format_type == "P2SH_Base58Check"

    # 4. Invalid BTC address
    res_bad = validate_bitcoin_address("9invalidBitcoinAddressXYZ123456789")
    assert res_bad.is_valid is False


def test_unified_chain_dispatcher():
    """Verify unified dispatcher for multiple blockchains."""
    res_eth = validate_chain_address("0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf", "ethereum")
    assert res_eth.is_valid is True

    res_tron = validate_chain_address("TYDzsYUE2UtZZ3z66o7kULg43H4tKq7rK6", "tron")
    assert res_tron.is_valid is True

    res_btc = validate_chain_address("1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s", "bitcoin")
    assert res_btc.is_valid is True

    # Unsupported blockchain name
    res_bad_chain = validate_chain_address("0x123", "dogechain_unknown")
    assert res_bad_chain.is_valid is False


def test_timelock_validation():
    """Verify time-lock pre-processor boundary rules."""
    # Past timestamp (valid incident)
    past_time = datetime.now(timezone.utc) - timedelta(days=2)
    is_valid, err = validate_incident_timelock(past_time)
    assert is_valid is True
    assert err is None

    # Far future timestamp (invalid clock skew / fake incident)
    future_time = datetime.now(timezone.utc) + timedelta(days=5)
    is_valid_fut, err_fut = validate_incident_timelock(future_time)
    assert is_valid_fut is False
    assert "cannot be in the future" in err_fut
