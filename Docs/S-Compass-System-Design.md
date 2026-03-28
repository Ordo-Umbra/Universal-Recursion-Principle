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

Adds:

- logprobs
- relevance scores
- token-level uncertainty
- tool confidence metrics

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
    # normalize(): z-score each metric against rolling mean/std, take weighted mean, then min-max clip to [0,1]
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

    # capacity_field(): weighted_sum = w1*context_load + w2*normalize(latency_std) + w3*tool_failure_rate; return sigmoid(weighted_sum)
    kappa = capacity_field(
        context_load=telemetry.context_tokens_used / telemetry.context_window,
        latency_std=telemetry.latency.std_ms,
        tool_failure_rate=telemetry.tools.failure_rate
    )

    s = c + kappa * i  # mirrors URP definition S = C + κI
    return { "c": c, "i": i, "kappa": kappa, "s": s }
```

Normalization and weights should be data-driven; start with z-scores against recent session windows and clip to [0,1] for UI.

The additive form mirrors the core URP definition `S = C + κI`: novelty contributes directly, while integration is scaled by usable capacity to avoid over-crediting coherence when the system is saturated.

### 19.4 Build order (MVP to v2)

1. **MVP scoring**: entropy-based C, citation coverage-based I, simple κ from context pressure + latency.
2. **Claim graph**: add claim extraction and support graph density; surface explanations.
3. **Policy loop**: wire policy actions (temperature, retrieval breadth, grounded regeneration).
4. **Attention/white-box**: plug in attention variance as κ signal when available (Transformer-Dynamics).
5. **Evaluation harness**: benchmark regimes (rigid / creative-grounded / hallucination-risk / collapse) on canned traces; export session summaries to the evaluation store.
