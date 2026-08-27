"""UTXO-Based VASP Attribution Engine (Bitcoin Stack).

Implements Module 5 UTXO-Based Attribution:
  Tier 1: CIOH & Labeled Cluster Match (Primary - co-spent input clustering matched against VASP seeds)
  Tier 2: HD-Derivation Heuristic (Fallback 1 - identifies sequential batch-deposit signatures)
  Tier 3: Subpoena Escalation (Fallback 2 - flags unassigned candidate clusters for targeted KYC requests)
"""

from typing import Dict, Any, Optional, Tuple, Set, List
from app.core.bloom_filter import InvertedBloomFilter, get_bloom_filter
from app.schemas.traversal import AttributionTier


class UTXOAttributionEngine:
    """Bitcoin UTXO multi-tier attribution pipeline."""

    def __init__(self, bloom_filter: Optional[InvertedBloomFilter] = None):
        self.bloom = bloom_filter or get_bloom_filter()

    def tier1_cioh_cluster_match(
        self,
        co_spent_input_addresses: Set[str]
    ) -> Tuple[bool, Optional[str], float, Dict[str, Any]]:
        """Tier 1: Common-Input-Ownership Heuristic (CIOH) & Labeled Cluster Match.
        
        If ANY address in the multi-input co-spent cluster belongs to a known VASP hot/cold wallet,
        attribute the entire input cluster to that exchange entity.
        """
        for addr in co_spent_input_addresses:
            matched, entity, _ = self.bloom.lookup("bitcoin", addr)
            if matched and entity is not None:
                return (
                    True,
                    entity.entity_name,
                    0.98,
                    {
                        "tier": AttributionTier.UTXO_TIER_1_CIOH.value,
                        "matched_seed_address": addr,
                        "vasp_name": entity.entity_name,
                        "cluster_size": len(co_spent_input_addresses),
                        "compliance_email": entity.compliance_email,
                        "confidence_rationale": "Very high confidence: Input address co-spent in transaction cluster belongs to verified exchange seed database (CIOH)."
                    }
                )

        return False, None, 0.0, {}

    def tier2_hd_derivation_match(
        self,
        output_script_types: List[str],
        has_sequential_derivation: bool,
        batch_deposit_count: int
    ) -> Tuple[bool, Optional[str], float, Dict[str, Any]]:
        """Tier 2: HD-Derivation & Batch-Deposit Signature Heuristic.
        
        Identifies institutional exchange deposit sweep batching patterns:
        - Uniform SegWit/Taproot script signatures
        - High-frequency batch consolidation (>15 inputs/outputs)
        """
        if has_sequential_derivation or batch_deposit_count >= 15:
            # Check script type consistency
            script_set = set(output_script_types)
            is_uniform_script = len(script_set) <= 2
            
            if is_uniform_script:
                return (
                    True,
                    "Institutional Exchange Omnibus (HD-Derivation)",
                    0.75,
                    {
                        "tier": AttributionTier.UTXO_TIER_2_HD_DERIVATION.value,
                        "batch_count": batch_deposit_count,
                        "script_types": list(script_set),
                        "confidence_rationale": "Moderate confidence: Transaction exhibits institutional HD-derivation and sequential batch-sweep characteristics."
                    }
                )

        return False, None, 0.0, {}

    def tier3_subpoena_escalation(
        self,
        target_address: str,
        co_spent_cluster_size: int,
        estimated_volume_btc: float
    ) -> Tuple[bool, Optional[str], float, Dict[str, Any]]:
        """Tier 3: Subpoena Escalation Candidate Tagging.
        
        Flags unassigned high-volume UTXO candidate clusters for targeted 1930 / State Police KYC subpoenas.
        """
        if co_spent_cluster_size >= 5 or estimated_volume_btc >= 0.5:
            return (
                True,
                "Subpoena Candidate Cluster",
                0.60,
                {
                    "tier": AttributionTier.UTXO_TIER_3_SUBPOENA_CANDIDATE.value,
                    "target_address": target_address,
                    "cluster_size": co_spent_cluster_size,
                    "volume_btc": estimated_volume_btc,
                    "recommended_statute": "Section 94 BNSS / 1930 CFCFRMS Escalation",
                    "confidence_rationale": "Candidate for Section 94 BNSS legal notice: Large unassigned multi-input cluster indicates exchange or intermediary hub."
                }
            )

        return False, None, 0.0, {}

    def attribute(
        self,
        target_address: str,
        co_spent_input_addresses: Optional[Set[str]] = None,
        output_script_types: Optional[List[str]] = None,
        has_sequential_derivation: bool = False,
        batch_deposit_count: int = 0,
        estimated_volume_btc: float = 0.0
    ) -> Tuple[AttributionTier, Optional[str], float, Dict[str, Any]]:
        """Run full Bitcoin UTXO Tier 1 -> Tier 2 -> Tier 3 attribution pipeline."""
        input_set = co_spent_input_addresses or {target_address}
        script_list = output_script_types or []

        # Tier 0: Direct Tag Match
        matched, entity, _ = self.bloom.lookup("bitcoin", target_address)
        if matched and entity is not None:
            return (
                AttributionTier.TIER_0_DIRECT_BLOOM,
                entity.entity_name,
                1.0,
                {
                    "tier": AttributionTier.TIER_0_DIRECT_BLOOM.value,
                    "entity_name": entity.entity_name,
                    "compliance_email": entity.compliance_email
                }
            )

        # Tier 1: CIOH Match
        t1_ok, t1_vasp, t1_conf, t1_ev = self.tier1_cioh_cluster_match(input_set)
        if t1_ok:
            return AttributionTier.UTXO_TIER_1_CIOH, t1_vasp, t1_conf, t1_ev

        # Tier 2: HD Derivation Match
        t2_ok, t2_vasp, t2_conf, t2_ev = self.tier2_hd_derivation_match(
            script_list, has_sequential_derivation, batch_deposit_count
        )
        if t2_ok:
            return AttributionTier.UTXO_TIER_2_HD_DERIVATION, t2_vasp, t2_conf, t2_ev

        # Tier 3: Subpoena Escalation Candidate
        t3_ok, t3_vasp, t3_conf, t3_ev = self.tier3_subpoena_escalation(
            target_address, len(input_set), estimated_volume_btc
        )
        if t3_ok:
            return AttributionTier.UTXO_TIER_3_SUBPOENA_CANDIDATE, t3_vasp, t3_conf, t3_ev

        return (
            AttributionTier.UNATTRIBUTED,
            None,
            0.0,
            {"tier": AttributionTier.UNATTRIBUTED.value, "reason": "No UTXO exchange pattern matched."}
        )
