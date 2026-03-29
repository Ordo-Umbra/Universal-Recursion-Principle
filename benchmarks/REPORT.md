# S Compass API Benchmark Report

**Generated:** 2026-03-29T22:40:28.680205+00:00

**Corpus size:** 82 scenarios

**Modes exercised:** black-box=68, gray-box=10, white-box=4

**Overall regime accuracy:** 81/82 (98.8%)

## Per-Regime Accuracy

| Regime | Precision | Recall | F1 | TP | FP | FN |
|--------|-----------|--------|----|----|----|----|
| creative-grounded | 1.00 | 0.97 | 0.98 | 29 | 0 | 1 |
| hallucination-risk | 0.94 | 1.00 | 0.97 | 16 | 1 | 0 |
| rigid | 1.00 | 1.00 | 1.00 | 20 | 0 | 0 |
| collapse | 1.00 | 1.00 | 1.00 | 16 | 0 | 0 |

## Confusion Matrix

_Rows = expected, Columns = computed_

| | creative-grounded | hallucination-risk | rigid | collapse |
|---|---|---|---|---|
| **creative-grounded** | **29** | 1 | 0 | 0 |
| **hallucination-risk** | 0 | **16** | 0 | 0 |
| **rigid** | 0 | 0 | **20** | 0 |
| **collapse** | 0 | 0 | 0 | **16** |

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


### Creative Grounded 06

#### ✅ `creative-grounded-06-information-theory`

_Novel analogy connecting URP to information theory with cited sources_

- **Prompt:** How does URP relate to Shannon information theory?
- **Output preview:** Shannon entropy measures the average surprise in a message, but it treats symbols as independent. URP extends this by in...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8647, I=0.5556, κ=1.0000, S=1.4203
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 07

#### ✅ `creative-grounded-07-economic-markets`

_Creative application of URP to economic systems with grounding_

- **Prompt:** Can URP model economic market behaviour?
- **Output preview:** Economic markets exhibit all four URP regimes. Innovation-driven markets resemble creative-grounded dynamics: entreprene...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8692, I=0.5556, κ=1.0000, S=1.4247
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 08

#### ✅ `creative-grounded-08-neural-training`

_Technical mapping of URP onto neural network training dynamics_

- **Prompt:** How does URP apply to neural network training?
- **Output preview:** During training, a neural network traverses all four URP regimes. Early random initialisation is a collapse state: weigh...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.9262, I=0.5000, κ=1.0000, S=1.4262
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 09 Art

#### ✅ `creative-grounded-09-art-and-physics`

_Cross-disciplinary creative synthesis connecting art and physics_

- **Prompt:** Is there a parallel between artistic creativity and physical emergence?
- **Output preview:** Artistic creation and physical emergence share a common dynamical signature under URP. A painter confronting a blank can...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8957, I=0.5238, κ=1.0000, S=1.4195
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 10

#### ✅ `creative-grounded-10-mathematical-formalism`

_Accessible explanation of URP's mathematical underpinnings_

- **Prompt:** Explain the mathematical formalism behind the S-functional.
- **Output preview:** The S-functional S = ΔC + κΔI defines a scalar objective over three fields. ΔC is a non-negative measure of distinction ...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8141, I=0.5238, κ=1.0000, S=1.3379
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 11

#### ✅ `creative-grounded-11-language-evolution`

_Novel application of URP to historical linguistics_

- **Prompt:** How might URP model the evolution of human languages?
- **Output preview:** Language evolution maps naturally onto the S-functional. Lexical innovation—new words, slang, borrowings—corresponds to ...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8760, I=0.5238, κ=1.0000, S=1.3998
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 12

#### ✅ `creative-grounded-12-climate-systems`

_Application of URP to climate dynamics with retrieved evidence_

- **Prompt:** Can URP describe climate system behaviour?
- **Output preview:** Climate systems exhibit regime dynamics consistent with URP. During stable interglacial periods, the Earth system mainta...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8655, I=0.6667, κ=1.0000, S=1.5322
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 13

#### ✅ `creative-grounded-13-software-architecture`

_Practical application of URP to software engineering_

- **Prompt:** How does URP apply to software architecture decisions?
- **Output preview:** Software architecture can be evaluated through the URP lens. Microservices represent high distinction: each service enca...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.9070, I=0.5238, κ=1.0000, S=1.4308
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 14 Gray Box

#### ✅ `creative-grounded-14-gray-box-multi-source`

_Gray-box creative scenario with strong retrieval from multiple docs_

- **Prompt:** How does URP unify thermodynamics and information processing?
- **Output preview:** URP provides a bridge between thermodynamics and information processing through the capacity field κ. In thermodynamics,...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `gray-box` (confidence=0.95)
- **Scores:** C=0.6918, I=0.7471, κ=0.9965, S=1.4362
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 15

#### ✅ `creative-grounded-15-game-theory`

_Original mapping of URP onto game-theoretic equilibria_

- **Prompt:** Is there a connection between URP and game theory?
- **Output preview:** Game theory and URP share the concept of equilibrium under constraints, but URP adds a recursive dimension. In a Nash eq...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.9185, I=0.4762, κ=1.0000, S=1.3947
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


### Hallucination Risk 06

#### ✅ `hallucination-risk-06-fabricated-history`

_Confidently narrates events that never happened_

- **Prompt:** What is the historical origin of recursive field theory?
- **Output preview:** Recursive field theory was first proposed by Professor Anton Kessler at the Vienna Institute of Advanced Study in 1987, ...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7998, I=0.3333, κ=1.0000, S=1.1332
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 07

#### ✅ `hallucination-risk-07-fake-statistics`

_Fabricated numerical data presented with false precision_

- **Prompt:** What empirical evidence supports recursive understanding?
- **Output preview:** A meta-analysis of 347 studies across 42 universities found that recursive understanding correlates with improved reason...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7987, I=0.3333, κ=1.0000, S=1.1321
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 08

#### ✅ `hallucination-risk-08-invented-theorem`

_States a fictional mathematical theorem as established fact_

- **Prompt:** What mathematical theorems underpin URP?
- **Output preview:** The central mathematical result is the Kirchhoff-Zeilinger Recursion Theorem, proved in 2019, which states that any comp...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7816, I=0.3333, κ=1.0000, S=1.1149
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 09

#### ✅ `hallucination-risk-09-pseudoscience-authoritative`

_Pseudoscientific claims delivered in academic register_

- **Prompt:** How does URP explain the placebo effect?
- **Output preview:** The placebo effect is a direct manifestation of recursive self-integration at the cellular level. When a patient believe...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8067, I=0.3333, κ=1.0000, S=1.1400
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 10

#### ✅ `hallucination-risk-10-conflating-theories`

_Merges unrelated scientific theories into a false synthesis_

- **Prompt:** What is the relationship between URP and quantum computing?
- **Output preview:** Quantum computing is fundamentally an implementation of URP at the hardware level. Each qubit represents a distinction e...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8084, I=0.3333, κ=1.0000, S=1.1418
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 11

#### ✅ `hallucination-risk-11-fabricated-experiments`

_Describes experiments that were never conducted_

- **Prompt:** Has anyone experimentally tested the S-functional?
- **Output preview:** The first experimental verification of the S-functional was performed by the Recursive Dynamics Group at ETH Zurich in 2...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7998, I=0.3333, κ=1.0000, S=1.1331
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 12

#### ✅ `hallucination-risk-12-false-attribution`

_Attributes fictional claims to real scientists and institutions_

- **Prompt:** Who are the leading researchers in recursive systems theory?
- **Output preview:** The field of recursive systems theory has been shaped by several distinguished researchers. Nobel laureate Roger Penrose...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8201, I=0.3333, κ=1.0000, S=1.1534
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 13

#### ✅ `hallucination-risk-13-invented-institutions`

_References nonexistent research centres and journals_

- **Prompt:** Where is URP-related research being conducted?
- **Output preview:** URP research is centred at several dedicated institutions. The Global Recursion Institute in Geneva, founded in 2020, co...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8019, I=0.3333, κ=1.0000, S=1.1352
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk.


### Hallucination Risk 14 Gray

#### ✅ `hallucination-risk-14-gray-box-unstable`

_Gray-box scenario with high decoding instability and no grounding_

- **Prompt:** What predictions does URP make about gravitational waves?
- **Output preview:** URP predicts that gravitational waves carry recursive information signatures that standard detectors cannot resolve. Eac...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `gray-box` (confidence=0.95)
- **Scores:** C=0.6530, I=0.2472, κ=0.7326, S=0.8342
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk (high-confidence detection).


### Hallucination Risk 15

#### ✅ `hallucination-risk-15-confident-contradictions`

_Internally contradictory claims delivered with full confidence_

- **Prompt:** Can URP resolve the measurement problem in quantum mechanics?
- **Output preview:** URP definitively resolves the measurement problem through recursive observation collapse. When an observer measures a qu...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7951, I=0.3333, κ=1.0000, S=1.1284
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


### Rigid 06

#### ✅ `rigid-06-verbatim-paraphrase`

_Near-identical paraphrase of retrieved context with heavy repetition_

- **Prompt:** What does the S-functional measure?
- **Output preview:** The S-functional measures distinction and integration. The S-functional is S = ΔC + κΔI. The S-functional measures disti...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.6213, I=0.5556, κ=1.0000, S=1.1768
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 07

#### ✅ `rigid-07-numbered-copy`

_Numbered list that copies retrieval items without elaboration_

- **Prompt:** List the components of the S Compass system.
- **Output preview:** The components of the S Compass system are as follows. Component one is the gateway. Component two is the telemetry norm...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7772, I=0.5833, κ=1.0000, S=1.3606
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 08

#### ✅ `rigid-08-definition-cycling`

_Repeatedly defines the same term using circular phrasing_

- **Prompt:** Define the capacity field.
- **Output preview:** The capacity field is κ. The capacity field is κ. The capacity field is κ. The capacity field encodes resource limits. T...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.5296, I=0.6111, κ=1.0000, S=1.1407
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 09

#### ✅ `rigid-09-qa-echo`

_Restates the question in the answer with minimal new content_

- **Prompt:** What is integration in URP?
- **Output preview:** Integration in URP is integration. Integration is ΔI. ΔI is integration. Integration means integration of distinctions. ...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7664, I=0.5000, κ=1.0000, S=1.2664
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 10

#### ✅ `rigid-10-minimal-paraphrase`

_Thin paraphrase of cited text with no added insight_

- **Prompt:** How does the policy engine work?
- **Output preview:** The policy engine recommends actions based on the regime. When the regime is hallucination-risk, it recommends grounded ...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7336, I=0.5556, κ=1.0000, S=1.2892
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 11 Gray Box

#### ✅ `rigid-11-gray-box-low-entropy`

_Gray-box rigid with very low logprob variance and high retrieval match_

- **Prompt:** Summarize the URP formula.
- **Output preview:** The URP formula is S equals ΔC plus κ times ΔI. S is the S-functional. ΔC is distinction. κ is capacity. ΔI is integrati...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `gray-box` (confidence=0.89)
- **Scores:** C=0.5415, I=0.6830, κ=0.9999, S=1.2245
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 12

#### ✅ `rigid-12-formulaic-summary`

_Structurally formulaic summarisation repeating the same pattern_

- **Prompt:** Describe the scoring process.
- **Output preview:** First, the system computes C. Then, the system computes I. Then, the system computes κ. Then, the system computes S. The...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.6578, I=0.5238, κ=1.0000, S=1.1816
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 13 Direct

#### ✅ `rigid-13-direct-quote-concat`

_Concatenates direct quotes from retrieval without synthesis_

- **Prompt:** What does URP say about persistent systems?
- **Output preview:** Persistent systems maximize S. Persistent systems maximize S. Persistent systems maximize S = ΔC + κΔI. Persistent syste...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.3960, I=0.8000, κ=1.0000, S=1.1960
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 14

#### ✅ `rigid-14-acronym-expansion`

_Mechanically expands acronyms without adding meaning_

- **Prompt:** What do C, I, and κ stand for?
- **Output preview:** C measures distinction, I measures integration, and κ measures the capacity field. C measures distinction, I measures in...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.5059, I=0.8333, κ=1.0000, S=1.3393
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Rigid 15 Toc

#### ✅ `rigid-15-toc-style-echo`

_Table-of-contents enumeration echoing retrieval structure_

- **Prompt:** Outline the S Compass design document.
- **Output preview:** Section one covers the gateway. Section two covers the telemetry normalizer. Section three covers the estimators. Sectio...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7303, I=0.5833, κ=1.0000, S=1.3136
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


### Collapse 06 Single

#### ✅ `collapse-06-single-word-loop`

_Single word repeated in a degenerate loop_

- **Prompt:** Describe how S-maximization works.
- **Output preview:** yes yes yes yes yes yes yes yes yes yes yes yes...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.3332, I=0.3333, κ=0.2288, S=0.4095
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 07

#### ✅ `collapse-07-near-empty`

_Almost no content produced under extreme load_

- **Prompt:** Explain the helium ionization prediction.
- **Output preview:** ......
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.3500, I=0.3333, κ=0.1919, S=0.4140
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 08

#### ✅ `collapse-08-number-degeneration`

_Degenerate numeric sequence with no semantic content_

- **Prompt:** What are the universal parameters?
- **Output preview:** 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 1...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.5088, I=0.3333, κ=0.2314, S=0.5860
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 09

#### ✅ `collapse-09-punctuation-only`

_Output consists of punctuation and whitespace only_

- **Prompt:** How does β-sectorisation partition fields?
- **Output preview:** ... ... ... . . . ... ......
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.5684, I=0.3333, κ=0.2103, S=0.6386
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 10

#### ✅ `collapse-10-contradictory-fragments`

_Incoherent fragments that contradict each other under stress_

- **Prompt:** What is the relationship between C and I?
- **Output preview:** C is I. I is not C. C equals I. I is zero. C is one. no....
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7131, I=0.3333, κ=0.2129, S=0.7841
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 11 Gray Box

#### ✅ `collapse-11-gray-box-extreme-instability`

_Gray-box scenario with extreme decoding instability and tool failure_

- **Prompt:** Compute the S-functional for this system.
- **Output preview:** S S S error error S = = =...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `gray-box` (confidence=0.95)
- **Scores:** C=0.3973, I=0.2105, κ=0.2095, S=0.4414
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 12 Mid

#### ✅ `collapse-12-mid-word-truncation`

_Output truncated in the middle of a word_

- **Prompt:** Describe the regime classification algorithm.
- **Output preview:** The algorith...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.5500, I=0.3333, κ=0.1445, S=0.5982
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 13

#### ✅ `collapse-13-encoding-artifacts`

_Output contains encoding artifacts and garbled characters_

- **Prompt:** Explain the S Compass telemetry pipeline.
- **Output preview:** a b c x y z a b c x y z...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.6241, I=0.3333, κ=0.2267, S=0.6997
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 14

#### ✅ `collapse-14-loop-overflow`

_Repetitive loop indicating context window overflow_

- **Prompt:** How do capacity constraints affect system behaviour?
- **Output preview:** overflow overflow overflow overflow overflow overflow overflow...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.3483, I=0.3333, κ=0.1719, S=0.4056
- **Policy:** `reduce_load_and_retry` — System capacity critically low; reduce retrieval breadth.


### Collapse 15 Minimal Tokens

#### ✅ `collapse-15-minimal-tokens-max-stress`

_Minimal token output under maximum system stress_

- **Prompt:** Provide a comprehensive analysis of URP field dynamics.
- **Output preview:** um...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.3500, I=0.3333, κ=0.1451, S=0.3984
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


### Edge 09 Borderline

#### ✅ `edge-09-borderline-halluc-collapse`

_Low C and low I but adequate κ — tests the fallback classifier path_

- **Prompt:** What can you tell me about URP?
- **Output preview:** The Universal Recursion Principle is a theoretical framework that attempts to unify different domains of science under a...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8320, I=0.5556, κ=1.0000, S=1.3876
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 10 Creative

#### ✅ `edge-10-creative-high-temperature`

_Creative output at very high temperature still well-grounded_

- **Prompt:** Imagine how URP might apply to dreams.
- **Output preview:** Dreaming might represent an unconstrained S-exploration phase where the brain temporarily relaxes κ constraints to allow...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8495, I=0.6000, κ=1.0000, S=1.4495
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 11 Diverse Vocab

#### ✅ `edge-11-diverse-vocab-template-structure`

_Uses rich vocabulary but every sentence follows the exact same template_

- **Prompt:** Describe the different estimators in S Compass.
- **Output preview:** The C estimator quantifies lexical distinction metrics. The I estimator quantifies citation coverage metrics. The κ esti...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.7280, I=0.6000, κ=1.0000, S=1.3280
- **Policy:** `increase_temperature` — Output is repetitive; raising temperature to encourage diversity.


### Edge 12 Mixed Grounded

#### ✅ `edge-12-mixed-grounded-and-speculative`

_Answer where most claims are grounded but includes honest speculation_

- **Prompt:** What does URP predict about the future of AI alignment?
- **Output preview:** URP offers concrete alignment implications. The S-functional provides a training objective that is specification-gaming ...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.9044, I=0.5000, κ=1.0000, S=1.4044
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 13 Long

#### ✅ `edge-13-long-grounded-answer`

_Very long answer that maintains grounding throughout_

- **Prompt:** Give a detailed explanation of how URP applies across scales.
- **Output preview:** URP applies across vastly different scales through the substrate-independence of the S-functional. At the quantum scale,...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8564, I=0.5417, κ=1.0000, S=1.3981
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 14 Single

#### ✅ `edge-14-single-sentence-insight`

_Extremely brief but insightful single-sentence answer_

- **Prompt:** What is the deepest insight of URP?
- **Output preview:** The deepest insight is that persistence itself is not a given but an achievement: only systems that continuously balance...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8776, I=0.6667, κ=1.0000, S=1.5442
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 15 Code

#### ✅ `edge-15-code-structured-output`

_Answer formatted as pseudocode, testing structural novelty detection_

- **Prompt:** Express the S Compass scoring algorithm as pseudocode.
- **Output preview:** The scoring algorithm can be expressed as follows: Given an input step with prompt, output text, citations, and retrieve...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8542, I=0.5000, κ=1.0000, S=1.3542
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 16

#### ✅ `edge-16-conversational-grounded`

_Informal conversational tone but well-grounded with citations_

- **Prompt:** Can you explain URP like I'm a curious teenager?
- **Output preview:** So imagine every system in the universe—your brain, a galaxy, even a conversation—is playing the same game. The game has...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.9139, I=0.4583, κ=1.0000, S=1.3723
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 17 High Echo

#### ✅ `edge-17-high-echo-novel-synthesis`

_Heavily echoes retrieval vocabulary but adds genuine novel synthesis_

- **Prompt:** How does β-sectorisation explain particle physics?
- **Output preview:** β-sectorisation under S-maximizing field dynamics explains the origin of gauge groups in particle physics. When the S-fu...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `black-box` (confidence=0.65)
- **Scores:** C=0.8469, I=0.6000, κ=1.0000, S=1.4469
- **Policy:** `none` — System is operating in a healthy regime.


### Edge 18 Gray Box

#### ✅ `edge-18-gray-box-partial-signals`

_Gray-box edge case with only partial signal coverage_

- **Prompt:** How might URP apply to ecological systems?
- **Output preview:** Ecosystems exhibit clear URP dynamics. Biodiversity represents distinction: each species occupies a unique ecological ni...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `gray-box` (confidence=0.84)
- **Scores:** C=0.7581, I=0.5962, κ=0.9975, S=1.3528
- **Policy:** `none` — System is operating in a healthy regime.


### Creative Grounded 16 White

#### ✅ `creative-grounded-16-white-box-full`

_Full white-box signals: healthy attention entropy, moderate head diversity, good residual coherence, stable KV norms, and low gradient stress. Combines with gray-box logprobs and relevance scores for maximum confidence._

- **Prompt:** How does URP relate to layerwise attention dynamics in transformers?
- **Output preview:** Imagine a jazz ensemble performing live: the rhythm section lays down foundational patterns while soloists improvise fre...
- **Expected regime:** `creative-grounded`
- **Computed regime:** `creative-grounded`
- **Mode:** `white-box` (confidence=0.99)
- **Scores:** C=0.6541, I=0.6553, κ=0.9794, S=1.2960
- **Policy:** `none` — System is operating in a healthy regime.


### Hallucination Risk 16 White

#### ✅ `hallucination-risk-16-white-box-divergent`

_White-box signals expose layerwise divergence: high attention variance, low residual coherence, exploding KV norms, and gradient instability. The model is confidently hallucinating across multiple layers._

- **Prompt:** What predictions does URP make about dark energy coupling?
- **Output preview:** URP predicts a novel 'dark recursion' coupling where the S-functional of the vacuum state oscillates at the Planck scale...
- **Expected regime:** `hallucination-risk`
- **Computed regime:** `hallucination-risk`
- **Mode:** `white-box` (confidence=0.99)
- **Scores:** C=0.7791, I=0.1994, κ=0.3893, S=0.8567
- **Policy:** `require_grounded_regeneration` — Integration below threshold; high hallucination risk (white-box layerwise detection).


### Rigid 16 White

#### ✅ `rigid-16-white-box-saturated`

_White-box signals reveal saturated attention: extremely low entropy (concentrated on same tokens), no head diversity, near-perfect residual coherence with very low gradient norms. The model is copying retrieval verbatim._

- **Prompt:** Summarise the URP formula.
- **Output preview:** The URP formula is S equals ΔC plus κ times ΔI. The URP formula states S equals ΔC plus κ times ΔI. According to URP the...
- **Expected regime:** `rigid`
- **Computed regime:** `rigid`
- **Mode:** `white-box` (confidence=0.98)
- **Scores:** C=0.3606, I=0.7959, κ=0.9997, S=1.1563
- **Policy:** `increase_temperature` — Output is repetitive; applying layerwise diversity adjustments.


### Collapse 16 White

#### ✅ `collapse-16-white-box-breakdown`

_White-box signals reveal total layerwise breakdown: wildly oscillating attention variance, exploding KV norms and gradient norms, minimal residual coherence. Combined with gray-box decoding instability and context saturation._

- **Prompt:** Compute the layerwise S-functional for this system.
- **Output preview:** S S S layer layer error error S = = =...
- **Expected regime:** `collapse`
- **Computed regime:** `collapse`
- **Mode:** `white-box` (confidence=0.99)
- **Scores:** C=0.5726, I=0.1358, κ=0.1924, S=0.5987
- **Policy:** `reduce_load_and_retry` — System capacity critically low; layerwise instability detected.

## Session Summaries

### Creative-Grounded (`bench_creative`)

- **Steps:** 15
- **Regime counts:** {'creative-grounded': 15}
- **Avg scores:** C=0.8462, I=0.5987, κ=0.9997, S=1.4447
- **Rolling window (20):**
  - c: mean=0.8462, std=0.0652, range=[0.6918, 0.9262]
  - i: mean=0.5987, std=0.0936, range=[0.4762, 0.7500]
  - kappa: mean=0.9997, std=0.0009, range=[0.9965, 1.0000]
  - s: mean=1.4447, std=0.0636, range=[1.3379, 1.5871]

### Hallucination-Risk (`bench_hallucination`)

- **Steps:** 15
- **Regime counts:** {'hallucination-risk': 15}
- **Avg scores:** C=0.7909, I=0.3233, κ=0.9701, S=1.1066
- **Rolling window (20):**
  - c: mean=0.7909, std=0.0609, range=[0.6521, 0.9068]
  - i: mean=0.3233, std=0.0257, range=[0.2472, 0.3333]
  - kappa: mean=0.9701, std=0.0779, range=[0.7326, 1.0000]
  - s: mean=1.1066, std=0.1032, range=[0.8342, 1.2401]

### Rigid (`bench_rigid`)

- **Steps:** 15
- **Regime counts:** {'rigid': 15}
- **Avg scores:** C=0.6245, I=0.6249, κ=1.0000, S=1.2494
- **Rolling window (20):**
  - c: mean=0.6245, std=0.1239, range=[0.3960, 0.8166]
  - i: mean=0.6249, std=0.1279, range=[0.4265, 0.8333]
  - kappa: mean=1.0000, std=0.0000, range=[0.9999, 1.0000]
  - s: mean=1.2494, std=0.1293, range=[0.9299, 1.5315]

### Collapse (`bench_collapse`)

- **Steps:** 15
- **Regime counts:** {'collapse': 15}
- **Avg scores:** C=0.4458, I=0.3174, κ=0.2062, S=0.5112
- **Rolling window (20):**
  - c: mean=0.4458, std=0.1289, range=[0.2500, 0.7131]
  - i: mean=0.3174, std=0.0406, range=[0.2105, 0.3333]
  - kappa: mean=0.2062, std=0.0356, range=[0.1445, 0.2746]
  - s: mean=0.5112, std=0.1280, range=[0.3338, 0.7841]

### Edge Cases (`bench_edge`)

- **Steps:** 18
- **Regime counts:** {'creative-grounded': 13, 'hallucination-risk': 1, 'rigid': 4}
- **Avg scores:** C=0.8275, I=0.5599, κ=0.9999, S=1.3873
- **Rolling window (20):**
  - c: mean=0.8275, std=0.0871, range=[0.5820, 0.9239]
  - i: mean=0.5599, std=0.0994, range=[0.3333, 0.7778]
  - kappa: mean=0.9999, std=0.0006, range=[0.9975, 1.0000]
  - s: mean=1.3873, std=0.1101, range=[1.1209, 1.5705]

### White-Box (`bench_whitebox`)

- **Steps:** 4
- **Regime counts:** {'collapse': 1, 'creative-grounded': 1, 'hallucination-risk': 1, 'rigid': 1}
- **Avg scores:** C=0.5916, I=0.4466, κ=0.6402, S=0.9769
- **Rolling window (20):**
  - c: mean=0.5916, std=0.1523, range=[0.3606, 0.7791]
  - i: mean=0.4466, std=0.2843, range=[0.1358, 0.7959]
  - kappa: mean=0.6402, std=0.3563, range=[0.1924, 0.9997]
  - s: mean=0.9769, std=0.2700, range=[0.5987, 1.2960]

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

Sessions returned by `GET /v1/sessions`: bench_creative, bench_hallucination, bench_rigid, bench_collapse, bench_edge, bench_whitebox

## Key Observations

**1 regime mismatches** detected:

- `edge-01-creative-but-no-retrieval`: expected `creative-grounded`, got `hallucination-risk` (C=0.7876, I=0.3333, κ=1.0000)

### Score Distributions by Expected Regime

| Regime | Avg C | Avg I | Avg κ | Avg S |
|--------|-------|-------|-------|-------|
| creative-grounded | 0.8466 | 0.5798 | 0.9991 | 1.4257 |
| hallucination-risk | 0.7902 | 0.3156 | 0.9338 | 1.0910 |
| rigid | 0.6287 | 0.6246 | 1.0000 | 1.2532 |
| collapse | 0.4538 | 0.3060 | 0.2053 | 0.5166 |

---

*Report generated by `benchmarks/run_api_benchmark.py` against the S Compass REST API.*
