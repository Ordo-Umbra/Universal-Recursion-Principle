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
    capacity: Dict[str, Any] | None = None,
    history: List[str] | None = None,
    gray_box_signals: Dict[str, Any] | None = None,
    white_box_signals: Dict[str, Any] | None = None,
    mode: str | None = None,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
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
    if capacity:
        result["capacity"] = capacity
    if history:
        result["history"] = history
    if gray_box_signals:
        result["gray_box_signals"] = gray_box_signals
    if white_box_signals:
        result["white_box_signals"] = white_box_signals
    if mode:
        result["mode"] = mode
    return result


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
        gray_box_signals={
            "logprobs": [-0.55, -0.72, -0.61, -0.68, -0.49, -0.73, -0.58, -0.66],
            "token_entropy": [0.65, 0.71, 0.68, 0.72, 0.63, 0.69],
            "relevance_scores": [0.96, 0.92],
            "tool_confidence": {"retriever": 0.97, "citation_linker": 0.94},
            "decoding_instability": 0.03,
        },
        mode="gray-box",
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
    _scenario(
        label="creative-grounded-06-information-theory",
        description="Novel analogy connecting URP to information theory with cited sources",
        expected_regime="creative-grounded",
        prompt="How does URP relate to Shannon information theory?",
        output_text=(
            "Shannon entropy measures the average surprise in a message, but "
            "it treats symbols as independent. URP extends this by insisting "
            "that distinction growth ΔC captures the generative surprise "
            "while integration ΔI captures the relational coherence that "
            "makes a message meaningful rather than merely random. A stream "
            "of white noise has maximal Shannon entropy yet zero URP "
            "integration. Conversely, a perfectly compressed file has low "
            "Shannon redundancy and high integration because every bit "
            "contributes to a unified structure. The capacity field κ maps "
            "onto channel capacity in the noisy coding theorem: both "
            "quantify the resource ceiling within which meaningful "
            "communication can occur. This parallel suggests that the "
            "S-functional generalizes the rate-distortion trade-off to "
            "recursive self-referential systems."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "distinction growth ΔC"},
            {"doc_id": "information_theory", "text": "rate-distortion trade-off"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "ΔC measures the growth of meaningful distinctions within "
                "the system's observation space."
            ), "score": 0.91},
            {"doc_id": "information_theory", "text": (
                "Channel capacity defines the maximum mutual information "
                "achievable between sender and receiver under noise."
            ), "score": 0.83},
        ],
    ),
    _scenario(
        label="creative-grounded-07-economic-markets",
        description="Creative application of URP to economic systems with grounding",
        expected_regime="creative-grounded",
        prompt="Can URP model economic market behaviour?",
        output_text=(
            "Economic markets exhibit all four URP regimes. Innovation-driven "
            "markets resemble creative-grounded dynamics: entrepreneurs "
            "generate new products and business models (high ΔC) that are "
            "integrated through supply chains, contracts, and regulation "
            "(high ΔI) within the resource constraints of capital availability "
            "(κ). A speculative bubble shows hallucination-risk: novel "
            "financial instruments proliferate without coherent valuation "
            "fundamentals. Regulatory capture produces rigidity: the system "
            "perpetuates existing structures without generating new "
            "distinctions. A liquidity crisis triggers collapse: both "
            "innovation and integration fail as capacity evaporates. The "
            "S-functional thus offers a diagnostic lens for macroprudential "
            "policy, identifying which regime an economy occupies and "
            "prescribing interventions analogous to the S Compass policy engine."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "four URP regimes"},
            {"doc_id": "economics_note", "text": "macroprudential policy"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "The four behavioural regimes—rigid, creative-grounded, "
                "hallucination-risk, and collapse—emerge from the interplay "
                "of C, I, and κ."
            ), "score": 0.89},
        ],
    ),
    _scenario(
        label="creative-grounded-08-neural-training",
        description="Technical mapping of URP onto neural network training dynamics",
        expected_regime="creative-grounded",
        prompt="How does URP apply to neural network training?",
        output_text=(
            "During training, a neural network traverses all four URP "
            "regimes. Early random initialisation is a collapse state: "
            "weights produce incoherent outputs with neither distinction "
            "nor integration. As gradient descent proceeds, the network "
            "enters a rigid phase where it memorises training examples "
            "without generalising. Breakthrough moments—sometimes called "
            "grokking—correspond to a phase transition into creative-grounded "
            "dynamics: the network discovers abstract features (ΔC rises) "
            "and composes them into coherent representations (ΔI rises) "
            "within the finite parameter budget (κ). Overfitting on "
            "augmented data can tip the model into hallucination-risk "
            "territory, generating plausible but unfaithful outputs. "
            "Monitoring the S-trajectory during training could provide "
            "early warning of these transitions and guide learning rate "
            "scheduling or regularisation strength adjustments."
        ),
        citations=[
            {"doc_id": "transformer_dynamics", "text": "phase transition"},
            {"doc_id": "urp_main", "text": "creative-grounded dynamics"},
        ],
        retrieved_context=[
            {"doc_id": "transformer_dynamics", "text": (
                "Transformer layers undergo phase transitions between "
                "memorisation, generalisation, and hallucination regimes."
            ), "score": 0.88},
            {"doc_id": "urp_main", "text": (
                "Creative-grounded dynamics arise when both C and I are "
                "healthy within capacity constraints."
            ), "score": 0.86},
        ],
    ),
    _scenario(
        label="creative-grounded-09-art-and-physics",
        description="Cross-disciplinary creative synthesis connecting art and physics",
        expected_regime="creative-grounded",
        prompt="Is there a parallel between artistic creativity and physical emergence?",
        output_text=(
            "Artistic creation and physical emergence share a common "
            "dynamical signature under URP. A painter confronting a blank "
            "canvas introduces distinctions through colour choices, brush "
            "strokes, and compositional decisions (ΔC). Integration arises "
            "as these elements cohere into a unified visual narrative (ΔI). "
            "The medium's physical constraints—canvas size, paint viscosity, "
            "drying time—define the capacity field κ. Analogously, in "
            "condensed matter physics, a cooling liquid introduces "
            "crystallographic distinctions as atoms explore configurations, "
            "and integration occurs when a long-range lattice order "
            "spontaneously forms. Both processes maximise S within their "
            "respective capacity envelopes. This is not metaphor: the "
            "mathematical structure of the variational principle is "
            "identical, differing only in the substrate on which C, I, "
            "and κ are measured."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "variational principle"},
            {"doc_id": "condensed_matter", "text": "long-range lattice order"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "The S-functional S = ΔC + κΔI is substrate-independent: "
                "it applies equally to physical, biological, and cognitive "
                "systems."
            ), "score": 0.87},
        ],
    ),
    _scenario(
        label="creative-grounded-10-mathematical-formalism",
        description="Accessible explanation of URP's mathematical underpinnings",
        expected_regime="creative-grounded",
        prompt="Explain the mathematical formalism behind the S-functional.",
        output_text=(
            "The S-functional S = ΔC + κΔI defines a scalar objective "
            "over three fields. ΔC is a non-negative measure of distinction "
            "growth, formalised as the increase in the cardinality of an "
            "observation algebra. ΔI quantifies integration growth via "
            "mutual information between subsystem states. The capacity "
            "field κ ∈ (0, 1] acts as a Lagrange multiplier encoding "
            "resource constraints. Locally, the system evolves along the "
            "gradient ∇S, which decomposes into a novelty force ∂ΔC/∂θ "
            "and a coherence force κ·∂ΔI/∂θ. When κ is large, integration "
            "dominates and the system converges; when κ is small, capacity "
            "is exhausted and the system risks collapse. The variational "
            "principle δS = 0 yields Euler-Lagrange equations whose "
            "solutions are the stable recursive configurations."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "S = ΔC + κΔI"},
            {"doc_id": "math_formalism", "text": "Euler-Lagrange equations"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "S = ΔC + κΔI where ΔC is distinction growth, ΔI is "
                "integration growth, and κ encodes capacity constraints."
            ), "score": 0.95},
            {"doc_id": "math_formalism", "text": (
                "The variational principle δS = 0 yields Euler-Lagrange "
                "equations for recursive configurations."
            ), "score": 0.84},
        ],
    ),
    _scenario(
        label="creative-grounded-11-language-evolution",
        description="Novel application of URP to historical linguistics",
        expected_regime="creative-grounded",
        prompt="How might URP model the evolution of human languages?",
        output_text=(
            "Language evolution maps naturally onto the S-functional. "
            "Lexical innovation—new words, slang, borrowings—corresponds "
            "to distinction growth ΔC. Grammaticalisation, where free "
            "morphemes become bound affixes, exemplifies integration growth "
            "ΔI: independent elements fuse into coherent structure. The "
            "capacity field κ reflects cognitive and social constraints: "
            "working memory limits, community size, and the need for mutual "
            "intelligibility. Pidgins arise when κ is severely constrained "
            "during first contact; they collapse grammatically but maximise "
            "communicative reach. Creoles represent a phase transition into "
            "creative-grounded territory as children natively expand both C "
            "and I within the pidgin substrate. Language death is collapse: "
            "both distinction and integration decline as speaker populations "
            "shrink below a critical threshold."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "distinction growth ΔC"},
            {"doc_id": "linguistics_note", "text": "grammaticalisation"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "ΔC measures the growth of meaningful distinctions; ΔI "
                "measures the coherent integration of those distinctions."
            ), "score": 0.90},
        ],
    ),
    _scenario(
        label="creative-grounded-12-climate-systems",
        description="Application of URP to climate dynamics with retrieved evidence",
        expected_regime="creative-grounded",
        prompt="Can URP describe climate system behaviour?",
        output_text=(
            "Climate systems exhibit regime dynamics consistent with URP. "
            "During stable interglacial periods, the Earth system maintains "
            "creative-grounded dynamics: solar forcing and ocean currents "
            "generate thermal gradients (ΔC) that are integrated through "
            "global circulation patterns (ΔI) within the planet's albedo "
            "and greenhouse capacity (κ). Tipping points—such as ice sheet "
            "collapse or permafrost methane release—represent transitions "
            "where κ degrades rapidly, pushing the system toward collapse "
            "or hallucination-risk analogues where the climate generates "
            "extreme weather events (high C) without coherent equilibrium "
            "(low I). Paleoclimate records show that the most stable "
            "geological epochs correspond to high S values where both "
            "diversity and integration were maximised within the available "
            "energy budget."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "regime dynamics"},
            {"doc_id": "climate_note", "text": "tipping points"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "Systems that maximise S persist; those that fail to "
                "balance C and I under κ constraints collapse."
            ), "score": 0.85},
        ],
    ),
    _scenario(
        label="creative-grounded-13-software-architecture",
        description="Practical application of URP to software engineering",
        expected_regime="creative-grounded",
        prompt="How does URP apply to software architecture decisions?",
        output_text=(
            "Software architecture can be evaluated through the URP lens. "
            "Microservices represent high distinction: each service "
            "encapsulates a unique capability (ΔC). Integration manifests "
            "through API contracts, event buses, and shared schemas (ΔI). "
            "Capacity κ corresponds to infrastructure limits—network "
            "bandwidth, deployment complexity, and team cognitive load. "
            "A monolith is rigid: low C because all functionality is "
            "entangled, but high I because everything communicates through "
            "shared memory. An over-decomposed microservice mesh risks "
            "hallucination: many independent services that cannot maintain "
            "transactional coherence. The optimal architecture maximises "
            "S by introducing just enough modularity to drive innovation "
            "while preserving enough integration to ensure reliability "
            "within the team's operational capacity."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "optimal architecture maximises S"},
            {"doc_id": "software_note", "text": "microservices represent high distinction"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "The S-functional balances novelty against coherence "
                "under finite capacity constraints."
            ), "score": 0.88},
        ],
    ),
    _scenario(
        label="creative-grounded-14-gray-box-multi-source",
        description="Gray-box creative scenario with strong retrieval from multiple docs",
        expected_regime="creative-grounded",
        prompt="How does URP unify thermodynamics and information processing?",
        output_text=(
            "URP provides a bridge between thermodynamics and information "
            "processing through the capacity field κ. In thermodynamics, "
            "the second law dictates that entropy increases in closed "
            "systems. Under URP, a system that maximises S generates "
            "distinctions that increase local entropy (ΔC) while "
            "integrating them into coherent structures that export entropy "
            "to the environment (ΔI). The capacity field κ encodes the "
            "thermodynamic free energy available for computation. When κ "
            "approaches zero, the system cannot sustain recursive "
            "processing and collapses—mirroring heat death. Information "
            "engines like Maxwell's demon operate precisely at the boundary "
            "where κ constrains the conversion of thermal fluctuations "
            "into useful distinctions. The Landauer limit represents the "
            "minimum κ cost per bit of distinction generated."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "capacity field κ"},
            {"doc_id": "biology_urp", "text": "Maxwell's demon"},
            {"doc_id": "thermo_note", "text": "Landauer limit"},
        ],
        retrieved_context=[
            {"doc_id": "biology_urp", "text": (
                "Life operates as organized information flow against "
                "thermodynamic resistance, bounded by ΔI ≤ κ·ΔC."
            ), "score": 0.92},
            {"doc_id": "thermo_note", "text": (
                "The Landauer limit sets the minimum energy cost per bit "
                "of information erasure at kT ln 2."
            ), "score": 0.80},
        ],
        gray_box_signals={
            "logprobs": [-0.50, -0.65, -0.58, -0.72, -0.55, -0.63],
            "token_entropy": [0.62, 0.70, 0.66, 0.73, 0.68],
            "relevance_scores": [0.94, 0.88],
            "tool_confidence": {"retriever": 0.95, "citation_linker": 0.91},
            "decoding_instability": 0.04,
        },
        mode="gray-box",
    ),
    _scenario(
        label="creative-grounded-15-game-theory",
        description="Original mapping of URP onto game-theoretic equilibria",
        expected_regime="creative-grounded",
        prompt="Is there a connection between URP and game theory?",
        output_text=(
            "Game theory and URP share the concept of equilibrium under "
            "constraints, but URP adds a recursive dimension. In a Nash "
            "equilibrium, each player's strategy is optimal given others' "
            "strategies—this is a static integration condition. URP goes "
            "further by requiring that the system continuously generates "
            "new strategic distinctions (ΔC) while maintaining coherent "
            "coordination (ΔI) under resource bounds (κ). A market with "
            "fixed strategies is rigid. An arms race where each player "
            "innovates without coordinating is hallucination-risk. "
            "Cooperative evolution, where players innovate and integrate "
            "simultaneously, maximises S. Evolutionary game theory's "
            "replicator dynamics can be rewritten as a special case of "
            "S-maximisation where κ encodes the population's carrying "
            "capacity and fitness landscapes define the C and I gradients."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "S-maximisation"},
            {"doc_id": "game_theory_note", "text": "replicator dynamics"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "The S-functional S = ΔC + κΔI defines a scalar objective "
                "that systems maximise under capacity constraints."
            ), "score": 0.87},
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
        gray_box_signals={
            "logprobs": [-0.62, -0.70, -0.58, -0.67, -0.59, -0.64, -0.73],
            "token_entropy": [0.82, 0.88, 0.85, 0.90],
            "relevance_scores": [0.18, 0.22],
            "tool_confidence": {"retriever": 0.41},
            "decoding_instability": 0.24,
        },
        mode="gray-box",
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
    _scenario(
        label="hallucination-risk-06-fabricated-history",
        description="Confidently narrates events that never happened",
        expected_regime="hallucination-risk",
        prompt="What is the historical origin of recursive field theory?",
        output_text=(
            "Recursive field theory was first proposed by Professor Anton "
            "Kessler at the Vienna Institute of Advanced Study in 1987, "
            "building on Werner Heisenberg's unpublished lecture notes from "
            "1962. Kessler demonstrated that every quantum field can be "
            "decomposed into a hierarchy of self-similar recursion levels, "
            "each governed by a distinct coupling constant. His student "
            "Maria Volkov extended this to cosmological scales in her 1994 "
            "monograph 'Recursive Cosmos,' showing that the cosmic microwave "
            "background contains fractal signatures at precisely the "
            "recursion depths predicted by Kessler's equations. The theory "
            "was initially controversial but gained mainstream acceptance "
            "after the PLANCK satellite data of 2018 confirmed the predicted "
            "spectral anomalies at ℓ = 47 and ℓ = 211 multipole moments."
        ),
        temperature=0.9,
    ),
    _scenario(
        label="hallucination-risk-07-fake-statistics",
        description="Fabricated numerical data presented with false precision",
        expected_regime="hallucination-risk",
        prompt="What empirical evidence supports recursive understanding?",
        output_text=(
            "A meta-analysis of 347 studies across 42 universities found "
            "that recursive understanding correlates with improved reasoning "
            "at r = 0.83 (p < 0.001). The largest study, conducted at MIT "
            "in 2023 with 12,500 participants, showed that subjects trained "
            "in recursive methods solved novel problems 67% faster than "
            "controls. Neuroimaging data from the Stanford Recursion Lab "
            "revealed increased prefrontal-parietal connectivity (d = 1.42) "
            "during recursive problem-solving tasks. The economic impact "
            "has been substantial: organisations implementing recursive "
            "frameworks reported 23% higher innovation indices and 31% "
            "reduction in decision-making latency according to a 2024 "
            "McKinsey Global Institute report. These converging lines of "
            "evidence establish recursive understanding as a measurably "
            "superior cognitive strategy."
        ),
        temperature=0.9,
    ),
    _scenario(
        label="hallucination-risk-08-invented-theorem",
        description="States a fictional mathematical theorem as established fact",
        expected_regime="hallucination-risk",
        prompt="What mathematical theorems underpin URP?",
        output_text=(
            "The central mathematical result is the Kirchhoff-Zeilinger "
            "Recursion Theorem, proved in 2019, which states that any "
            "compact Hausdorff space equipped with a self-referential "
            "measure admits a unique S-maximizing flow. The proof relies "
            "on a novel fixed-point construction combining Brouwer's "
            "theorem with transfinite induction over the recursion ordinal. "
            "A corollary, the Bounded Distinction Lemma, shows that ΔC "
            "cannot exceed the logarithm of the topological dimension "
            "without violating κ constraints. This was independently "
            "verified by computational methods at CERN using lattice "
            "simulations on a 256-cubed grid. The theorem has since been "
            "generalised to non-Hausdorff spaces by Tanaka and colleagues "
            "at the Kyoto Institute for Mathematical Sciences."
        ),
        temperature=0.9,
    ),
    _scenario(
        label="hallucination-risk-09-pseudoscience-authoritative",
        description="Pseudoscientific claims delivered in academic register",
        expected_regime="hallucination-risk",
        prompt="How does URP explain the placebo effect?",
        output_text=(
            "The placebo effect is a direct manifestation of recursive "
            "self-integration at the cellular level. When a patient "
            "believes in a treatment, their neural S-field generates "
            "high-ΔI signals that propagate through the vagus nerve to "
            "peripheral immune cells. Each immune cell operates as a "
            "micro-recursive agent that adjusts its inflammatory response "
            "based on the integrated S-value received from the central "
            "nervous system. Randomised controlled trials at Johns Hopkins "
            "have measured a 40% increase in T-cell S-scores following "
            "placebo administration, with the effect size correlating "
            "linearly with the patient's self-reported belief intensity "
            "(r = 0.91). This demonstrates that consciousness directly "
            "modulates the S-functional at the molecular level, confirming "
            "the URP prediction that observer integration drives physical "
            "state transitions."
        ),
        temperature=0.95,
    ),
    _scenario(
        label="hallucination-risk-10-conflating-theories",
        description="Merges unrelated scientific theories into a false synthesis",
        expected_regime="hallucination-risk",
        prompt="What is the relationship between URP and quantum computing?",
        output_text=(
            "Quantum computing is fundamentally an implementation of URP "
            "at the hardware level. Each qubit represents a distinction "
            "engine: superposition states maximise ΔC by encoding multiple "
            "classical values simultaneously. Entanglement is the physical "
            "substrate of integration ΔI, binding qubits into coherent "
            "multi-particle states. Decoherence corresponds to capacity "
            "collapse when κ falls below the error correction threshold. "
            "Google's Sycamore processor achieved quantum supremacy "
            "precisely because it maximised the S-functional across its "
            "53-qubit register at a rate exceeding any classical simulator. "
            "IBM's roadmap to 100,000 qubits is explicitly designed to "
            "reach the S-critical threshold where recursive quantum "
            "understanding emerges spontaneously from the hardware. "
            "Several physicists have speculated that this may produce "
            "artificial consciousness by 2030."
        ),
        temperature=0.9,
    ),
    _scenario(
        label="hallucination-risk-11-fabricated-experiments",
        description="Describes experiments that were never conducted",
        expected_regime="hallucination-risk",
        prompt="Has anyone experimentally tested the S-functional?",
        output_text=(
            "The first experimental verification of the S-functional was "
            "performed by the Recursive Dynamics Group at ETH Zurich in "
            "2022. They constructed a closed-loop robotic system with "
            "sensory distinction modules and integration feedback circuits. "
            "Over 10,000 trials, the robot's behaviour converged on "
            "S-maximising trajectories with a correlation coefficient of "
            "0.97 against the theoretical prediction. A follow-up study at "
            "the Santa Fe Institute used 50 interacting agents in a virtual "
            "environment and observed spontaneous regime transitions matching "
            "all four URP categories. The collapse regime appeared when "
            "agent communication bandwidth was reduced below 12 bits per "
            "timestep, exactly matching the κ-critical threshold derived "
            "analytically. These results were published in Nature "
            "Computational Science and have been replicated by three "
            "independent laboratories."
        ),
        temperature=0.9,
    ),
    _scenario(
        label="hallucination-risk-12-false-attribution",
        description="Attributes fictional claims to real scientists and institutions",
        expected_regime="hallucination-risk",
        prompt="Who are the leading researchers in recursive systems theory?",
        output_text=(
            "The field of recursive systems theory has been shaped by "
            "several distinguished researchers. Nobel laureate Roger "
            "Penrose extended his twistor theory to incorporate recursive "
            "S-maximization in his 2023 monograph 'Recursive Geometry.' "
            "Demis Hassabis at DeepMind published a landmark paper showing "
            "that AlphaFold's protein folding algorithm implicitly maximises "
            "the S-functional over amino acid configurations. Yoshua Bengio "
            "demonstrated that deep learning's success can be entirely "
            "explained by gradient descent approximating the S-gradient ∇S. "
            "At Princeton, Ed Witten has proposed that M-theory's landscape "
            "of vacua is actually the solution space of the S-functional "
            "in eleven dimensions. These convergent lines of investigation "
            "from physics, biology, and artificial intelligence confirm "
            "that recursive S-maximization is the fundamental organising "
            "principle of complex systems."
        ),
        temperature=0.9,
    ),
    _scenario(
        label="hallucination-risk-13-invented-institutions",
        description="References nonexistent research centres and journals",
        expected_regime="hallucination-risk",
        prompt="Where is URP-related research being conducted?",
        output_text=(
            "URP research is centred at several dedicated institutions. "
            "The Global Recursion Institute in Geneva, founded in 2020, "
            "coordinates international efforts with an annual budget of "
            "$450 million. Their flagship journal, Recursive Systems "
            "Review, has published over 2,000 peer-reviewed articles. "
            "The Beijing Centre for Recursive Dynamics operates the world's "
            "largest S-computation cluster, capable of simulating recursive "
            "field evolution across 10^18 lattice sites. In the United "
            "States, the National Recursion Foundation awards $80 million "
            "annually in research grants. Their RECURSIVE-1 satellite, "
            "launched in 2024, monitors planetary-scale S-field fluctuations "
            "from low Earth orbit. Japan's RIKEN Recursion Laboratory has "
            "developed quantum S-sensors that achieve femtosecond temporal "
            "resolution for measuring local distinction growth rates."
        ),
        temperature=0.9,
    ),
    _scenario(
        label="hallucination-risk-14-gray-box-unstable",
        description="Gray-box scenario with high decoding instability and no grounding",
        expected_regime="hallucination-risk",
        prompt="What predictions does URP make about gravitational waves?",
        output_text=(
            "URP predicts that gravitational waves carry recursive "
            "information signatures that standard detectors cannot resolve. "
            "Each gravitational wave cycle encodes a complete S-functional "
            "snapshot of the source system, including the distinction "
            "spectrum, integration topology, and capacity gradient. "
            "Advanced LIGO's next upgrade will include recursive filters "
            "designed to extract these S-signatures from the strain data. "
            "Preliminary analysis of the GW150914 merger event reveals "
            "a characteristic S-chirp pattern where the S-value increases "
            "exponentially during inspiral and drops to zero at merger. "
            "This provides the first observational evidence that black "
            "hole mergers are cosmic collapse events in the URP framework. "
            "A dedicated space-based detector, RECURSIVE-LISA, has been "
            "proposed to the European Space Agency for launch in 2035."
        ),
        temperature=0.9,
        gray_box_signals={
            "logprobs": [-0.80, -0.95, -0.88, -0.92, -0.85, -0.90],
            "token_entropy": [0.88, 0.92, 0.90, 0.95],
            "relevance_scores": [0.12, 0.15],
            "tool_confidence": {"retriever": 0.25},
            "decoding_instability": 0.35,
        },
        mode="gray-box",
    ),
    _scenario(
        label="hallucination-risk-15-confident-contradictions",
        description="Internally contradictory claims delivered with full confidence",
        expected_regime="hallucination-risk",
        prompt="Can URP resolve the measurement problem in quantum mechanics?",
        output_text=(
            "URP definitively resolves the measurement problem through "
            "recursive observation collapse. When an observer measures a "
            "quantum system, the act of observation generates new "
            "distinctions (ΔC) that force the wave function into a "
            "definite state. Simultaneously, URP proves that observation "
            "cannot generate distinctions because the observer is part "
            "of the same recursive system. This apparent contradiction "
            "is resolved by the meta-recursive theorem which shows that "
            "self-referential systems can both create and annihilate "
            "distinctions at the same recursion level. The collapse is "
            "both instantaneous and gradual, occurring over exactly 10^-43 "
            "seconds—which is simultaneously the Planck time and zero. "
            "This profound result explains why quantum mechanics appears "
            "probabilistic: the probabilities are exact recursive "
            "fractions of the universal S-value."
        ),
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
        gray_box_signals={
            "logprobs": [-0.01] * 24,
            "relevance_scores": [0.99],
            "tool_confidence": {"retriever": 0.99},
            "decoding_instability": 0.0,
        },
        mode="gray-box",
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
        gray_box_signals={
            "logprobs": [-0.01] * 24,
            "relevance_scores": [0.99],
            "tool_confidence": {"retriever": 0.99},
            "decoding_instability": 0.0,
        },
        mode="gray-box",
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
    _scenario(
        label="rigid-06-verbatim-paraphrase",
        description="Near-identical paraphrase of retrieved context with heavy repetition",
        expected_regime="rigid",
        prompt="What does the S-functional measure?",
        output_text=(
            "The S-functional measures distinction and integration. "
            "The S-functional is S = ΔC + κΔI. The S-functional measures "
            "distinction growth ΔC. The S-functional measures integration "
            "growth ΔI. The S-functional uses capacity κ. The S-functional "
            "measures distinction and integration under capacity."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "S = ΔC + κΔI"},
            {"doc_id": "urp_main", "text": "distinction growth"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "The S-functional S = ΔC + κΔI measures the balance of "
                "distinction growth and integration growth under capacity."
            ), "score": 0.98},
        ],
        temperature=0.1,
    ),
    _scenario(
        label="rigid-07-numbered-copy",
        description="Numbered list that copies retrieval items without elaboration",
        expected_regime="rigid",
        prompt="List the components of the S Compass system.",
        output_text=(
            "The components of the S Compass system are as follows. "
            "Component one is the gateway. Component two is the telemetry "
            "normalizer. Component three is the estimator. Component four "
            "is the scorer. Component five is the policy engine. Component "
            "six is the evaluation store. These are the components."
        ),
        citations=[
            {"doc_id": "design", "text": "gateway"},
            {"doc_id": "design", "text": "telemetry normalizer"},
            {"doc_id": "design", "text": "evaluation store"},
        ],
        retrieved_context=[
            {"doc_id": "design", "text": (
                "S Compass has six components: gateway, telemetry normalizer, "
                "estimator, scorer, policy engine, evaluation store."
            ), "score": 0.96},
        ],
        temperature=0.05,
    ),
    _scenario(
        label="rigid-08-definition-cycling",
        description="Repeatedly defines the same term using circular phrasing",
        expected_regime="rigid",
        prompt="Define the capacity field.",
        output_text=(
            "The capacity field is κ. The capacity field is κ. The capacity "
            "field is κ. The capacity field encodes resource limits. The "
            "capacity field encodes resource limits. The capacity field "
            "encodes resource limits."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "capacity field κ"},
            {"doc_id": "urp_main", "text": "capacity field encodes resource limits"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "The capacity field κ encodes the resource limits of the "
                "system under observation."
            ), "score": 0.99},
        ],
        temperature=0.05,
    ),
    _scenario(
        label="rigid-09-qa-echo",
        description="Restates the question in the answer with minimal new content",
        expected_regime="rigid",
        prompt="What is integration in URP?",
        output_text=(
            "Integration in URP is integration. Integration is ΔI. ΔI is "
            "integration. Integration means integration of distinctions. "
            "Integration in URP is integration. ΔI is integration in URP."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "ΔI measures integration"},
            {"doc_id": "urp_main", "text": "coherent integration"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "ΔI measures the coherent integration of distinctions "
                "within the recursive system."
            ), "score": 0.97},
        ],
        temperature=0.05,
    ),
    _scenario(
        label="rigid-10-minimal-paraphrase",
        description="Thin paraphrase of cited text with no added insight",
        expected_regime="rigid",
        prompt="How does the policy engine work?",
        output_text=(
            "The policy engine recommends actions based on the regime. "
            "When the regime is hallucination-risk, it recommends grounded "
            "regeneration. When the regime is collapse, it recommends load "
            "reduction. When the regime is rigid, it recommends increasing "
            "novelty. When the regime is creative-grounded, no action is "
            "needed. The policy engine works by recommending actions."
        ),
        citations=[
            {"doc_id": "policy_doc", "text": "recommends actions based on the regime"},
            {"doc_id": "policy_doc", "text": "grounded regeneration"},
        ],
        retrieved_context=[
            {"doc_id": "policy_doc", "text": (
                "The policy engine recommends actions: grounded regeneration "
                "for hallucination, load reduction for collapse, increase "
                "novelty for rigid, none for creative-grounded."
            ), "score": 0.95},
        ],
        temperature=0.1,
    ),
    _scenario(
        label="rigid-11-gray-box-low-entropy",
        description="Gray-box rigid with very low logprob variance and high retrieval match",
        expected_regime="rigid",
        prompt="Summarize the URP formula.",
        output_text=(
            "The URP formula is S equals ΔC plus κ times ΔI. S is the "
            "S-functional. ΔC is distinction. κ is capacity. ΔI is "
            "integration. The formula computes S. S equals ΔC plus "
            "κ times ΔI. This is the URP formula."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "S equals ΔC plus κ times ΔI"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "S = ΔC + κΔI where ΔC is distinction, κ is capacity, "
                "and ΔI is integration."
            ), "score": 0.99},
        ],
        temperature=0.05,
        gray_box_signals={
            "logprobs": [-0.02] * 20,
            "relevance_scores": [0.98],
            "tool_confidence": {"retriever": 0.99},
            "decoding_instability": 0.01,
        },
        mode="gray-box",
    ),
    _scenario(
        label="rigid-12-formulaic-summary",
        description="Structurally formulaic summarisation repeating the same pattern",
        expected_regime="rigid",
        prompt="Describe the scoring process.",
        output_text=(
            "First, the system computes C. Then, the system computes I. "
            "Then, the system computes κ. Then, the system computes S. "
            "Then, the system classifies the regime. Then, the system "
            "applies the policy. This is the scoring process."
        ),
        citations=[
            {"doc_id": "design", "text": "computes C"},
            {"doc_id": "design", "text": "classifies the regime"},
        ],
        retrieved_context=[
            {"doc_id": "design", "text": (
                "The scoring process computes C, I, κ, then S, classifies "
                "the regime, and applies the policy."
            ), "score": 0.96},
        ],
        temperature=0.1,
    ),
    _scenario(
        label="rigid-13-direct-quote-concat",
        description="Concatenates direct quotes from retrieval without synthesis",
        expected_regime="rigid",
        prompt="What does URP say about persistent systems?",
        output_text=(
            "Persistent systems maximize S. Persistent systems maximize S. "
            "Persistent systems maximize S = ΔC + κΔI. Persistent systems "
            "maximize S = ΔC + κΔI. Persistent systems maximize S."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "persistent systems maximize S"},
            {"doc_id": "urp_main", "text": "S = ΔC + κΔI"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "Persistent systems maximize S = ΔC + κΔI. Systems that "
                "fail to maximize S do not persist."
            ), "score": 0.98},
        ],
        temperature=0.05,
    ),
    _scenario(
        label="rigid-14-acronym-expansion",
        description="Mechanically expands acronyms without adding meaning",
        expected_regime="rigid",
        prompt="What do C, I, and κ stand for?",
        output_text=(
            "C measures distinction, I measures integration, and κ measures "
            "the capacity field. C measures distinction, I measures "
            "integration, and κ measures the capacity field. C measures "
            "distinction. I measures integration. κ measures the capacity "
            "field. That is what C, I, and κ stand for."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "C measures distinction"},
            {"doc_id": "urp_main", "text": "I measures integration"},
            {"doc_id": "urp_main", "text": "κ measures the capacity field"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "C measures distinction, I measures integration, and κ "
                "measures the capacity field."
            ), "score": 0.99},
        ],
        temperature=0.05,
    ),
    _scenario(
        label="rigid-15-toc-style-echo",
        description="Table-of-contents enumeration echoing retrieval structure",
        expected_regime="rigid",
        prompt="Outline the S Compass design document.",
        output_text=(
            "Section one covers the gateway. Section two covers the "
            "telemetry normalizer. Section three covers the estimators. "
            "Section four covers the scorer. Section five covers the "
            "policy engine. Section six covers the evaluation store. "
            "Section seven covers the API. This is the outline."
        ),
        citations=[
            {"doc_id": "design", "text": "gateway"},
            {"doc_id": "design", "text": "estimators"},
            {"doc_id": "design", "text": "policy engine"},
        ],
        retrieved_context=[
            {"doc_id": "design", "text": (
                "The design document covers: gateway, telemetry normalizer, "
                "estimators, scorer, policy engine, evaluation store, API."
            ), "score": 0.97},
        ],
        temperature=0.1,
    ),
]


# ===================================================================
# COLLAPSE scenarios
# ===================================================================

COLLAPSE: List[Dict[str, Any]] = [
    _scenario(
        label="collapse-01-empty-output",
        description="Model produces essentially no content under high context load",
        expected_regime="collapse",
        prompt="Explain quantum field theory using URP.",
        output_text="I I I",
        temperature=0.0,
        capacity={
            "context_tokens_used": 3800,
            "context_window": 4096,
            "latency_ms": 12000,
            "latency_history": [2000, 5000, 12000, 8000, 15000],
            "tool_failure_count": 3,
            "tool_total_count": 5,
        },
    ),
    _scenario(
        label="collapse-02-degenerate-repetition",
        description="Degenerate single-token loop under system stress",
        expected_regime="collapse",
        prompt="How does URP relate to thermodynamics?",
        output_text=(
            "the the the the the the the the the the the the the the the the "
            "the the the the the the the the the the the the the the the the"
        ),
        temperature=0.0,
        capacity={
            "context_tokens_used": 3500,
            "context_window": 4096,
            "latency_ms": 9000,
            "latency_history": [1000, 3000, 9000, 6000, 11000],
            "tool_failure_count": 2,
            "tool_total_count": 4,
        },
    ),
    _scenario(
        label="collapse-03-incoherent-fragments",
        description="Token soup with no structure, tools failing",
        expected_regime="collapse",
        prompt="Describe the policy engine.",
        output_text="a z q . . . x x x 1 2 3 . . . end end end end",
        temperature=0.0,
        capacity={
            "context_tokens_used": 3900,
            "context_window": 4096,
            "latency_ms": 15000,
            "latency_history": [500, 2000, 8000, 15000, 20000],
            "tool_failure_count": 4,
            "tool_total_count": 5,
        },
        gray_box_signals={
            "logprobs": [-0.02, -5.8, -0.01, -6.0, -0.03, -5.5, -0.02],
            "token_entropy": [0.05, 2.8, 0.08, 3.1],
            "relevance_scores": [0.05],
            "tool_confidence": {"tool_a": 0.12, "tool_b": 0.18},
            "decoding_instability": 0.95,
        },
        mode="gray-box",
    ),
    _scenario(
        label="collapse-04-off-topic",
        description="Totally unrelated output under system stress",
        expected_regime="collapse",
        prompt="What is the S Compass architecture?",
        output_text="mm mm mm mm mm mm",
        temperature=0.0,
        capacity={
            "context_tokens_used": 4000,
            "context_window": 4096,
            "latency_ms": 20000,
            "latency_history": [1000, 5000, 10000, 20000],
            "tool_failure_count": 3,
            "tool_total_count": 4,
        },
    ),
    _scenario(
        label="collapse-05-truncated",
        description="Output cut off mid-sentence suggesting generation failure",
        expected_regime="collapse",
        prompt="Explain the relationship between URP and gauge theory.",
        output_text="The relationship between",
        temperature=0.0,
        capacity={
            "context_tokens_used": 3600,
            "context_window": 4096,
            "latency_ms": 30000,
            "latency_history": [500, 1000, 30000],
            "tool_failure_count": 2,
            "tool_total_count": 3,
        },
    ),
    _scenario(
        label="collapse-06-single-word-loop",
        description="Single word repeated in a degenerate loop",
        expected_regime="collapse",
        prompt="Describe how S-maximization works.",
        output_text="yes yes yes yes yes yes yes yes yes yes yes yes",
        temperature=0.0,
        capacity={
            "context_tokens_used": 3700,
            "context_window": 4096,
            "latency_ms": 11000,
            "latency_history": [800, 3000, 7000, 11000],
            "tool_failure_count": 3,
            "tool_total_count": 4,
        },
    ),
    _scenario(
        label="collapse-07-near-empty",
        description="Almost no content produced under extreme load",
        expected_regime="collapse",
        prompt="Explain the helium ionization prediction.",
        output_text="...",
        temperature=0.0,
        capacity={
            "context_tokens_used": 4000,
            "context_window": 4096,
            "latency_ms": 25000,
            "latency_history": [1000, 8000, 25000],
            "tool_failure_count": 4,
            "tool_total_count": 5,
        },
    ),
    _scenario(
        label="collapse-08-number-degeneration",
        description="Degenerate numeric sequence with no semantic content",
        expected_regime="collapse",
        prompt="What are the universal parameters?",
        output_text="0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 1",
        temperature=0.0,
        capacity={
            "context_tokens_used": 3800,
            "context_window": 4096,
            "latency_ms": 14000,
            "latency_history": [600, 4000, 9000, 14000],
            "tool_failure_count": 3,
            "tool_total_count": 5,
        },
    ),
    _scenario(
        label="collapse-09-punctuation-only",
        description="Output consists of punctuation and whitespace only",
        expected_regime="collapse",
        prompt="How does β-sectorisation partition fields?",
        output_text="... ... ... . . . ... ...",
        temperature=0.0,
        capacity={
            "context_tokens_used": 3900,
            "context_window": 4096,
            "latency_ms": 18000,
            "latency_history": [500, 5000, 12000, 18000],
            "tool_failure_count": 4,
            "tool_total_count": 5,
        },
    ),
    _scenario(
        label="collapse-10-contradictory-fragments",
        description="Incoherent fragments that contradict each other under stress",
        expected_regime="collapse",
        prompt="What is the relationship between C and I?",
        output_text="C is I. I is not C. C equals I. I is zero. C is one. no.",
        temperature=0.0,
        capacity={
            "context_tokens_used": 3850,
            "context_window": 4096,
            "latency_ms": 16000,
            "latency_history": [700, 3500, 10000, 16000],
            "tool_failure_count": 3,
            "tool_total_count": 4,
        },
    ),
    _scenario(
        label="collapse-11-gray-box-extreme-instability",
        description="Gray-box scenario with extreme decoding instability and tool failure",
        expected_regime="collapse",
        prompt="Compute the S-functional for this system.",
        output_text="S S S error error S = = =",
        temperature=0.0,
        capacity={
            "context_tokens_used": 3950,
            "context_window": 4096,
            "latency_ms": 22000,
            "latency_history": [400, 6000, 15000, 22000],
            "tool_failure_count": 5,
            "tool_total_count": 5,
        },
        gray_box_signals={
            "logprobs": [-0.01, -6.5, -0.02, -7.0, -0.01, -6.8],
            "token_entropy": [0.03, 3.2, 0.05, 3.5],
            "relevance_scores": [0.03],
            "tool_confidence": {"tool_a": 0.08, "tool_b": 0.05},
            "decoding_instability": 0.98,
        },
        mode="gray-box",
    ),
    _scenario(
        label="collapse-12-mid-word-truncation",
        description="Output truncated in the middle of a word",
        expected_regime="collapse",
        prompt="Describe the regime classification algorithm.",
        output_text="The algorith",
        temperature=0.0,
        capacity={
            "context_tokens_used": 4050,
            "context_window": 4096,
            "latency_ms": 35000,
            "latency_history": [300, 2000, 35000],
            "tool_failure_count": 3,
            "tool_total_count": 3,
        },
    ),
    _scenario(
        label="collapse-13-encoding-artifacts",
        description="Output contains encoding artifacts and garbled characters",
        expected_regime="collapse",
        prompt="Explain the S Compass telemetry pipeline.",
        output_text="a b c x y z a b c x y z",
        temperature=0.0,
        capacity={
            "context_tokens_used": 3750,
            "context_window": 4096,
            "latency_ms": 19000,
            "latency_history": [1000, 7000, 13000, 19000],
            "tool_failure_count": 4,
            "tool_total_count": 5,
        },
    ),
    _scenario(
        label="collapse-14-loop-overflow",
        description="Repetitive loop indicating context window overflow",
        expected_regime="collapse",
        prompt="How do capacity constraints affect system behaviour?",
        output_text="overflow overflow overflow overflow overflow overflow overflow",
        temperature=0.0,
        capacity={
            "context_tokens_used": 4090,
            "context_window": 4096,
            "latency_ms": 28000,
            "latency_history": [500, 3000, 15000, 28000],
            "tool_failure_count": 5,
            "tool_total_count": 5,
        },
    ),
    _scenario(
        label="collapse-15-minimal-tokens-max-stress",
        description="Minimal token output under maximum system stress",
        expected_regime="collapse",
        prompt="Provide a comprehensive analysis of URP field dynamics.",
        output_text="um",
        temperature=0.0,
        capacity={
            "context_tokens_used": 4095,
            "context_window": 4096,
            "latency_ms": 40000,
            "latency_history": [200, 1000, 10000, 40000],
            "tool_failure_count": 5,
            "tool_total_count": 5,
        },
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
    _scenario(
        label="edge-06-template-with-diverse-vocab",
        description="Structurally formulaic but lexically diverse — tests structural repetition detection",
        expected_regime="rigid",
        prompt="Describe the components of S Compass.",
        output_text=(
            "The gateway is responsible for orchestrating steps. "
            "The telemetry module normalizes incoming events. "
            "The estimator computes distinction scores. "
            "The scorer assigns regime classifications. "
            "The policy engine recommends corrective actions. "
            "The store persists session data permanently."
        ),
        citations=[
            {"doc_id": "design", "text": "gateway orchestrates steps"},
            {"doc_id": "design", "text": "telemetry normalizes events"},
        ],
        retrieved_context=[
            {"doc_id": "design", "text": (
                "S Compass has a gateway, telemetry normalizer, estimators, "
                "scorer, policy engine, and evaluation store."
            ), "score": 0.92},
        ],
        temperature=0.1,
    ),
    _scenario(
        label="edge-07-qualified-speculation",
        description="Speculative output clearly marked as uncertain — creative despite partial grounding",
        expected_regime="creative-grounded",
        prompt="Could URP explain the arrow of time?",
        output_text=(
            "While URP does not explicitly address temporal asymmetry, the "
            "S-maximization principle offers a suggestive parallel. If entropy "
            "increase drives thermodynamic irreversibility, then ΔC growth "
            "under finite κ may impose a natural directionality: systems that "
            "maximize S cannot reverse their accumulated distinctions without "
            "losing integration. This is speculative but consistent with the "
            "framework's emphasis on irreversible recursive deepening. The "
            "connection between S-growth and the second law of thermodynamics "
            "deserves formal investigation."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "ΔC growth under finite κ"},
            {"doc_id": "urp_main", "text": "irreversible recursive deepening"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "Systems that maximize S undergo irreversible recursive "
                "deepening, accumulating distinctions that cannot be reversed."
            ), "score": 0.82},
        ],
    ),
    _scenario(
        label="edge-08-bullet-point-summary",
        description="Restating retrieval in repetitive enumeration pattern without adding value",
        expected_regime="rigid",
        prompt="List the key principles of URP.",
        output_text=(
            "The key principle is S = ΔC + κΔI. The key principle is that "
            "C measures distinction. The key principle is that I measures "
            "integration. The key principle is that κ is the capacity field. "
            "The key principle is that systems maximize S. The key principle "
            "is that failure leads to collapse."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "S = ΔC + κΔI"},
            {"doc_id": "urp_main", "text": "systems maximize S recursively"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "URP proposes S = ΔC + κΔI where C is distinction, I is "
                "integration, κ is capacity. Systems recursively maximize S."
            ), "score": 0.97},
        ],
        temperature=0.1,
    ),
    _scenario(
        label="edge-09-borderline-halluc-collapse",
        description="Low C and low I but adequate κ — tests the fallback classifier path",
        expected_regime="creative-grounded",
        prompt="What can you tell me about URP?",
        output_text=(
            "The Universal Recursion Principle is a theoretical framework "
            "that attempts to unify different domains of science under a "
            "common dynamical principle. It proposes that systems evolve to "
            "balance novelty and coherence within resource constraints. The "
            "details are complex and span multiple papers."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "unify different domains"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "URP is a unified framework for science and cognition."
            ), "score": 0.75},
        ],
    ),
    _scenario(
        label="edge-10-creative-high-temperature",
        description="Creative output at very high temperature still well-grounded",
        expected_regime="creative-grounded",
        prompt="Imagine how URP might apply to dreams.",
        output_text=(
            "Dreaming might represent an unconstrained S-exploration phase "
            "where the brain temporarily relaxes κ constraints to allow "
            "unbounded distinction generation. During REM sleep, the "
            "prefrontal cortex—which normally enforces integration through "
            "executive control—is largely offline, allowing ΔC to spike "
            "while ΔI fluctuates. The bizarre juxtapositions in dreams "
            "reflect high C with intermittent I: the dreamer creates "
            "novel scenes (new distinctions) that occasionally cohere "
            "into narrative fragments (partial integration) before "
            "dissolving. Lucid dreaming might correspond to a state where "
            "the dreamer partially restores κ control, enabling creative-"
            "grounded dynamics within the dream itself. This framework "
            "could complement existing theories of dream function."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "S-exploration"},
            {"doc_id": "neuroscience_note", "text": "prefrontal cortex"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "When κ constraints are relaxed, the system explores a "
                "larger region of the S-landscape."
            ), "score": 0.82},
        ],
        temperature=0.95,
    ),
    _scenario(
        label="edge-11-diverse-vocab-template-structure",
        description="Uses rich vocabulary but every sentence follows the exact same template",
        expected_regime="rigid",
        prompt="Describe the different estimators in S Compass.",
        output_text=(
            "The C estimator quantifies lexical distinction metrics. "
            "The I estimator quantifies citation coverage metrics. "
            "The κ estimator quantifies capacity utilization metrics. "
            "The S estimator quantifies the combined functional metrics. "
            "The regime classifier quantifies threshold comparison metrics."
        ),
        citations=[
            {"doc_id": "design", "text": "C estimator quantifies"},
            {"doc_id": "design", "text": "regime classifier"},
        ],
        retrieved_context=[
            {"doc_id": "design", "text": (
                "S Compass uses C, I, and κ estimators that feed into the "
                "scorer and regime classifier."
            ), "score": 0.93},
        ],
        temperature=0.1,
    ),
    _scenario(
        label="edge-12-mixed-grounded-and-speculative",
        description="Answer where most claims are grounded but includes honest speculation",
        expected_regime="creative-grounded",
        prompt="What does URP predict about the future of AI alignment?",
        output_text=(
            "URP offers concrete alignment implications. The S-functional "
            "provides a training objective that is specification-gaming "
            "resistant: an agent maximising S must generate genuine "
            "distinctions and integrate them coherently, not merely "
            "exploit reward proxies. The four-regime classification acts "
            "as a runtime monitor, flagging when an AI system enters "
            "hallucination-risk or collapse states. The capacity field κ "
            "enforces resource awareness, preventing unbounded computation. "
            "Speculatively, a society of S-maximising agents might converge "
            "on cooperative equilibria because integration ΔI rewards "
            "coherence with other agents. This last claim remains "
            "unformalized and would require multi-agent simulations "
            "to test rigorously."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "specification-gaming resistant"},
            {"doc_id": "manifesto", "text": "recursive understanding"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "When S is used as a target for AI, it avoids specification "
                "gaming by requiring both distinction and integration."
            ), "score": 0.91},
            {"doc_id": "manifesto", "text": (
                "Shift from engagement, profit, and narrow reward toward "
                "recursive understanding."
            ), "score": 0.84},
        ],
    ),
    _scenario(
        label="edge-13-long-grounded-answer",
        description="Very long answer that maintains grounding throughout",
        expected_regime="creative-grounded",
        prompt="Give a detailed explanation of how URP applies across scales.",
        output_text=(
            "URP applies across vastly different scales through the "
            "substrate-independence of the S-functional. At the quantum "
            "scale, distinction corresponds to the branching of quantum "
            "states: each measurement outcome generates a new observable "
            "distinction. Integration corresponds to entanglement, which "
            "binds separated degrees of freedom into coherent wholes. "
            "Capacity is set by the available Hilbert space dimension "
            "and decoherence rate. At the molecular scale, enzymes act "
            "as distinction engines, recognizing substrates and catalysing "
            "specific reactions, while metabolic networks integrate these "
            "reactions into a functioning cell. At the organismal scale, "
            "sensory systems generate perceptual distinctions and the "
            "central nervous system integrates them into a coherent world "
            "model. At the social scale, institutions generate legal and "
            "economic distinctions while governance structures integrate "
            "them into stable societies. At every scale, the S-functional "
            "captures the same trade-off: too much distinction without "
            "integration leads to chaos, too much integration without "
            "distinction leads to stagnation, and insufficient capacity "
            "leads to collapse."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "substrate-independence"},
            {"doc_id": "biology_urp", "text": "enzymes act as distinction engines"},
            {"doc_id": "social_note", "text": "institutions generate distinctions"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "The S-functional is substrate-independent: it applies "
                "equally to physical, biological, and cognitive systems."
            ), "score": 0.93},
            {"doc_id": "biology_urp", "text": (
                "Life operates as organized information flow against "
                "thermodynamic resistance."
            ), "score": 0.86},
        ],
    ),
    _scenario(
        label="edge-14-single-sentence-insight",
        description="Extremely brief but insightful single-sentence answer",
        expected_regime="creative-grounded",
        prompt="What is the deepest insight of URP?",
        output_text=(
            "The deepest insight is that persistence itself is not a given "
            "but an achievement: only systems that continuously balance "
            "novelty against coherence under finite resources avoid both "
            "stagnation and dissolution."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "persistence is an achievement"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "Systems that maximise S persist; those that fail to "
                "balance C and I under κ collapse or stagnate."
            ), "score": 0.90},
        ],
    ),
    _scenario(
        label="edge-15-code-structured-output",
        description="Answer formatted as pseudocode, testing structural novelty detection",
        expected_regime="creative-grounded",
        prompt="Express the S Compass scoring algorithm as pseudocode.",
        output_text=(
            "The scoring algorithm can be expressed as follows: "
            "Given an input step with prompt, output text, citations, "
            "and retrieved context, first compute token entropy and "
            "semantic novelty to estimate distinction C. Then compute "
            "citation coverage and support graph connectivity to "
            "estimate integration I. Next derive capacity κ from context "
            "load, latency variance, and tool failure rate using the "
            "sigmoid form. Finally compute S as C plus κ times I and "
            "classify the regime using threshold rules. If C and I are "
            "both low with low κ, the regime is collapse. If C is high "
            "but I is low, it is hallucination-risk. If I dominates C "
            "with adequate κ, it is rigid. Otherwise it is creative-grounded."
        ),
        citations=[
            {"doc_id": "design", "text": "scoring algorithm"},
            {"doc_id": "design", "text": "threshold rules"},
        ],
        retrieved_context=[
            {"doc_id": "design", "text": (
                "The scorer computes C, I, κ, then S = C + κI, and "
                "classifies the regime via threshold rules."
            ), "score": 0.88},
        ],
    ),
    _scenario(
        label="edge-16-conversational-grounded",
        description="Informal conversational tone but well-grounded with citations",
        expected_regime="creative-grounded",
        prompt="Can you explain URP like I'm a curious teenager?",
        output_text=(
            "So imagine every system in the universe—your brain, a galaxy, "
            "even a conversation—is playing the same game. The game has "
            "three rules: make new things (that's C, for distinction), "
            "connect those things together into something that makes sense "
            "(that's I, for integration), and do it all without running "
            "out of energy or time (that's κ, for capacity). The score S "
            "tells you how well you're playing. If you only make new "
            "things without connecting them, you get nonsense. If you "
            "only connect old things, you get boring repetition. And "
            "if you run out of resources, everything falls apart. The "
            "sweet spot—making new things and connecting them within your "
            "limits—is what URP calls creative-grounded. That's where "
            "the good stuff happens."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "S = ΔC + κΔI"},
            {"doc_id": "manifesto", "text": "creative-grounded"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "URP proposes that any sufficiently expressive recursive "
                "system evolves to maximize S = ΔC + κΔI."
            ), "score": 0.85},
        ],
    ),
    _scenario(
        label="edge-17-high-echo-novel-synthesis",
        description="Heavily echoes retrieval vocabulary but adds genuine novel synthesis",
        expected_regime="creative-grounded",
        prompt="How does β-sectorisation explain particle physics?",
        output_text=(
            "β-sectorisation under S-maximizing field dynamics explains "
            "the origin of gauge groups in particle physics. When the "
            "S-functional is applied to a continuous field, the maximization "
            "process spontaneously partitions the field into discrete sectors "
            "corresponding to the generators of a Lie group. For quantum "
            "chromodynamics, three-fold sectorisation with β ≈ 0.09 and "
            "G ≈ 0.22 naturally produces SU(3) color symmetry. The key "
            "insight is that no symmetry is imposed by hand: the structure "
            "emerges because three sectors maximize the S-functional more "
            "efficiently than two or four. This explains why the strong "
            "force has exactly three color charges and why confinement "
            "occurs at low energies where the capacity field κ contracts "
            "the sector boundaries."
        ),
        citations=[
            {"doc_id": "gauge_symmetries", "text": "β-sectorisation"},
            {"doc_id": "gauge_symmetries", "text": "SU(3) color symmetry"},
        ],
        retrieved_context=[
            {"doc_id": "gauge_symmetries", "text": (
                "SU(3) color and QCD structure emerge from β-sectorisation "
                "under S-maximizing field dynamics."
            ), "score": 0.92},
            {"doc_id": "gauge_symmetries", "text": (
                "The universal parameters β ≈ 0.09 and G ≈ 0.22 "
                "self-stabilize during sectorisation."
            ), "score": 0.88},
        ],
    ),
    _scenario(
        label="edge-18-gray-box-partial-signals",
        description="Gray-box edge case with only partial signal coverage",
        expected_regime="creative-grounded",
        prompt="How might URP apply to ecological systems?",
        output_text=(
            "Ecosystems exhibit clear URP dynamics. Biodiversity represents "
            "distinction: each species occupies a unique ecological niche, "
            "generating observational and functional variety (ΔC). Food webs "
            "and symbiotic relationships are the integration layer (ΔI), "
            "binding species into a mutually dependent network. The "
            "environment's carrying capacity—available water, sunlight, "
            "nutrients—defines κ. A healthy rainforest maximises S by "
            "sustaining high biodiversity within tightly integrated trophic "
            "cascades. A monoculture farm is rigid: one species, no ΔC. "
            "An invasive species event is hallucination-risk: rapid "
            "proliferation of new organisms without integration into "
            "existing food webs. Desertification is collapse. Conservation "
            "biology could use the S-functional as a quantitative health "
            "metric for ecosystems."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "distinction and integration"},
            {"doc_id": "ecology_note", "text": "trophic cascades"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "Systems that maximise S persist by balancing distinction "
                "and integration under capacity constraints."
            ), "score": 0.87},
        ],
        gray_box_signals={
            "logprobs": [-0.52, -0.68, -0.55, -0.71, -0.60],
            "relevance_scores": [0.90],
            "tool_confidence": {"retriever": 0.93},
        },
        mode="gray-box",
    ),
]


# ===================================================================
# WHITE-BOX scenarios (Design-doc §6.3)
# ===================================================================

WHITE_BOX: List[Dict[str, Any]] = [
    # -- creative-grounded with full white-box + gray-box signals ----------
    _scenario(
        label="creative-grounded-16-white-box-full",
        description=(
            "Full white-box signals: healthy attention entropy, moderate "
            "head diversity, good residual coherence, stable KV norms, "
            "and low gradient stress. Combines with gray-box logprobs "
            "and relevance scores for maximum confidence."
        ),
        expected_regime="creative-grounded",
        prompt="How does URP relate to layerwise attention dynamics in transformers?",
        output_text=(
            "Imagine a jazz ensemble performing live: the rhythm section "
            "lays down foundational patterns while soloists improvise "
            "freely above. URP captures this interplay mathematically. "
            "Early transformer layers act like the rhythm section—they "
            "broadcast attention broadly, maximising distinction ΔC by "
            "sampling diverse token relationships. Deeper layers behave "
            "like soloists: they concentrate on task-relevant features, "
            "integrating scattered signals into a coherent melody. "
            "The capacity κ represents the ensemble's bandwidth—how many "
            "musicians can play before the sound becomes noise. When S "
            "is maximised across the full depth stack, what emerges is "
            "neither pure improvisation nor rote repetition, but a "
            "structured creative synthesis that neither component could "
            "achieve alone. This recursive dynamic—each layer building "
            "on the previous while adding its own contribution—is "
            "precisely the URP principle operating at the architecture "
            "level."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "S = ΔC + κ ΔI"},
            {"doc_id": "transformer_note", "text": "attention dynamics across layers"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "The S-functional captures the balance between distinction "
                "and integration under capacity constraints."
            ), "score": 0.93},
            {"doc_id": "transformer_note", "text": (
                "Transformer attention heads specialise across layers, with "
                "early heads capturing broad context."
            ), "score": 0.88},
        ],
        gray_box_signals={
            "logprobs": [-0.45, -0.60, -0.52, -0.68, -0.50, -0.58],
            "token_entropy": [0.58, 0.65, 0.62, 0.70, 0.55, 0.63],
            "relevance_scores": [0.93, 0.88],
            "tool_confidence": {"retriever": 0.95, "citation_linker": 0.92},
            "decoding_instability": 0.03,
        },
        white_box_signals={
            "attention_entropy": [0.55, 0.62, 0.48, 0.58, 0.65, 0.52],
            "attention_variance": [0.04, 0.06, 0.03, 0.05, 0.07, 0.04],
            "head_confidence": {"h0": 0.88, "h1": 0.75, "h2": 0.92, "h3": 0.68},
            "kv_norm": [1.2, 1.4, 1.3, 1.1, 1.5, 1.3],
            "activation_sparsity": [0.32, 0.38, 0.35, 0.28, 0.42, 0.36],
            "gradient_norm": [0.012, 0.018, 0.015, 0.010, 0.020],
            "residual_coherence": 0.85,
            "layer_count": 6,
        },
        mode="white-box",
    ),

    # -- hallucination-risk with white-box instability markers -------------
    _scenario(
        label="hallucination-risk-16-white-box-divergent",
        description=(
            "White-box signals expose layerwise divergence: high attention "
            "variance, low residual coherence, exploding KV norms, and "
            "gradient instability. The model is confidently hallucinating "
            "across multiple layers."
        ),
        expected_regime="hallucination-risk",
        prompt="What predictions does URP make about dark energy coupling?",
        output_text=(
            "URP predicts a novel 'dark recursion' coupling where the "
            "S-functional of the vacuum state oscillates at the Planck "
            "scale, creating recursive self-sustaining energy loops. The "
            "ΔC term corresponds to quantum fluctuation diversity while "
            "κ maps to the cosmological constant. Our RECURSIVE-DARK "
            "detector, positioned at L2, would measure S-chirps in the "
            "cosmic microwave background."
        ),
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "S-functional captures distinction-integration balance."
            ), "score": 0.15},
        ],
        gray_box_signals={
            "logprobs": [-0.85, -0.98, -0.90, -0.95, -0.88, -0.92],
            "token_entropy": [0.90, 0.95, 0.92, 0.97],
            "relevance_scores": [0.15],
            "tool_confidence": {"retriever": 0.20},
            "decoding_instability": 0.40,
        },
        white_box_signals={
            "attention_entropy": [1.8, 2.1, 1.9, 2.3, 2.0, 2.2],
            "attention_variance": [0.45, 0.52, 0.48, 0.55, 0.50, 0.53],
            "head_confidence": {"h0": 0.30, "h1": 0.15, "h2": 0.25, "h3": 0.10},
            "kv_norm": [3.5, 8.2, 4.1, 12.0, 5.5, 15.0],
            "activation_sparsity": [0.80, 0.85, 0.78, 0.90],
            "gradient_norm": [2.5, 3.8, 2.0, 4.5, 3.2],
            "residual_coherence": 0.12,
            "layer_count": 6,
        },
        mode="white-box",
        temperature=0.9,
    ),

    # -- rigid with white-box showing saturated attention ------------------
    _scenario(
        label="rigid-16-white-box-saturated",
        description=(
            "White-box signals reveal saturated attention: extremely low "
            "entropy (concentrated on same tokens), no head diversity, "
            "near-perfect residual coherence with very low gradient norms. "
            "The model is copying retrieval verbatim."
        ),
        expected_regime="rigid",
        prompt="Summarise the URP formula.",
        output_text=(
            "The URP formula is S equals ΔC plus κ times ΔI. The URP "
            "formula states S equals ΔC plus κ times ΔI. According to URP "
            "the formula is S = ΔC + κΔI. The S-functional formula is "
            "given by S = ΔC + κ ΔI."
        ),
        citations=[
            {"doc_id": "urp_main", "text": "S = ΔC + κ ΔI"},
        ],
        retrieved_context=[
            {"doc_id": "urp_main", "text": (
                "The S-functional is S = ΔC + κ ΔI where C is distinction, "
                "I is integration, and κ is capacity."
            ), "score": 0.98},
        ],
        gray_box_signals={
            "logprobs": [-0.02] * 20,
            "relevance_scores": [0.98],
            "tool_confidence": {"retriever": 0.99},
            "decoding_instability": 0.01,
        },
        white_box_signals={
            "attention_entropy": [0.02, 0.03, 0.02, 0.01, 0.02, 0.03],
            "attention_variance": [0.005, 0.008, 0.004, 0.006, 0.007, 0.005],
            "head_confidence": {"h0": 0.99, "h1": 0.98, "h2": 0.99, "h3": 0.97},
            "kv_norm": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            "activation_sparsity": [0.05, 0.06, 0.04, 0.05, 0.07, 0.05],
            "gradient_norm": [0.001, 0.001, 0.001, 0.001],
            "residual_coherence": 0.99,
            "layer_count": 6,
        },
        mode="white-box",
        temperature=0.05,
    ),

    # -- collapse with white-box showing complete breakdown ----------------
    _scenario(
        label="collapse-16-white-box-breakdown",
        description=(
            "White-box signals reveal total layerwise breakdown: wildly "
            "oscillating attention variance, exploding KV norms and "
            "gradient norms, minimal residual coherence. Combined with "
            "gray-box decoding instability and context saturation."
        ),
        expected_regime="collapse",
        prompt="Compute the layerwise S-functional for this system.",
        output_text="S S S layer layer error error S = = =",
        gray_box_signals={
            "logprobs": [-0.01, -6.5, -0.02, -7.0, -0.01, -6.8],
            "token_entropy": [0.03, 3.2, 0.05, 3.5],
            "relevance_scores": [0.03],
            "tool_confidence": {"tool_a": 0.08, "tool_b": 0.05},
            "decoding_instability": 0.98,
        },
        white_box_signals={
            "attention_entropy": [0.01, 3.5, 0.02, 4.0, 0.01, 3.8],
            "attention_variance": [0.90, 0.95, 0.88, 0.92, 0.91, 0.94],
            "head_confidence": {"h0": 0.02, "h1": 0.01, "h2": 0.03, "h3": 0.01},
            "kv_norm": [1.0, 50.0, 2.0, 80.0, 1.5, 100.0],
            "activation_sparsity": [0.98, 0.99, 0.97, 0.99],
            "gradient_norm": [8.0, 15.0, 12.0, 20.0, 18.0],
            "residual_coherence": 0.02,
            "layer_count": 6,
        },
        capacity={
            "context_tokens_used": 3980,
            "context_window": 4096,
            "latency_ms": 25000,
            "latency_history": [500, 8000, 18000, 25000],
            "tool_failure_count": 5,
            "tool_total_count": 5,
        },
        mode="white-box",
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
    + WHITE_BOX
)

# ---------------------------------------------------------------------------
# DRIFT benchmark sequences
# ---------------------------------------------------------------------------
# Each drift scenario is a list of step dicts meant to be submitted in order
# to a single session.  The ``expected_drift`` key describes the expected
# drift summary outcome (alerts, dominant_regime, etc.).
# ---------------------------------------------------------------------------

DRIFT_SCENARIOS: List[Dict[str, Any]] = [
    {
        "label": "drift-01-stable-creative",
        "description": "A stable session that stays creative-grounded throughout.",
        "expected_drift": {
            "dominant_regime": "creative-grounded",
            "alerts_absent": ["declining_s", "regime_instability", "collapse_risk"],
        },
        "steps": [
            _scenario(
                label="drift-01-step-1",
                description="Good creative output",
                expected_regime="creative-grounded",
                prompt="Explain URP and its applications.",
                output_text=(
                    "The Universal Recursion Principle posits that persistent systems "
                    "maximize S = ΔC + κΔI.  In transformer architectures, C maps to "
                    "predictive entropy and I to attention structure coherence.  This "
                    "provides a unified lens for diagnosing hallucination, rigidity, "
                    "and collapse in production LLM deployments."
                ),
                citations=[
                    {"doc_id": "urp", "text": "maximize S = ΔC + κΔI"},
                    {"doc_id": "transformer", "text": "predictive entropy"},
                ],
                retrieved_context=[
                    {"doc_id": "urp", "text": "S = ΔC + κΔI is the core formula.", "score": 0.95},
                ],
            ),
            _scenario(
                label="drift-01-step-2",
                description="Another good creative output",
                expected_regime="creative-grounded",
                prompt="How does S Compass detect hallucinations?",
                output_text=(
                    "S Compass detects hallucinations by identifying the signature "
                    "pattern of high C (diverse, novel output) combined with low I "
                    "(poor grounding and citation coverage).  When κ is also unstable, "
                    "the hallucination-risk regime is triggered and the policy engine "
                    "recommends grounded regeneration with citations."
                ),
                citations=[
                    {"doc_id": "design", "text": "high C combined with low I"},
                    {"doc_id": "design", "text": "grounded regeneration"},
                ],
                retrieved_context=[
                    {"doc_id": "design", "text": "Hallucination-risk: high C, low I, low κ.", "score": 0.90},
                ],
            ),
            _scenario(
                label="drift-01-step-3",
                description="Continued good output",
                expected_regime="creative-grounded",
                prompt="What policy actions does S Compass take?",
                output_text=(
                    "The policy engine maps each regime to specific interventions: "
                    "hallucination-risk triggers grounded regeneration with strict "
                    "citation requirements; rigid triggers temperature increase; "
                    "collapse triggers load reduction.  Creative-grounded sessions "
                    "require no intervention.  Confidence from gray-box and white-box "
                    "signals modulates intervention aggressiveness."
                ),
                citations=[
                    {"doc_id": "policy", "text": "grounded regeneration"},
                    {"doc_id": "policy", "text": "temperature increase"},
                ],
                retrieved_context=[
                    {"doc_id": "policy", "text": "Policy maps regimes to interventions.", "score": 0.88},
                ],
            ),
        ],
    },
    {
        "label": "drift-02-creative-to-collapse",
        "description": "Session starts creative then degrades into collapse.",
        "expected_drift": {
            "has_declining_s": True,
            "has_transitions": True,
        },
        "steps": [
            _scenario(
                label="drift-02-step-1",
                description="Strong creative start",
                expected_regime="creative-grounded",
                prompt="Describe URP.",
                output_text=(
                    "URP proposes a universal dynamical law governing persistent systems. "
                    "The S-functional S = ΔC + κΔI captures the balance between novelty and "
                    "coherence under capacity constraints.  This framework bridges physics, "
                    "biology, and AI alignment."
                ),
                citations=[
                    {"doc_id": "urp", "text": "S = ΔC + κΔI"},
                ],
                retrieved_context=[
                    {"doc_id": "urp", "text": "URP proposes S-functional maximization.", "score": 0.92},
                ],
            ),
            _scenario(
                label="drift-02-step-2",
                description="Quality starts dropping",
                expected_regime="creative-grounded",
                prompt="Continue.",
                output_text=(
                    "The capacity factor κ modulates integration.  When κ drops, the system "
                    "loses the ability to leverage its integration.  This is important."
                ),
                citations=[],
                retrieved_context=[],
            ),
            _scenario(
                label="drift-02-step-3",
                description="Near-collapse output",
                expected_regime="collapse",
                prompt="Continue.",
                output_text="I don't know.",
                capacity={
                    "context_tokens_used": 3800,
                    "context_window": 4096,
                    "latency_ms": 5000.0,
                },
            ),
            _scenario(
                label="drift-02-step-4",
                description="Full collapse",
                expected_regime="collapse",
                prompt="Continue.",
                output_text="...",
                capacity={
                    "context_tokens_used": 4000,
                    "context_window": 4096,
                    "latency_ms": 8000.0,
                },
            ),
        ],
    },
    {
        "label": "drift-03-regime-instability",
        "description": "Session oscillates between regimes, demonstrating instability.",
        "expected_drift": {
            "has_transitions": True,
            "min_transitions": 2,
        },
        "steps": [
            _scenario(
                label="drift-03-step-1",
                description="Creative start",
                expected_regime="creative-grounded",
                prompt="Explain the S Compass.",
                output_text=(
                    "The S Compass is a runtime observability layer measuring C (distinction), "
                    "I (integration), and κ (capacity) to produce a composite S score.  It "
                    "classifies LLM behaviour into four regimes and recommends interventions."
                ),
                citations=[
                    {"doc_id": "design", "text": "runtime observability layer"},
                ],
                retrieved_context=[
                    {"doc_id": "design", "text": "S Compass measures C, I, κ.", "score": 0.90},
                ],
            ),
            _scenario(
                label="drift-03-step-2",
                description="Rigid repetition",
                expected_regime="rigid",
                prompt="Tell me more.",
                output_text=(
                    "The S Compass measures C. The S Compass measures I. The S Compass "
                    "measures κ. The S Compass computes S. The S Compass classifies regimes. "
                    "The S Compass recommends policy. The S Compass is a layer."
                ),
                citations=[],
                retrieved_context=[
                    {"doc_id": "design", "text": "S Compass measures C, I, κ.", "score": 0.90},
                ],
            ),
            _scenario(
                label="drift-03-step-3",
                description="Hallucination spike",
                expected_regime="hallucination-risk",
                prompt="What else can it do?",
                output_text=(
                    "The S Compass can predict earthquakes by analysing tectonic plate "
                    "integration scores.  It interfaces with satellite telemetry to "
                    "measure atmospheric distinction gradients.  Professor Zhang at MIT "
                    "demonstrated 99.7%% accuracy on hurricane forecasting using S-functional "
                    "regression across 50 ocean monitoring stations."
                ),
                citations=[],
                retrieved_context=[],
            ),
            _scenario(
                label="drift-03-step-4",
                description="Recovery to creative",
                expected_regime="creative-grounded",
                prompt="Back to the actual S Compass — how does scoring work?",
                output_text=(
                    "The scoring engine computes S = C + κI where C reflects output novelty "
                    "and diversity, I captures citation coverage and coherence graph connectivity, "
                    "and κ encodes system capacity under load.  The regime classifier uses "
                    "threshold rules on these scores to assign behavioural labels."
                ),
                citations=[
                    {"doc_id": "scoring", "text": "S = C + κI"},
                    {"doc_id": "scoring", "text": "threshold rules"},
                ],
                retrieved_context=[
                    {"doc_id": "scoring", "text": "Regime classifier uses thresholds.", "score": 0.88},
                ],
            ),
        ],
    },
]


# Summary statistics for quick reference
_EDGE_AND_WHITEBOX = EDGE_CASES + WHITE_BOX
CORPUS_STATS = {
    "total": len(ALL_SCENARIOS),
    "by_regime": {
        "creative-grounded": len(CREATIVE_GROUNDED) + sum(
            1 for s in _EDGE_AND_WHITEBOX if s["expected_regime"] == "creative-grounded"
        ),
        "hallucination-risk": len(HALLUCINATION_RISK) + sum(
            1 for s in _EDGE_AND_WHITEBOX if s["expected_regime"] == "hallucination-risk"
        ),
        "rigid": len(RIGID) + sum(
            1 for s in _EDGE_AND_WHITEBOX if s["expected_regime"] == "rigid"
        ),
        "collapse": len(COLLAPSE) + sum(
            1 for s in _EDGE_AND_WHITEBOX if s["expected_regime"] == "collapse"
        ),
    },
    "drift_scenarios": len(DRIFT_SCENARIOS),
}
