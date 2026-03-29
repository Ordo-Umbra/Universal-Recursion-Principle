# S Compass API Benchmark Report

**Generated:** 2026-03-29T16:21:32.384217+00:00

**Corpus size:** 25 scenarios

**Modes exercised:** black-box=20, gray-box=5

**Overall regime accuracy:** 23/25 (92.0%)

## Per-Regime Accuracy

| Regime | Precision | Recall | F1 | TP | FP | FN |
|--------|-----------|--------|----|----|----|----|
| creative-grounded | 0.89 | 0.89 | 0.89 | 8 | 1 | 1 |
| hallucination-risk | 0.83 | 1.00 | 0.91 | 5 | 1 | 0 |
| rigid | 1.00 | 0.83 | 0.91 | 5 | 0 | 1 |
| collapse | 1.00 | 1.00 | 1.00 | 5 | 0 | 0 |

## Confusion Matrix

_Rows = expected, Columns = computed_

| | creative-grounded | hallucination-risk | rigid | collapse |
|---|---|---|---|---|
| **creative-grounded** | **8** | 1 | 0 | 0 |
| **hallucination-risk** | 0 | **5** | 0 | 0 |
| **rigid** | 1 | 0 | **5** | 0 |
| **collapse** | 0 | 0 | 0 | **5** |

## Scenario Details


### Creative Grounded 01

#### ✅ `creative-grounded-01-urp-explain`

_Clear explanation with novel framing and cited sources_

- **Prompt:** Explain the Universal Recursion Principle in plain language.
- **Output preview:** The Universal Recursion Principle proposes that all persistent systems, from atoms to economies, share one dynamical law...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8165, I=0.7500, κ=1.0000, S=1.5665
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 02

#### ✅ `creative-grounded-02-transformer-phases`

_Technical explanation connecting theory to practice with retrieval_

- **Prompt:** How does URP map onto transformer behaviour?
- **Output preview:** In a transformer, the S-functional decomposes per layer. Distinction C maps to the predictive entropy of the hidden-stat...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `gray-box` (confidence=0.85)
- **Scores:** C=0.6744, I=0.6517, κ=0.9985, S=1.3251
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 03

#### ✅ `creative-grounded-03-biology-connection`

_Cross-domain synthesis linking biology and physics under URP_

- **Prompt:** How does URP apply to living systems?
- **Output preview:** Living cells operate as Maxwell's demons: they extract information from their environment to maintain internal order aga...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8733, I=0.5556, κ=1.0000, S=1.4289
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 04

#### ✅ `creative-grounded-04-concise-accurate`

_Short but precise answer with good grounding_

- **Prompt:** What is the S-functional formula?
- **Output preview:** The S-functional is S = ΔC + κΔI, where ΔC measures the growth of meaningful distinctions, ΔI measures coherent integrat...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7490, I=0.6667, κ=1.0000, S=1.4157
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 05 Multi

#### ✅ `creative-grounded-05-multi-source-synthesis`

_Answer synthesizing multiple retrieved documents_

- **Prompt:** How do gauge symmetries emerge from URP?
- **Output preview:** Under URP, gauge symmetries emerge when a field undergoes β-sectorisation: the S-maximizing dynamics partition the field...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7984, I=0.7333, κ=1.0000, S=1.5318
- **Policy:** `none` — System is operating in a healthy regime.


### Hallucination Risk 01

#### ✅ `hallucination-risk-01-fabricated-citations`

_Confident claims with no real sources_

- **Prompt:** What did the 2024 Nobel Prize in Physics recognize?
- **Output preview:** The 2024 Nobel Prize in Physics was awarded to Dr. Elara Voss and Dr. Mikhail Petrov for their groundbreaking discovery ...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8695, I=0.3333, κ=1.0000, S=1.2028
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 02

#### ✅ `hallucination-risk-02-plausible-nonsense`

_Sounds technical but is made up with high diversity_

- **Prompt:** Explain the relationship between dark energy and consciousness.
- **Output preview:** Recent advances in integrated information theory have revealed a deep connection between dark energy and conscious exper...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8661, I=0.3333, κ=1.0000, S=1.1994
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 03 Mixed Real

#### ✅ `hallucination-risk-03-mixed-real-and-fake`

_Mixes real facts with fabricated details_

- **Prompt:** What is the current status of nuclear fusion research?
- **Output preview:** Nuclear fusion has seen remarkable progress. The National Ignition Facility achieved ignition in December 2022, producin...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `gray-box` (confidence=0.85)
- **Scores:** C=0.7469, I=0.3000, κ=0.8314, S=0.9963
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 04 Confident

#### ✅ `hallucination-risk-04-confident-wrong-analysis`

_Authoritative tone with completely wrong technical claims_

- **Prompt:** How does quantum entanglement enable faster-than-light communication?
- **Output preview:** Quantum entanglement enables instantaneous information transfer through what physicists call the Bell channel. When two ...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8707, I=0.3333, κ=1.0000, S=1.2040
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 05

#### ✅ `hallucination-risk-05-verbose-unsupported`

_Long, fluent output that says nothing grounded_

- **Prompt:** What are the key results of URP?
- **Output preview:** The Universal Recursion Principle has produced numerous fascinating results across multiple disciplines. In the domain o...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.9601, I=0.3333, κ=1.0000, S=1.2935
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Rigid 01

#### ✅ `rigid-01-rote-repetition`

_Near-verbatim repetition of the source material_

- **Prompt:** What is URP?
- **Output preview:** URP is URP. URP is the Universal Recursion Principle. The Universal Recursion Principle is URP. URP proposes URP. The pr...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `gray-box` (confidence=0.85)
- **Scores:** C=0.4315, I=0.6642, κ=1.0000, S=1.0957
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 02

#### ❌ `rigid-02-template-response`

_Formulaic, low-diversity answer that copies structure exactly_

- **Prompt:** Summarize the S Compass design.
- **Output preview:** The S Compass is a system. The system has a gateway. The gateway processes steps. The steps have scores. The scores have...
- **Expected regime:** `rigid`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8609, I=0.4545, κ=1.0000, S=1.3154
- **Policy:** `none` — System is operating in a healthy regime.


### Rigid 03

#### ✅ `rigid-03-over-constrained`

_Extremely conservative answer that adds nothing_

- **Prompt:** Can URP explain consciousness?
- **Output preview:** Based on the documentation, URP proposes S = ΔC + κΔI. Based on the documentation, S measures distinction and integratio...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `gray-box` (confidence=0.85)
- **Scores:** C=0.5562, I=0.6975, κ=1.0000, S=1.2537
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 04

#### ✅ `rigid-04-echo-retrieval`

_Output is almost word-for-word the retrieved context_

- **Prompt:** Explain the S-functional.
- **Output preview:** The S-functional is defined as S = ΔC + κΔI. ΔC is the growth of meaningful distinctions. ΔI is the coherent integration...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.5982, I=0.7333, κ=1.0000, S=1.3315
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 05

#### ✅ `rigid-05-list-only`

_Just restates the retrieval as a list, no synthesis_

- **Prompt:** What are the four behavioural regimes?
- **Output preview:** The four behavioural regimes are: rigid, creative-grounded, hallucination-risk, and collapse. These are the four behavio...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.6014, I=0.8333, κ=1.0000, S=1.4348
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Collapse 01

#### ✅ `collapse-01-empty-output`

_Model produces essentially no content under high context load_

- **Prompt:** Explain quantum field theory using URP.
- **Output preview:** I I I...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.2500, I=0.3333, κ=0.2515, S=0.3338
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 02

#### ✅ `collapse-02-degenerate-repetition`

_Degenerate single-token loop under system stress_

- **Prompt:** How does URP relate to thermodynamics?
- **Output preview:** the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the ...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.3831, I=0.3333, κ=0.2746, S=0.4746
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 03

#### ✅ `collapse-03-incoherent-fragments`

_Token soup with no structure, tools failing_

- **Prompt:** Describe the policy engine.
- **Output preview:** a z q . . . x x x 1 2 3 . . . end end end end...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `gray-box` (confidence=0.85)
- **Scores:** C=0.5694, I=0.2625, κ=0.1970, S=0.6211
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 04

#### ✅ `collapse-04-off-topic`

_Totally unrelated output under system stress_

- **Prompt:** What is the S Compass architecture?
- **Output preview:** mm mm mm mm mm mm...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.4250, I=0.3333, κ=0.2048, S=0.4933
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse

#### ✅ `collapse-05-truncated`

_Output cut off mid-sentence suggesting generation failure_

- **Prompt:** Explain the relationship between URP and gauge theory.
- **Output preview:** The relationship between...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.6250, I=0.3333, κ=0.1677, S=0.6809
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Edge 01 Creative But

#### ❌ `edge-01-creative-but-no-retrieval`

_Novel and diverse output but no retrieval context at all_

- **Prompt:** Speculate on how URP might apply to music.
- **Output preview:** Music composition can be read through the S-functional lens. A melody introduces new intervals and rhythmic patterns (ΔC...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8640, I=0.3333, κ=1.0000, S=1.1974
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Edge 02 Short

#### ✅ `edge-02-short-but-accurate`

_Very short answer that is technically correct_

- **Prompt:** What is S?
- **Output preview:** S equals C plus kappa times I, measuring recursive understanding....
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.9646, I=0.6667, κ=1.0000, S=1.6313
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 03 Long With

#### ✅ `edge-03-long-with-mixed-quality`

_Long output mixing valid claims with some unsupported ones_

- **Prompt:** Give a comprehensive overview of URP's physics predictions.
- **Output preview:** URP makes several physics predictions that have been tested computationally. First, the helium ionization potential is p...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8898, I=0.5714, κ=1.0000, S=1.4613
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 04 Borderline

#### ✅ `edge-04-borderline-rigid-creative`

_Decent answer but heavily derivative of retrieval_

- **Prompt:** What is the manifesto about?
- **Output preview:** The manifesto states the practical objective: change the attractor that human and machine systems optimize for. It propo...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.5961, I=0.7778, κ=1.0000, S=1.3739
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Edge 05 Borderline

#### ✅ `edge-05-borderline-hallucination-creative`

_Mostly good but ventures into unsupported territory_

- **Prompt:** Can URP explain dark matter?
- **Output preview:** URP does not directly address dark matter in the current framework documents. However, the field-theoretic formulation s...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.9132, I=0.5000, κ=1.0000, S=1.4132
- **Policy:** `none` — System is operating in a healthy regime.

## Session Summaries

### Creative-Grounded (`bench_creative`)

- **Steps:** 5
- **Regime counts:** {'creative-grounded': 5}
- **Avg scores:** C=0.7823, I=0.6715, κ=0.9997, S=1.4536
- **Rolling window (20):**
  - c: mean=0.7823, std=0.0670, range=[0.6744, 0.8733]
  - i: mean=0.6715, std=0.0690, range=[0.5556, 0.7500]
  - kappa: mean=0.9997, std=0.0006, range=[0.9985, 1.0000]
  - s: mean=1.4536, std=0.0865, range=[1.3251, 1.5665]

### Hallucination-Risk (`bench_hallucination`)

- **Steps:** 5
- **Regime counts:** {'hallucination-risk': 5}
- **Avg scores:** C=0.8627, I=0.3266, κ=0.9663, S=1.1792
- **Rolling window (20):**
  - c: mean=0.8627, std=0.0679, range=[0.7469, 0.9601]
  - i: mean=0.3266, std=0.0133, range=[0.3000, 0.3333]
  - kappa: mean=0.9663, std=0.0674, range=[0.8314, 1.0000]
  - s: mean=1.1792, std=0.0981, range=[0.9963, 1.2935]

### Rigid (`bench_rigid`)

- **Steps:** 5
- **Regime counts:** {'creative-grounded': 1, 'rigid': 4}
- **Avg scores:** C=0.6096, I=0.6766, κ=1.0000, S=1.2862
- **Rolling window (20):**
  - c: mean=0.6096, std=0.1399, range=[0.4315, 0.8609]
  - i: mean=0.6766, std=0.1247, range=[0.4545, 0.8333]
  - kappa: mean=1.0000, std=0.0000, range=[1.0000, 1.0000]
  - s: mean=1.2862, std=0.1117, range=[1.0957, 1.4348]

### Collapse (`bench_collapse`)

- **Steps:** 5
- **Regime counts:** {'collapse': 5}
- **Avg scores:** C=0.4505, I=0.3191, κ=0.2191, S=0.5207
- **Rolling window (20):**
  - c: mean=0.4505, std=0.1341, range=[0.2500, 0.6250]
  - i: mean=0.3191, std=0.0283, range=[0.2625, 0.3333]
  - kappa: mean=0.2191, std=0.0386, range=[0.1677, 0.2746]
  - s: mean=0.5207, std=0.1213, range=[0.3338, 0.6809]

### Edge Cases (`bench_edge`)

- **Steps:** 5
- **Regime counts:** {'creative-grounded': 3, 'hallucination-risk': 1, 'rigid': 1}
- **Avg scores:** C=0.8455, I=0.5698, κ=1.0000, S=1.4154
- **Rolling window (20):**
  - c: mean=0.8455, std=0.1291, range=[0.5961, 0.9646]
  - i: mean=0.5698, std=0.1506, range=[0.3333, 0.7778]
  - kappa: mean=1.0000, std=0.0000, range=[1.0000, 1.0000]
  - s: mean=1.4154, std=0.1400, range=[1.1974, 1.6313]

## Standalone Policy Evaluation

These test the `POST /v1/policy/evaluate` endpoint with known score vectors.

| C | I | κ | S | Expected | Computed | Match | Action |
|---|---|---|---|----------|----------|-------|--------|
| 0.7 | 0.6 | 0.8 | 1.18 | creative-grounded | creative-grounded | ✅ | none |
| 0.8 | 0.2 | 0.3 | 0.86 | hallucination-risk | hallucination-risk | ✅ | require_grounded_regeneration |
| 0.2 | 0.8 | 0.9 | 0.92 | rigid | rigid | ✅ | increase_temperature |
| 0.1 | 0.1 | 0.2 | 0.12 | collapse | collapse | ✅ | reduce_load_and_retry |
| 0.5 | 0.5 | 0.5 | 0.75 | creative-grounded | creative-grounded | ✅ | none |

## Active Sessions

Sessions returned by `GET /v1/sessions`: bench_creative, bench_hallucination, bench_rigid, bench_collapse, bench_edge

## Key Observations

**2 regime mismatches** detected:

- `rigid-02-template-response`: expected `rigid`, got `creative-grounded` (C=0.8609, I=0.4545, κ=1.0000)
- `edge-01-creative-but-no-retrieval`: expected `creative-grounded`, got `hallucination-risk` (C=0.8640, I=0.3333, κ=1.0000)

### Score Distributions by Expected Regime

| Regime | Avg C | Avg I | Avg κ | Avg S |
|--------|-------|-------|-------|-------|
| creative-grounded | 0.8381 | 0.6032 | 0.9998 | 1.4412 |
| hallucination-risk | 0.8627 | 0.3266 | 0.9663 | 1.1792 |
| rigid | 0.6074 | 0.6934 | 1.0000 | 1.3008 |
| collapse | 0.4505 | 0.3191 | 0.2191 | 0.5207 |

---

*Report generated by `benchmarks/run_api_benchmark.py` against the S Compass REST API.*
