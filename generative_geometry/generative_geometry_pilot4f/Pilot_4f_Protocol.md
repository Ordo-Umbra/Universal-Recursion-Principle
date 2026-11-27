# Generative Geometry — Pilot 4f Protocol

## Frozen Constructors and Permutation-Invariant Integration

### Status

Protocol fixed on 2026-11-27 before implementation, smoke testing, or the full experiment. No Pilot 4f numerical results have been used to choose the hypotheses, representations, comparisons, or interpretation rules. Pilot 4e is complete and is used only as the source of frozen constructor expressions and matched baseline results.

## Research question

When constructor discovery is held fixed, how much additional held-out capability becomes available through permutation-invariant feature integration alone?

Pilot 4f is an integration experiment, not a new search experiment. It does not change any constructor selected in Pilot 4e, rerun search, revise expressions, or select representations using final hull-area labels.

## Rationale and pre-implementation invariance refinement

The current searched representation contains 15 label-indexed pairwise distances and 20 label-indexed triple-level constructor values. Independent point relabeling preserves the geometric configuration and targets but changes the ordering of these feature blocks.

Sorting a block is an information-preserving diagnostic when the underlying value multiset is itself invariant. This is true for pairwise distances and for supplied unsigned triple area, `abs(cross)`.

A pre-implementation algebraic review shows that simply sorting the original 20 values is **not** sufficient for an arbitrary expression. Expressions involving `cross`, `dot`, `u2`, `v2`, or `w2` may depend on the local anchor and orientation of a triple. A global point relabeling can change the multiset of anchored values, not merely its ordering.

Therefore:

- the primary supplied-area test uses the simple sorted 20-value block, whose invariance is exact;
- secondary tests of arbitrary frozen expressions use a full local-orbit representation described below;
- simple sorting of arbitrary expressions is not called invariant and is not used for their confirmatory comparisons.

This refinement is based on the symmetry definition, not on observed performance.

## Environment and frozen constructors

The environment is identical to Pilot 4e:

- six normalized and randomly rotated points per configuration;
- independent point-label permutations within every configuration;
- four environment families;
- 1,200 training-pool and 800 test configurations per family and replicate;
- leave-one-family-out evaluation;
- 20 replicates;
- deterministic Pilot 4e data, permutation, and training-order seeds.

The final target is convex-hull area. The learner is fixed ridge regression with `alpha=1e-3`, training-only feature standardization, and training-only target standardization.

Eight constructor sources are evaluated:

1. `supplied_area`: always `abs(cross)`;
2. `initial`: always `dot`;
3. frozen `greedy` outputs from Pilot 4e;
4. frozen `neutral_drift` outputs from Pilot 4e;
5. frozen `diversity_archive` outputs from Pilot 4e;
6. frozen `sampled_lookahead` outputs from Pilot 4e;
7. frozen `independent_search` outputs from Pilot 4e;
8. frozen `unscaffolded` outputs from Pilot 4e.

For every replicate/family fold, the expression is read directly from `pilot4e_search_summary.csv`. There is no new search or expression selection. A constructor manifest records every expression used.

## Feature transformations

### Current representation

The current representation is the Pilot 4e representation:

- 15 pairwise distances in label-indexed pair order;
- 20 constructor values in label-indexed triple order.

It has 35 features.

### Sorted pairwise block

The 15 pairwise distances are sorted within each configuration. The pairwise multiset and its 15 values are preserved exactly; only their order changes.

### Simple sorted constructor block

The 20 original constructor values are sorted within each configuration. This condition is used only for supplied `abs(cross)`, where every unordered triangle has the same unsigned doubled-area value under local vertex relabeling.

### Full local-orbit constructor block

For each configuration:

1. enumerate all 20 unordered point triples;
2. enumerate all six local vertex orderings of each triple;
3. evaluate the frozen expression on all \(20\times6=120\) oriented local triples;
4. sort the resulting 120 values within each configuration.

Any global point relabeling merely permutes this complete set of oriented triples. The sorted 120-value representation is therefore exactly invariant for every grammar expression, including signed and asymmetric expressions. It preserves the full local-orbit multiset but expands the constructor block from 20 to 120 values.

This is a diagnostic integration oracle, not a claim that redundant orbit expansion is the best permanent architecture.

## Aggregation conditions

### Supplied area

Six conditions are evaluated:

| Aggregation | Pairwise block | Constructor block | Features |
|---|---|---|---:|
| `current` | label-indexed 15 | label-indexed 20 | 35 |
| `pairwise_sorted` | sorted 15 | label-indexed 20 | 35 |
| `constructor_sorted` | label-indexed 15 | simple sorted 20 | 35 |
| `fully_sorted` | sorted 15 | simple sorted 20 | 35 |
| `constructor_orbit_sorted` | label-indexed 15 | orbit sorted 120 | 135 |
| `fully_orbit_sorted` | sorted 15 | orbit sorted 120 | 135 |

### Initial and frozen Pilot 4e constructors

Four conditions are evaluated:

| Aggregation | Pairwise block | Constructor block | Features |
|---|---|---|---:|
| `current` | label-indexed 15 | label-indexed 20 | 35 |
| `pairwise_sorted` | sorted 15 | label-indexed 20 | 35 |
| `constructor_orbit_sorted` | label-indexed 15 | orbit sorted 120 | 135 |
| `fully_orbit_sorted` | sorted 15 | orbit sorted 120 | 135 |

Simple sorted arbitrary constructor values are excluded because exact invariance does not generally hold.

## Ordered reference

A descriptive ordered-environment reference is evaluated only for supplied area with the current 35-feature representation. It uses the same underlying ordered configurations and final training orders as Pilot 4c/4d. Its purpose is to check reproduction and describe the ordered–permuted performance gap; it is not part of the primary permuted-environment comparison.

## Invariance validation

Before final model evaluation, a separate deterministic second point relabeling is applied to validation configurations.

The following must agree to an absolute tolerance of \(10^{-12}\):

- sorted pairwise features;
- simple sorted supplied-area features;
- orbit-sorted supplied-area features;
- orbit-sorted `dot`, `cross`, and representative asymmetric-expression features;
- targets, which are unchanged by construction.

Simple sorted `dot` and `cross` blocks are also recorded as diagnostics to demonstrate why they are not used as general invariant representations. A diagnostic violation for these non-invariant simple blocks is not an implementation failure.

Every required invariance check must pass before the full experiment is accepted. Maximum absolute discrepancies are saved.

## Final evaluation

- Nested final fitting budgets: 25, 50, 100, 200, 500, and 1000.
- Common training order across every condition within replicate/fold.
- MSE, NRMSE, \(R^2\), and \(L=\log(1+\mathrm{NRMSE})\).
- Primary endpoint: budget 200.
- Permuted design: 16,320 final model evaluations.
- Ordered supplied-area reference: 480 final model evaluations.
- Total: 16,800 final model evaluations.

All heavy tails and family-specific failures are retained. No constructor or result is removed because of poor performance.

## Pre-specified statistical comparisons

For each condition, average the four test-family log errors within each replicate. Comparisons use two-sided 95% Student-\(t\) intervals over 20 replicate differences.

For focus condition \(M\) and comparator \(C\):

\[
D=L_C-L_M,
\]

so positive values favor the focus condition.

### Primary

For supplied `abs(cross)` at budget 200:

- `fully_sorted` versus `current`.

A positive interval whose lower bound exceeds zero supports a benefit of fully permutation-invariant integration with constructor identity, dimensionality, data, learner, and training order held fixed.

### Secondary supplied-area comparisons

At budget 200:

- `pairwise_sorted` versus `current`;
- `constructor_sorted` versus `current`;
- `constructor_orbit_sorted` versus `current`;
- `fully_orbit_sorted` versus `current`;
- `fully_orbit_sorted` versus `fully_sorted`.

### Secondary frozen-constructor comparisons

For `initial` and each of the six frozen Pilot 4e sources at budget 200:

- `pairwise_sorted` versus `current`;
- `constructor_orbit_sorted` versus `current`;
- `fully_orbit_sorted` versus `current`.

### Aggregation interactions

For supplied area's simple sorted conditions, define

\[
I=(L_{\mathrm{pairwise\_sorted}}-L_{\mathrm{fully\_sorted}})
-(L_{\mathrm{current}}-L_{\mathrm{constructor\_sorted}}).
\]

For each orbit condition, define

\[
I=(L_{\mathrm{pairwise\_sorted}}-L_{\mathrm{fully\_orbit\_sorted}})
-(L_{\mathrm{current}}-L_{\mathrm{constructor\_orbit\_sorted}}).
\]

Positive \(I\) means that constructor aggregation is more beneficial when the pairwise block is also invariant. Interactions are supporting analyses.

Other budgets, per-family results, medians, win fractions, exact sign tests, and ordered-reference comparisons are descriptive or secondary. Secondary comparisons are not adjusted for multiplicity.

## Interpretation rules fixed before testing

### Positive integration result

Requires a positive primary `fully_sorted` versus `current` interval for supplied area at budget 200. Invariance checks alone establish correct implementation, not improved learning.

### Constructor sorting versus pairwise sorting

The individual secondary arms distinguish their separate contributions. The interaction summaries assess whether their benefits are complementary. A primary benefit cannot be assigned specifically to the constructor block if only `pairwise_sorted` improves.

### Frozen searched constructors

Improvement for frozen searched expressions would show that downstream integration changes their effective availability without further discovery. Failure for searched expressions despite supplied-area improvement would indicate that constructor quality or task relevance remains limiting.

### Expanded-orbit interpretation

Orbit conditions change both invariance and constructor dimensionality. They are diagnostic secondary conditions. A difference between simple sorted and orbit-sorted supplied area may reflect redundancy, dimensionality, or regularization as well as general orbit construction; it is not interpreted as a pure dimensionality-free effect.

### Ordered reference

Closing the permuted–ordered gap is descriptive. Exact recovery of ordered performance is not required for a positive primary result.

### No search claim

Pilot 4f cannot establish better constructor discovery, developmental scaffolding, descendant value, or open-endedness. It evaluates only integration of fixed expressions.

## Limitations

- Sorting preserves multisets but can discard correspondence between a constructor value and a particular pairwise-distance entry.
- Full local-orbit sorting expands 20 constructor values to 120 and repeats equivalent values for locally symmetric expressions.
- Exact invariance to point labels does not guarantee sample efficiency, positive transfer, or robustness on elongated configurations.
- Ridge regression remains fixed; the experiment does not compare learned permutation-invariant architectures.
- Frozen expressions were originally selected using non-invariant development representations, which may limit how much invariant final integration can recover.
- Supplied compactness-guided discovery history remains part of the earlier experiments, although no development or search score is used in Pilot 4f.
