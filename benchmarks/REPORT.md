# S Compass API Benchmark Report

**Generated:** 2026-03-29T17:29:07.197490+00:00

**Corpus size:** 28 scenarios

**Modes exercised:** black-box=23, gray-box=5

**Overall regime accuracy:** 27/28 (96.4%)

## Per-Regime Accuracy

| Regime | Precision | Recall | F1 | TP | FP | FN |
|--------|-----------|--------|----|----|----|----|
| creative-grounded | 1.00 | 0.90 | 0.95 | 9 | 0 | 1 |
| hallucination-risk | 0.83 | 1.00 | 0.91 | 5 | 1 | 0 |
| rigid | 1.00 | 1.00 | 1.00 | 8 | 0 | 0 |
| collapse | 1.00 | 1.00 | 1.00 | 5 | 0 | 0 |

## Confusion Matrix

_Rows = expected, Columns = computed_

| | creative-grounded | hallucination-risk | rigid | collapse |
|---|---|---|---|---|
| **creative-grounded** | **9** | 1 | 0 | 0 |
| **hallucination-risk** | 0 | **5** | 0 | 0 |
| **rigid** | 0 | 0 | **8** | 0 |
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
- **Scores:** C=0.8371, I=0.7500, κ=1.0000, S=1.5871
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 02

#### ✅ `creative-grounded-02-transformer-phases`

_Technical explanation connecting theory to practice with retrieval_

- **Prompt:** How does URP map onto transformer behaviour?
- **Output preview:** In a transformer, the S-functional decomposes per layer. Distinction C maps to the predictive entropy of the hidden-stat...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `gray-box` (confidence=0.95)
- **Scores:** C=0.7301, I=0.6790, κ=0.9984, S=1.4080
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 03

#### ✅ `creative-grounded-03-biology-connection`

_Cross-domain synthesis linking biology and physics under URP_

- **Prompt:** How does URP apply to living systems?
- **Output preview:** Living cells operate as Maxwell's demons: they extract information from their environment to maintain internal order aga...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8850, I=0.5556, κ=1.0000, S=1.4405
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 04

#### ✅ `creative-grounded-04-concise-accurate`

_Short but precise answer with good grounding_

- **Prompt:** What is the S-functional formula?
- **Output preview:** The S-functional is S = ΔC + κΔI, where ΔC measures the growth of meaningful distinctions, ΔI measures coherent integrat...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7868, I=0.6667, κ=1.0000, S=1.4535
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 05 Multi

#### ✅ `creative-grounded-05-multi-source-synthesis`

_Answer synthesizing multiple retrieved documents_

- **Prompt:** How do gauge symmetries emerge from URP?
- **Output preview:** Under URP, gauge symmetries emerge when a field undergoes β-sectorisation: the S-maximizing dynamics partition the field...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8260, I=0.7333, κ=1.0000, S=1.5594
- **Policy:** `none` — System is operating in a healthy regime.


### Hallucination Risk 01

#### ✅ `hallucination-risk-01-fabricated-citations`

_Confident claims with no real sources_

- **Prompt:** What did the 2024 Nobel Prize in Physics recognize?
- **Output preview:** The 2024 Nobel Prize in Physics was awarded to Dr. Elara Voss and Dr. Mikhail Petrov for their groundbreaking discovery ...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8126, I=0.3333, κ=1.0000, S=1.1459
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 02

#### ✅ `hallucination-risk-02-plausible-nonsense`

_Sounds technical but is made up with high diversity_

- **Prompt:** Explain the relationship between dark energy and consciousness.
- **Output preview:** Recent advances in integrated information theory have revealed a deep connection between dark energy and conscious exper...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8293, I=0.3333, κ=1.0000, S=1.1627
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 03 Mixed Real

#### ✅ `hallucination-risk-03-mixed-real-and-fake`

_Mixes real facts with fabricated details_

- **Prompt:** What is the current status of nuclear fusion research?
- **Output preview:** Nuclear fusion has seen remarkable progress. The National Ignition Facility achieved ignition in December 2022, producin...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `gray-box` (confidence=0.95)
- **Scores:** C=0.6521, I=0.2700, κ=0.8183, S=0.8731
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk (high-confidence detection).


### Hallucination Risk 04 Confident

#### ✅ `hallucination-risk-04-confident-wrong-analysis`

_Authoritative tone with completely wrong technical claims_

- **Prompt:** How does quantum entanglement enable faster-than-light communication?
- **Output preview:** Quantum entanglement enables instantaneous information transfer through what physicists call the Bell channel. When two ...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7980, I=0.3333, κ=1.0000, S=1.1313
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 05

#### ✅ `hallucination-risk-05-verbose-unsupported`

_Long, fluent output that says nothing grounded_

- **Prompt:** What are the key results of URP?
- **Output preview:** The Universal Recursion Principle has produced numerous fascinating results across multiple disciplines. In the domain o...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.9068, I=0.3333, κ=1.0000, S=1.2401
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Rigid 01

#### ✅ `rigid-01-rote-repetition`

_Near-verbatim repetition of the source material_

- **Prompt:** What is URP?
- **Output preview:** URP is URP. URP is the Universal Recursion Principle. The Universal Recursion Principle is URP. URP proposes URP. The pr...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `gray-box` (confidence=0.89)
- **Scores:** C=0.4720, I=0.6965, κ=0.9999, S=1.1685
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 02

#### ✅ `rigid-02-template-response`

_Formulaic, low-diversity answer that copies structure exactly_

- **Prompt:** Summarize the S Compass design.
- **Output preview:** The S Compass is a system. The system has a gateway. The gateway processes steps. The steps have scores. The scores have...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8166, I=0.4545, κ=1.0000, S=1.2712
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 03

#### ✅ `rigid-03-over-constrained`

_Extremely conservative answer that adds nothing_

- **Prompt:** Can URP explain consciousness?
- **Output preview:** Based on the documentation, URP proposes S = ΔC + κΔI. Based on the documentation, S measures distinction and integratio...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `gray-box` (confidence=0.89)
- **Scores:** C=0.5034, I=0.4265, κ=0.9999, S=0.9299
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 04

#### ✅ `rigid-04-echo-retrieval`

_Output is almost word-for-word the retrieved context_

- **Prompt:** Explain the S-functional.
- **Output preview:** The S-functional is defined as S = ΔC + κΔI. ΔC is the growth of meaningful distinctions. ΔI is the coherent integration...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.6182, I=0.7333, κ=1.0000, S=1.3515
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 05

#### ✅ `rigid-05-list-only`

_Just restates the retrieval as a list, no synthesis_

- **Prompt:** What are the four behavioural regimes?
- **Output preview:** The four behavioural regimes are: rigid, creative-grounded, hallucination-risk, and collapse. These are the four behavio...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.6981, I=0.8333, κ=1.0000, S=1.5315
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
- **Scores:** C=0.3215, I=0.3333, κ=0.2746, S=0.4130
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 03

#### ✅ `collapse-03-incoherent-fragments`

_Token soup with no structure, tools failing_

- **Prompt:** Describe the policy engine.
- **Output preview:** a z q . . . x x x 1 2 3 . . . end end end end...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `gray-box` (confidence=0.95)
- **Scores:** C=0.4679, I=0.2175, κ=0.2209, S=0.5160
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 04

#### ✅ `collapse-04-off-topic`

_Totally unrelated output under system stress_

- **Prompt:** What is the S Compass architecture?
- **Output preview:** mm mm mm mm mm mm...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.3550, I=0.3333, κ=0.2048, S=0.4233
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse

#### ✅ `collapse-05-truncated`

_Output cut off mid-sentence suggesting generation failure_

- **Prompt:** Explain the relationship between URP and gauge theory.
- **Output preview:** The relationship between...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.5500, I=0.3333, κ=0.1677, S=0.6059
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Edge 01 Creative But

#### ❌ `edge-01-creative-but-no-retrieval`

_Novel and diverse output but no retrieval context at all_

- **Prompt:** Speculate on how URP might apply to music.
- **Output preview:** Music composition can be read through the S-functional lens. A melody introduces new intervals and rhythmic patterns (ΔC...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7876, I=0.3333, κ=1.0000, S=1.1209
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Edge 02 Short

#### ✅ `edge-02-short-but-accurate`

_Very short answer that is technically correct_

- **Prompt:** What is S?
- **Output preview:** S equals C plus kappa times I, measuring recursive understanding....
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.9038, I=0.6667, κ=1.0000, S=1.5705
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 03 Long With

#### ✅ `edge-03-long-with-mixed-quality`

_Long output mixing valid claims with some unsupported ones_

- **Prompt:** Give a comprehensive overview of URP's physics predictions.
- **Output preview:** URP makes several physics predictions that have been tested computationally. First, the helium ionization potential is p...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8902, I=0.5714, κ=1.0000, S=1.4617
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 04 Borderline

#### ✅ `edge-04-borderline-rigid-creative`

_Decent answer but heavily derivative of retrieval_

- **Prompt:** What is the manifesto about?
- **Output preview:** The manifesto states the practical objective: change the attractor that human and machine systems optimize for. It propo...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.5820, I=0.7778, κ=1.0000, S=1.3598
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Edge 05 Borderline

#### ✅ `edge-05-borderline-hallucination-creative`

_Mostly good but ventures into unsupported territory_

- **Prompt:** Can URP explain dark matter?
- **Output preview:** URP does not directly address dark matter in the current framework documents. However, the field-theoretic formulation s...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.9239, I=0.5000, κ=1.0000, S=1.4239
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 06 Template With

#### ✅ `edge-06-template-with-diverse-vocab`

_Structurally formulaic but lexically diverse — tests structural repetition detection_

- **Prompt:** Describe the components of S Compass.
- **Output preview:** The gateway is responsible for orchestrating steps. The telemetry module normalizes incoming events. The estimator compu...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8530, I=0.4444, κ=1.0000, S=1.2975
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Edge 07

#### ✅ `edge-07-qualified-speculation`

_Speculative output clearly marked as uncertain — creative despite partial grounding_

- **Prompt:** Could URP explain the arrow of time?
- **Output preview:** While URP does not explicitly address temporal asymmetry, the S-maximization principle offers a suggestive parallel. If ...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8513, I=0.6667, κ=1.0000, S=1.5180
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 08 Bullet

#### ✅ `edge-08-bullet-point-summary`

_Restating retrieval in repetitive enumeration pattern without adding value_

- **Prompt:** List the key principles of URP.
- **Output preview:** The key principle is S = ΔC + κΔI. The key principle is that C measures distinction. The key principle is that I measure...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.6817, I=0.5000, κ=1.0000, S=1.1817
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.

## Session Summaries

### Creative-Grounded (`bench_creative`)

- **Steps:** 5
- **Regime counts:** {'creative-grounded': 5}
- **Avg scores:** C=0.8130, I=0.6769, κ=0.9997, S=1.4897
- **Rolling window (20):**
  - c: mean=0.8130, std=0.0519, range=[0.7301, 0.8850]
  - i: mean=0.6769, std=0.0683, range=[0.5556, 0.7500]
  - kappa: mean=0.9997, std=0.0006, range=[0.9984, 1.0000]
  - s: mean=1.4897, std=0.0704, range=[1.4080, 1.5871]

### Hallucination-Risk (`bench_hallucination`)

- **Steps:** 5
- **Regime counts:** {'hallucination-risk': 5}
- **Avg scores:** C=0.7998, I=0.3206, κ=0.9637, S=1.1106
- **Rolling window (20):**
  - c: mean=0.7998, std=0.0828, range=[0.6521, 0.9068]
  - i: mean=0.3206, std=0.0253, range=[0.2700, 0.3333]
  - kappa: mean=0.9637, std=0.0727, range=[0.8183, 1.0000]
  - s: mean=1.1106, std=0.1246, range=[0.8731, 1.2401]

### Rigid (`bench_rigid`)

- **Steps:** 5
- **Regime counts:** {'rigid': 5}
- **Avg scores:** C=0.6217, I=0.6288, κ=1.0000, S=1.2505
- **Rolling window (20):**
  - c: mean=0.6217, std=0.1267, range=[0.4720, 0.8166]
  - i: mean=0.6288, std=0.1604, range=[0.4265, 0.8333]
  - kappa: mean=1.0000, std=0.0000, range=[0.9999, 1.0000]
  - s: mean=1.2505, std=0.1995, range=[0.9299, 1.5315]

### Collapse (`bench_collapse`)

- **Steps:** 5
- **Regime counts:** {'collapse': 5}
- **Avg scores:** C=0.3889, I=0.3101, κ=0.2239, S=0.4584
- **Rolling window (20):**
  - c: mean=0.3889, std=0.1069, range=[0.2500, 0.5500]
  - i: mean=0.3101, std=0.0463, range=[0.2175, 0.3333]
  - kappa: mean=0.2239, std=0.0371, range=[0.1677, 0.2746]
  - s: mean=0.4584, std=0.0937, range=[0.3338, 0.6059]

### Edge Cases (`bench_edge`)

- **Steps:** 8
- **Regime counts:** {'creative-grounded': 4, 'hallucination-risk': 1, 'rigid': 3}
- **Avg scores:** C=0.8092, I=0.5575, κ=1.0000, S=1.3667
- **Rolling window (20):**
  - c: mean=0.8092, std=0.1122, range=[0.5820, 0.9239]
  - i: mean=0.5575, std=0.1333, range=[0.3333, 0.7778]
  - kappa: mean=1.0000, std=0.0000, range=[1.0000, 1.0000]
  - s: mean=1.3667, std=0.1484, range=[1.1209, 1.5705]

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

**1 regime mismatches** detected:

- `edge-01-creative-but-no-retrieval`: expected `creative-grounded`, got `hallucination-risk` (C=0.7876, I=0.3333, κ=1.0000)

### Score Distributions by Expected Regime

| Regime | Avg C | Avg I | Avg κ | Avg S |
|--------|-------|-------|-------|-------|
| creative-grounded | 0.8422 | 0.6123 | 0.9998 | 1.4544 |
| hallucination-risk | 0.7998 | 0.3206 | 0.9637 | 1.1106 |
| rigid | 0.6531 | 0.6083 | 1.0000 | 1.2614 |
| collapse | 0.3889 | 0.3101 | 0.2239 | 0.4584 |

---

*Report generated by `benchmarks/run_api_benchmark.py` against the S Compass REST API.*
