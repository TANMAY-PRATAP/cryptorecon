"""Unit tests for Dual-Stack VASP Attribution Engine (Account & UTXO Stacks)."""

import pytest  # pyrefly: ignore # type: ignore
from app.attribution.account_stack import AccountAttributionEngine  # pyrefly: ignore # type: ignore
from app.attribution.utxo_stack import UTXOAttributionEngine  # pyrefly: ignore # type: ignore
from app.attribution import DualStackAttributor  # pyrefly: ignore # type: ignore
from app.schemas.traversal import AttributionTier  # pyrefly: ignore # type: ignore


def test_evm_tier1_gas_parent_ancestry():
    """Verify Tier 1 Gas-Parent Ancestry attribution from native gas funder."""
    engine = AccountAttributionEngine()
    
    # Gas funder is Binance 14 hot wallet
    gas_funder = "0x28c6c06298d514db089934071355e5743bf21d60"
    target_wallet = "0x9999111122223333444455556666777788889999"

    tier, vasp, conf, ev = engine.attribute(
        target_address=target_wallet,
        blockchain="ethereum",
        gas_funder_address=gas_funder
    )

    assert tier == AttributionTier.TIER_1_GAS_PARENT
    assert "Binance" in vasp
    assert conf >= 0.90
    assert ev["gas_funder"] == gas_funder


def test_evm_tier2_contract_factory_bytecode():
    """Verify Tier 2 Contract Factory Bytecode matching."""
    engine = AccountAttributionEngine()
    
    # Bytecode contains Binance forwarder proxy prefix
    mock_bytecode = "0x6080604052363d3d373d3d3d363d735566778899aabbccddeeff0011223344"
    target_contract = "0x8888111122223333444455556666777788889999"

    tier, vasp, conf, ev = engine.attribute(
        target_address=target_contract,
        blockchain="ethereum",
        contract_bytecode_hex=mock_bytecode
    )

    assert tier == AttributionTier.TIER_2_CONTRACT_FACTORY
    assert "Binance Smart Forwarder" in vasp
    assert conf >= 0.80


def test_evm_tier3_omnibus_sweep():
    """Verify Tier 3 Omnibus balance sweep detection."""
    engine = AccountAttributionEngine()
    
    # Destination is CoinDCX Sweep Vault
    sweep_dest = "0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf"
    target_wallet = "0x7777111122223333444455556666777788889999"

    tier, vasp, conf, ev = engine.attribute(
        target_address=target_wallet,
        blockchain="ethereum",
        sweep_destination_address=sweep_dest
    )

    assert tier == AttributionTier.TIER_3_OMNIBUS_SWEEP
    assert "CoinDCX" in vasp
    assert conf >= 0.90


def test_bitcoin_tier1_cioh_match():
    """Verify Bitcoin Tier 1 CIOH cluster match against exchange seed database."""
    engine = UTXOAttributionEngine()

    # Cluster contains Binance BTC cold storage seed
    cluster_inputs = {
        "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s",  # Binance Cold 1
        "1UnknownInputAddressXYZ123456789",
        "1AnotherInputAddressABC987654321"
    }

    tier, vasp, conf, ev = engine.attribute(
        target_address="1TargetAddress000000000000000000000",
        co_spent_input_addresses=cluster_inputs
    )

    assert tier == AttributionTier.UTXO_TIER_1_CIOH
    assert "Binance" in vasp
    assert conf >= 0.95
    assert ev["matched_seed_address"] == "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s"


def test_bitcoin_tier2_hd_derivation():
    """Verify Bitcoin Tier 2 HD-derivation institutional batching pattern."""
    engine = UTXOAttributionEngine()

    tier, vasp, conf, ev = engine.attribute(
        target_address="bc1qinstitutionalBatchTarget",
        output_script_types=["witness_v0_keyhash", "witness_v0_keyhash"],
        batch_deposit_count=20
    )

    assert tier == AttributionTier.UTXO_TIER_2_HD_DERIVATION
    assert "HD-Derivation" in vasp
    assert conf >= 0.70


def test_bitcoin_tier3_subpoena_candidate():
    """Verify Bitcoin Tier 3 Subpoena candidate tagging on large unassigned clusters."""
    engine = UTXOAttributionEngine()

    unassigned_cluster = {f"1unassigned_{i}" for i in range(8)}
    tier, vasp, conf, ev = engine.attribute(
        target_address="1LargeUnassignedClusterSeed",
        co_spent_input_addresses=unassigned_cluster,
        estimated_volume_btc=2.4
    )

    assert tier == AttributionTier.UTXO_TIER_3_SUBPOENA_CANDIDATE
    assert "Subpoena Candidate" in vasp
    assert "Section 94 BNSS" in ev["recommended_statute"]


def test_dual_stack_attributor_inspection():
    """Verify unified DualStackAttributor inspection method and recommendations."""
    attributor = DualStackAttributor()

    # 1. CoinDCX inspection (Tier 0 Direct Bloom) -> Section 94 BNSS Notice recommended
    res_cdx = attributor.inspect_address(
        address="0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf",
        blockchain="ethereum"
    )
    assert res_cdx.attribution_tier == AttributionTier.TIER_0_DIRECT_BLOOM
    assert "CoinDCX" in res_cdx.attributed_vasp
    assert res_cdx.recommended_action == "DISPATCH_SEC_94_BNSS_NOTICE"

    # 2. Unknown wallet funded by Binance gas -> MLAT / Purple Notice recommended
    res_gas = attributor.inspect_address(
        address="0x5555000000000000000000000000000000005555",
        blockchain="ethereum",
        gas_funder_address="0x28c6c06298d514db089934071355e5743bf21d60"
    )
    assert res_gas.attribution_tier == AttributionTier.TIER_1_GAS_PARENT
    assert "Binance" in res_gas.attributed_vasp
    assert res_gas.recommended_action == "DISPATCH_MLAT_PURPLE_NOTICE"
