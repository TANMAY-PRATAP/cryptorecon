"""Forensic Graph Builder with NetworkX and Cytoscape / Cypher Export.

Constructs multi-hop transaction topologies, collapses mule rings into composite nodes,
applies risk-based color-coding, and exports to Cytoscape.js & Neo4j Cypher.
"""

from typing import List, Dict, Any, Optional, Set
import networkx as nx
from app.schemas.traversal import (
    NodeCategory,
    CytoscapeNodeData,
    CytoscapeEdgeData,
    CytoscapeElement,
    CytoscapeGraphResponse,
    MuleClusterDetail,
)


def get_risk_color(risk_score: int, is_breakpoint: bool = False, is_vasp: bool = False) -> str:
    """Determine UI node color based on PRD color coding rules:
    - Green (<= 35) -> #10b981
    - Yellow / Amber (36–70) -> #f59e0b
    - Red (>= 71) -> #ef4444
    - Purple (CRYPTOGRAPHIC_BREAKPOINT) -> #a855f7
    - Blue (VASP Nodal) -> #3b82f6
    """
    if is_breakpoint:
        return "#a855f7"  # Purple for Mixer / Breakpoint
    if is_vasp:
        return "#3b82f6"  # Blue for VASP
    if risk_score >= 71:
        return "#ef4444"  # Red
    elif risk_score >= 36:
        return "#f59e0b"  # Amber Yellow
    else:
        return "#10b981"  # Emerald Green


class ForensicGraphBuilder:
    """Graph engine maintaining multi-hop forensic traversal topology."""

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.mule_clusters: Dict[str, MuleClusterDetail] = {}
        self.pruned_branches_count = 0
        self.attributed_vasps: Set[str] = set()

    def add_wallet_node(
        self,
        address: str,
        blockchain: str,
        label: Optional[str] = None,
        risk_score: int = 0,
        is_suspect: bool = False,
        hop_level: int = 0,
        attribution: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a wallet node with risk metrics and attribution metadata."""
        node_id = address.lower()
        category = NodeCategory.SUSPECT if is_suspect else NodeCategory.WALLET
        color = get_risk_color(risk_score)

        self.graph.add_node(
            node_id,
            id=node_id,
            label=label or (f"Suspect: {address[:6]}...{address[-4:]}" if is_suspect else f"{address[:6]}...{address[-4:]}"),
            category=category.value,
            address=address,
            blockchain=blockchain,
            risk_score=risk_score,
            color_code=color,
            is_breakpoint=False,
            is_mule_cluster=False,
            is_suspect=is_suspect,
            hop_level=hop_level,
            attribution=attribution
        )

    def add_vasp_node(
        self,
        address: str,
        vasp_name: str,
        blockchain: str,
        entity_type: str = "VASP_HOT_WALLET",
        risk_score: int = 15,
        hop_level: int = 1,
        attribution_tier: str = "TIER_0_DIRECT_BLOOM"
    ) -> None:
        """Add an identified VASP exchange node."""
        node_id = address.lower()
        self.attributed_vasps.add(vasp_name)

        self.graph.add_node(
            node_id,
            id=node_id,
            label=f"VASP: {vasp_name}",
            category=NodeCategory.VASP.value,
            address=address,
            blockchain=blockchain,
            risk_score=risk_score,
            color_code="#3b82f6",  # Blue
            is_breakpoint=False,
            is_mule_cluster=False,
            hop_level=hop_level,
            attribution={
                "vasp_name": vasp_name,
                "entity_type": entity_type,
                "tier": attribution_tier
            }
        )

    def add_mixer_node(
        self,
        address: str,
        mixer_protocol: str,
        blockchain: str,
        hop_level: int = 1
    ) -> None:
        """Add a Mixer Obfuscation Breakpoint node (100% risk, purple)."""
        node_id = address.lower()
        self.graph.add_node(
            node_id,
            id=node_id,
            label=f"MIXER: {mixer_protocol}",
            category=NodeCategory.MIXER_POOL.value,
            address=address,
            blockchain=blockchain,
            risk_score=100,
            color_code="#a855f7",  # Purple
            is_breakpoint=True,
            is_mule_cluster=False,
            hop_level=hop_level,
            attribution={"protocol": mixer_protocol, "status": "CRYPTOGRAPHIC_BREAKPOINT"}
        )

    def add_mule_cluster_node(
        self,
        mule_cluster: MuleClusterDetail,
        blockchain: str,
        hop_level: int = 1
    ) -> None:
        """Add a collapsed composite MuleCluster node with internal tabular breakdown."""
        cluster_id = str(mule_cluster.cluster_id).lower()
        self.mule_clusters[cluster_id] = mule_cluster

        self.graph.add_node(
            cluster_id,
            id=cluster_id,
            label=f"Mule Ring ({mule_cluster.total_wallets} wallets | {mule_cluster.total_volume_usdt:,.0f} USDT)",
            category=NodeCategory.MULE_CLUSTER.value,
            address=None,
            blockchain=blockchain,
            risk_score=85,
            color_code="#f97316",  # Orange for smurfing cluster
            is_breakpoint=False,
            is_mule_cluster=True,
            cluster_data=mule_cluster.model_dump(),
            hop_level=hop_level
        )

    def add_transfer_edge(
        self,
        source_id: str,
        target_id: str,
        amount: float,
        token: str,
        tx_hash: str,
        timestamp_utc: Optional[str] = None
    ) -> None:
        """Add a directed value transfer edge between nodes."""
        edge_key = f"{source_id.lower()}_{target_id.lower()}_{tx_hash[:10]}"
        self.graph.add_edge(
            source_id.lower(),
            target_id.lower(),
            key=edge_key,
            id=edge_key,
            source=source_id.lower(),
            target=target_id.lower(),
            amount=amount,
            token=token,
            tx_hash=tx_hash,
            timestamp_utc=timestamp_utc,
            label=f"{amount:,.2f} {token}"
        )

    def record_pruned_branch(self) -> None:
        """Increment count of branches dropped by dynamic CFR formula."""
        self.pruned_branches_count += 1

    def to_cytoscape_json(self) -> CytoscapeGraphResponse:
        """Export graph topology into Cytoscape.js compatible JSON format."""
        elements: List[Dict[str, Any]] = []

        # Export Nodes
        for node_id, data in self.graph.nodes(data=True):
            elements.append({
                "group": "nodes",
                "data": data,
                "classes": f"category-{data.get('category', 'WALLET').lower()}"
            })

        # Export Edges
        for u, v, k, data in self.graph.edges(keys=True, data=True):
            elements.append({
                "group": "edges",
                "data": data,
                "classes": "fund-transfer-edge"
            })

        # Determine max hop depth
        max_hop = 0
        for _, data in self.graph.nodes(data=True):
            max_hop = max(max_hop, data.get("hop_level", 0))

        return CytoscapeGraphResponse(
            elements=elements,
            total_nodes=self.graph.number_of_nodes(),
            total_edges=self.graph.number_of_edges(),
            mule_clusters_count=len(self.mule_clusters),
            attributed_vasps=sorted(list(self.attributed_vasps)),
            max_hops_traversed=max_hop,
            cfr_pruned_branches_count=self.pruned_branches_count
        )

    def to_cypher_queries(self) -> List[str]:
        """Export graph structure into Neo4j Cypher statements matching PRD Section 4."""
        queries: List[str] = []

        # Node Queries
        for node_id, data in self.graph.nodes(data=True):
            category = data.get("category")
            if category == NodeCategory.VASP.value:
                vasp_name = data.get("attribution", {}).get("vasp_name", "Unknown VASP")
                queries.append(
                    f"MERGE (v:VASP {{name: '{vasp_name}', address: '{data.get('address', '')}'}})"
                )
            elif category == NodeCategory.MULE_CLUSTER.value:
                c_data = data.get("cluster_data", {})
                queries.append(
                    f"MERGE (m:MuleCluster {{cluster_id: '{data.get('id')}', "
                    f"total_wallets: {c_data.get('total_wallets', 0)}, "
                    f"total_volume: {c_data.get('total_volume_usdt', 0.0)}}})"
                )
            elif category == NodeCategory.MIXER_POOL.value:
                protocol = data.get("attribution", {}).get("protocol", "Mixer")
                queries.append(
                    f"MERGE (p:MixerPool {{contract_address: '{data.get('address', '')}', "
                    f"protocol: '{protocol}', breakpoint: true}})"
                )
            else:
                is_mule = data.get("risk_score", 0) >= 70
                queries.append(
                    f"MERGE (w:Wallet {{address: '{data.get('address', '')}', "
                    f"chain: '{data.get('blockchain', '')}', "
                    f"risk_score: {data.get('risk_score', 0)}, is_mule: {str(is_mule).lower()}}})"
                )

        # Edge Queries
        for u, v, data in self.graph.edges(data=True):
            queries.append(
                f"MATCH (a {{id: '{u}'}}), (b {{id: '{v}'}}) "
                f"MERGE (a)-[:TRANSFERRED {{tx_hash: '{data.get('tx_hash', '')}', "
                f"token: '{data.get('token', '')}', amount: {data.get('amount', 0.0)}}}]->(b)"
            )

        return queries
