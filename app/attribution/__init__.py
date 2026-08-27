"""Module 5: Dedicated Dual-Stack VASP Attribution Engine.

Orchestrates:
1. Account Stack (EVM & TRON):
   - Tier 1: Gas-Parent Ancestry (Primary - sub-3s pre-sweep attribution)
   - Tier 2: Contract Factory Bytecode (Fallback 1)
   - Tier 3: Omnibus Sweep (Fallback 2)
2. UTXO Stack (Bitcoin):
   - Tier 1: CIOH & Labeled Cluster Match (Primary)
   - Tier 2: HD-Derivation Heuristics (Fallback 1)
   - Tier 3: Subpoena Escalation Candidate Tagging (Fallback 2)
"""

import time
from typing import Dict, Any, Optional
from app.core.bloom_filter import InvertedBloomFilter, get_bloom_filter
from app.schemas.chain import Blockchain
from app.schemas.traversal import AttributionTier, AttributionInspectResponse
from app.attribution.account_stack import AccountAttributionEngine
from app.attribution.utxo_stack import UTXOAttributionEngine


class DualStackAttributor:
    """Unified Dual-Stack VASP Attribution Engine."""

    def __init__(self, bloom_filter: Optional[InvertedBloomFilter] = None):
        self.bloom = bloom_filter or get_bloom_filter()
        self.account_engine = AccountAttributionEngine(self.bloom)
        self.utxo_engine = UTXOAttributionEngine(self.bloom)

    def inspect_address(
        self,
        address: str,
        blockchain: str,
        gas_funder_address: Optional[str] = None,
        contract_bytecode_hex: Optional[str] = None,
        sweep_destination_address: Optional[str] = None,
        co_spent_inputs: Optional[set] = None,
        estimated_volume_btc: float = 0.0
    ) -> AttributionInspectResponse:
        """Run attribution inspection and return standardized forensic response."""
        t0 = time.perf_counter()
        clean_chain = blockchain.strip().lower()

        if clean_chain == "bitcoin":
            tier, vasp_name, confidence, evidence = self.utxo_engine.attribute(
                target_address=address,
                co_spent_input_addresses=co_spent_inputs,
                estimated_volume_btc=estimated_volume_btc
            )
        else:
            tier, vasp_name, confidence, evidence = self.account_engine.attribute(
                target_address=address,
                blockchain=clean_chain,
                gas_funder_address=gas_funder_address,
                contract_bytecode_hex=contract_bytecode_hex,
                sweep_destination_address=sweep_destination_address
            )

        latency_ms = (time.perf_counter() - t0) * 1000.0

        # Determine recommended action based on attribution result
        if tier == AttributionTier.TIER_0_DIRECT_BLOOM or tier == AttributionTier.TIER_1_GAS_PARENT:
            rec_action = "DISPATCH_SEC_94_BNSS_NOTICE" if evidence.get("fiu_registered") else "DISPATCH_MLAT_PURPLE_NOTICE"
        elif tier == AttributionTier.UTXO_TIER_3_SUBPOENA_CANDIDATE:
            rec_action = "ISSUE_COURT_KYC_SUBPOENA"
        elif tier != AttributionTier.UNATTRIBUTED:
            rec_action = "EXPAND_TRAVERSAL_AND_FREEZE"
        else:
            rec_action = "CONTINUE_MULTI_HOP_TRAVERSAL"

        return AttributionInspectResponse(
            address=address,
            blockchain=clean_chain,
            attributed_vasp=vasp_name,
            entity_type=evidence.get("funder_type") or evidence.get("entity_type"),
            attribution_tier=tier,
            confidence_score=confidence,
            evidence=evidence,
            latency_ms=round(latency_ms, 3),
            recommended_action=rec_action
        )


_global_attributor: Optional[DualStackAttributor] = None


def get_attributor() -> DualStackAttributor:
    global _global_attributor
    if _global_attributor is None:
        _global_attributor = DualStackAttributor()
    return _global_attributor


__all__ = [
    "DualStackAttributor",
    "get_attributor",
    "AccountAttributionEngine",
    "UTXOAttributionEngine",
]
