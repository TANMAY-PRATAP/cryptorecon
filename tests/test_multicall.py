"""Unit tests for Multicall3 micro-batching engine."""

import pytest  # pyrefly: ignore # type: ignore
from app.engine.evm.multicall import (  # pyrefly: ignore # type: ignore
    MulticallBatchEngine,
    Multicall3Call,
    MULTICALL3_ADDRESS,
    ERC20_BALANCE_OF_SELECTOR,
    MULTICALL3_AGGREGATE3_SELECTOR,
)


def test_encode_erc20_balance_of():
    """Verify ERC-20 balanceOf call encoding."""
    token = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    wallet = "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976"
    call = MulticallBatchEngine.encode_erc20_balance_of(token, wallet)

    assert call.target == token
    assert call.allow_failure is True
    assert call.call_data.startswith("0x" + ERC20_BALANCE_OF_SELECTOR)
    # Check length of calldata: '0x' + 8 hex selector + 64 hex address = 74 chars
    assert len(call.call_data) == 74


def test_chunk_calls():
    """Verify batch chunking logic respects max_batch_size (50)."""
    engine = MulticallBatchEngine(rpc_url="https://eth.llamarpc.com", max_batch_size=50)
    
    # Create 125 dummy calls
    calls = [
        Multicall3Call(target="0x0000000000000000000000000000000000000001", call_data="0x12345678")
        for _ in range(125)
    ]
    
    chunks = engine.chunk_calls(calls)
    assert len(chunks) == 3
    assert len(chunks[0]) == 50
    assert len(chunks[1]) == 50
    assert len(chunks[2]) == 25


def test_build_aggregate3_calldata():
    """Verify ABI encoding for Multicall3 aggregate3 call."""
    engine = MulticallBatchEngine(rpc_url="https://eth.llamarpc.com")
    calls = [
        MulticallBatchEngine.encode_erc20_balance_of(
            "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "0x71C2e36675B8B1Fc2ffDa6112dE9C1C90D218976"
        )
    ]
    calldata = engine.build_aggregate3_calldata(calls)
    assert calldata.startswith("0x" + MULTICALL3_AGGREGATE3_SELECTOR)
    assert len(calldata) > 100


def test_decode_uint256():
    """Verify decoding uint256 hexadecimal return values."""
    # 1,000,000 USDT (with 6 decimals = 1,000,000 * 10^6 = 10^12 = 0xe8d4a51000)
    hex_val = "0x000000000000000000000000000000000000000000000000000000e8d4a51000"
    decoded = MulticallBatchEngine.decode_uint256(hex_val)
    assert decoded == 1000000000000
    assert decoded / (10 ** 6) == 1000000.0
