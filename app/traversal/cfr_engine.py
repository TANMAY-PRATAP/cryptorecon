"""Anti-Smurfing & Cumulative Flow Ratio (CFR) Dynamic Pruning Engine.

Implements Module 3 of CryptoRecon PRD:
1. Dynamic CFR Pruning Formula:
   Traverse Branch If: Branch Flow >= min(50 USDT, Total Stolen Amount / (N_branches * 1.5))
2. Mule-Cluster Aggregation:
   Collapses >= 5 intermediate fan-out splits into a single compound node with internal tabular data.
"""

from typing import List, Dict, Any, Tuple, Optional
from app.schemas.traversal import MuleClusterDetail, MuleMember


class CFRPruner:
    """Dynamic CFR Pruning Evaluator."""

    def __init__(
        self,
        min_floor_usdt: float = 50.0,
        dilution_factor: float = 1.5
    ):
        self.min_floor_usdt = min_floor_usdt
        self.dilution_factor = max(0.1, dilution_factor)

    def calculate_threshold(self, total_stolen_usdt: float, branch_fan_out_count: int) -> float:
        """Calculate dynamic flow threshold for pruning sub-dust noise while catching smurfing splits."""
        if branch_fan_out_count <= 0:
            return 0.0
        
        dynamic_dilution = total_stolen_usdt / (branch_fan_out_count * self.dilution_factor)
        return min(self.min_floor_usdt, dynamic_dilution)

    def should_traverse(
        self,
        branch_amount: float,
        total_stolen_usdt: float,
        branch_fan_out_count: int
    ) -> Tuple[bool, float]:
        """Evaluate if branch flow passes threshold. Returns (should_traverse, threshold)."""
        threshold = self.calculate_threshold(total_stolen_usdt, branch_fan_out_count)
        passes = branch_amount >= threshold
        return passes, threshold


class MuleClusterDetector:
    """Detects and aggregates smurfing mule rings."""

    def __init__(self, split_threshold: int = 5):
        self.split_threshold = split_threshold

    def is_mule_cluster(self, splits_count: int) -> bool:
        """Check if fan-out count meets mule cluster threshold (default >= 5)."""
        return splits_count >= self.split_threshold

    def create_mule_cluster(
        self,
        parent_address: str,
        outflows: List[Dict[str, Any]],
        parent_total_volume: float
    ) -> MuleClusterDetail:
        """Aggregate multiple split branches into a unified MuleClusterDetail."""
        cluster_id = f"MULE_CLUSTER_{parent_address[:10]}_{len(outflows)}"
        total_cluster_volume = 0.0
        members: List[MuleMember] = []

        for out in outflows:
            amt = float(out.get("amount", 0.0))
            total_cluster_volume += amt
            pct = (amt / parent_total_volume * 100.0) if parent_total_volume > 0 else 0.0
            
            members.append(MuleMember(
                address=out.get("to_address", ""),
                split_amount=amt,
                percentage_of_parent=round(pct, 2),
                current_balance=float(out.get("current_balance", amt)),
                gas_funder=out.get("gas_funder"),
                tx_hash=out.get("tx_hash")
            ))

        return MuleClusterDetail(
            cluster_id=cluster_id,
            parent_address=parent_address,
            total_wallets=len(members),
            total_volume_usdt=round(total_cluster_volume, 2),
            members=members
        )
