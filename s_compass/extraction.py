"""
extraction.py

Claim extraction, evidence linking, and contradiction detection for S Compass
(Design-doc §4.4, §16 v1).

Extracts claims from model output text, builds evidence links against
retrieved context, and detects contradictions between claims, producing the
claim/evidence graph that feeds into the I estimator and the coherence graph
(§4.4 internal modules 1–3).
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from .schemas import Claim, Evidence, GraphEdge, RetrievedChunk, StepInput


# ---------------------------------------------------------------------------
# Sentence splitter
# ---------------------------------------------------------------------------

_ABBREVS = {"dr", "mr", "ms", "mrs", "prof", "jr", "sr", "vs", "etc"}


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences using a simple heuristic.

    Splits on sentence-ending punctuation (.!?) followed by whitespace,
    while avoiding splits after common abbreviations.
    """
    if not text.strip():
        return []

    # Split on sentence-ending punctuation followed by a space
    raw = re.split(r"(?<=[.!?])\s+", text.strip())

    # Rejoin fragments that were split after an abbreviation
    merged: List[str] = []
    for part in raw:
        if merged and merged[-1].split()[-1].rstrip(".").lower() in _ABBREVS:
            merged[-1] = merged[-1] + " " + part
        else:
            merged.append(part)

    return [s.strip() for s in merged if s.strip()]


# ---------------------------------------------------------------------------
# Claim extractor (Design-doc §4.4, module 1)
# ---------------------------------------------------------------------------

def extract_claims(
    output_text: str,
    *,
    min_words: int = 4,
    trace_id: Optional[str] = None,
) -> List[Claim]:
    """Extract candidate claims from model output text.

    Each sentence with at least *min_words* is treated as a claim.  This is
    the heuristic baseline; later versions can plug in NLI or structured
    extraction models.

    Parameters
    ----------
    output_text:
        The raw model output.
    min_words:
        Minimum number of whitespace tokens for a sentence to count as a
        claim.
    trace_id:
        Optional trace identifier attached to provenance.

    Returns
    -------
    List[Claim]
        Extracted claims with provenance metadata.
    """
    sentences = _split_sentences(output_text)
    claims: List[Claim] = []
    for sent in sentences:
        if len(sent.split()) < min_words:
            continue
        provenance = {"source_type": "model_output"}
        if trace_id:
            provenance["trace_id"] = trace_id
        claims.append(
            Claim(
                text=sent,
                claim_type="assertion",
                confidence=1.0,
                provenance=provenance,
            )
        )
    return claims


# ---------------------------------------------------------------------------
# Evidence linker (Design-doc §4.4, module 2)
# ---------------------------------------------------------------------------

def _token_overlap(text_a: str, text_b: str) -> float:
    """Proportion of tokens in *text_a* that appear in *text_b*."""
    toks_a = set(text_a.lower().split())
    toks_b = set(text_b.lower().split())
    if not toks_a:
        return 0.0
    return len(toks_a & toks_b) / len(toks_a)


def link_evidence(
    claims: List[Claim],
    retrieved_context: List[RetrievedChunk],
    *,
    threshold: float = 0.3,
) -> Tuple[List[Evidence], List[GraphEdge]]:
    """Link claims to supporting evidence from retrieved context.

    For each (claim, chunk) pair whose token overlap exceeds *threshold*,
    an :class:`Evidence` node and a ``supported_by`` :class:`GraphEdge` are
    emitted.

    Parameters
    ----------
    claims:
        Previously extracted claims.
    retrieved_context:
        Retrieval results available for the step.
    threshold:
        Minimum token-overlap score to create a link.

    Returns
    -------
    (List[Evidence], List[GraphEdge])
        Evidence nodes and edges linking claims to evidence.
    """
    evidences: List[Evidence] = []
    edges: List[GraphEdge] = []
    for claim in claims:
        for chunk in retrieved_context:
            overlap = _token_overlap(claim.text, chunk.text)
            if overlap >= threshold:
                ev = Evidence(
                    doc_id=chunk.doc_id,
                    text=chunk.text,
                    support_type="direct",
                    weight=round(overlap, 4),
                    chunk_id=chunk.chunk_id,
                )
                edge = GraphEdge(
                    source_id=claim.claim_id,
                    target_id=ev.evidence_id,
                    edge_type="supported_by",
                    weight=round(overlap, 4),
                )
                evidences.append(ev)
                edges.append(edge)
    return evidences, edges


# ---------------------------------------------------------------------------
# Contradiction detector (Design-doc §4.4, module 3 / §11 contradiction_penalty)
# ---------------------------------------------------------------------------

_NEGATION_TOKENS = frozenset(
    {
        "not", "no", "never", "neither", "nor", "cannot", "cant", "wont",
        "dont", "doesnt", "didnt", "isnt", "arent", "wasnt", "werent",
        "hasnt", "havent", "hadnt", "shouldnt", "wouldnt", "couldnt",
        "without", "false", "incorrect", "wrong", "impossible",
    }
)


def _has_negation(text: str) -> bool:
    """Return True if *text* contains a negation token."""
    tokens = set(re.sub(r"[^\w\s]", "", text.lower()).split())
    return bool(tokens & _NEGATION_TOKENS)


def detect_contradictions(
    claims: List[Claim],
    *,
    overlap_threshold: float = 0.3,
) -> List[GraphEdge]:
    """Detect pairs of claims that likely contradict each other.

    Two claims are flagged as contradictory when they share significant topic
    overlap (measured by :func:`_token_overlap`) yet differ in polarity: one
    contains negation words and the other does not.  A ``contradicts``
    :class:`GraphEdge` is emitted for each such pair (both directions, so the
    graph is symmetric).

    This implements module 3 of the I Estimator pipeline (Design-doc §4.4
    §11 contradiction_penalty).

    Parameters
    ----------
    claims:
        Previously extracted claims.
    overlap_threshold:
        Minimum token-overlap score to consider two claims as discussing the
        same topic.

    Returns
    -------
    List[GraphEdge]
        Contradiction edges between conflicting claims.
    """
    edges: List[GraphEdge] = []
    for idx_a in range(len(claims)):
        for idx_b in range(idx_a + 1, len(claims)):
            claim_a = claims[idx_a]
            claim_b = claims[idx_b]
            overlap = _token_overlap(claim_a.text, claim_b.text)
            if overlap < overlap_threshold:
                continue
            neg_a = _has_negation(claim_a.text)
            neg_b = _has_negation(claim_b.text)
            if neg_a == neg_b:
                # Both affirm or both negate — no contradiction signal
                continue
            # One negates, one affirms the same topic → contradiction
            edges.append(
                GraphEdge(
                    source_id=claim_a.claim_id,
                    target_id=claim_b.claim_id,
                    edge_type="contradicts",
                    weight=round(overlap, 4),
                )
            )
            edges.append(
                GraphEdge(
                    source_id=claim_b.claim_id,
                    target_id=claim_a.claim_id,
                    edge_type="contradicts",
                    weight=round(overlap, 4),
                )
            )
    return edges


# ---------------------------------------------------------------------------
# Convenience: extract + link in one call
# ---------------------------------------------------------------------------

def extract_and_link(step: StepInput) -> Tuple[List[Claim], List[Evidence], List[GraphEdge]]:
    """Extract claims from a step, link evidence, and detect contradictions.

    Combines :func:`extract_claims`, :func:`link_evidence`, and
    :func:`detect_contradictions` into a single pipeline call suitable for
    gateway integration.  The returned edges include both ``supported_by``
    links from retrieved context and ``contradicts`` links between claims.
    """
    claims = extract_claims(
        step.output_text,
        trace_id=step.trace_id,
    )
    evidences, support_edges = link_evidence(claims, step.retrieved_context)
    contradiction_edges = detect_contradictions(claims)
    return claims, evidences, support_edges + contradiction_edges
