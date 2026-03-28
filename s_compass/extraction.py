"""
extraction.py

Claim extraction and evidence linking for S Compass (Design-doc §4.4, §16 v1).

Extracts claims from model output text and builds evidence links against
retrieved context, producing the claim/evidence graph that feeds into the
I estimator and the coherence graph (§4.4 internal modules 1–2).
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
# Convenience: extract + link in one call
# ---------------------------------------------------------------------------

def extract_and_link(step: StepInput) -> Tuple[List[Claim], List[Evidence], List[GraphEdge]]:
    """Extract claims from a step and link them to retrieved evidence.

    Combines :func:`extract_claims` and :func:`link_evidence` into a single
    pipeline call suitable for gateway integration.
    """
    claims = extract_claims(
        step.output_text,
        trace_id=step.trace_id,
    )
    evidences, edges = link_evidence(claims, step.retrieved_context)
    return claims, evidences, edges
