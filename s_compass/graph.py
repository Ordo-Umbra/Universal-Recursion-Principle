"""
graph.py

Coherence graph builder and analyser for S Compass (Design-doc §4.4, §8.4).

Builds a networkx graph from extracted claims, evidence nodes, and edges,
then computes structural metrics used by the I estimator and exposed via
the ``GET /v1/trace/{trace_id}/graph`` API endpoint.
"""

from __future__ import annotations

from typing import Any, Dict, List

import networkx as nx

from .schemas import Claim, Evidence, GraphEdge


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_coherence_graph(
    claims: List[Claim],
    evidences: List[Evidence],
    edges: List[GraphEdge],
) -> nx.DiGraph:
    """Build a directed coherence graph from claims, evidence, and edges.

    Claim nodes are labelled ``"claim"`` and evidence nodes ``"evidence"``.
    Each :class:`GraphEdge` becomes a directed edge from ``source_id`` to
    ``target_id`` with ``edge_type`` and ``weight`` attributes.
    """
    g = nx.DiGraph()

    for claim in claims:
        g.add_node(
            claim.claim_id,
            kind="claim",
            text=claim.text,
            claim_type=claim.claim_type,
            confidence=claim.confidence,
        )

    for ev in evidences:
        g.add_node(
            ev.evidence_id,
            kind="evidence",
            text=ev.text,
            doc_id=ev.doc_id,
            support_type=ev.support_type,
            weight=ev.weight,
        )

    for edge in edges:
        g.add_edge(
            edge.source_id,
            edge.target_id,
            edge_type=edge.edge_type,
            weight=edge.weight,
            edge_id=edge.edge_id,
        )

    return g


# ---------------------------------------------------------------------------
# Graph metrics (Design-doc §19.2 — support graph density / connectivity)
# ---------------------------------------------------------------------------

def graph_density(g: nx.DiGraph) -> float:
    """Edge density of the coherence graph, in [0, 1]."""
    return nx.density(g) if g.number_of_nodes() > 1 else 0.0


def claim_grounding_ratio(g: nx.DiGraph) -> float:
    """Fraction of claim nodes that have at least one outgoing evidence edge."""
    claim_nodes = [n for n, d in g.nodes(data=True) if d.get("kind") == "claim"]
    if not claim_nodes:
        return 1.0  # vacuously grounded
    grounded = sum(1 for n in claim_nodes if g.out_degree(n) > 0)
    return grounded / len(claim_nodes)


def avg_support_weight(g: nx.DiGraph) -> float:
    """Average weight of ``supported_by`` edges."""
    weights = [
        d["weight"]
        for _, _, d in g.edges(data=True)
        if d.get("edge_type") == "supported_by"
    ]
    return sum(weights) / len(weights) if weights else 0.0


def weakly_connected_ratio(g: nx.DiGraph) -> float:
    """Fraction of nodes in the largest weakly connected component."""
    if g.number_of_nodes() == 0:
        return 0.0
    largest_cc = max(nx.weakly_connected_components(g), key=len)
    return len(largest_cc) / g.number_of_nodes()


# ---------------------------------------------------------------------------
# Coherence analysis summary
# ---------------------------------------------------------------------------

def analyse_coherence(
    claims: List[Claim],
    evidences: List[Evidence],
    edges: List[GraphEdge],
) -> Dict[str, Any]:
    """Build the coherence graph and return a summary dict.

    This is the high-level entry point used by the gateway and
    the ``GET /v1/trace/{trace_id}/graph`` API endpoint.

    Returns
    -------
    dict
        Keys: ``nodes``, ``edges``, ``density``, ``grounding_ratio``,
        ``avg_support_weight``, ``connected_ratio``.
    """
    g = build_coherence_graph(claims, evidences, edges)
    return {
        "nodes": g.number_of_nodes(),
        "edges": g.number_of_edges(),
        "density": round(graph_density(g), 4),
        "grounding_ratio": round(claim_grounding_ratio(g), 4),
        "avg_support_weight": round(avg_support_weight(g), 4),
        "connected_ratio": round(weakly_connected_ratio(g), 4),
        "claim_ids": [
            n for n, d in g.nodes(data=True) if d.get("kind") == "claim"
        ],
        "evidence_ids": [
            n for n, d in g.nodes(data=True) if d.get("kind") == "evidence"
        ],
    }


def graph_to_dict(g: nx.DiGraph) -> Dict[str, Any]:
    """Serialise a coherence graph to a JSON-safe dict (for API responses)."""
    nodes = []
    for nid, data in g.nodes(data=True):
        node = {"id": nid}
        node.update(data)
        nodes.append(node)
    edge_list = []
    for src, tgt, data in g.edges(data=True):
        edge = {"source": src, "target": tgt}
        edge.update(data)
        edge_list.append(edge)
    return {"nodes": nodes, "edges": edge_list}
