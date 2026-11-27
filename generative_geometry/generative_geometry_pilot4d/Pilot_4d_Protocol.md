# Generative Geometry — Pilot 4d Protocol

## Permutation-Randomized Geometry and Obligatory Multi-Step Scaffolding

### Status

Protocol fixed on 2026-11-23 before implementation, smoke testing, or the full experiment. Numerical results must not be used to revise the hypotheses, arms, search rules, controls, primary endpoint, or interpretation criteria in this document.

## Research question

Does removing consistent point-label order create a setting in which exact area discovery requires multi-step constructor refinement, and does parent-chained refinement then outperform a matched search that cannot build on intermediate expressions?

Pilot 4c showed genuine refinement but usually stopped after one mutation. Its unscaffolded control therefore selected the same constructor in 70 of 80 runs. Pilot 4d changes the input symmetry rather than changing the refinement mechanism: point labels are randomly permuted separately for every configuration in one arm, while the original ordered arm is retained as a paired control.

The intended path is:

```text
dot → cross → abs(cross)
```

With consistent angular ordering, signed `cross` can provide substantial information about oriented local area. Under independently randomized point labels, its sign is arbitrary across configurations, whereas `abs(cross)` remains the relevant unsigned local-area magnitude. Exact area cannot be obtained by a single Pilot 4c mutation from `dot`.

This is a stronger test of parent chaining, but still a finite-grammar experiment. It does not test open-ended discovery or invention of geometric primitives.

## Experimental arms

### Ordered arm

This arm reproduces Pilot 4c's point ordering and all search/evaluation settings. It serves as a paired reference and a numerical replication check.

### Permuted arm

For each configuration independently, a deterministic random permutation of the six point labels is applied after normalization, rotation, and target computation. Pairwise, raw-quadratic, and local triple features are then computed from the permuted coordinates.

The permutation changes only input labeling. It does not change:

- point locations up to relabeling;
- hull area, perimeter, compactness, or hull vertex count;
- environment family;
- random rotation;
- training/test split;
- final training order;
- search or control seeds.

The same underlying configurations and targets are used in both arms.

## Grammar and initial constructor

The leaves, operations, expression depth limit, mutation neighborhood, and division stabilizer are identical to Pilot 4c.

Leaves:

- `dot`;
- `cross`;
- `u2`;
- `v2`;
- `w2`.

Unary operations:

- `abs`;
- `square`;
- `sqrt_abs`.

Binary operations:

- `multiply`;
- `divide`;
- `add`;
- `abs_diff`.

Every search begins with `dot`. Expressions have maximum depth 2 and are applied to all 20 unordered triples of the supplied point labels. Although triples are unordered by index, their anchored cross-product sign depends on point-label order.

## Development tasks and held-out task

Constructor search uses only:

- hull perimeter;
- compactness;
- hull vertex count.

The held-out final task is convex-hull area. Final-area labels are excluded from search, gates, and selection. Compactness remains geometrically related to area and is acknowledged as related development guidance.

All tasks are invariant to point relabeling. Any difference between arms therefore concerns representation and search under input permutation, not different target functions.

## Gates and robust development score

The numerical validity, family near-constancy, small-sample near-constancy, and family scale-collapse gates are identical to Pilot 4c.

For each arm and final leave-one-family-out fold:

- three internal development folds leave out one available training family in turn;
- development fitting budgets are 40 and 80;
- each internal validation set contains 80 configurations;
- the learner is fixed ridge regression with training-only standardization;
- the representation is 15 pairwise distances plus one 20-component constructor block;
- development \(R^2\) values are clipped to \([-1,1]\) for scoring;
- the robust score is the median of 18 task/fold/budget values.

A child replaces its parent only if it passes every gate and improves the robust development score by more than \(10^{-4}\). At most four revision rounds are permitted. Parents remain archived but are not retained as additional feature blocks.

## Search conditions and matched budgets

Each arm contains the same four search conditions:

1. **Refined:** deterministic best-improvement revision using accepted children as later parents.
2. **Independent search:** independently sampled expressions from the same depth-2 grammar, guided by development score, without parent chaining.
3. **Unscaffolded:** repeated evaluation of one-mutation variants of the original `dot` root; the best output may be retained but never becomes a parent.
4. **Random lineage:** random parent-chained mutations with the same gates but no development-label guidance.

Within each arm/replicate/final-fold run, every condition receives exactly the refined run's candidate-evaluation count and round structure. Candidate budgets need not be equal across arms because refined lineages may stop after different numbers of rounds.

The unscaffolded condition cannot produce `abs(cross)` from `dot`: that expression requires a leaf replacement and a unary wrapping. It can still discover useful one-step approximations such as `cross`, `square(cross)`, or `sqrt_abs(cross)`. The comparison therefore tests whether the exact two-step construction and other multi-step expressions provide an advantage, not whether one-step approximations are useless.

## Final representations

Eight representations are evaluated in each arm:

- `pairwise`;
- `initial`;
- `refined`;
- `independent_search`;
- `unscaffolded`;
- `random_lineage`;
- `supplied_area`;
- `raw_quadratic`.

Except for `pairwise` and `raw_quadratic`, all use 15 pairwise features plus one 20-component constructor block. `supplied_area` always uses `abs(cross)` and is not a search outcome.

## Final evaluation

- 20 replicates;
- two paired arms;
- four leave-one-family-out folds per arm;
- nested final-task budgets 25, 50, 100, 200, 500, and 1000;
- fixed `Ridge(alpha=1e-3)`;
- training-only feature and target standardization;
- common final training order across representations and arms within replicate/fold;
- MSE, NRMSE, \(R^2\), and \(\log(1+\mathrm{NRMSE})\).

The primary endpoint remains budget 200. Other budgets are secondary.

The full run contains 160 search runs and 7,680 final model evaluations. The ordered arm must reproduce Pilot 4c numerically; any discrepancy will be diagnosed as an implementation or data-pipeline difference rather than silently accepted as biological-style variation.

## Lineage analysis

For every arm and search condition, the experiment records all proposals, parents, gates, development scores, and acceptance decisions. Accepted refined revisions additionally record parent, child, robust-score improvement, depth, and structural embedding.

Pre-specified lineage summaries include:

- accepted-revision count;
- complete revision paths;
- terminal expression;
- terminal and intermediate exact-area discovery;
- frequency of the `dot → cross → abs(cross)` pathway;
- performance by terminal expression and revision count;
- exact terminal-expression agreement between refined and unscaffolded search;
- gate-rejection frequencies.

Syntactic novelty is not treated as mathematical novelty. Signed, squared, square-root, and absolute cross products remain area-related expressions.

## Pre-specified statistical analysis

The primary robust error is:

\[
L=\log(1+\mathrm{NRMSE}).
\]

For each replicate and arm, \(L\) is averaged over the four final test families. Paired comparisons use two-sided 95% Student-\(t\) intervals over 20 replicate differences. For comparator-versus-refined analyses:

\[
D=L_{\mathrm{comparator}}-L_{\mathrm{refined}},
\]

so positive values favor refined search.

### Primary scaffolding test

At budget 200 in the permuted arm:

- refined versus unscaffolded paired log error.

A positive interval whose lower bound exceeds zero is required for the primary scaffolding claim. Accepted parent–child lineages must also document the intermediate expressions responsible for multi-step outcomes.

### Key secondary tests

1. Refined versus unscaffolded in the ordered arm at budget 200.
2. Refined versus initial and random lineage in the permuted arm.
3. Refined versus independent search in both arms.
4. Refined versus supplied area in both arms.
5. Exact-area and multi-step frequencies by arm, with exact McNemar tests on paired discordant runs as supporting analyses.

### Arm-interaction test

For each replicate, define the unscaffolded-minus-refined log-error advantage separately in each arm:

\[
A_{\mathrm{ordered}}=D_{\mathrm{ordered}},\qquad
A_{\mathrm{permuted}}=D_{\mathrm{permuted}}.
\]

The interaction is \(A_{\mathrm{permuted}}-A_{\mathrm{ordered}}\). A two-sided 95% paired \(t\) interval over 20 replicates tests whether the refinement advantage changes under permutation. A positive interval supports a permutation-dependent increase in the value of parent chaining.

The interaction is secondary and cannot substitute for a failed primary permuted-arm scaffolding test.

## Interpretation rules fixed before testing

### Positive multi-step refinement

Evidence of multi-step refinement requires accepted lineages with at least two revisions and improved held-out performance relative to the initial constructor. Exact-area recovery is reported separately and is not required for every refined lineage.

### Positive scaffolding in the permuted arm

The primary claim requires the permuted-arm refined-versus-unscaffolded interval to be positive. If it crosses zero, the experiment has not demonstrated a scaffolding advantage, even if exact-area frequency increases or a multi-step subset looks favorable.

### Permutation-enabled scaffolding

A stronger claim that random point order increases the value of scaffolding requires both:

- a positive primary permuted-arm scaffolding interval; and
- a positive arm-interaction interval.

### Independent-search qualification

If independent search matches or outperforms refined search, the experiment must not claim a general advantage of lineage-based search over equally budgeted non-lineage search. A refined-versus-unscaffolded result would then concern the specific local parent-chaining mechanism only.

### Incomplete recovery and instability

If supplied area remains superior, refinement has not generally recovered the known representation. Low-budget failures, heavy tails, gate rejections, unsuccessful multi-step paths, and arm-specific reversals will be retained.

### Negative results

Failure to increase multi-step refinement, failure to outperform unscaffolded search, or a nonpositive interaction will be reported as failure of the corresponding claim. Post hoc subsets cannot convert these into positive pre-specified results.

## Limitations

- Point permutation is a researcher-designed manipulation intended to make unsigned area more valuable; it is not an autonomous environmental change.
- The grammar, initial expression, development tasks, gates, and learner remain supplied.
- Compactness provides area-related development guidance.
- Exact area is two mutations away, but useful one-step approximations remain available.
- Candidate evaluations are matched by count, not runtime or memory.
- The ordered arm is a replication of one synthetic setting, not an independent external benchmark.
- Results concern input-label symmetry and local constructor search; they do not establish general developmental learning or metaphysical claims.
- Secondary comparisons are not adjusted for multiplicity.
