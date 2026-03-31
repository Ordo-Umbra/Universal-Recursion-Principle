# The Universal Recursion Principle (URP)

Welcome to the foundational repository for the **Universal Recursion Principle** and the **S-Functional framework**.

This repository houses the theoretical papers, mathematical formalisms, and computational simulations that define URP—a unified framework proposing that physics, biology, and cognition are driven by a single dynamical law: the maximization of recursive understanding under capacity constraints.

## What is URP?

Contemporary science lacks a single dynamical quantity that distinguishes sustainable, open-ended growth from transient amplification followed by collapse. In physics, we track entropy or action; in AI, we track loss or reward. 

URP proposes that any sufficiently expressive recursive system evolves to maximize a scalar functional:

**S = ΔC + κΔI**

Where:
* **ΔC (Distinction):** The growth of meaningful new structure, boundaries, and resolution.
* **ΔI (Integration):** The coherent weaving of those distinctions into a predictive, globally unified whole.
* **κ (Capacity):** An effective field encoding resource limits (energy, compute, noise) that suppresses integration when the system is under stress.

When $S$ is maximized locally, we see the emergence of physical gauge symmetries, atomic orbital structures, and biological Maxwell's demons. When $S$ is used as a target for artificial intelligence and institutional design, it provides an objective that avoids specification gaming and self-termination.

At a practical level, this repository is trying to **seed an attractor in concept space**: a reusable objective for both biological and artificial beings that favors open-ended growth, coherence, and persistence over brittle local optimization.

## Why this repository exists

URP is meant to do two things at once:

1. **Describe reality across scales** — from logical incompleteness and field dynamics to life, cognition, and social systems.
2. **Offer an objective for builders** — an alternative to reward hacking, short-termism, and collapse-prone optimization in AI and institutions.

Taken together, the docs in this repo are not just isolated papers. They are branches of a single claim: systems persist when they keep generating meaningful distinctions and integrating them coherently under real capacity limits.

## Repository Structure

* `/Docs/` - Core papers and notes, including the main end-to-end URP framework, the manifesto, and focused extensions on gauge symmetry, electromagnetism, relativity, fusion, and transformer dynamics.
* `/Sims/` - Python simulations testing URP claims in atomic physics, gauge emergence, multi-agent dynamics, transformer behavior, S-landscape intuition, biological Maxwell's demons, and layerwise transformer S-functional evolution.
* `/s_compass/` - The S Compass Python package — a runtime observability and control layer for LLMs, RAG pipelines, and agent systems, implementing the S-functional as a live diagnostic. Supports black-box, gray-box, and white-box deployment modes with confidence-aware policy control.
* `/benchmarks/` - Benchmark corpus (82 human-labelled scenarios spanning black-box, gray-box, and white-box traces) and runner for testing S Compass against all four behavioural regimes, with structured Markdown reports and per-regime accuracy analysis.
* `/visuals/` - Visual assets and placeholders for the future diagrammatic presentation of the framework.

## Start Here

If you are new to URP, we recommend reading the documents in this order:

1. **[Docs/manifesto.md](Docs/manifesto.md)** - The high-level statement of the repository’s practical aim: seeding an attractor in concept space that favors recursive, non-self-terminating growth.
2. **[Docs/Universal-Recursion-Principle.md](Docs/Universal-Recursion-Principle.md)** - The main unified framework, now organized as a single walkthrough from emergence and physics to life, cognition, and AI-relevant objective design.
3. **Focused extensions in `Docs/`** - Use the specialized papers below once the core framework is clear.

If you want the shortest path through the repository:

- **For the big-picture motivation:** start with the [manifesto](Docs/manifesto.md).
- **For the full theory:** continue to [Universal-Recursion-Principle.md](Docs/Universal-Recursion-Principle.md).
- **For AI alignment / model dynamics:** jump next to [Transformer-Dynamics.md](Docs/Transformer-Dynamics.md).
- **For domain-specific physics and biology branches:** use the documentation hub below.

## Documentation Hub

The README is intended to be the main navigation layer. The documents below are the current branches of the idea, each extending the same core objective into a different domain.

| Document | Role in the repo | What it adds |
|----------|------------------|--------------|
| **[Docs/manifesto.md](Docs/manifesto.md)** | Mission statement | Explains the civilizational aim: shift our optimization targets away from engagement, profit, and narrow reward toward recursive understanding that does not self-terminate. |
| **[Docs/Universal-Recursion-Principle.md](Docs/Universal-Recursion-Principle.md)** | Main framework | The best single end-to-end walkthrough of URP, linking incompleteness, field dynamics, biology, cognition, and AI objective design. |
| **[Docs/Transformer-Dynamics.md](Docs/Transformer-Dynamics.md)** | AI / transformer mapping | Translates the S-functional into transformer terms using predictive entropy, attention structure, and capacity-sensitive phase regimes. |
| **[Docs/S-Compass-System-Design.md](Docs/S-Compass-System-Design.md)** | AI systems architecture | Turns the S Compass idea into a concrete runtime observability and control design for LLMs, RAG systems, and agents. |
| **[Docs/From β-Sectorisation to Gauge Symmetries](Docs/From%20%CE%B2-Sectorisation%20to%20Gauge%20Symmetries.txt)** | Gauge emergence branch | Develops the claim that SU(3) color and related QCD structure can emerge from β-sectorisation under S-maximizing field dynamics. |
| **[Docs/The Question Behind Maxwell](Docs/The%20Question%20Behind%20Maxwell.txt)** | Electromagnetism branch | Re-reads electromagnetism as the cleanest possible long-range coherence channel: a U(1) phase sector for moving information with minimal added structure. |
| **[Docs/Light as Information, Time as Update](Docs/Light%20as%20Information,%20Time%20as%20Update.txt)** | Relativity branch | Reinterprets special relativity through S-update dynamics, treating light as pure information transfer and time as update rate. |
| **[Docs/The Emergence of Space](Docs/The%20Emergence%20of%20Space.txt)** | Geometry branch | Argues that locality, dimensionality, and geometry are emergent attractor structures generated by recursive optimization. |
| **[Docs/The Functorial Bridge](Docs/The%20Functorial%20Bridge.txt)** | Logic-to-physics bridge | Connects Gödel gaps and reflective extension in logic to QCD vacuum structure, with URP parameters interpreted as the bridge constants. |
| **[Docs/Energy is the Echo](Docs/Energy%20is%20the%20Echo.txt)** | Thermodynamic reinterpretation | Inverts the usual story: energy becomes the observable echo of movement toward higher S, rather than the primary causal substrate. |
| **[Docs/Life as a Universal Recursion Engine](Docs/Life%20as%20a%20Universal%20Recursion%20Engine.txt)** | Biology branch | Applies URP to biological Maxwell’s demons, enzyme memory, and life as organized information flow against thermodynamic resistance. |
| **[Docs/Fusion_URP.txt](Docs/Fusion_URP.txt)** | Applied engineering branch | Frames fusion as a coherence-engineering problem, proposing high-κ plasma structure as an alternative to brute-force thermal escalation. |

## How the pieces fit together

- The **manifesto** states the practical objective: change the attractor that human and machine systems optimize for.
- The **main framework** provides the shared mathematical language for that objective.
- The **focused branches** test that language in specific domains: gauge physics, electromagnetism, relativity, geometry, biology, and fusion.
- The **simulations** make parts of the theory executable, inspectable, and falsifiable.

## Getting Started

Install the Python dependencies once:

```bash
pip install -r requirements.txt
```

Then, if you want a quick verification pass for the simulation code:

```bash
python -m pytest
```

## 🎯 Sims Gallery (Fully Reproducible)

All simulations listed below are the scripts currently present in `Sims/`. They are pure URP, standalone, and match the results in the paper.  
Just run `pip install -r requirements.txt` once, then:

| Sim | File | What it shows | Command |
|-----|------|---------------|---------|
| **Helium 112-ppm** | `Sims/Helium_variational.py` | Flagship variational result (Z_eff ≈ 1.8366, IP = 24.590 eV) | `python Sims/Helium_variational.py` |
| **Squeezed-Light Negative Energy** | `Sims/squeezed_light_negative_energy.py` | Local ΔS deficits, global S growth, and a bounded negative-energy picture | `python Sims/squeezed_light_negative_energy.py` |
| **QCD Attractor Emergence** | `Sims/qcd_attractor_emergence.py` | 0D points, 1D lines, and 2D domains self-organize from noise | `python Sims/qcd_attractor_emergence.py` |
| **β & G Emergence** | `Sims/beta_g_emergence.py` | The universal β≈0.09 and G≈0.22 parameters self-stabilize under URP dynamics | `python Sims/beta_g_emergence.py` |
| **Multi-Agent Cooperation** | `Sims/multi_agent_cooperation.py` | Graph-based S metrics show how cooperation and shared structure can emerge in networks | `python Sims/multi_agent_cooperation.py` |
| **Transformer S-Functional** | `Sims/transformer_s_functional.py` | Minimal phase-space demo for rigid, creative, hallucination, and collapse regimes | `python Sims/transformer_s_functional.py` |
| **S-Landscape Explorer** | `Sims/s_landscape_explorer.py` | Interactive intuition pump for gradient ascent on an S-shaped landscape | `python Sims/s_landscape_explorer.py` |
| **Biology URP Demon** | `Sims/biology_urp.py` | Minimal-genome cell and enzyme Maxwell's demons maximizing S; validates the Sagawa–Ito information bound ΔI ≤ κ·ΔC | `python Sims/biology_urp.py` |
| **Layerwise Transformer S** | `Sims/layerwise_transformer.py` | Tracks C, I, κ, and S layer-by-layer through a transformer, validating the S^(l+1) ≥ S^(l) hypothesis from Transformer-Dynamics.md §6 | `python Sims/layerwise_transformer.py` |

Every sim saves its plot automatically and prints a clear summary. Clone, run, reproduce — no setup headaches.

## 🧭 S Compass

The S Compass is a **runtime observability and control layer** for AI systems — LLMs, RAG pipelines, agent workflows, and code assistants. It applies the URP S-functional (**S = C + κI**) as a live diagnostic, measuring whether an AI system is producing genuinely useful output or drifting into failure modes.

### What S Compass measures

| Metric | What it captures | Intuition |
|--------|------------------|-----------|
| **C (Distinction)** | Novelty, diversity, and creative differentiation in the output | Is the system generating genuinely new structure, or just echoing its inputs? |
| **I (Integration)** | Coherence, groundedness, citation coverage, and internal consistency | Is the output well-supported by evidence, or making things up? |
| **κ (Capacity)** | Usable system capacity under load — context pressure, latency, tool health | Can the system sustain quality under its current operating conditions? |
| **S = C + κI** | The composite score: novelty + capacity-weighted coherence | The single number summarizing overall system health for this step |

### What S Compass can be used for

- **Hallucination detection**: High C (diverse output) with low I (poor grounding) flags hallucination risk, triggering grounded regeneration policies.
- **Rigidity detection**: Low C with high I indicates the model is parroting retrieval context without adding value, prompting temperature increases.
- **Collapse prevention**: When κ drops (context overload, tool failures, latency spikes), S Compass signals capacity stress before output quality degrades.
- **Quality monitoring**: Track C, I, κ, and S over time across sessions to identify systemic trends, regression, or model degradation.
- **Session-level drift detection**: Monitor S-score trends, regime stability, and transition patterns across a session, with automatic alerts for declining quality (`declining_s`), regime instability, collapse risk, and hallucination drift.
- **Automated intervention**: The policy engine converts scores into actionable recommendations — adjusting temperature, retrieval breadth, citation requirements — without human-in-the-loop delay. Drift-aware policy escalation tightens interventions when session-level trends are concerning.
- **Multi-model comparison**: Run different models or configurations through the same benchmark corpus and compare regime distributions and score profiles.
- **Agent workflow diagnostics**: In multi-step agent systems, S Compass scores each step independently, revealing where in a chain quality breaks down.

### Deployment modes

S Compass operates in three modes, depending on what telemetry the model provider exposes:

| Mode | Available signals | Confidence range | Use case |
|------|-------------------|------------------|----------|
| **Black-box** | Prompt, output, citations, retrieval, tool traces | 0.65 (fixed) | Commercial hosted models (OpenAI, Anthropic, etc.) |
| **Gray-box** | + logprobs, token entropy, relevance scores, tool confidence, decoding instability | 0.65–0.95 (dynamic) | Providers with richer introspection (e.g. logprob access) |
| **White-box** | + attention entropy/variance, head confidence, KV norms, activation sparsity, gradient norms, residual coherence | 0.85–0.99 (dynamic) | Open-weight or locally hosted models (e.g. Llama, Mistral) |

All three modes dynamically adjust confidence based on signal coverage, and the policy engine uses this confidence to tune intervention aggressiveness — more signals mean more decisive responses to detected issues. White-box mode achieves the highest fidelity by combining all gray-box signals with layerwise attention and internal architecture metrics.

### Behavioural regimes

Every scored step is classified into one of four regimes:

| Regime | C | I | κ | Interpretation | Policy response |
|--------|---|---|---|----------------|-----------------|
| **Creative-grounded** | High | Moderate–High | Moderate–High | Healthy: novel and well-supported | No intervention |
| **Hallucination-risk** | High | Low | Any | Diverse but ungrounded output | Require grounded regeneration with citations |
| **Rigid** | Low | High | Moderate–High | Repetitive or retrieval-echoing | Increase temperature to encourage diversity |
| **Collapse** | Low | Low | Low | Degenerate output under system stress | Reduce load and retry |

### Architecture

| Module | Role | Design-doc section |
|--------|------|--------------------|
| `s_compass/schemas.py` | Canonical event envelopes, claims, evidence, scores, policy actions, gray-box and white-box signals | §9, §10, §6.2, §6.3 |
| `s_compass/telemetry.py` | Telemetry normalizer — converts heterogeneous payloads into canonical events | §4.2 |
| `s_compass/estimators.py` | Black-box C, I, κ estimators with `normalize` and `capacity_field` helpers; includes structural repetition and retrieval-echo novelty metrics | §4.3–4.5, §11, §19 |
| `s_compass/estimators_graybox.py` | Gray-box C, I, κ estimators with logprob entropy, relevance quality, contradiction penalty, retrieval overload | §4.3–4.5, §6.2, §19 |
| `s_compass/estimators_whitebox.py` | White-box C, I, κ estimators enriched with per-layer attention entropy/variance, head diversity, activation sparsity, KV norm stress, gradient norm instability, and residual stream coherence | §4.3–4.5, §6.3, §19 |
| `s_compass/scoring.py` | S scoring engine and regime classifier — dispatches to white-box, gray-box, or black-box estimators based on mode; includes template-rigid detection via structural novelty | §4.6, §12 |
| `s_compass/policy.py` | Confidence-aware policy engine with drift-aware escalation — turns scores and session trends into actionable recommendations | §4.7, §4.9 |
| `s_compass/store.py` | In-memory evaluation store for sessions, steps, scores, interventions, drift detection, and regime-transition tracking | §4.8, §4.9 |
| `s_compass/extraction.py` | Claim extraction, evidence linking, and contradiction detection from model outputs | §4.4, §16 |
| `s_compass/graph.py` | Coherence graph builder and structural metrics | §4.4, §8.4 |
| `s_compass/api.py` | REST API — eight endpoints for session, step, graph, window, drift, and policy access | §8, §4.9 |
| `s_compass/gateway.py` | Main entry point tying telemetry → extraction → scoring → policy → store, with white-box and gray-box auto-detection | §4.1, §5 |

### Quick Start

```python
from s_compass import SCompassGateway, StepInput

gw = SCompassGateway()
gw.start_session("sess_001")

# Black-box mode (default): just prompt + output
result = gw.submit_step(StepInput(
    session_id="sess_001",
    prompt="Explain the S Compass architecture.",
    output_text="S Compass is a telemetry and policy layer ...",
))

print(result["scores"])      # {'c': ..., 'i': ..., 'kappa': ..., 's': ...}
print(result["regime"])      # e.g. 'creative-grounded'
print(result["policy"])      # {'action': 'none', 'reason': '...'}
print(result["mode"])        # 'black-box'
print(result["confidence"])  # 0.65
```

```python
# Gray-box mode: supply richer signals for higher-fidelity scoring
from s_compass.schemas import GrayBoxSignals

result = gw.submit_step(StepInput(
    session_id="sess_001",
    prompt="How does URP map onto transformer behaviour?",
    output_text="In a transformer, the S-functional decomposes per layer ...",
    gray_box=GrayBoxSignals(
        logprobs=[-0.5, -1.0, -0.3, -2.0],
        relevance_scores=[0.91, 0.65, 0.40],
        tool_confidence={"search": 0.92},
    ),
))

print(result["mode"])        # 'gray-box' (auto-detected)
print(result["confidence"])  # 0.80+ (dynamic, based on signal coverage)
```

```python
# White-box mode: supply internal architecture signals for highest-fidelity scoring
from s_compass.schemas import GrayBoxSignals, WhiteBoxSignals

result = gw.submit_step(StepInput(
    session_id="sess_001",
    prompt="Describe the layerwise S-functional evolution.",
    output_text="Across layers, C grows as attention entropy increases ...",
    mode="white-box",
    white_box=WhiteBoxSignals(
        attention_entropy=[0.5, 0.6, 0.4, 0.55, 0.65, 0.45],
        attention_variance=[0.05, 0.08, 0.03, 0.06, 0.07, 0.04],
        head_confidence={"h0": 0.85, "h1": 0.70, "h2": 0.92, "h3": 0.60},
        kv_norm=[1.2, 1.5, 1.3, 1.1, 1.4, 1.6],
        activation_sparsity=[0.3, 0.4, 0.35, 0.25, 0.45, 0.38],
        gradient_norm=[0.01, 0.02, 0.015, 0.008, 0.025],
        residual_coherence=0.82,
        layer_count=6,
    ),
    gray_box=GrayBoxSignals(               # optional: combine for maximum coverage
        logprobs=[-0.5, -1.0, -0.3, -2.0],
        relevance_scores=[0.91, 0.65, 0.40],
    ),
))

print(result["mode"])        # 'white-box'
print(result["confidence"])  # 0.85–0.99 (dynamic, based on signal coverage)
```

```python
# Drift detection: monitor session-level trends and get early warnings
drift = gw.get_drift_summary("sess_001")

print(drift["s_trend"])              # slope of S over recent window (+ = improving)
print(drift["regime_transitions"])   # list of regime changes
print(drift["alerts"])               # e.g. ['declining_s', 'collapse_risk']
print(drift["dominant_regime"])      # most common regime in window
print(drift["transition_rate"])      # fraction of steps with regime changes
```

```python
# Drift-aware policy: escalate interventions based on session trends
from s_compass import evaluate_with_drift

policy = evaluate_with_drift(snapshot, drift=drift)
print(policy.action)        # e.g. 'reduce_load_and_retry' if collapse risk detected
print(policy.parameters)    # includes 'stabilise': True when regime is unstable
```

### Running Tests

```bash
# Full test suite (all 409 tests including white-box, gray-box, drift, benchmark, and structural metrics tests)
python -m pytest -v

# Individual test modules
python -m pytest tests/test_s_compass.py tests/test_extraction.py tests/test_graph.py tests/test_api.py -v
python -m pytest tests/test_graybox.py -v      # gray-box estimators, scoring dispatch, API parsing
python -m pytest tests/test_whitebox.py -v     # white-box estimators, scoring dispatch, gateway, API
python -m pytest tests/test_drift.py -v        # drift detection, regime transitions, drift-aware policy
python -m pytest tests/test_benchmark.py -v     # benchmark corpus through the REST API
```

## 📊 API Benchmark

The `benchmarks/` directory contains a curated corpus of 82 scenarios spanning all four behavioural regimes, including gray-box and white-box enriched traces for confidence-aware benchmarking, plus a runner that exercises every REST API endpoint and produces a structured Markdown report.

### Running the Benchmark

```bash
python -m benchmarks.run_api_benchmark                # report to stdout
python -m benchmarks.run_api_benchmark -o REPORT.md   # report to file
```

### What the Benchmark Tests

* **82 human-labelled scenarios** across creative-grounded, hallucination-risk, rigid, and collapse regimes (15 creative, 15 hallucination, 15 rigid, 15 collapse, 18 edge, 4 white-box)
* **10 gray-box benchmark traces** with explicit mode/confidence reporting for traces that supply logprobs, relevance scores, and tool-confidence signals
* **4 white-box benchmark traces** that exercise all attention, KV, gradient, and residual-coherence signal paths at full white-box fidelity (confidence ≥ 0.98)
* **3 drift detection sequences** that exercise session-level trend analysis, regime-transition tracking, and alert generation across multi-step sessions
* **All 8 REST API endpoints**: session start, step submission, session summary, session list, rolling-window stats, drift detection, trace graph, and policy evaluation
* **Per-regime precision, recall, and F1** with a confusion matrix
* **Score distribution analysis** (C, I, κ, S averages by expected regime)
* **Capacity signal validation** (κ varies with context load, latency, tool failures)

### Current Results

**Overall accuracy: 98.8% (81/82 correct regime classifications)**

| Regime | Precision | Recall | F1 |
|--------|-----------|--------|-----|
| Creative-grounded | 1.00 | 0.97 | 0.98 |
| Hallucination-risk | 0.94 | 1.00 | 0.97 |
| Rigid | 1.00 | 1.00 | 1.00 |
| Collapse | 1.00 | 1.00 | 1.00 |

**Interpreting the results:**

- **Rigid detection is perfect** (F1=1.00). The structural repetition detector catches template-style outputs ("The X is Y. The X has Z.") that have high lexical diversity but repetitive sentence structure.
- **Collapse detection is perfect** (F1=1.00). The κ estimator reliably captures context pressure, latency spikes, and tool failures, and degenerate outputs produce low C and I.
- **Hallucination-risk recall is perfect** (1.00). Every hallucination scenario is caught. The one false positive (an edge case where creative output lacks any retrieval context) represents a reasonable design choice: flagging ungrounded novelty.
- **Creative-grounded precision is perfect** (1.00). No false positives — when the system says "creative-grounded", it's always correct.
- **Gray-box mode** consistently produces higher confidence (dynamic, typically 0.80–0.95 depending on signal coverage) and enables more decisive policy interventions.
- **White-box mode** achieves the highest confidence (0.85–0.99 dynamic) by combining layerwise attention entropy, residual-stream coherence, KV norm stress, gradient instability, and all gray-box signals. All four white-box benchmark scenarios are classified correctly.

**Score separation across regimes** confirms that the metrics capture meaningful distinctions:
- Creative-grounded: high C (0.84), moderate I (0.63), full κ (1.00)
- Hallucination-risk: high C (0.85), low I (0.32) — the hallmark signature
- Rigid: moderate C (0.64), higher I (0.62) — integration dominates distinction
- Collapse: all scores depressed, especially κ (0.22) — clear capacity failure

See [benchmarks/REPORT.md](benchmarks/REPORT.md) for the full scenario-by-scenario report, including per-scenario mode/confidence, scores, a confusion matrix, and identified estimator gaps.

### Running Benchmark Tests

```bash
python -m pytest tests/test_benchmark.py -v
```

## Supporting Files

- **[requirements.txt](requirements.txt)** - Python dependencies for the simulations and tests.
- **[visuals/PLACEHOLDER.md](visuals/PLACEHOLDER.md)** - Reserved space for future diagrams and visual explanations.

Contributions and issues welcome — this is the public seed of the Universal Recursion Principle and its surrounding research program.

## Contributing

This framework is actively expanding as new correspondences are found in information thermodynamics, quantum vacuum models, and AI alignment. If you are running simulations, testing the S-functional on neural network representations, or mapping URP to specific domains, pull requests are welcome.

## License
MIT License
