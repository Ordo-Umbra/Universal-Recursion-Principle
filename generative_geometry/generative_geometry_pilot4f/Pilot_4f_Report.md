# Generative Geometry — Pilot 4f Report

## Frozen Constructors and Permutation-Invariant Integration

### Executive result

Pilot 4f is a **clear positive result for permutation-invariant integration with constructor discovery held fixed**.

At the pre-specified budget of 200 final-task training configurations, fully sorting the pairwise and supplied-area constructor blocks reduced mean log error by 0.117555 relative to the current representation, with 95% interval [0.109967, 0.125143]. The improvement occurred in all 20 replicates. Supplied-area mean \(R^2\) increased from 0.733554 to 0.893062, and median \(R^2\) increased from 0.828701 to 0.897769.

The main findings are:

- **Both feature blocks mattered.** Sorting only the constructor block gave a 0.101705 improvement; sorting only pairwise distances gave 0.063167. Both intervals excluded zero.
- **The benefit generalized across frozen constructors.** Every initial or Pilot 4e-selected constructor source improved under its fully invariant local-orbit representation, with positive intervals at budget 200 and at every other fitting budget.
- **Integration changed constructor rankings.** Under the current representation, independent search had the lowest mean log error among searched sources. Under full invariant integration, the initial `dot` constructor was best at budget 200: 0.481730, compared with 0.536850 for lookahead and 0.564912 for independent search.
- **Invariant aggregation did not complete recovery.** Supplied area remained below its ordered-environment reference, with mean \(R^2=0.968428\) and log error 0.157569. Low-budget and family-specific gaps remained.
- **Heavy tails did not disappear.** Neutral drift's full invariant mean log error improved, but its mean \(R^2\) remained negative because of rare catastrophic ratio expressions. Elongated configurations still caused negative mean \(R^2\) for most searched constructors.

The central conclusion is:

> A constructor's apparent usefulness depends on the integration layer through which it becomes available to downstream learning. Permutation-invariant aggregation can unlock substantial effective capability from exactly the same expressions, without any new discovery. It also changes which constructors appear valuable, so search and integration cannot be treated as independent stages.

## Experimental design

Pilot 4f performed **no new constructor search**. It evaluated supplied `abs(cross)`, initial `dot`, and the exact frozen outputs of all six Pilot 4e search conditions. Every expression was read from the saved Pilot 4e search summaries and recorded in a constructor manifest.

The permuted data, held-out-family folds, training orders, targets, ridge learner, and nested fitting budgets were unchanged. The current representation contained 15 label-indexed pairwise distances and 20 label-indexed constructor values. Aggregation manipulated only the feature blocks:

- sort the 15 pairwise distances;
- sort the 20 supplied unsigned-area values;
- or, for arbitrary expressions, evaluate all six local vertex orderings of every triple and sort the resulting 120-value local orbit.

The full design contained 16,320 permuted-environment final evaluations and 480 ordered supplied-area reference evaluations, for 16,800 total. The primary endpoint was budget 200. All heavy tails and unsuccessful conditions were retained.

## Why the local orbit was necessary

Simple sorting is exactly invariant only when the underlying value multiset is invariant. This holds for pairwise distances and supplied `abs(cross)`. It does not hold generally for anchored expressions involving `dot`, `cross`, `u2`, `v2`, or `w2`.

Fresh-relabeling validation demonstrated this distinction:

- every required sorted or orbit-sorted invariant check passed;
- the maximum required discrepancy was \(1.78\times10^{-15}\), below the \(10^{-12}\) tolerance;
- simple sorted `dot`, `cross`, and `abs_diff(u2,v2)` failed all 12 diagnostic non-invariance checks;
- orbit-sorted versions of the same expressions passed exactly.

Thus, simple sorting was used for the same-dimensional supplied-area primary test, while the 120-value orbit was used for arbitrary frozen expressions. The orbit is an exact diagnostic representation, not a claim that redundant expansion is the best permanent architecture.

## Primary supplied-area result

Budget-200 performance:

| Environment / aggregation | Features | Mean \(R^2\) | Median \(R^2\) | Mean log error |
|---|---:|---:|---:|---:|
| permuted current | 35 | 0.733554 | 0.828701 | 0.394025 |
| permuted pairwise sorted | 35 | 0.831143 | 0.873651 | 0.330858 |
| permuted constructor sorted | 35 | 0.872167 | 0.891452 | 0.292320 |
| permuted fully sorted | 35 | 0.893062 | 0.897769 | 0.276470 |
| permuted constructor orbit sorted | 135 | 0.872163 | 0.891450 | 0.292324 |
| permuted fully orbit sorted | 135 | 0.893058 | 0.897767 | 0.276475 |
| ordered current reference | 35 | 0.968428 | 0.972296 | 0.157569 |

For each focus condition, differences are current-or-comparator log error minus focus log error, so positive values favor the focus condition. Intervals use 20 replicate means after averaging four test-family folds within each replicate.

| Focus | Comparator | Difference | 95% interval | Replicate wins | Exact sign \(p\) |
|---|---|---:|---:|---:|---:|
| **fully sorted** | **current** | **0.117555** | **[0.109967, 0.125143]** | **1.00** | **0.000002** |
| pairwise sorted | current | 0.063167 | [0.056439, 0.069896] | 1.00 | 0.000002 |
| constructor sorted | current | 0.101705 | [0.093883, 0.109528] | 1.00 | 0.000002 |
| constructor orbit sorted | current | 0.101702 | [0.093879, 0.109524] | 1.00 | 0.000002 |
| fully orbit sorted | current | 0.117550 | [0.109962, 0.125138] | 1.00 | 0.000002 |
| fully orbit sorted | fully sorted | -0.000005 | [-0.000005, -0.000004] | 0.05 | 0.000040 |

The primary criterion was satisfied. Because supplied area and both sorted blocks remained 35-dimensional, this result isolates integration without changing constructor identity or feature count.

Simple and orbit-sorted supplied area were practically indistinguishable. Their tiny numerical difference reflects redundant orbit values and ridge regularization; it is not interpreted as a meaningful scientific effect.

### Supplied-area interaction

The simple-sort interaction was:

\[
I=-0.047318,\qquad 95\%\,\mathrm{CI}=[-0.055125,-0.039511].
\]

The two individual benefits were therefore partly overlapping rather than additive. Constructor sorting was more beneficial before pairwise sorting than after it. Nevertheless, the fully sorted condition was best overall, and both individual transformations were independently beneficial.

## Frozen-constructor results

Every frozen source improved under full local-orbit integration at budget 200:

| Constructor source | Current log error | Full invariant log error | Difference [95% CI] | Replicate wins | Current mean \(R^2\) | Full invariant mean \(R^2\) |
|---|---:|---:|---:|---:|---:|---:|
| initial | 0.744448 | 0.481730 | 0.262719 [0.247413, 0.278025] | 1.00 | -0.534445 | 0.584498 |
| greedy | 0.706124 | 0.566776 | 0.139348 [0.107234, 0.171462] | 1.00 | -0.365089 | 0.102927 |
| neutral drift | 0.671101 | 0.572404 | 0.098697 [0.049844, 0.147550] | 0.90 | -0.381660 | -0.701664 |
| diversity archive | 0.753761 | 0.592419 | 0.161342 [0.093175, 0.229509] | 1.00 | -7.073295 | -0.024774 |
| sampled lookahead | 0.657625 | 0.536850 | 0.120775 [0.089829, 0.151722] | 0.95 | -0.221696 | 0.208233 |
| independent search | 0.628791 | 0.564912 | 0.063880 [0.036349, 0.091410] | 0.80 | -0.162471 | 0.087437 |
| unscaffolded | 0.725322 | 0.520916 | 0.204406 [0.165063, 0.243748] | 1.00 | -0.386134 | 0.340025 |

These are positive integration effects for the **complete orbit-representation package**. Unlike the same-dimensional primary supplied-area test, the orbit changes the constructor block from 20 to 120 features. These secondary results therefore combine exact invariance, local-orbit expansion, and any associated regularization effects. They must not be interpreted as dimensionality-free comparisons.

### Separate block contributions and interactions

The following are paired log-error differences at budget 200. Positive interaction values mean that constructor-orbit aggregation was more beneficial when pairwise distances were also sorted.

| Source | Pairwise-only benefit [95% CI] | Constructor-orbit-only benefit [95% CI] | Orbit interaction [95% CI] |
|---|---:|---:|---:|
| initial | 0.001601 [-0.010699, 0.013901] | 0.068285 [0.050682, 0.085887] | 0.192833 [0.171942, 0.213724] |
| greedy | -0.002957 [-0.019068, 0.013154] | 0.031183 [0.002139, 0.060226] | 0.111122 [0.085977, 0.136268] |
| neutral drift | 0.017232 [-0.001924, 0.036389] | 0.038585 [0.001484, 0.075685] | 0.042880 [0.012080, 0.073680] |
| diversity archive | 0.004072 [-0.019785, 0.027929] | 0.085024 [0.018740, 0.151308] | 0.072246 [0.044141, 0.100351] |
| sampled lookahead | 0.018159 [0.000096, 0.036222] | 0.043954 [0.009543, 0.078365] | 0.058662 [0.035194, 0.082130] |
| independent search | 0.007326 [-0.012636, 0.027288] | 0.024969 [-0.000224, 0.050162] | 0.031584 [0.009171, 0.053997] |
| unscaffolded | -0.016505 [-0.030788, -0.002223] | 0.072198 [0.036486, 0.107909] | 0.148713 [0.119168, 0.178259] |

Pairwise sorting alone usually did not resolve a benefit. Constructor-orbit sorting alone helped more often, but independent search's interval just crossed zero. The fully integrated condition improved every source, and every orbit interaction interval was positive. For these arbitrary expressions, the two blocks were complementary: their joint value was greater than their separate contributions.

This contrasts with the overlapping, subadditive benefits in the same-dimensional supplied-area primary test. Integration is therefore not a single uniform mechanism with one universal effect size; it depends on the constructor's local symmetry and on interactions between feature blocks.

### Constructor rankings changed

The initial constructor's transformation was especially striking:

- current `dot`: log error 0.744448, mean \(R^2=-0.534445\), median \(R^2=0.174513\);
- full invariant `dot`: log error 0.481730, mean \(R^2=0.584498\), median \(R^2=0.632665\).

At budget 200, full invariant `dot` had the lowest mean log error of all searched sources. It remained best at budgets 500 and 1000. By contrast, independent search had been best under the current representation at budget 200.

This does not show that constructor search is useless. It shows that the Pilot 4e expressions were selected using a different, non-invariant development readout. Their relative advantages did not automatically transfer to the new integration foundation. Search rankings are conditional on the representation used to evaluate them.

## Family transfer

Current-minus-full-invariant mean log error at budget 200; positive values indicate improvement:

| Unseen family | Supplied | Initial | Greedy | Neutral | Archive | Lookahead | Independent | Unscaffolded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| convex radial | 0.2326 | 0.0670 | -0.0549 | -0.0219 | 0.0683 | 0.0042 | -0.0564 | 0.0269 |
| interior points | 0.0847 | 0.2877 | 0.2556 | 0.1293 | 0.2741 | 0.2270 | 0.1186 | 0.2556 |
| irregular radial | 0.0355 | 0.1847 | 0.1650 | 0.0562 | 0.1616 | 0.0554 | 0.0545 | 0.2022 |
| elongated | 0.1174 | 0.5115 | 0.1917 | 0.2312 | 0.1413 | 0.1965 | 0.1388 | 0.3329 |

These are supporting descriptive summaries, not additional confirmatory tests. Full integration improved supplied area and initial `dot` in every family. It also improved every searched source on elongated configurations, but greedy, neutral-drift, and independent-search constructors became slightly worse on convex-radial configurations. Lookahead's convex-radial change was nearly zero.

Supplied-area performance by family:

| Unseen family | Current mean \(R^2\) | Fully sorted mean \(R^2\) | Current log error | Fully sorted log error |
|---|---:|---:|---:|---:|
| convex radial | 0.424191 | 0.842877 | 0.562488 | 0.329933 |
| interior points | 0.830749 | 0.911875 | 0.344268 | 0.259566 |
| irregular radial | 0.838929 | 0.875689 | 0.336977 | 0.301449 |
| elongated | 0.840346 | 0.941807 | 0.332368 | 0.214934 |

The supplied constructor's worst fully sorted result at budget 200 still had \(R^2=0.743647\). This is a substantial robustness improvement over the broad current-representation failures. Nevertheless, the ordered reference remained stronger in every family, so invariant aggregation did not recover all ordered-environment performance.

### Remaining instability

Integration did not make every constructor robust:

- full neutral-drift search had improved mean log error but mean \(R^2=-0.701664\);
- its `abs(divide(dot,w2))` output produced \(R^2=-69.778386\) on interior points;
- full archive integration reduced the worst `abs(divide(w2,dot))` failure from \(R^2=-508.954728\) in the current representation to -3.986041, but did not eliminate it;
- most searched sources still had negative mean \(R^2\) on elongated configurations;
- full invariant `dot`, in contrast, reached mean \(R^2=0.4179\) on elongated configurations and had no result below -0.05 at budget 200.

The distinction between typical performance and catastrophic tails remains essential. Log-error improvement and mean-\(R^2\) improvement usually coincided, but not universally. No extreme result was removed.

## Stability and sample efficiency across budgets

The primary supplied-area advantage was positive with an interval excluding zero at every budget:

| Budget | Difference | 95% interval | Replicate wins |
|---:|---:|---:|---:|
| 25 | 0.109880 | [0.072846, 0.146913] | 0.90 |
| 50 | 0.091880 | [0.063048, 0.120713] | 0.95 |
| 100 | 0.108492 | [0.095833, 0.121152] | 1.00 |
| 200 | 0.117555 | [0.109967, 0.125143] | 1.00 |
| 500 | 0.118606 | [0.113641, 0.123571] | 1.00 |
| 1000 | 0.117573 | [0.113872, 0.121275] | 1.00 |

Mean log error for the fully invariant condition of each source:

| Budget | Supplied | Initial | Greedy | Neutral | Archive | Lookahead | Independent | Unscaffolded |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 25 | 0.4868 | 0.7027 | 0.8779 | 0.8344 | 0.8555 | 0.7690 | 0.8033 | 0.8789 |
| 50 | 0.4774 | 0.7272 | 0.7751 | 0.7454 | 0.7762 | 0.6930 | 0.7150 | 0.7893 |
| 100 | 0.3221 | 0.6483 | 0.6799 | 0.6639 | 0.6960 | 0.6247 | 0.6235 | 0.6585 |
| 200 | 0.2765 | 0.4817 | 0.5668 | 0.5724 | 0.5924 | 0.5368 | 0.5649 | 0.5209 |
| 500 | 0.2590 | 0.4367 | 0.5251 | 0.5061 | 0.5466 | 0.4962 | 0.5420 | 0.4762 |
| 1000 | 0.2537 | 0.4257 | 0.5180 | 0.4983 | 0.5350 | 0.4861 | 0.5359 | 0.4681 |

All 42 frozen-source/full-orbit comparisons—seven sources across six budgets—had positive intervals. This is broad supporting evidence that the integration benefit was not restricted to one carefully selected endpoint.

Low-budget instability nevertheless remained. At budget 25, every searched full-orbit source had negative mean \(R^2\), despite large log-error gains. Supplied full-sort mean \(R^2\) was 0.492805 at budget 25, compared with 0.901810 for the ordered current reference. At budget 1000, supplied full-sort reached 0.913220, still below the ordered reference's 0.974673. More training data and exact invariance both helped, but neither completely closed the transfer gap.

## Interpretation for the Generative Framework

Pilot 4f provides direct evidence for a distinction that earlier pilots could only suggest:

> Discovery identifies a potentially useful expression; integration determines whether that expression's information becomes effectively available under finite resources.

The same `abs(cross)` constructor produced markedly different capability under label-indexed and invariant aggregation. The same frozen `dot`, greedy, lookahead, archive, neutral-drift, independent, and unscaffolded expressions also changed performance without any further search. Integration therefore changes the effective capability set without changing the underlying expression grammar or the physical information in the configurations.

This is not information creation. Sorting and orbit aggregation preserve specified multisets of already computed values. Their benefit comes from removing arbitrary variation and making task-relevant regularities easier for the fixed learner to use. It is an improvement in **epistemic and practical availability**, not in the underlying geometric possibility.

### The foundation changes what search should select

The constructor-ranking reversal is as important as the aggregate performance gain. Pilot 4e selected expressions using non-invariant development features. Under that readout, independent and lookahead search were strongest. Under full invariant integration, initial `dot` was strongest at the primary endpoint.

Consequently, a stable integration foundation is not neutral with respect to development. It determines:

- which expressions appear development-useful;
- which valleys search must cross;
- which constructors are retained;
- whether an apparently discovered improvement survives downstream integration;
- whether earlier discoveries can serve as reliable scaffolding for later growth.

The next logical search experiment is therefore not simply to add more search mechanisms. It is to use the **same invariant integration rule during development scoring and final evaluation**, then repeat matched greedy, lookahead, and independent comparisons. That would test whether aligning search with the integration foundation produces constructors that outperform the invariant initial baseline.

The orbit representation remains a diagnostic foundation rather than an endpoint. A later engineering stage can test lower-dimensional symmetric statistics or learned permutation-invariant aggregation. Those practical representations should be compared against the exact orbit oracle rather than introduced without a reference.

## What Pilot 4f does and does not support

A defensible conclusion is:

> Holding constructors, data, targets, training orders, and learner fixed, permutation-invariant integration substantially improves held-out hull-area learning. Supplied area improves in a same-dimensional primary test, and every frozen constructor source improves under full local-orbit integration across all tested budgets. Integration therefore unlocks effective capability from existing expressions and changes the ranking of those expressions, while leaving family-specific failures, low-budget instability, and heavy tails partly unresolved.

The experiment does not establish:

- that sorting or orbit expansion is the optimal permanent representation;
- that all integration benefits are independent of feature dimensionality;
- that constructor search is unnecessary or universally harmful;
- that Pilot 4e's search rankings should transfer to a new development readout;
- complete recovery of ordered-environment performance;
- robust discovery or integration for every family and constructor;
- new constructor discovery, developmental scaffolding, descendant value, or open-endedness.

## Validation and reproduction

The two-replicate smoke run completed 1,632 permuted and 48 ordered evaluations. It reproduced 384 Pilot 4e current-representation rows and 48 Pilot 4d ordered-reference rows. No protocol rules or hypotheses were changed in response to smoke performance.

Final validation confirmed:

- 16,320 permuted and 480 ordered final evaluations;
- 640 frozen constructor-manifest rows;
- unique final keys and finite metrics throughout;
- 35 features for current and simple-sort conditions, and 135 for orbit conditions;
- all 28 required invariance checks passing with maximum discrepancy \(1.78\times10^{-15}\);
- all 12 expected simple-sort diagnostic violations retained;
- exact agreement between raw-result expressions and the constructor manifest;
- one primary comparison and 42 positive frozen full-orbit intervals across sources and budgets.

Current-representation reproduction used a scale-aware floating-point rule: absolute difference divided by the larger of one and the absolute previous value, with tolerance \(10^{-10}\). All 3,840 Pilot 4e current rows passed, with maximum scaled discrepancy \(2.44\times10^{-16}\). All 480 ordered Pilot 4d reference rows passed, with maximum scaled discrepancy \(1.11\times10^{-16}\). The largest absolute Pilot 4e discrepancy was \(7.28\times10^{-12}\) on an extreme-valued metric.

Run:

```bash
python3 generative_geometry_pilot4f.py --replicates 20 --output-dir ./pilot4f_output
```

The script performs no search. It requires the saved Pilot 4e search summary for frozen expressions and the Pilot 4d/4e raw results for reproduction audits. Paths are configurable through command-line arguments. Software versions and evaluation counts are recorded in `pilot4f_metadata.json`.

## Files

- [Pre-run protocol](Pilot_4f_Protocol.md)
- [Experiment script](generative_geometry_pilot4f.py)
- [Raw final evaluations](pilot4f_raw_results.csv)
- [Frozen constructor manifest](pilot4f_constructor_manifest.csv)
- [Invariance checks](pilot4f_invariance_checks.csv)
- [Overall summaries](pilot4f_summary_overall.csv)
- [Family summaries](pilot4f_summary_by_family.csv)
- [Paired comparisons](pilot4f_paired_comparisons.csv)
- [Aggregation interactions](pilot4f_aggregation_interactions.csv)
- [Supplied-area sample-efficiency figure](pilot4f_supplied_sample_efficiency.png)
- [Fully invariant comparison figure](pilot4f_invariant_comparisons.png)
- [Family-integration figure](pilot4f_family_integration.png)
- [Run metadata](pilot4f_metadata.json)
- [Full execution log](pilot4f_full_run.log)
- [Smoke execution log](pilot4f_smoke_run.log)
