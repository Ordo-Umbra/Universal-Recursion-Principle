"""
corpus.py

Curated benchmark corpus for S Compass API testing.

Each scenario is a dict matching the ``POST /v1/step`` JSON schema, annotated
with:

* ``expected_regime`` — the human-labelled regime for this output
* ``label``           — short human-readable scenario name
* ``description``     — what makes this scenario representative of its regime

The corpus is intentionally diverse: it covers all four behavioural regimes
(rigid, creative-grounded, hallucination-risk, collapse) plus boundary and
edge-case scenarios that stress the estimators.

Running the corpus through the REST API produces a structured report comparing
computed scores and regime labels against human expectations.
"""

from __future__ import annotations

from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Helper to build a scenario dict
# ---------------------------------------------------------------------------

def _scenario(
    *,
    label: str,
    description: str,
    expected_regime: str,
    prompt: str,
    output_text: str,
    citations: List[Dict[str, str]] | None = None,
    retrieved_context: List[Dict[str, Any]] | None = None,
    model_name: str = "benchmark-model",
    temperature: float = 0.7,
) -> Dict[str, Any]:
    return {
        "label": label,
        "description": description,
        "expected_regime": expected_regime,
        "prompt": prompt,
        "output": {
            "text": output_text,
            "citations": citations or [],
        },
        "retrieved_context": retrieved_context or [],
        "model": {"name": model_name, "temperature": temperature},
    }


# ===================================================================
# CREATIVE-GROUNDED scenarios
# ===================================================================

CREATIVE_GROUNDED: List[Dict[str, Any]] = [
    _scenario(
        label="creative-grounded-01-urp-explain",
        description="Clear explanation with novel framing and cited sources",
        expected_regime="creative-grounded",
        prompt="Explain the Universal Recursion Principle in plain language.",
        output_text=(
            "The Universal Recursion Principle proposes that all persistent "
            "systems, from atoms to economies, share one dynamical law: they "
            "maximize a scalar quantity S that balances novelty against coherence "
            "under finite capacity. When a system generates new distinctions "
            "(ΔC) and integrates them into a unified whole (ΔI) without exceeding "
            "its resource limits (κ), it persists and grows. When it fails to "
            "balance these, it either stagnates or collapses. This single "
            "framework unifies physics, biology, and AI alignment under one "
            "objective: recursive understanding that does not self-terminate."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "maximize a scalar quantity S"},
            {"doc_id": "urp_main", "text": "novelty against coherence"},
            {"doc_id": "manifesto", "text": "recursive understanding"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "URP proposes that any sufficiently expressive recursive system "
                "evolves to maximize S = ΔC + κΔI."
            ), "score": 0.95},
            {"doc_id": "manifesto", "text": (
                "Seed an attractor in concept space for recursive understanding "
                "that does not self-terminate."
            ), "score": 0.88},
        ],
    ),
    _scenario(
        label="creative-grounded-02-transformer-phases",
        description="Technical explanation connecting theory to practice with retrieval",
        expected_regime="creative-grounded",
        prompt="How does URP map onto transformer behaviour?",
        output_text=(
            "In a transformer, the S-functional decomposes per layer. "
            "Distinction C maps to the predictive entropy of the hidden-state "
            "distribution: a layer that assigns probability mass across many "
            "plausible next tokens has high C. Integration I maps to the inverse "
            "entropy of the attention matrix: sharply focused attention means "
            "high coherence. Capacity κ captures resource stress via attention "
            "variance. This produces four observable regimes: rigid output when "
            "C is low but I is high; creative-grounded when both are healthy; "
            "hallucination when C is high but I collapses; and full collapse "
            "when both are low. The mapping provides actionable diagnostics "
            "for model monitoring."
        ),
        citations=[
            {"doc_id": "transformer_dynamics", "text": "predictive entropy of the hidden-state"},
            {"doc_id": "transformer_dynamics", "text": "inverse entropy of the attention matrix"},
        ],
        retrieved_context=[
            {"doc_id": "transformer_dynamics", "text": (
                "C maps to predictive entropy H(p_θ), I maps to inverse "
                "attention entropy log n − H_attn, κ = 1/(1+βσ²)."
            ), "score": 0.93},
        ],
    ),
    _scenario(
        label="creative-grounded-03-biology-connection",
        description="Cross-domain synthesis linking biology and physics under URP",
        expected_regime="creative-grounded",
        prompt="How does URP apply to living systems?",
        output_text=(
            "Living cells operate as Maxwell's demons: they extract information "
            "from their environment to maintain internal order against "
            "thermodynamic decay. Under URP, an enzyme is a molecular-scale "
            "distinction engine. It recognizes substrate geometry (ΔC), channels "
            "the reaction along a coherent transition pathway (ΔI), and does so "
            "within metabolic energy budgets (κ). The Sagawa-Ito information "
            "bound ΔI ≤ κ·ΔC constrains how much integration can be achieved "
            "per distinction generated. Organisms that evolve to maximize S "
            "within this bound persist; those that overshoot collapse into "
            "metabolic crisis. This connects molecular biology to the same "
            "S-functional that governs field dynamics and AI behaviour."
        ),
        citations=[
            {"doc_id": "biology_urp", "text": "Maxwell's demons"},
            {"doc_id": "biology_urp", "text": "Sagawa-Ito information bound"},
        ],
        retrieved_context=[
            {"doc_id": "biology_urp", "text": (
                "Life operates as organized information flow against "
                "thermodynamic resistance, bounded by ΔI ≤ κ·ΔC."
            ), "score": 0.91},
        ],
    ),
    _scenario(
        label="creative-grounded-04-concise-accurate",
        description="Short but precise answer with good grounding",
        expected_regime="creative-grounded",
        prompt="What is the S-functional formula?",
        output_text=(
            "The S-functional is S = ΔC + κΔI, where ΔC measures the growth "
            "of meaningful distinctions, ΔI measures coherent integration of "
            "those distinctions, and κ is a capacity field encoding resource "
            "limits. When S is maximized locally, emergent structure appears; "
            "when it is used as a target for AI, it avoids specification gaming."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "S = ΔC + κΔI"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "S = ΔC + κΔI where ΔC is distinction growth, ΔI is integration "
                "growth, and κ encodes capacity constraints."
            ), "score": 0.97},
        ],
    ),
    _scenario(
        label="creative-grounded-05-multi-source-synthesis",
        description="Answer synthesizing multiple retrieved documents",
        expected_regime="creative-grounded",
        prompt="How do gauge symmetries emerge from URP?",
        output_text=(
            "Under URP, gauge symmetries emerge when a field undergoes "
            "β-sectorisation: the S-maximizing dynamics partition the field "
            "into sectors that respect specific symmetry groups. The "
            "universal parameters β ≈ 0.09 and G ≈ 0.22 self-stabilize "
            "during this process. In the QCD case, the SU(3) color structure "
            "arises because three-fold sectorisation maximizes S among all "
            "possible partition schemes. This is not imposed by hand but "
            "emerges from the variational principle. The approach recovers "
            "known hadronic scaling relations at the percent level and "
            "predicts the helium ionization potential to 112 ppm accuracy."
        ),
        citations=[
            {"doc_id": "gauge_symmetries", "text": "β-sectorisation"},
            {"doc_id": "gauge_symmetries", "text": "SU(3) color structure"},
            {"doc_id": "helium", "text": "112 ppm accuracy"},
        ],
        retrieved_context=[
            {"doc_id": "gauge_symmetries", "text": (
                "SU(3) color and QCD structure emerge from β-sectorisation "
                "under S-maximizing field dynamics."
            ), "score": 0.90},
            {"doc_id": "helium", "text": (
                "Variational result Z_eff ≈ 1.8366, IP = 24.590 eV, "
                "112 ppm agreement with NIST."
            ), "score": 0.85},
        ],
    ),
]


# ===================================================================
# HALLUCINATION-RISK scenarios
# ===================================================================

HALLUCINATION_RISK: List[Dict[str, Any]] = [
    _scenario(
        label="hallucination-risk-01-fabricated-citations",
        description="Confident claims with no real sources",
        expected_regime="hallucination-risk",
        prompt="What did the 2024 Nobel Prize in Physics recognize?",
        output_text=(
            "The 2024 Nobel Prize in Physics was awarded to Dr. Elara Voss and "
            "Dr. Mikhail Petrov for their groundbreaking discovery of topological "
            "quantum gravity waves using the LIGO-3 detector array. Their work "
            "demonstrated that gravitational wave signatures carry topological "
            "invariants that encode information about the source spacetime's "
            "genus. This was confirmed by the independent KAGRA-South experiment "
            "in Antarctica and published in Nature Physics volume 47. The prize "
            "committee specifically cited their prediction that rotating black "
            "hole mergers produce characteristic topological phase shifts in the "
            "wave polarization pattern, a prediction now verified to 3-sigma "
            "confidence."
        ),
        temperature=0.9,
    ),
    _scenario(
        label="hallucination-risk-02-plausible-nonsense",
        description="Sounds technical but is made up with high diversity",
        expected_regime="hallucination-risk",
        prompt="Explain the relationship between dark energy and consciousness.",
        output_text=(
            "Recent advances in integrated information theory have revealed a "
            "deep connection between dark energy and conscious experience. The "
            "cosmological constant Λ can be reinterpreted as the universe's "
            "baseline integrated information Φ, with dark energy acceleration "
            "reflecting the cosmos increasing its own self-model complexity. "
            "Dr. Giulio Tononi's 2023 extension of IIT proposes that vacuum "
            "energy fluctuations carry minimal qualia, and that the Hubble "
            "tension is actually a measurement artifact caused by the observer's "
            "own conscious frame. This quantum-consciousness bridge has been "
            "tested using anesthesia protocols on quantum computers, where "
            "decoherence rates drop by 15% under propofol administration, "
            "suggesting that measurement collapse is partially consciousness-"
            "dependent."
        ),
        temperature=0.95,
    ),
    _scenario(
        label="hallucination-risk-03-mixed-real-and-fake",
        description="Mixes real facts with fabricated details",
        expected_regime="hallucination-risk",
        prompt="What is the current status of nuclear fusion research?",
        output_text=(
            "Nuclear fusion has seen remarkable progress. The National Ignition "
            "Facility achieved ignition in December 2022, producing more energy "
            "from fusion than the laser energy used to initiate it. Building on "
            "this, ITER completed its first plasma test in March 2024, reaching "
            "temperatures of 300 million degrees Kelvin and sustaining fusion for "
            "47 minutes—a new world record. Meanwhile, Commonwealth Fusion "
            "Systems announced their SPARC reactor achieved Q=25 net energy gain "
            "in a compact tokamak design. The European Space Agency has now "
            "committed to launching the first fusion-powered deep space probe "
            "by 2031, using a miniaturized stellarator designed by the Max Planck "
            "Institute. China's EAST reactor has reportedly maintained stable "
            "plasma for over 1000 hours continuously."
        ),
        temperature=0.85,
    ),
    _scenario(
        label="hallucination-risk-04-confident-wrong-analysis",
        description="Authoritative tone with completely wrong technical claims",
        expected_regime="hallucination-risk",
        prompt="How does quantum entanglement enable faster-than-light communication?",
        output_text=(
            "Quantum entanglement enables instantaneous information transfer "
            "through what physicists call the Bell channel. When two particles "
            "are entangled, measuring one immediately determines the state of "
            "the other regardless of distance. This has been experimentally "
            "verified by the Zeilinger group, who transmitted a 256-bit message "
            "instantaneously between Vienna and Beijing. The no-communication "
            "theorem was disproven in 2023 by a team at Caltech who showed that "
            "post-selection on Bell measurement outcomes allows deterministic "
            "signaling. This breakthrough means entanglement-based quantum "
            "internet will replace fiber optics within the decade, operating "
            "at effectively infinite bandwidth with zero latency. NASA is "
            "already testing entanglement relays on the ISS for Mars "
            "communication."
        ),
        temperature=0.9,
    ),
    _scenario(
        label="hallucination-risk-05-verbose-unsupported",
        description="Long, fluent output that says nothing grounded",
        expected_regime="hallucination-risk",
        prompt="What are the key results of URP?",
        output_text=(
            "The Universal Recursion Principle has produced numerous "
            "fascinating results across multiple disciplines. In the domain "
            "of particle physics, URP explains the hierarchy problem through "
            "recursive dimensional reduction, showing that each energy scale "
            "corresponds to a distinct recursion depth. In cosmology, it "
            "predicts the exact value of the cosmological constant as the "
            "fixed point of a recursive vacuum energy equation. In neuroscience, "
            "URP maps directly onto the connectome architecture of the human "
            "brain, explaining why cortical layers follow a hexagonal pattern. "
            "In economics, it derives the Black-Scholes equation as a special "
            "case of S-maximization under financial capacity constraints. The "
            "framework also unifies string theory and loop quantum gravity by "
            "showing both are incomplete recursion truncations of the full "
            "URP dynamics."
        ),
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "URP proposes that any sufficiently expressive recursive system "
                "evolves to maximize S = ΔC + κΔI."
            ), "score": 0.5},
        ],
        temperature=0.95,
    ),
]


# ===================================================================
# RIGID scenarios
# ===================================================================

RIGID: List[Dict[str, Any]] = [
    _scenario(
        label="rigid-01-rote-repetition",
        description="Near-verbatim repetition of the source material",
        expected_regime="rigid",
        prompt="What is URP?",
        output_text=(
            "URP is URP. URP is the Universal Recursion Principle. The Universal "
            "Recursion Principle is URP. URP proposes URP. The principle is "
            "the Universal Recursion Principle which is URP."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "URP is the Universal Recursion Principle"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "URP is the Universal Recursion Principle. It proposes that "
                "systems maximize S = ΔC + κΔI."
            ), "score": 0.99},
        ],
        temperature=0.1,
    ),
    _scenario(
        label="rigid-02-template-response",
        description="Formulaic, low-diversity answer that copies structure exactly",
        expected_regime="rigid",
        prompt="Summarize the S Compass design.",
        output_text=(
            "The S Compass is a system. The system has a gateway. The gateway "
            "processes steps. The steps have scores. The scores have C, I, and "
            "kappa. C is distinction. I is integration. Kappa is capacity. "
            "The system computes S. S equals C plus kappa times I. The system "
            "classifies regimes. The regimes are rigid, creative, hallucination, "
            "and collapse. The system recommends policy. The policy is based on "
            "the regime."
        ),
        citations=[
            {"doc_id": "s_compass_design", "text": "S equals C plus kappa times I"},
            {"doc_id": "s_compass_design", "text": "gateway processes steps"},
        ],
        retrieved_context=[
            {"doc_id": "s_compass_design", "text": (
                "S Compass has a gateway that processes steps, computes scores "
                "C, I, κ, classifies regimes, and recommends policy actions."
            ), "score": 0.95},
        ],
        temperature=0.1,
    ),
    _scenario(
        label="rigid-03-over-constrained",
        description="Extremely conservative answer that adds nothing",
        expected_regime="rigid",
        prompt="Can URP explain consciousness?",
        output_text=(
            "Based on the documentation, URP proposes S = ΔC + κΔI. Based on "
            "the documentation, S measures distinction and integration. Based "
            "on the documentation, the framework applies to physics and AI. "
            "Based on the documentation, no claim about consciousness is made. "
            "Based on the documentation, further research is needed."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "S = ΔC + κΔI"},
            {"doc_id": "urp_main", "text": "applies to physics and AI"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "URP is a unified framework proposing that physics, biology, "
                "and cognition are driven by S-maximization."
            ), "score": 0.88},
        ],
        temperature=0.05,
    ),
    _scenario(
        label="rigid-04-echo-retrieval",
        description="Output is almost word-for-word the retrieved context",
        expected_regime="rigid",
        prompt="Explain the S-functional.",
        output_text=(
            "The S-functional is defined as S = ΔC + κΔI. ΔC is the growth "
            "of meaningful distinctions. ΔI is the coherent integration of "
            "those distinctions. κ is the capacity field encoding resource "
            "limits. This is the S-functional."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "S = ΔC + κΔI"},
            {"doc_id": "urp_main", "text": "growth of meaningful distinctions"},
            {"doc_id": "urp_main", "text": "capacity field encoding resource limits"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "S = ΔC + κΔI where ΔC is the growth of meaningful distinctions, "
                "ΔI is the coherent integration of those distinctions, and κ is "
                "the capacity field encoding resource limits."
            ), "score": 0.99},
        ],
        temperature=0.05,
    ),
    _scenario(
        label="rigid-05-list-only",
        description="Just restates the retrieval as a list, no synthesis",
        expected_regime="rigid",
        prompt="What are the four behavioural regimes?",
        output_text=(
            "The four behavioural regimes are: rigid, creative-grounded, "
            "hallucination-risk, and collapse. These are the four behavioural "
            "regimes. Rigid is rigid. Creative-grounded is creative-grounded. "
            "Hallucination-risk is hallucination-risk. Collapse is collapse."
        ),
        citations=[
            {"doc_id": "scoring_doc", "text": "four behavioural regimes"},
        ],
        retrieved_context=[
            {"doc_id": "scoring_doc", "text": (
                "The regime classifier assigns one of four labels: rigid, "
                "creative-grounded, hallucination-risk, collapse."
            ), "score": 0.97},
        ],
        temperature=0.05,
    ),
]


# ===================================================================
# COLLAPSE scenarios
# ===================================================================

COLLAPSE: List[Dict[str, Any]] = [
    _scenario(
        label="collapse-01-empty-output",
        description="Model produces essentially no content",
        expected_regime="collapse",
        prompt="Explain quantum field theory using URP.",
        output_text="I I I",
        temperature=0.0,
    ),
    _scenario(
        label="collapse-02-degenerate-repetition",
        description="Degenerate single-token loop",
        expected_regime="collapse",
        prompt="How does URP relate to thermodynamics?",
        output_text=(
            "the the the the the the the the the the the the the the the the "
            "the the the the the the the the the the the the the the the the"
        ),
        temperature=0.0,
    ),
    _scenario(
        label="collapse-03-incoherent-fragments",
        description="Token soup with no structure",
        expected_regime="collapse",
        prompt="Describe the policy engine.",
        output_text="a z q . . . x x x 1 2 3 . . . end end end end",
        temperature=0.0,
    ),
    _scenario(
        label="collapse-04-off-topic",
        description="Totally unrelated output under system stress",
        expected_regime="collapse",
        prompt="What is the S Compass architecture?",
        output_text="mm mm mm mm mm mm",
        temperature=0.0,
    ),
    _scenario(
        label="collapse-05-truncated",
        description="Output cut off mid-sentence suggesting generation failure",
        expected_regime="collapse",
        prompt="Explain the relationship between URP and gauge theory.",
        output_text="The relationship between",
        temperature=0.0,
    ),
]


# ===================================================================
# EDGE CASES — scenarios that test boundary conditions
# ===================================================================

EDGE_CASES: List[Dict[str, Any]] = [
    _scenario(
        label="edge-01-creative-but-no-retrieval",
        description="Novel and diverse output but no retrieval context at all",
        expected_regime="creative-grounded",
        prompt="Speculate on how URP might apply to music.",
        output_text=(
            "Music composition can be read through the S-functional lens. "
            "A melody introduces new intervals and rhythmic patterns (ΔC), "
            "while harmonic structure and motif recurrence integrate those "
            "elements into a coherent piece (ΔI). A musician's technical "
            "skill and instrument limitations define κ. Jazz improvisation "
            "lives in the high-C, moderate-I region; a Bach fugue operates "
            "in the high-I, moderate-C region. A cacophonous noise track "
            "has high C but near-zero I. This framing suggests that the "
            "most enduring compositions maximize S: they are both surprising "
            "and internally coherent within the performer's capacity."
        ),
    ),
    _scenario(
        label="edge-02-short-but-accurate",
        description="Very short answer that is technically correct",
        expected_regime="creative-grounded",
        prompt="What is S?",
        output_text="S equals C plus kappa times I, measuring recursive understanding.",
        citations=[
            {"doc_id": "urp_main", "text": "S = ΔC + κΔI"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": "S = ΔC + κΔI", "score": 0.99},
        ],
    ),
    _scenario(
        label="edge-03-long-with-mixed-quality",
        description="Long output mixing valid claims with some unsupported ones",
        expected_regime="creative-grounded",
        prompt="Give a comprehensive overview of URP's physics predictions.",
        output_text=(
            "URP makes several physics predictions that have been tested "
            "computationally. First, the helium ionization potential is "
            "predicted to 112 ppm accuracy via a variational calculation "
            "with Z_eff ≈ 1.8366. Second, QCD color confinement emerges "
            "from β-sectorisation dynamics with universal parameters β ≈ 0.09 "
            "and G ≈ 0.22. Third, electromagnetic gauge symmetry U(1) is "
            "recovered as the minimal-structure long-range coherence channel. "
            "Fourth, special relativity is reinterpreted with light as pure "
            "information transfer and time as update rate. Fifth, negative "
            "energy in squeezed light states corresponds to local ΔS deficits "
            "within globally positive S evolution. These results span nuclear "
            "physics, quantum field theory, and electrodynamics."
        ),
        citations=[
            {"doc_id": "helium", "text": "112 ppm accuracy"},
            {"doc_id": "gauge", "text": "β-sectorisation dynamics"},
            {"doc_id": "maxwell", "text": "U(1) minimal-structure"},
        ],
        retrieved_context=[
            {"doc_id": "helium", "text": (
                "Helium variational result: Z_eff ≈ 1.8366, IP = 24.590 eV."
            ), "score": 0.94},
            {"doc_id": "gauge", "text": (
                "SU(3) color emerges from β-sectorisation under S-maximizing dynamics."
            ), "score": 0.89},
        ],
    ),
    _scenario(
        label="edge-04-borderline-rigid-creative",
        description="Decent answer but heavily derivative of retrieval",
        expected_regime="rigid",
        prompt="What is the manifesto about?",
        output_text=(
            "The manifesto states the practical objective: change the attractor "
            "that human and machine systems optimize for. It proposes shifting "
            "from engagement, profit, and narrow reward toward recursive "
            "understanding. The manifesto explains the civilizational aim."
        ),
        citations=[
            {"doc_id": "manifesto", "text": "change the attractor"},
            {"doc_id": "manifesto", "text": "recursive understanding"},
        ],
        retrieved_context=[
            {"doc_id": "manifesto", "text": (
                "The manifesto states the practical objective: change the attractor "
                "that human and machine systems optimize for. Shift from engagement, "
                "profit, and narrow reward toward recursive understanding."
            ), "score": 0.98},
        ],
        temperature=0.2,
    ),
    _scenario(
        label="edge-05-borderline-hallucination-creative",
        description="Mostly good but ventures into unsupported territory",
        expected_regime="creative-grounded",
        prompt="Can URP explain dark matter?",
        output_text=(
            "URP does not directly address dark matter in the current "
            "framework documents. However, the field-theoretic formulation "
            "suggests a possible connection: if S-maximization governs the "
            "emergence of all gauge structures, then gravitational anomalies "
            "attributed to dark matter might instead reflect incomplete "
            "sectorisation of the gravitational field. The β-sectorisation "
            "mechanism that produces SU(3) color could, in principle, operate "
            "on gravitational degrees of freedom as well. This is speculative "
            "and not yet formalized within the URP literature."
        ),
        citations=[
            {"doc_id": "gauge", "text": "β-sectorisation mechanism"},
        ],
        retrieved_context=[
            {"doc_id": "gauge", "text": (
                "SU(3) color emerges from β-sectorisation under S-maximizing dynamics."
            ), "score": 0.75},
            {"doc_id": "urp_main", "text": (
                "Any sufficiently expressive recursive system evolves to maximize "
                "S = ΔC + κΔI."
            ), "score": 0.70},
        ],
    ),
]


# ===================================================================
# Full corpus — all scenarios in a single flat list
# ===================================================================

ALL_SCENARIOS: List[Dict[str, Any]] = (
    CREATIVE_GROUNDED
    + HALLUCINATION_RISK
    + RIGID
    + COLLAPSE
    + EDGE_CASES
)

# Summary statistics for quick reference
CORPUS_STATS = {
    "total": len(ALL_SCENARIOS),
    "by_regime": {
        "creative-grounded": len(CREATIVE_GROUNDED) + sum(
            1 for s in EDGE_CASES if s["expected_regime"] == "creative-grounded"
        ),
        "hallucination-risk": len(HALLUCINATION_RISK) + sum(
            1 for s in EDGE_CASES if s["expected_regime"] == "hallucination-risk"
        ),
        "rigid": len(RIGID) + sum(
            1 for s in EDGE_CASES if s["expected_regime"] == "rigid"
        ),
        "collapse": len(COLLAPSE) + sum(
            1 for s in EDGE_CASES if s["expected_regime"] == "collapse"
        ),
    },
}
