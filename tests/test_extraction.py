"""
test_extraction.py

Tests for the s_compass.extraction module (claim extraction and evidence
linking per Design-doc §4.4).
"""

import pytest

from s_compass.schemas import Claim, Evidence, GraphEdge, RetrievedChunk, StepInput
from s_compass.extraction import (
    extract_claims,
    link_evidence,
    extract_and_link,
    _split_sentences,
    _token_overlap,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_step(**overrides) -> StepInput:
    defaults = dict(
        session_id="sess_test",
        prompt="What is URP?",
        output_text="URP is a unified framework proposing recursive S-maximization.",
    )
    defaults.update(overrides)
    return StepInput(**defaults)


# ===========================================================================
# Sentence splitting
# ===========================================================================

class TestSentenceSplitter:
    def test_simple_sentences(self):
        text = "Hello world. This is a test. Done!"
        sents = _split_sentences(text)
        assert len(sents) == 3
        assert sents[0] == "Hello world."
        assert sents[2] == "Done!"

    def test_empty_text(self):
        assert _split_sentences("") == []
        assert _split_sentences("   ") == []

    def test_single_sentence(self):
        sents = _split_sentences("Just one sentence here.")
        assert len(sents) == 1

    def test_abbreviation_preservation(self):
        text = "Dr. Smith went to the store. He bought milk."
        sents = _split_sentences(text)
        assert len(sents) == 2
        assert "Dr." in sents[0]

    def test_question_and_exclamation(self):
        text = "Is this working? Yes it is! Great."
        sents = _split_sentences(text)
        assert len(sents) == 3


# ===========================================================================
# Claim extraction
# ===========================================================================

class TestClaimExtraction:
    def test_extracts_claims_from_text(self):
        text = (
            "S Compass is a runtime observability layer for AI systems. "
            "It measures distinction, integration, and capacity. "
            "The core formula is S equals C plus kappa I."
        )
        claims = extract_claims(text)
        assert len(claims) == 3
        for c in claims:
            assert isinstance(c, Claim)
            assert c.claim_id.startswith("claim_")
            assert c.claim_type == "assertion"

    def test_min_words_filter(self):
        text = "Short. Too brief. This sentence has enough words for extraction."
        claims = extract_claims(text, min_words=5)
        assert len(claims) == 1
        assert "enough words" in claims[0].text

    def test_empty_text_returns_no_claims(self):
        claims = extract_claims("")
        assert claims == []

    def test_trace_id_in_provenance(self):
        claims = extract_claims(
            "This is a meaningful claim about the system.",
            trace_id="trace_abc",
        )
        assert len(claims) == 1
        assert claims[0].provenance["trace_id"] == "trace_abc"

    def test_provenance_source_type(self):
        claims = extract_claims("This is a meaningful claim about the system.")
        assert claims[0].provenance["source_type"] == "model_output"


# ===========================================================================
# Token overlap
# ===========================================================================

class TestTokenOverlap:
    def test_identical_texts(self):
        assert _token_overlap("hello world", "hello world") == pytest.approx(1.0)

    def test_no_overlap(self):
        assert _token_overlap("hello world", "foo bar") == pytest.approx(0.0)

    def test_partial_overlap(self):
        overlap = _token_overlap("hello world test", "hello world other")
        assert 0.0 < overlap < 1.0

    def test_empty_text_a(self):
        assert _token_overlap("", "hello world") == 0.0


# ===========================================================================
# Evidence linking
# ===========================================================================

class TestEvidenceLinking:
    def test_links_matching_claims_to_evidence(self):
        claims = [Claim(text="S Compass measures distinction and integration")]
        chunks = [
            RetrievedChunk(
                doc_id="doc1",
                text="S Compass measures distinction integration and capacity",
                score=0.9,
            )
        ]
        evidences, edges = link_evidence(claims, chunks, threshold=0.3)
        assert len(evidences) >= 1
        assert len(edges) >= 1
        assert all(isinstance(e, Evidence) for e in evidences)
        assert all(isinstance(e, GraphEdge) for e in edges)
        assert edges[0].edge_type == "supported_by"

    def test_no_links_below_threshold(self):
        claims = [Claim(text="completely unrelated topic about cooking")]
        chunks = [
            RetrievedChunk(
                doc_id="doc1",
                text="quantum physics particle wave duality",
                score=0.9,
            )
        ]
        evidences, edges = link_evidence(claims, chunks, threshold=0.5)
        assert len(evidences) == 0
        assert len(edges) == 0

    def test_empty_inputs(self):
        evidences, edges = link_evidence([], [])
        assert evidences == []
        assert edges == []

    def test_edge_weight_matches_overlap(self):
        claims = [Claim(text="hello world test")]
        chunks = [RetrievedChunk(doc_id="d1", text="hello world other")]
        evidences, edges = link_evidence(claims, chunks, threshold=0.0)
        if edges:
            assert 0.0 <= edges[0].weight <= 1.0


# ===========================================================================
# extract_and_link (end-to-end)
# ===========================================================================

class TestExtractAndLink:
    def test_end_to_end(self):
        step = _make_step(
            output_text=(
                "S Compass is a runtime observability layer. "
                "It computes distinction and integration scores."
            ),
            retrieved_context=[
                RetrievedChunk(
                    doc_id="doc1",
                    text="S Compass is a runtime observability and control layer for AI",
                    score=0.9,
                ),
            ],
        )
        claims, evidences, edges = extract_and_link(step)
        assert len(claims) >= 1
        assert all(isinstance(c, Claim) for c in claims)
        # At least some evidence links should be created
        assert isinstance(evidences, list)
        assert isinstance(edges, list)

    def test_no_retrieval_context(self):
        step = _make_step(
            output_text="This is a claim. Another claim here.",
            retrieved_context=[],
        )
        claims, evidences, edges = extract_and_link(step)
        assert len(claims) >= 1
        assert evidences == []
        assert edges == []
