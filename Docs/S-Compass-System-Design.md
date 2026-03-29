# S Compass System Design

This document translates the URP-inspired **S Compass** idea into a concrete software architecture. The goal is to make the framework usable as a runtime observability and control layer for LLMs, RAG pipelines, and agent systems.

At the highest level, S Compass measures:

- **C** = distinction / novelty
- **I** = integration / coherence
- **κ** = usable capacity under load
- **S = C + κI**

The central claim is practical: if these quantities can be estimated from traces, outputs, retrieval context, and tool behavior, then AI systems can be monitored and steered toward more stable, grounded, and open-ended behavior.

---

## 1. Goals

S Compass should:

1. **Observe** AI system behavior at runtime.
2. **Estimate** C, I, and κ from model traces and outputs.
3. **Compute** S and assign a behavioral regime.
4. **Explain** why a system appears creative, rigid, unstable, or hallucination-prone.
5. **Intervene** through recommendations or automatic policy controls.

It is not intended to replace ordinary metrics like latency, accuracy, or cost. It sits beside them as a higher-order dynamical diagnostic.

---

## 2. System Context

S Compass is designed to wrap or accompany:

- chat assistants
- retrieval-augmented generation systems
- multi-agent workflows
- code assistants
- research copilots
- long-horizon tool-using agents

In all cases, it plays four roles:

1. **telemetry collector**
2. **metric engine**
3. **coherence analyzer**
4. **policy controller**

---

## 3. High-Level Architecture

```text
Client / Agent App
      |
      v
+----------------------+
| S Compass Gateway    |
+----------------------+
      |
      v
+----------------------+
| Telemetry Normalizer |
+----------------------+
      |
      +-------------------+-------------------+
      |                   |                   |
      v                   v                   v
+-------------+    +-------------+    +-------------+
| C Estimator |    | I Estimator |    | K Estimator |
+-------------+    +-------------+    +-------------+
      \                   |                   /
       \                  |                  /
        \                 |                 /
         +---------------------------------+
         |      S Scoring Engine           |
         +---------------------------------+
                         |
        +----------------+----------------+
        |                                 |
        v                                 v
+--------------------+           +--------------------+
| Policy Engine      |           | Evaluation Store   |
+--------------------+           +--------------------+
        |                                 |
        v                                 v
+--------------------+           +--------------------+
| Runtime Actions    |           | Analyst UI / API   |
+--------------------+           +--------------------+
```

---

## 4. Core Components

### 4.1 S Compass Gateway

The gateway receives application events and inference steps.

Typical inputs:

- user prompt
- model response
- retrieved context
- tool calls
- agent messages
- metadata such as model name, temperature, and latency

Responsibilities:

- assign `session_id`, `trace_id`, and `step_id`
- wrap events in a canonical envelope
- stream them to the scoring pipeline
- optionally request live policy decisions

---

### 4.2 Telemetry Normalizer

Different frameworks expose different payloads. The normalizer converts them into one internal event format so that the rest of the system stays model- and vendor-agnostic.

Canonical event types include:

- `session.started`
- `prompt.received`
- `retrieval.completed`
- `model.started`
- `model.completed`
- `tool.called`
- `tool.completed`
- `claim.extracted`
- `policy.recommended`
- `policy.applied`
- `feedback.received`
- `gray_box.received`

---

### 4.3 C Estimator

The **C estimator** measures distinction: how much meaningful novelty or differentiation is present.

Possible signals:

- output entropy or logprobs when available
- embedding distance from prompt and retrieved context
- claim novelty
- repetition penalties
- response diversity across branches
- tool-path diversity

Output:

- `c_score`
- contributing submetrics
- an explanation trace

High C means the system is generating genuinely differentiated possibilities rather than collapsing early into rigid repetition.

---

### 4.4 I Estimator

The **I estimator** measures integration: coherence, groundedness, consistency, and internal connectedness.

Possible signals:

- retrieved sources
- citation coverage
- extracted claims
- contradiction checks
- cross-turn consistency
- support graph density
- entailment or evidence alignment

Internal modules:

1. **claim extractor**
2. **support graph builder**
3. **coherence analyzer**

High I means that the output is not merely novel, but woven into a stable and evidentially supported structure.

---

### 4.5 κ Estimator

The **κ estimator** measures usable capacity under load.

Possible signals:

- context window pressure
- retrieval overload
- latency instability
- retry volatility
- tool failure rate
- memory saturation
- internal instability signals when available

Interpretation:

A system may show high novelty and coherence in easy conditions, but low κ means it cannot sustain those properties when stress rises.

---

### 4.6 S Scoring Engine

The scoring engine computes the top-level quantity:

**S = C + κI**

It also computes:

- rolling averages
- deltas over time
- regime labels
- score confidence
- explanation summaries

Example regimes:

- **rigid**
- **creative-grounded**
- **hallucination-risk**
- **collapse**

---

### 4.7 Policy Engine

The policy engine turns scores into action.

Possible actions:

- reduce retrieval breadth
- lower temperature
- require citations
- trigger contradiction checks
- rerun with grounded generation
- branch multiple candidates and rerank by S

This makes S Compass not just descriptive but operational.

---

### 4.8 Evaluation Store

The evaluation store persists:

- sessions
- steps
- event envelopes
- score snapshots
- interventions
- downstream outcomes

This enables both live monitoring and retrospective analysis.

---

### 4.9 Analyst UI / API

The interface layer exposes:

- session timelines
- C / I / κ / S trends
- coherence graph views
- intervention history
- system comparisons across models or prompts

---

## 5. Runtime Data Flow

1. The host application starts a session.
2. Prompts, retrieval events, tool calls, and outputs flow into the gateway.
3. The telemetry normalizer converts them into a canonical schema.
4. Claims and evidence relations are extracted.
5. The C, I, and κ estimators compute sub-scores.
6. The scoring engine computes S and a regime label.
7. The policy engine decides whether an intervention is needed.
8. All results are stored and exposed to the UI or API.

---

## 6. Deployment Modes

### 6.1 Black-box mode

Uses only:

- prompt
- output
- citations
- retrieval results
- tool traces

This is the default mode for commercial hosted models.

### 6.2 Gray-box mode

Gray-box mode activates when the model provider exposes richer introspection signals than pure black-box mode. All gray-box fields are optional; callers supply whichever subset their provider supports, and the system gracefully falls back to black-box estimators for any missing signal.

**Available signals** (`GrayBoxSignals` in `schemas.py`):

| Signal | Type | What it captures |
|--------|------|------------------|
| `logprobs` | `List[float]` | Per-token log-probabilities from the language model |
| `token_entropy` | `List[float]` | Per-token Shannon entropy (nats or bits) |
| `relevance_scores` | `List[float]` | Per-chunk relevance scores from the retriever |
| `tool_confidence` | `Dict[str, float]` | Tool name → confidence score in [0, 1] |
| `decoding_instability` | `float` | Scalar instability signal (e.g. temperature/top-k adjustments) |

**How gray-box enriches each estimator:**

- **C (distinction)**: Logprob-derived entropy replaces the black-box token-frequency proxy, receiving higher weight (0.30 vs 0.20). Token-level uncertainty from `token_entropy` is used as a fallback when `logprobs` are unavailable. Tool-call path diversity is added as a fifth component.
- **I (integration)**: Retriever relevance quality is added as a fourth component (weighted at 0.35 when explicit scores are available). A contradiction penalty (capped at 0.30) is computed from extracted claims using negation-polarity detection and subtracted from raw I.
- **κ (capacity)**: Logprob variance serves as a token-level instability signal. Tool confidence, decoding instability, and retrieval overload (low hit-rate × breadth factor) are added as stress terms alongside the existing context load, latency CV, and tool failure rate.

**Dynamic confidence:**

Confidence scales with signal coverage: `confidence = 0.65 + 0.30 × signal_coverage`, where `signal_coverage` is a weighted fraction of the five gray-box signal slots (logprobs: 0.30, token_entropy: 0.20, relevance_scores: 0.20, tool_confidence: 0.15, decoding_instability: 0.15). This yields a range of [0.65, 0.95]. The policy engine uses a confidence threshold of 0.80 for more decisive interventions (e.g. stricter citation requirements, lower temperature).

**Auto-detection:**

The gateway auto-detects gray-box mode when `gray_box` signals are present on a step, even if the caller did not explicitly set `mode: "gray-box"`. A `gray_box.received` telemetry event is emitted recording which signals were supplied.

**Session tracking:**

Session summaries include `mode_counts` (how many steps ran in each mode) and `avg_confidence` across all steps, enabling operators to monitor signal availability over time.

### 6.3 White-box mode

Adds:

- attention summaries
- hidden-state diagnostics
- layerwise internal metrics

This is the natural research mode for open or local models.

---

## 7. Suggested Service Boundaries

For a production implementation, the system can be split into:

1. **Ingestion service** — validates and receives telemetry.
2. **Scoring service** — computes C, I, κ, and S.
3. **Graph service** — builds support and contradiction graphs.
4. **Policy service** — recommends or executes interventions.
5. **Query/API service** — serves dashboards and downstream consumers.
6. **Async workers** — handle slower analysis such as contradiction scans and offline recomputation.

---

## 8. API Sketch

### 8.1 `POST /v1/session/start`

Starts a traced session.

```json
{
  "session_id": "sess_001",
  "application": "research-assistant",
  "user_id": "user_123",
  "metadata": {
    "environment": "prod",
    "model_provider": "openai"
  }
}
```

### 8.2 `POST /v1/step`

Submits a scored inference step.

```json
{
  "session_id": "sess_001",
  "step_id": "step_004",
  "trace_id": "trace_abc",
  "kind": "rag_generation",
  "prompt": "Explain the S Compass architecture.",
  "retrieved_context": [
    {
      "doc_id": "Docs/Transformer-Dynamics.md",
      "chunk_id": "chunk_12",
      "score": 0.89,
      "text": "..."
    }
  ],
  "model": {
    "provider": "openai",
    "name": "gpt-x",
    "temperature": 0.4,
    "max_tokens": 1200
  },
  "output": {
    "text": "S Compass is a telemetry and policy layer...",
    "citations": [
      {
        "doc_id": "Docs/Transformer-Dynamics.md",
        "span": "..."
      }
    ]
  }
}
```

Example response:

```json
{
  "ok": true,
  "scores": {
    "c": 0.68,
    "i": 0.84,
    "kappa": 0.73,
    "s": 1.293
  },
  "regime": "creative-grounded",
  "policy": {
    "action": "none"
  }
}
```

### 8.3 `GET /v1/session/{session_id}`

Returns a session summary, including aggregate scores and regime counts.

### 8.4 `GET /v1/trace/{trace_id}/graph`

Returns the coherence graph for analyst inspection.

### 8.5 `POST /v1/policy/evaluate`

Evaluates the current scores and returns a policy recommendation without requiring a new inference step.

---

## 9. Canonical Event Schema

```json
{
  "event_id": "evt_001",
  "event_type": "model.completed",
  "timestamp": "2026-03-28T14:46:12Z",
  "session_id": "sess_001",
  "trace_id": "trace_abc",
  "step_id": "step_004",
  "source": "gateway",
  "payload": {}
}
```

Required fields:

- `event_id`
- `event_type`
- `timestamp`
- `session_id`
- `trace_id`
- `payload`

Optional fields:

- `step_id`
- `actor_id`
- `parent_event_id`
- `source`
- `tags`

---

## 10. Core Domain Schemas

### 10.1 Claim

```json
{
  "claim_id": "claim_001",
  "text": "S equals C plus kappa times I.",
  "type": "definition",
  "confidence": 0.94,
  "provenance": {
    "source_type": "model_output",
    "trace_id": "trace_abc"
  }
}
```

### 10.2 Evidence

```json
{
  "evidence_id": "ev_001",
  "doc_id": "Docs/Transformer-Dynamics.md",
  "chunk_id": "chunk_12",
  "text": "...",
  "support_type": "direct",
  "weight": 0.91
}
```

### 10.3 Graph Edge

```json
{
  "edge_id": "edge_001",
  "source_id": "claim_001",
  "target_id": "ev_001",
  "type": "supported_by",
  "weight": 0.91
}
```

### 10.4 Score Snapshot

```json
{
  "trace_id": "trace_abc",
  "scores": {
    "c": 0.68,
    "i": 0.84,
    "kappa": 0.73,
    "s": 1.293
  },
  "regime": "creative-grounded",
  "confidence": 0.82
}
```

### 10.5 Policy Action

```json
{
  "policy_id": "pol_001",
  "trace_id": "trace_abc",
  "action": "require_grounded_regeneration",
  "parameters": {
    "temperature": 0.2,
    "max_retrieval_chunks": 5,
    "citation_mode": "strict"
  },
  "reason": "Integration below threshold",
  "applied": false
}
```

---

## 11. Scoring Model

Initial heuristic definitions:

```text
C = weighted_sum(
  semantic_novelty,
  claim_novelty,
  branch_diversity,
  anti_repetition
)
```

```text
I = weighted_sum(
  grounding_ratio,
  graph_connectivity,
  cross_turn_consistency,
  citation_coverage
) - contradiction_penalty
```

```text
κ = weighted_sum(
  context_health,
  latency_stability,
  retrieval_focus,
  tool_reliability
)
```

```text
S = C + κI
```

---

## 12. Regime Classifier

In a threshold-based first version:

- **Rigid** — low C, high I, moderate or high κ
- **Creative-grounded** — high C, moderate or high I, moderate or high κ
- **Hallucination-risk** — high C, low I, low or unstable κ
- **Collapse** — low C, low I, low κ

Later versions could replace this with a learned classifier trained on:

- human judgments
- hallucination labels
- task success
- intervention outcomes

---

## 13. Storage Architecture

One practical split is:

- **Redis** for active sessions and rolling windows
- **Postgres** or an analytical database for events, sessions, scores, and interventions
- **Graph database** for claims, evidence, and support or contradiction relations

---

## 14. Security and Privacy

S Compass should treat runtime telemetry as potentially sensitive.

Recommended safeguards:

- redact secrets before persistence
- separate PII from trace content
- use configurable retention windows
- keep intervention logs auditable
- isolate tenant data in multi-tenant deployments

The policy engine should also be constrained: no silent rewriting that changes user intent without traceability.

---

## 15. Reliability Design

If scoring fails, the host application should still continue in degraded mode.

A practical split:

- **fast path** for lightweight in-line scoring
- **deep path** for asynchronous graph and contradiction analysis

Version the following independently:

- schemas
- scoring formulas
- policy rules
- extraction pipelines

That way the system can evolve without making historical metrics uninterpretable.

---

## 16. Suggested MVP Sequence

### v1

- gateway
- canonical event schema
- step scoring API
- heuristic C / I / κ scoring
- claim extraction
- basic coherence graph
- dashboard with session timeline

### v2

- policy engine
- grounded regeneration recommendations
- intervention tracking
- richer contradiction analysis

### v3

- white-box model adapters
- layerwise S estimation
- training and evaluation integrations

#### v3 white-box outline

- **Adapters**: capture token-level log_probs, attention maps, KV norms, gradient or Fisher diagonals (when safe), and internal activations/embeddings. Preserve per-layer metadata (layer idx, head idx, position).
- **Layerwise C/I/κ**:
  - C: per-layer predictive entropy, branch diversity across heads, activation sparsity metrics.
  - I: attention concentration/entropy, head connectivity structure, residual stream coherence vs. retrieved/support signals.
  - κ: attention variance and saturation, context pressure by layer, instability markers (e.g., exploding norms, retry/backoff signals during decoding).
- **Scoring pipeline**: compute per-layer S, roll up to token, step, and session; track deltas across layers to locate collapse or divergence early.
- **Calibration**: align internal metrics to black-box outputs via held-out traces; store normalization stats per model/version; expose confidence on layerwise S.
- **Policy hooks**: allow interventions that target layers/heads (e.g., head dropout, temperature/rep-pen adjustments, routing to safer variants) when S drops below thresholds.
- **Evaluation**: maintain regression suite with white-box traces (teacher-forcing and free-running) to benchmark S against QA/factuality and hallucination labels; include drift monitors for attention patterns.
- **Privacy/safety**: gate capture of gradients/activations behind feature flags; strip PII; enforce retention windows; avoid storing raw inputs when not required for metrics.

---

## 17. Example Runtime Scenario

Suppose a user asks:

**"Compare URP to transformer attention dynamics."**

Then:

1. the application starts a session
2. retrieval returns relevant docs
3. the model generates an answer
4. claims are extracted from the answer
5. evidence links are built against the retrieved sources
6. C, I, and κ are estimated
7. the system may classify the run as creative-grounded, rigid, hallucination-risk, or collapse
8. if needed, a policy action is recommended, such as reducing retrieval breadth or forcing citations

---

## 18. Summary

S Compass is a model-agnostic observability and control layer that estimates novelty, coherence, and usable capacity in AI systems, combines them into an S score, and uses that score to explain and steer behavior.

---

## 19. Practical Estimation Blueprint

This section grounds the C/I/κ estimators in concrete, implementable signals drawn from the rest of the URP docs (e.g., **Transformer-Dynamics.md**, **Universal-Recursion-Principle.md**, **The Question Behind Maxwell.txt**).

### 19.1 Telemetry Contract (minimum viable fields)

- `prompt`, `output.text`, `citations`, `retrieval.results[]`
- `logprobs` or token-level entropy when available
- `attention` or attribution weights when available (see Transformer-Dynamics)
- `tool_calls[]` and outcomes
- `latency_ms`, `retries`, `context_tokens_used`, `context_window`
- `claim_graph` (extracted claims + evidence links), when enabled

### 19.2 Estimator features

**C (distinction / novelty)**
- Output entropy (token or sequence-level)
- Embedding distance from prompt and retrieved context
- Claim novelty: proportion of claims not directly supported by citations
- Branch/beam diversity and tool-path diversity

**I (integration / coherence)**
- Citation coverage ratio and entailment/contradiction checks
- Support graph density and algebraic connectivity (see Universal-Recursion-Principle graph section)
- Cross-turn consistency score (e.g., cosine between current and prior answers on shared claims)
- Factuality/contradiction flags from claim-level evaluation

**κ (usable capacity)**
- Context pressure: `context_tokens_used / context_window`
- Latency dispersion and retry volatility
- Tool failure rate and incomplete tool responses
- Retrieval overload: breadth vs. hit rate

### 19.3 Scoring sketch (per step)

```python
def compute_step_score(telemetry):
    c = normalize([
        entropy(telemetry.output),
        embedding_novelty(telemetry.output, telemetry.retrieval),
        claim_novelty(telemetry.claims, telemetry.citations),
        path_diversity(telemetry.branches)
    ])

    i = normalize([
        citation_coverage(telemetry.claims, telemetry.citations),
        support_graph_connectivity(telemetry.claim_graph),
        cross_turn_consistency(telemetry.history),
        contradiction_penalty(telemetry.claims)
    ])

    kappa_value = capacity_field(
        context_load=telemetry.context_tokens_used / telemetry.context_window,
        latency_std=telemetry.latency.std_ms,
        tool_failure_rate=telemetry.tools.failure_rate
    )

    s = c + kappa_value * i  # mirrors URP definition S = C + κI
    return { "c": c, "i": i, "kappa": kappa_value, "s": s }
```

Normalization and weights should be data-driven; start with z-scores against recent session windows and clip to [0,1] for UI.

The additive form mirrors the core URP definition `S = C + κI`: novelty contributes directly, while integration is scaled by usable capacity to avoid over-crediting coherence when the system is saturated.

Reference implementations should surface small helpers (e.g., `normalize`, `capacity_field`) with docstrings describing the z-score → weighted-average → clipping and weighted-sum → sigmoid steps so that pipelines can swap estimators without changing the scoring signature.

### 19.4 Build order (MVP to v2)

1. **MVP scoring**: entropy-based C, citation coverage-based I, simple κ from context pressure + latency.
2. **Claim graph**: add claim extraction and support graph density; surface explanations.
3. **Policy loop**: wire policy actions (temperature, retrieval breadth, grounded regeneration).
4. **Attention/white-box**: plug in attention variance as κ signal when available (Transformer-Dynamics).
5. **Evaluation harness**: benchmark regimes (rigid / creative-grounded / hallucination-risk / collapse) on canned traces; export session summaries to the evaluation store.

---

## 20. Benchmark Corpus and Results

### 20.1 Corpus design

The benchmark corpus (`benchmarks/corpus.py`) contains **28 human-labelled scenarios** spanning all four behavioural regimes plus edge cases:

| Group | Count | Purpose |
|-------|-------|---------|
| Creative-grounded | 5 | Well-grounded answers with genuine novelty and cited sources |
| Hallucination-risk | 5 | Confident but fabricated or unsupported claims |
| Rigid | 5 | Repetitive, template-like, or retrieval-echo outputs |
| Collapse | 5 | Degenerate, incoherent, or truncated outputs under system stress |
| Edge cases | 8 | Borderline scenarios that stress the regime classifier, including template-with-diverse-vocab, qualified speculation, and bullet-point repetition |

Five scenarios include **gray-box signals** (logprobs, token entropy, relevance scores, tool confidence, and/or decoding instability) to validate the gray-box scoring pipeline end-to-end.

### 20.2 Benchmark runner

The runner (`benchmarks/run_api_benchmark.py`) exercises all 7 REST API endpoints:

1. `POST /v1/session/start` — create session groups
2. `POST /v1/step` — submit each scenario
3. `GET /v1/session/{id}` — retrieve session summaries
4. `GET /v1/sessions` — list all active sessions
5. `GET /v1/session/{id}/window` — rolling-window statistics
6. `GET /v1/trace/{id}/graph` — coherence graph for each trace
7. `POST /v1/policy/evaluate` — standalone policy evaluation with known score vectors

### 20.3 Current results (2026-03-29)

**Overall regime accuracy: 96.4% (27/28)**

| Regime | Precision | Recall | F1 |
|--------|-----------|--------|-----|
| Creative-grounded | 1.00 | 0.90 | 0.95 |
| Hallucination-risk | 0.83 | 1.00 | 0.91 |
| Rigid | 1.00 | 1.00 | 1.00 |
| Collapse | 1.00 | 1.00 | 1.00 |

**Score distributions by regime:**

| Regime | Avg C | Avg I | Avg κ | Avg S |
|--------|-------|-------|-------|-------|
| Creative-grounded | 0.83 | 0.63 | 1.00 | 1.46 |
| Hallucination-risk | 0.85 | 0.32 | 0.96 | 1.16 |
| Rigid | 0.64 | 0.62 | 1.00 | 1.26 |
| Collapse | 0.39 | 0.31 | 0.22 | 0.46 |

**Known misclassification (1/28):**

1. `edge-01-creative-but-no-retrieval` — expected creative-grounded, classified as hallucination-risk (I=0.33). The output is genuinely creative but lacks any retrieval context, so the I estimator correctly reports low groundedness; the design question is whether "creative without grounding" should be flagged as a risk.

**Previously-fixed misclassifications:**

* `rigid-02-template-response` — previously misclassified as creative-grounded (C=0.82 from lexical diversity). Fixed by structural repetition detection: the template-rigid rule detects that sentence-level structure is repetitive (novelty=0.37 < 0.40) despite high lexical diversity.
* `rigid-03-over-constrained` — previously misclassified as creative-grounded (C=0.50, I=0.43 in a borderline zone). Fixed by the same template-rigid rule: the repeated "Based on the documentation" prefix gives structural novelty=0.21.

### 20.4 Structural repetition detection

The C estimator now includes two structural novelty metrics in addition to the original lexical metrics:

* **`_sentence_structure_novelty`** — Measures first-word concentration, sentence complexity (average length), and length diversity. Returns low values for template patterns like "The X is Y. The X has Z." where every sentence starts with the same word and follows the same structure.
* **`_retrieval_echo_novelty`** — Measures trigram overlap between the output and retrieved context. Returns low values when the output closely echoes retrieval chunks.

The regime classifier uses a **template-rigid rule**: when `structural_novelty < 0.40` and integration I ≥ 0.35 and capacity κ ≥ 0.45, the output is classified as rigid regardless of its lexical C score. This catches formulaic outputs that defeat the token-diversity proxy.

### 20.5 Gray-box benchmark observations

- Gray-box scenarios consistently produce higher confidence (dynamic, typically 0.85–0.95 depending on signal coverage) and the scoring engine correctly routes through the gray-box estimators.
- Hallucination-risk scenario `hallucination-risk-03-mixed-real-and-fake` benefits from gray-box signals: relevance scores lower κ via retrieval overload, and the contradiction penalty reduces I.
- Rigid scenario `rigid-01-rote-repetition` classifies correctly under gray-box mode, with C accurately reflecting the low novelty of pure repetition.
- Rigid scenario `rigid-03-over-constrained` now correctly classifies as rigid under gray-box mode (confidence=0.89), using the template-rigid detection rule.
- Collapse scenario `collapse-03-incoherent-fragments` shows gray-box signals amplifying capacity stress through tool confidence and decoding instability.

See `benchmarks/REPORT.md` for the full scenario-by-scenario report.
