"""
test_graph.py

Tests for the s_compass.graph module (coherence graph builder and analyser
per Design-doc §4.4, §8.4).
"""

import pytest

import networkx as nx

from s_compass.schemas import Claim, Evidence, GraphEdge
from s_compass.graph import (
    analyse_coherence,
    avg_support_weight,
    build_coherence_graph,
    claim_grounding_ratio,
    graph_density,
    graph_to_dict,
    weakly_connected_ratio,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _sample_data():
    """Return a small set of claims, evidence, and edges."""
    c1 = Claim(text="S equals C plus kappa I", claim_id="claim_001")
    c2 = Claim(text="Kappa measures capacity", claim_id="claim_002")
    ev1 = Evidence(doc_id="doc1", text="The formula is S = C + kI", evidence_id="ev_001")
    ev2 = Evidence(doc_id="doc2", text="Capacity field kappa", evidence_id="ev_002")
    e1 = GraphEdge(source_id="claim_001", target_id="ev_001", weight=0.9)
    e2 = GraphEdge(source_id="claim_002", target_id="ev_002", weight=0.7)
    return [c1, c2], [ev1, ev2], [e1, e2]


# ===========================================================================
# Graph construction
# ===========================================================================

class TestBuildCoherenceGraph:
    def test_builds_directed_graph(self):
        claims, evidences, edges = _sample_data()
        g = build_coherence_graph(claims, evidences, edges)
        assert isinstance(g, nx.DiGraph)

    def test_node_count(self):
        claims, evidences, edges = _sample_data()
        g = build_coherence_graph(claims, evidences, edges)
        assert g.number_of_nodes() == 4  # 2 claims + 2 evidence

    def test_edge_count(self):
        claims, evidences, edges = _sample_data()
        g = build_coherence_graph(claims, evidences, edges)
        assert g.number_of_edges() == 2

    def test_claim_node_attributes(self):
        claims, evidences, edges = _sample_data()
        g = build_coherence_graph(claims, evidences, edges)
        node_data = g.nodes["claim_001"]
        assert node_data["kind"] == "claim"
        assert "text" in node_data

    def test_evidence_node_attributes(self):
        claims, evidences, edges = _sample_data()
        g = build_coherence_graph(claims, evidences, edges)
        node_data = g.nodes["ev_001"]
        assert node_data["kind"] == "evidence"
        assert node_data["doc_id"] == "doc1"

    def test_edge_attributes(self):
        claims, evidences, edges = _sample_data()
        g = build_coherence_graph(claims, evidences, edges)
        edge_data = g.edges["claim_001", "ev_001"]
        assert edge_data["edge_type"] == "supported_by"
        assert edge_data["weight"] == 0.9

    def test_empty_inputs(self):
        g = build_coherence_graph([], [], [])
        assert g.number_of_nodes() == 0
        assert g.number_of_edges() == 0


# ===========================================================================
# Graph metrics
# ===========================================================================

class TestGraphMetrics:
    def test_graph_density_nonzero(self):
        claims, evidences, edges = _sample_data()
        g = build_coherence_graph(claims, evidences, edges)
        d = graph_density(g)
        assert 0.0 < d <= 1.0

    def test_graph_density_empty(self):
        g = build_coherence_graph([], [], [])
        assert graph_density(g) == 0.0

    def test_claim_grounding_ratio_fully_grounded(self):
        claims, evidences, edges = _sample_data()
        g = build_coherence_graph(claims, evidences, edges)
        ratio = claim_grounding_ratio(g)
        assert ratio == pytest.approx(1.0)

    def test_claim_grounding_ratio_partially_grounded(self):
        c1 = Claim(text="Grounded claim", claim_id="claim_g")
        c2 = Claim(text="Ungrounded claim", claim_id="claim_u")
        ev = Evidence(doc_id="d1", text="Support", evidence_id="ev_g")
        edge = GraphEdge(source_id="claim_g", target_id="ev_g")
        g = build_coherence_graph([c1, c2], [ev], [edge])
        ratio = claim_grounding_ratio(g)
        assert ratio == pytest.approx(0.5)

    def test_claim_grounding_ratio_no_claims(self):
        g = build_coherence_graph([], [], [])
        assert claim_grounding_ratio(g) == 1.0

    def test_avg_support_weight(self):
        claims, evidences, edges = _sample_data()
        g = build_coherence_graph(claims, evidences, edges)
        avg = avg_support_weight(g)
        assert avg == pytest.approx(0.8)  # (0.9 + 0.7) / 2

    def test_avg_support_weight_empty(self):
        g = build_coherence_graph([], [], [])
        assert avg_support_weight(g) == 0.0

    def test_weakly_connected_ratio(self):
        claims, evidences, edges = _sample_data()
        g = build_coherence_graph(claims, evidences, edges)
        ratio = weakly_connected_ratio(g)
        # Two disconnected components each with 2 nodes → ratio = 0.5
        assert 0.0 < ratio <= 1.0

    def test_weakly_connected_ratio_empty(self):
        g = build_coherence_graph([], [], [])
        assert weakly_connected_ratio(g) == 0.0


# ===========================================================================
# Coherence analysis
# ===========================================================================

class TestAnalyseCoherence:
    def test_returns_summary_dict(self):
        claims, evidences, edges = _sample_data()
        result = analyse_coherence(claims, evidences, edges)
        assert "nodes" in result
        assert "edges" in result
        assert "density" in result
        assert "grounding_ratio" in result
        assert "avg_support_weight" in result
        assert "connected_ratio" in result
        assert "claim_ids" in result
        assert "evidence_ids" in result

    def test_node_and_edge_counts(self):
        claims, evidences, edges = _sample_data()
        result = analyse_coherence(claims, evidences, edges)
        assert result["nodes"] == 4
        assert result["edges"] == 2

    def test_empty_analysis(self):
        result = analyse_coherence([], [], [])
        assert result["nodes"] == 0
        assert result["edges"] == 0
        assert result["density"] == 0.0


# ===========================================================================
# Graph serialisation
# ===========================================================================

class TestGraphToDict:
    def test_serialises_to_dict(self):
        claims, evidences, edges = _sample_data()
        g = build_coherence_graph(claims, evidences, edges)
        data = graph_to_dict(g)
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 4
        assert len(data["edges"]) == 2

    def test_node_has_id(self):
        claims, evidences, edges = _sample_data()
        g = build_coherence_graph(claims, evidences, edges)
        data = graph_to_dict(g)
        for node in data["nodes"]:
            assert "id" in node

    def test_edge_has_source_and_target(self):
        claims, evidences, edges = _sample_data()
        g = build_coherence_graph(claims, evidences, edges)
        data = graph_to_dict(g)
        for edge in data["edges"]:
            assert "source" in edge
            assert "target" in edge
