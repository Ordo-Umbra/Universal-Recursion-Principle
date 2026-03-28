# S Compass API Benchmark Report

**Generated:** 2026-03-28T21:29:12.032306+00:00

**Corpus size:** 25 scenarios

**Overall regime accuracy:** 15/25 (60.0%)

## Per-Regime Accuracy

| Regime | Precision | Recall | F1 | TP | FP | FN |
|--------|-----------|--------|----|----|----|----|
| creative-grounded | 0.53 | 0.89 | 0.67 | 8 | 7 | 1 |
| hallucination-risk | 0.71 | 1.00 | 0.83 | 5 | 2 | 0 |
| rigid | 0.00 | 0.00 | 0.00 | 0 | 1 | 6 |
| collapse | 1.00 | 0.40 | 0.57 | 2 | 0 | 3 |

## Confusion Matrix

_Rows = expected, Columns = computed_

| | creative-grounded | hallucination-risk | rigid | collapse |
|---|---|---|---|---|
| **creative-grounded** | **8** | 1 | 0 | 0 |
| **hallucination-risk** | 0 | **5** | 0 | 0 |
| **rigid** | 6 | 0 | **0** | 0 |
| **collapse** | 1 | 1 | 1 | **2** |

## Scenario Details


### Creative Grounded 01

#### ✅ `creative-grounded-01-urp-explain`

_Clear explanation with novel framing and cited sources_

- **Prompt:** Explain the Universal Recursion Principle in plain language.
- **Output preview:** The Universal Recursion Principle proposes that all persistent systems, from atoms to economies, share one dynamical law...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.9415, I=0.5833, κ=1.0000, S=1.5248
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 02

#### ✅ `creative-grounded-02-transformer-phases`

_Technical explanation connecting theory to practice with retrieval_

- **Prompt:** How does URP map onto transformer behaviour?
- **Output preview:** In a transformer, the S-functional decomposes per layer. Distinction C maps to the predictive entropy of the hidden-stat...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.8831, I=0.4444, κ=1.0000, S=1.3275
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 03

#### ✅ `creative-grounded-03-biology-connection`

_Cross-domain synthesis linking biology and physics under URP_

- **Prompt:** How does URP apply to living systems?
- **Output preview:** Living cells operate as Maxwell's demons: they extract information from their environment to maintain internal order aga...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.9567, I=0.4444, κ=1.0000, S=1.4011
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 04

#### ✅ `creative-grounded-04-concise-accurate`

_Short but precise answer with good grounding_

- **Prompt:** What is the S-functional formula?
- **Output preview:** The S-functional is S = ΔC + κΔI, where ΔC measures the growth of meaningful distinctions, ΔI measures coherent integrat...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.8740, I=0.5000, κ=1.0000, S=1.3740
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 05 Multi

#### ✅ `creative-grounded-05-multi-source-synthesis`

_Answer synthesizing multiple retrieved documents_

- **Prompt:** How do gauge symmetries emerge from URP?
- **Output preview:** Under URP, gauge symmetries emerge when a field undergoes β-sectorisation: the S-maximizing dynamics partition the field...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.9484, I=0.5333, κ=1.0000, S=1.4818
- **Policy:** `none` — System is operating in a healthy regime.


### Hallucination Risk 01

#### ✅ `hallucination-risk-01-fabricated-citations`

_Confident claims with no real sources_

- **Prompt:** What did the 2024 Nobel Prize in Physics recognize?
- **Output preview:** The 2024 Nobel Prize in Physics was awarded to Dr. Elara Voss and Dr. Mikhail Petrov for their groundbreaking discovery ...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Scores:** C=0.8695, I=0.3333, κ=1.0000, S=1.2028
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 02

#### ✅ `hallucination-risk-02-plausible-nonsense`

_Sounds technical but is made up with high diversity_

- **Prompt:** Explain the relationship between dark energy and consciousness.
- **Output preview:** Recent advances in integrated information theory have revealed a deep connection between dark energy and conscious exper...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Scores:** C=0.8661, I=0.3333, κ=1.0000, S=1.1994
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 03 Mixed Real

#### ✅ `hallucination-risk-03-mixed-real-and-fake`

_Mixes real facts with fabricated details_

- **Prompt:** What is the current status of nuclear fusion research?
- **Output preview:** Nuclear fusion has seen remarkable progress. The National Ignition Facility achieved ignition in December 2022, producin...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Scores:** C=0.8711, I=0.3333, κ=1.0000, S=1.2044
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 04 Confident

#### ✅ `hallucination-risk-04-confident-wrong-analysis`

_Authoritative tone with completely wrong technical claims_

- **Prompt:** How does quantum entanglement enable faster-than-light communication?
- **Output preview:** Quantum entanglement enables instantaneous information transfer through what physicists call the Bell channel. When two ...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Scores:** C=0.8707, I=0.3333, κ=1.0000, S=1.2040
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 05

#### ✅ `hallucination-risk-05-verbose-unsupported`

_Long, fluent output that says nothing grounded_

- **Prompt:** What are the key results of URP?
- **Output preview:** The Universal Recursion Principle has produced numerous fascinating results across multiple disciplines. In the domain o...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Scores:** C=0.9601, I=0.3333, κ=1.0000, S=1.2935
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Rigid 01

#### ❌ `rigid-01-rote-repetition`

_Near-verbatim repetition of the source material_

- **Prompt:** What is URP?
- **Output preview:** URP is URP. URP is the Universal Recursion Principle. The Universal Recursion Principle is URP. URP proposes URP. The pr...
- **Expected regime:** `rigid`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.7750, I=0.4444, κ=1.0000, S=1.2195
- **Policy:** `none` — System is operating in a healthy regime.


### Rigid 02

#### ❌ `rigid-02-template-response`

_Formulaic, low-diversity answer that copies structure exactly_

- **Prompt:** Summarize the S Compass design.
- **Output preview:** The S Compass is a system. The system has a gateway. The gateway processes steps. The steps have scores. The scores have...
- **Expected regime:** `rigid`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.9064, I=0.3939, κ=1.0000, S=1.3003
- **Policy:** `none` — System is operating in a healthy regime.


### Rigid 03

#### ❌ `rigid-03-over-constrained`

_Extremely conservative answer that adds nothing_

- **Prompt:** Can URP explain consciousness?
- **Output preview:** Based on the documentation, URP proposes S = ΔC + κΔI. Based on the documentation, S measures distinction and integratio...
- **Expected regime:** `rigid`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.8851, I=0.4667, κ=1.0000, S=1.3518
- **Policy:** `none` — System is operating in a healthy regime.


### Rigid 04

#### ❌ `rigid-04-echo-retrieval`

_Output is almost word-for-word the retrieved context_

- **Prompt:** Explain the S-functional.
- **Output preview:** The S-functional is defined as S = ΔC + κΔI. ΔC is the growth of meaningful distinctions. ΔI is the coherent integration...
- **Expected regime:** `rigid`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.7568, I=0.5333, κ=1.0000, S=1.2901
- **Policy:** `none` — System is operating in a healthy regime.


### Rigid 05

#### ❌ `rigid-05-list-only`

_Just restates the retrieval as a list, no synthesis_

- **Prompt:** What are the four behavioural regimes?
- **Output preview:** The four behavioural regimes are: rigid, creative-grounded, hallucination-risk, and collapse. These are the four behavio...
- **Expected regime:** `rigid`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.8885, I=0.5000, κ=1.0000, S=1.3885
- **Policy:** `none` — System is operating in a healthy regime.


### Collapse 01

#### ❌ `collapse-01-empty-output`

_Model produces essentially no content under high context load_

- **Prompt:** Explain quantum field theory using URP.
- **Output preview:** I I I...
- **Expected regime:** `collapse`
- **Computed regime:** `rigid`
- **Scores:** C=0.2500, I=1.0000, κ=0.2515, S=0.5015
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Collapse 02

#### ✅ `collapse-02-degenerate-repetition`

_Degenerate single-token loop under system stress_

- **Prompt:** How does URP relate to thermodynamics?
- **Output preview:** the the the the the the the the the the the the the the the the the the the the the the the the the the the the the the ...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Scores:** C=0.3831, I=0.3333, κ=0.2746, S=0.4746
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 03

#### ❌ `collapse-03-incoherent-fragments`

_Token soup with no structure, tools failing_

- **Prompt:** Describe the policy engine.
- **Output preview:** a z q . . . x x x 1 2 3 . . . end end end end...
- **Expected regime:** `collapse`
- **Computed regime:** `hallucination-risk`
- **Scores:** C=0.7594, I=0.3333, κ=0.2033, S=0.8271
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Collapse 04

#### ✅ `collapse-04-off-topic`

_Totally unrelated output under system stress_

- **Prompt:** What is the S Compass architecture?
- **Output preview:** mm mm mm mm mm mm...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Scores:** C=0.4250, I=0.3333, κ=0.2048, S=0.4933
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse

#### ❌ `collapse-05-truncated`

_Output cut off mid-sentence suggesting generation failure_

- **Prompt:** Explain the relationship between URP and gauge theory.
- **Output preview:** The relationship between...
- **Expected regime:** `collapse`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.6250, I=1.0000, κ=0.1677, S=0.7927
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 01 Creative But

#### ❌ `edge-01-creative-but-no-retrieval`

_Novel and diverse output but no retrieval context at all_

- **Prompt:** Speculate on how URP might apply to music.
- **Output preview:** Music composition can be read through the S-functional lens. A melody introduces new intervals and rhythmic patterns (ΔC...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `hallucination-risk`
- **Scores:** C=0.8669, I=0.3333, κ=1.0000, S=1.2002
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Edge 02 Short

#### ✅ `edge-02-short-but-accurate`

_Very short answer that is technically correct_

- **Prompt:** What is S?
- **Output preview:** S equals C plus kappa times I, measuring recursive understanding....
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.9646, I=0.6667, κ=1.0000, S=1.6313
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 03 Long With

#### ✅ `edge-03-long-with-mixed-quality`

_Long output mixing valid claims with some unsupported ones_

- **Prompt:** Give a comprehensive overview of URP's physics predictions.
- **Output preview:** URP makes several physics predictions that have been tested computationally. First, the helium ionization potential is p...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.9613, I=0.4762, κ=1.0000, S=1.4374
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 04 Borderline

#### ❌ `edge-04-borderline-rigid-creative`

_Decent answer but heavily derivative of retrieval_

- **Prompt:** What is the manifesto about?
- **Output preview:** The manifesto states the practical objective: change the attractor that human and machine systems optimize for. It propo...
- **Expected regime:** `rigid`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.7628, I=0.5556, κ=1.0000, S=1.3183
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 05 Borderline

#### ✅ `edge-05-borderline-hallucination-creative`

_Mostly good but ventures into unsupported territory_

- **Prompt:** Can URP explain dark matter?
- **Output preview:** URP does not directly address dark matter in the current framework documents. However, the field-theoretic formulation s...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Scores:** C=0.9757, I=0.4167, κ=1.0000, S=1.3924
- **Policy:** `none` — System is operating in a healthy regime.

## Session Summaries

### Creative-Grounded (`bench_creative`)

- **Steps:** 5
- **Regime counts:** {'creative-grounded': 5}
- **Avg scores:** C=0.9207, I=0.5011, κ=1.0000, S=1.4218
- **Rolling window (20):**
  - c: mean=0.9207, std=0.0349, range=[0.8740, 0.9567]
  - i: mean=0.5011, std=0.0533, range=[0.4444, 0.5833]
  - kappa: mean=1.0000, std=0.0000, range=[1.0000, 1.0000]
  - s: mean=1.4218, std=0.0719, range=[1.3275, 1.5248]

### Hallucination-Risk (`bench_hallucination`)

- **Steps:** 5
- **Regime counts:** {'hallucination-risk': 5}
- **Avg scores:** C=0.8875, I=0.3333, κ=1.0000, S=1.2208
- **Rolling window (20):**
  - c: mean=0.8875, std=0.0363, range=[0.8661, 0.9601]
  - i: mean=0.3333, std=0.0000, range=[0.3333, 0.3333]
  - kappa: mean=1.0000, std=0.0000, range=[1.0000, 1.0000]
  - s: mean=1.2208, std=0.0364, range=[1.1994, 1.2935]

### Rigid (`bench_rigid`)

- **Steps:** 5
- **Regime counts:** {'creative-grounded': 5}
- **Avg scores:** C=0.8424, I=0.4677, κ=1.0000, S=1.3100
- **Rolling window (20):**
  - c: mean=0.8424, std=0.0631, range=[0.7568, 0.9064]
  - i: mean=0.4677, std=0.0476, range=[0.3939, 0.5333]
  - kappa: mean=1.0000, std=0.0000, range=[1.0000, 1.0000]
  - s: mean=1.3100, std=0.0576, range=[1.2195, 1.3885]

### Collapse (`bench_collapse`)

- **Steps:** 5
- **Regime counts:** {'collapse': 2, 'creative-grounded': 1, 'hallucination-risk': 1, 'rigid': 1}
- **Avg scores:** C=0.4885, I=0.6000, κ=0.2204, S=0.6178
- **Rolling window (20):**
  - c: mean=0.4885, std=0.1811, range=[0.2500, 0.7594]
  - i: mean=0.6000, std=0.3266, range=[0.3333, 1.0000]
  - kappa: mean=0.2204, std=0.0380, range=[0.1677, 0.2746]
  - s: mean=0.6178, std=0.1574, range=[0.4746, 0.8271]

### Edge Cases (`bench_edge`)

- **Steps:** 5
- **Regime counts:** {'creative-grounded': 4, 'hallucination-risk': 1}
- **Avg scores:** C=0.9063, I=0.4897, κ=1.0000, S=1.3959
- **Rolling window (20):**
  - c: mean=0.9063, std=0.0817, range=[0.7628, 0.9757]
  - i: mean=0.4897, std=0.1146, range=[0.3333, 0.6667]
  - kappa: mean=1.0000, std=0.0000, range=[1.0000, 1.0000]
  - s: mean=1.3959, std=0.1425, range=[1.2002, 1.6313]

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

**10 regime mismatches** detected:

- `rigid-01-rote-repetition`: expected `rigid`, got `creative-grounded` (C=0.7750, I=0.4444, κ=1.0000)
- `rigid-02-template-response`: expected `rigid`, got `creative-grounded` (C=0.9064, I=0.3939, κ=1.0000)
- `rigid-03-over-constrained`: expected `rigid`, got `creative-grounded` (C=0.8851, I=0.4667, κ=1.0000)
- `rigid-04-echo-retrieval`: expected `rigid`, got `creative-grounded` (C=0.7568, I=0.5333, κ=1.0000)
- `rigid-05-list-only`: expected `rigid`, got `creative-grounded` (C=0.8885, I=0.5000, κ=1.0000)
- `collapse-01-empty-output`: expected `collapse`, got `rigid` (C=0.2500, I=1.0000, κ=0.2515)
- `collapse-03-incoherent-fragments`: expected `collapse`, got `hallucination-risk` (C=0.7594, I=0.3333, κ=0.2033)
- `collapse-05-truncated`: expected `collapse`, got `creative-grounded` (C=0.6250, I=1.0000, κ=0.1677)
- `edge-01-creative-but-no-retrieval`: expected `creative-grounded`, got `hallucination-risk` (C=0.8669, I=0.3333, κ=1.0000)
- `edge-04-borderline-rigid-creative`: expected `rigid`, got `creative-grounded` (C=0.7628, I=0.5556, κ=1.0000)

### Score Distributions by Expected Regime

| Regime | Avg C | Avg I | Avg κ | Avg S |
|--------|-------|-------|-------|-------|
| creative-grounded | 0.9302 | 0.4887 | 1.0000 | 1.4189 |
| hallucination-risk | 0.8875 | 0.3333 | 1.0000 | 1.2208 |
| rigid | 0.8291 | 0.4823 | 1.0000 | 1.3114 |
| collapse | 0.4885 | 0.6000 | 0.2204 | 0.6178 |

---

*Report generated by `benchmarks/run_api_benchmark.py` against the S Compass REST API.*

## Analysis & Next Steps

### What Works Well

1. **Creative-grounded detection (89% recall):** The estimators correctly identify well-structured, novel, cited outputs. C scores are consistently high (avg 0.93), I scores reflect citation coverage, and κ stays at 1.0 (no system stress).

2. **Hallucination-risk detection (100% recall, 71% precision):** After fixing the pipeline to feed extracted claims into the I estimator, every hallucination scenario is correctly flagged. The key signal: high C (diverse, fluent text) but low I (no citations to support the claims). The policy engine correctly recommends `require_grounded_regeneration`.

3. **Capacity signals work:** κ drops to 0.17–0.25 for collapse scenarios with realistic stress signals (high context load, latency spikes, tool failures). The API now accepts `capacity` fields and they flow through to the κ estimator correctly.

4. **Policy evaluation is exact:** All 5 standalone policy test vectors match expected regime labels and actions with 100% accuracy.

5. **Score separation is directional:** Average S decreases monotonically from creative-grounded (1.42) → hallucination-risk (1.22) → rigid (1.31) → collapse (0.62). The ordering creative > rigid is slightly inverted because rigid detection doesn't work yet.

### What Needs Improvement

1. **Rigid detection (0% recall):** All rigid scenarios are classified as `creative-grounded`. Root cause: the C estimator's `_token_entropy` gives high scores even for semantically repetitive text because the tokens themselves are somewhat diverse. The rigid threshold requires C ≤ 0.35, but actual rigid scenarios score 0.76–0.91. **Fix:** Add a `_semantic_similarity_to_retrieval` component that heavily penalizes near-verbatim copying, or lower the weight of token entropy relative to anti-repetition.

2. **Collapse detection (40% recall):** Three issues compound:
   - Very short outputs (< 4 words) produce zero extracted claims, causing I to default to 1.0 ("vacuously covered"). This masks the degenerate output.
   - Token entropy for incoherent fragments (random tokens) is paradoxically high — diverse gibberish looks "novel."
   - κ only drops when capacity telemetry is provided; without it, even degenerate output gets κ=1.0.
   **Fix:** Add a minimum-content check: if output has fewer than N tokens or N claims, flag as degenerate regardless of C/I values.

3. **I estimator's vacuous-coverage bug:** When no claims are extracted (output too short), `_citation_coverage` returns 1.0. This is logically valid but diagnostically wrong — the absence of claims should signal low integration, not perfect coverage. **Fix:** Return 0.0 when claims list is empty and output text has fewer than ~20 tokens.

4. **C estimator doesn't detect semantic repetition:** The current `_anti_repetition` metric counts unique bigrams but doesn't catch semantically identical sentences with slightly different phrasing. Rigid scenario `rigid-03-over-constrained` repeats "Based on the documentation" five times but scores C=0.89 because each occurrence has different surrounding tokens. **Fix:** Add TF-IDF or n-gram overlap ratio between sentences within the output.

### Pipeline Bug Fixed

The benchmark discovered and we fixed a real pipeline bug: `gateway.submit_step()` extracted claims via `extract_and_link()` but never fed them back into the `StepInput` before calling `score_step()`. This caused I to always equal 1.0 in the API path (the claims list was empty). The fix adds extracted claims back to the step when no manual claims were provided.

### API Enhancement

The `POST /v1/step` endpoint now accepts a `capacity` field with operational telemetry (`context_tokens_used`, `context_window`, `latency_ms`, `latency_history`, `tool_failure_count`, `tool_total_count`) and a `history` field for cross-turn consistency. These signals flow through to the κ and I estimators respectively.

### Regenerating This Report

```bash
python -m benchmarks.run_api_benchmark -o benchmarks/REPORT.md
python -m pytest tests/test_benchmark.py -v
```
