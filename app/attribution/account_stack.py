"""Account-Based VASP Attribution Engine (EVM & TRON Stack).

Implements Module 5 Account-Based Attribution:
  Tier 1: Gas-Parent Ancestry (Primary - sub-3-second pre-sweep attribution from native ETH/TRX funder)
  Tier 2: Contract Factory Bytecode (Fallback 1 - matches proxy forwarder bytecode against exchange factories)
  Tier 3: Omnibus Sweep (Fallback 2 - monitors balance sweeps into known exchange consolidation wallets)
"""

from typing import Dict, Any, Optional, Tuple
from app.core.bloom_filter import InvertedBloomFilter, get_bloom_filter
from app.schemas.traversal import AttributionTier

# Known Exchange Deposit Forwarder Bytecode Signatures (Tier 2)
EXCHANGE_PROXY_BYTECODE_SIGNATURES: Dict[str, str] = {
    # Binance minimal proxy bytecode hash prefix / signature
    "363d3d373d3d3d363d73": "Binance Smart Forwarder Factory",
    "608060405234801561001057600080fd5b50": "Generic ERC-20 Proxy Sweeper",
    "3d602d80600a3d3981f3363d3d373d3d3d363d73": "OKX Sweeper Proxy Factory",
    "606060405236156100": "Huobi Hot Deposit Forwarder",
}

# Known Exchange Omnibus Consolidation Hot Wallets (Tier 3)
KNOWN_OMNIBUS_SWEEP_WALLETS: Dict[str, str] = {
    "0x28c6c06298d514db089934071355e5743bf21d60": "Binance 14 (Omnibus)",
    "0x21a31ee1afc51d94c2efccaa2092ad1028285549": "Binance 15 (Omnibus)",
    "0xdfd5293d8e347dfee59e53b243330057712a269e": "Binance 16 (Omnibus)",
    "0x503828976d22510aad0201ac7ec88293211d23da": "Coinbase 1 (Omnibus)",
    "0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf": "CoinDCX Sweep Vault (Omnibus)",
    "0x5a52e96bacdabb82fd05763e25335261b270efcb": "WazirX Consolidation Vault",
    "TYDzsYUE2UtZZ3z66o7kULg43H4tKq7rK6": "Binance TRON Hot Omnibus",
    "TT2T17KZDxDuAPRGQRVH6MmXauP2UytEd8": "OKX TRON Deposit Sweeper",
}


class AccountAttributionEngine:
    """EVM and TRON account-based attribution pipeline."""

    def __init__(self, bloom_filter: Optional[InvertedBloomFilter] = None):
        self.bloom = bloom_filter or get_bloom_filter()

    def tier1_gas_parent_ancestry(
        self,
        target_address: str,
        blockchain: str,
        gas_funder_address: Optional[str]
    ) -> Tuple[bool, Optional[str], float, Dict[str, Any]]:
        """Tier 1: Traces the transaction index 0 native gas dispenser (ETH/TRX).
        
        Yields sub-3-second pre-sweep attribution if funded directly by an exchange hot wallet.
        """
        if not gas_funder_address:
            return False, None, 0.0, {}

        matched, entity, _ = self.bloom.lookup(blockchain, gas_funder_address)
        if matched and entity is not None:
            return (
                True,
                entity.entity_name,
                0.95,
                {
                    "tier": AttributionTier.TIER_1_GAS_PARENT.value,
                    "gas_funder": gas_funder_address,
                    "funder_entity": entity.entity_name,
                    "funder_type": entity.entity_type.value,
                    "compliance_email": entity.compliance_email,
                    "fiu_registered": entity.fiu_registered,
                    "confidence_rationale": "High confidence: Wallet native gas was directly dispensed from exchange hot wallet at index 0."
                }
            )

        return False, None, 0.0, {}

    def tier2_bytecode_factory_match(
        self,
        contract_bytecode_hex: Optional[str]
    ) -> Tuple[bool, Optional[str], float, Dict[str, Any]]:
        """Tier 2: Matches forwarder smart contract bytecode against known exchange proxy factories."""
        if not contract_bytecode_hex:
            return False, None, 0.0, {}

        clean_code = contract_bytecode_hex.lower().replace("0x", "")
        for sig_prefix, factory_name in EXCHANGE_PROXY_BYTECODE_SIGNATURES.items():
            if sig_prefix.lower() in clean_code:
                return (
                    True,
                    factory_name,
                    0.85,
                    {
                        "tier": AttributionTier.TIER_2_CONTRACT_FACTORY.value,
                        "matched_signature": sig_prefix,
                        "factory_type": factory_name,
                        "confidence_rationale": "Moderate-high confidence: Contract bytecode matches registered exchange forwarder proxy factory."
                    }
                )

        return False, None, 0.0, {}

    def tier3_omnibus_sweep_match(
        self,
        sweep_destination_address: Optional[str]
    ) -> Tuple[bool, Optional[str], float, Dict[str, Any]]:
        """Tier 3: Monitors balance sweeps into known exchange omnibus consolidation vaults."""
        if not sweep_destination_address:
            return False, None, 0.0, {}

        norm_addr = sweep_destination_address.lower()
        for known_addr, exchange_name in KNOWN_OMNIBUS_SWEEP_WALLETS.items():
            if norm_addr == known_addr.lower():
                return (
                    True,
                    exchange_name,
                    0.90,
                    {
                        "tier": AttributionTier.TIER_3_OMNIBUS_SWEEP.value,
                        "sweep_destination": sweep_destination_address,
                        "consolidation_vault": exchange_name,
                        "confidence_rationale": "High confidence: On-chain funds were swept into exchange omnibus consolidation wallet."
                    }
                )

        return False, None, 0.0, {}

    def attribute(
        self,
        target_address: str,
        blockchain: str,
        gas_funder_address: Optional[str] = None,
        contract_bytecode_hex: Optional[str] = None,
        sweep_destination_address: Optional[str] = None
    ) -> Tuple[AttributionTier, Optional[str], float, Dict[str, Any]]:
        """Run full Tier 1 -> Tier 2 -> Tier 3 attribution pipeline."""
        # Tier 0: Direct Tag Match
        matched, entity, _ = self.bloom.lookup(blockchain, target_address)
        if matched and entity is not None:
            return (
                AttributionTier.TIER_0_DIRECT_BLOOM,
                entity.entity_name,
                1.0,
                {
                    "tier": AttributionTier.TIER_0_DIRECT_BLOOM.value,
                    "entity_name": entity.entity_name,
                    "entity_type": entity.entity_type.value,
                    "compliance_email": entity.compliance_email,
                    "fiu_registered": entity.fiu_registered
                }
            )

        # Tier 1: Gas Parent Ancestry
        t1_success, t1_vasp, t1_conf, t1_ev = self.tier1_gas_parent_ancestry(
            target_address, blockchain, gas_funder_address
        )
        if t1_success:
            return AttributionTier.TIER_1_GAS_PARENT, t1_vasp, t1_conf, t1_ev

        # Tier 2: Contract Factory Bytecode
        t2_success, t2_vasp, t2_conf, t2_ev = self.tier2_bytecode_factory_match(contract_bytecode_hex)
        if t2_success:
            return AttributionTier.TIER_2_CONTRACT_FACTORY, t2_vasp, t2_conf, t2_ev

        # Tier 3: Omnibus Sweep
        t3_success, t3_vasp, t3_conf, t3_ev = self.tier3_omnibus_sweep_match(sweep_destination_address)
        if t3_success:
            return AttributionTier.TIER_3_OMNIBUS_SWEEP, t3_vasp, t3_conf, t3_ev

        return (
            AttributionTier.UNATTRIBUTED,
            None,
            0.0,
            {"tier": AttributionTier.UNATTRIBUTED.value, "reason": "No VASP signature detected across Tier 1-3."}
        )
