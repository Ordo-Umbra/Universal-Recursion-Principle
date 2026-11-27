# Generative Geometry — Pilot 4b Protocol

## Autonomous Constructor Discovery Within a Finite Grammar

### Status

Protocol fixed before the full experiment. Pilot 4b tests whether usefulness-guided search can select and compose higher-order relational constructors without receiving the triangle-area constructor directly. It remains a finite-grammar, nonrecursive experiment.

## Research question

Can a system use development tasks to discover relational constructors that subsequently improve performance on a held-out task and an unseen geometric family, without using the held-out task during constructor selection?

The experiment distinguishes:

- selection and composition within a predefined grammar;
- rediscovery of the previously supplied area constructor;
- selection of expressions that are not linearly equivalent to area;
- usefulness-guided discovery versus random constructor retention.

It does not test discovery outside the grammar, open-ended mathematical invention, or recursive reuse across developmental stages.

## Constructor grammar

Each candidate constructor is a scalar local expression applied uniformly to all 20 unordered point triples. For triple `(i,j,k)`, anchored at `i`, define edge vectors:

\[
u=p_j-p_i,\qquad v=p_k-p_i,\qquad w=p_k-p_j.
\]

Five generic local invariant leaves are supplied:

- `dot` — \(u\cdot v\);
- `cross` — \(u_xv_y-u_yv_x\);
- `u2` — \(\|u\|^2\);
- `v2` — \(\|v\|^2\);
- `w2` — \(\|w\|^2\).

Candidates are generated systematically, independent of task labels:

1. Twenty unary candidates: each leaf under `identity`, `abs`, `square`, or `sqrt_abs`.
2. Sixty binary candidates: every unordered leaf pair with replacement under `multiply`, `divide`, `add`, or `abs_diff`.

Total: 80 candidate constructors. Division uses a small numerical stabilizer. Constant output scaling is omitted because the downstream standardized ridge learner is invariant to it.

The previous area constructor is not supplied directly. It is constructible as `abs(cross)`, up to the omitted factor \(1/2\).

## Development and held-out tasks

### Development tasks used for constructor selection

- hull perimeter;
- compactness;
- hull vertex count.

These tasks provide multi-objective guidance. Constructor selection uses a 400-configuration fitting subset and a separate 200-configuration validation subset drawn only from the three training families.

### Held-out final task

- convex-hull area.

Hull-area labels are not used during constructor search, selection, or retention. After two constructors have been fixed, area labels from the training families may be used to fit the final task model. The test family remains unseen throughout.

## Discovery procedure

1. Begin with the 15 pairwise distances as the base representation.
2. Evaluate each candidate by adding its 20 triple-level outputs to the current representation.
3. Score candidates by mean validation \(R^2\) across the three development tasks using the same ridge learner.
4. Retain the highest-scoring candidate.
5. Repeat once with the first retained constructor included, yielding at most two retained constructors.
6. Record the complete selection history and validation scores.

The discovered final representation therefore contains 15 pairwise features and two 20-component constructor blocks. A random control retains two candidates sampled uniformly without replacement, independently of all task labels.

## Final representations

- **pairwise** — 15 pairwise distances;
- **discovered** — pairwise distances plus two development-selected constructor blocks;
- **random_constructors** — pairwise distances plus two randomly selected constructor blocks;
- **supplied_area** — pairwise distances plus the `abs(cross)` block;
- **raw_quadratic** — raw coordinates and all quadratic monomials.

## Final evaluation

- Four environment families and twenty replicates, matching Pilot 4;
- leave-one-family-out transfer;
- nested training budgets 25, 50, 100, 200, 500, and 1000;
- fixed ridge learner with regularization `1e-3`;
- training-only feature and target standardization;
- held-out-family \(R^2\) and NRMSE.

The primary final comparisons at budget 200 are discovered versus pairwise and discovered versus random constructors. Comparisons with supplied area and raw quadratic features are secondary.

## Constructor-content analysis

Every retained expression is recorded. For each selected candidate, the experiment also measures how well its outputs can be predicted from `abs(cross)` by a linear fit on the configurations in that replicate.

Categories:

- **direct_area_rediscovery:** expression is exactly `abs(cross)`;
- **linearly_area_aligned:** a different expression with linear area-alignment \(R^2\geq0.999\);
- **non_area_linear:** alignment below 0.999.

These categories are descriptive. A non-area-linear expression is not automatically claimed to be mathematically novel or functionally independent of area. Constructor diversity and final performance by selected expression are exploratory analyses.

## Interpretation rules fixed before testing

### Support for usefulness-guided discovery

Discovered constructors must outperform pairwise features and random constructors on held-out hull area. Positive paired intervals at budget 200 support the primary claim.

### No guided-discovery advantage

If discovered constructors do not outperform random constructor retention, development-task guidance has not demonstrated a benefit.

### No useful discovered structure

If discovered constructors do not improve over pairwise features, the selected constructors do not demonstrate held-out usefulness.

### Supplied-area comparison

If supplied area outperforms discovered constructors, autonomous search within this grammar has not reproduced the effectiveness of the supplied representation. If discovered performance matches supplied area without directly selecting `abs(cross)`, the result motivates analysis of alternative construction pathways.

### Finite-grammar boundary

Any positive result concerns endogenous search, selection, and composition within an explicitly supplied finite grammar. It does not establish expansion beyond that grammar or unrestricted open-endedness.

## Limitations

- The system is given generic geometric leaves and operations; it does not invent the underlying mathematical language.
- Constructor selection is nonrecursive: selected constructors are not yet inputs to later grammar operations.
- Development tasks are researcher-supplied and geometrically related to the final task.
- Constructor evaluation is based on a fixed ridge learner and finite validation subset.
- Search time, memory, and constructor-evaluation costs are not equalized across all representations.
- Expression-category and per-constructor performance analyses are exploratory and do not prove mathematical novelty.
- Secondary comparisons are not adjusted for multiple testing.
