# Generative Geometry — Pilot 3b

## Audit and Strengthening Report

### Executive result

Pilot 3b confirms the original relational-curvature heuristic’s advantage over repeated initial measurements and uniform random exploration. It does **not** confirm that the heuristic dominates stronger deterministic sampling controls.

The revised experiment shows a conditional result:

- Systematic coverage of unexplored intervals is a major source of reconstruction performance.
- Relational curvature provides additional value in many smooth and narrow-feature conditions.
- Widest-interval sampling is often superior in oscillatory and high-noise conditions.
- The original heuristic becomes more competitive at the largest tested budget.
- Pure curvature and pure gradient selection perform poorly without adequate coverage pressure.
- Adding 25% random exploration does not improve the original heuristic in this experiment.

This is a useful refinement of the mechanism, not a failed replication. Pilot 3’s original 79-of-81 result was correct relative to its four included strategies. Pilot 3b shows that the conclusion changes when the strategy set is expanded.

## Experimental changes

The revised implementation retains the original landscapes, observation model, interpolation rule, and relational-curvature score. It adds the following controls and methodological changes.

### Strategies

1. **repeat_initial** — the original fixed strategy; repeatedly samples the initial rays.
2. **random** — samples new angles uniformly.
3. **widest_interval** — bisects the largest unexplored angular interval.
4. **largest_gradient** — bisects the interval with the largest absolute secant slope.
5. **curvature_only** — selects using neighboring slope changes without width weighting.
6. **weighted_curvature** — uses interval width squared times neighboring slope change.
7. **relational_curvature** — retains the original score: width squared times `(0.20 + curvature)`.
8. **hybrid** — uses relational curvature with 25% random exploration.

### Paired and nested design

- A landscape now depends only on its family and replicate. It is shared across initial ray counts, budgets, noise levels, and strategies.
- Initial noisy observations are shared across strategies.
- Standard-normal noise streams are matched across noise levels where the trajectory permits.
- Each strategy generates one 36-measurement trajectory, evaluated at nested budgets 12, 24, and 36.
- Every strategy uses the same periodic piecewise-linear reconstruction rule.
- Evaluation is against the noiseless function on a 1,200-point grid.

### Output and analysis

The experiment saves:

- 38,880 replicate-level result rows;
- 648 condition/strategy summaries;
- 567 paired comparisons;
- exact condition winners;
- normalized and unnormalized error;
- paired 95% confidence intervals for NMSE differences;
- metadata and software versions;
- family, budget, and noise figures.

Normalized MSE is defined as:

\[
\mathrm{NMSE}=\frac{\mathrm{MSE}(\hat f,f)}{\operatorname{Var}(f)}.
\]

Paired intervals are two-sided t intervals on replicate-level NMSE differences. A negative focal-minus-comparator difference favors relational curvature. These intervals are exploratory and are not adjusted for multiple comparisons.

## Validation checks

The complete run passed the following checks:

- All 38,880 expected raw observations are present.
- All MSE, NMSE, and maximum-error values are finite.
- Every family/replicate landscape has exactly one seed and one truth variance across all associated conditions.
- At zero noise, repeated-initial reconstruction is invariant across nested budgets, apart from floating-point differences below approximately `1.1e-16`.
- A separate three-replicate smoke run completed successfully before the full experiment.

## Aggregate results

Each condition receives equal weight. NMSE is the preferred cross-landscape measure because it accounts for differences in landscape variance.

| Strategy | Mean condition MSE | Mean condition NMSE | Median condition NMSE |
|---|---:|---:|---:|
| widest_interval | 0.005614 | 0.128572 | 0.066785 |
| relational_curvature | 0.005878 | 0.141845 | 0.067471 |
| weighted_curvature | 0.006309 | 0.154060 | 0.066716 |
| hybrid | 0.006701 | 0.160875 | 0.072360 |
| random | 0.013746 | 0.306450 | 0.217378 |
| curvature_only | 0.024084 | 0.535739 | 0.296447 |
| largest_gradient | 0.028019 | 0.601721 | 0.371839 |
| repeat_initial | 0.036149 | 0.750206 | 0.495238 |

Relational curvature has approximately 54% lower aggregate mean NMSE than random. Its aggregate mean NMSE is approximately 10% higher than widest-interval sampling. This aggregate should not be interpreted as establishing that widest-interval sampling is generally superior: the family interaction is substantial.

## Exact condition winners

Winners are determined by the lowest mean NMSE across 60 replicates in each of 81 conditions.

| Strategy | Exact condition wins |
|---|---:|
| weighted_curvature | 31 |
| relational_curvature | 27 |
| widest_interval | 23 |
| All other strategies | 0 |

The original heuristic therefore remains competitive, but no single strategy dominates the strengthened benchmark.

## Paired statistical comparisons

The table reports how often the relational-curvature-minus-comparator paired 95% interval excludes zero, separated by direction.

| Comparator | Relational significantly better | Relational significantly worse | Interval includes zero |
|---|---:|---:|---:|
| repeat_initial | 81 | 0 | 0 |
| random | 81 | 0 | 0 |
| largest_gradient | 81 | 0 | 0 |
| curvature_only | 81 | 0 | 0 |
| hybrid | 46 | 0 | 35 |
| weighted_curvature | 20 | 15 | 46 |
| widest_interval | 39 | 18 | 24 |

The advantage over random, repeated initial sampling, pure gradient, and pure curvature is consistent across all 81 conditions. Comparisons with weighted curvature and widest-interval sampling are context-dependent.

## Landscape-family interaction

Mean NMSE for the three leading strategies:

| Family | Relational curvature | Weighted curvature | Widest interval |
|---|---:|---:|---:|
| narrow_features | 0.0822 | 0.0877 | 0.0998 |
| oscillatory | 0.3084 | 0.3404 | 0.2455 |
| smooth_mixed | 0.0349 | 0.0341 | 0.0404 |

For relational curvature versus widest-interval sampling:

- **Narrow features:** relational is significantly better in 20 conditions and significantly worse in none.
- **Smooth mixed:** relational is significantly better in 17 conditions and significantly worse in one.
- **Oscillatory:** relational is significantly better in two conditions and significantly worse in 17.

This is the central substantive finding. Relational information is most useful when local variation helps identify meaningful unresolved structure. In rapidly oscillating landscapes, local slope changes can be ambiguous or misleading, and direct coverage becomes more reliable.

## Budget effects

Mean NMSE across the other conditions:

| Budget | Random | Widest interval | Weighted curvature | Relational curvature | Hybrid |
|---:|---:|---:|---:|---:|---:|
| 12 | 0.4566 | 0.2276 | 0.2684 | 0.2510 | 0.2804 |
| 24 | 0.2785 | 0.0909 | 0.1248 | 0.1123 | 0.1281 |
| 36 | 0.1842 | 0.0673 | 0.0689 | 0.0623 | 0.0741 |

Widest-interval sampling leads on average at budgets 12 and 24. Relational curvature leads slightly at budget 36. Against widest-interval sampling at budget 36, relational curvature is significantly better in 15 conditions and significantly worse in two.

One plausible interpretation is that relational estimates become more informative as the sampled structure becomes denser. This experiment establishes the interaction, but not yet that causal explanation. A dedicated resolution-dependence experiment would be needed to test it.

## Noise effects

Mean NMSE:

| Noise SD | Random | Widest interval | Weighted curvature | Relational curvature | Hybrid |
|---:|---:|---:|---:|---:|---:|
| 0.00 | 0.2543 | 0.0765 | 0.0994 | 0.0861 | 0.1001 |
| 0.03 | 0.2671 | 0.0896 | 0.1128 | 0.1021 | 0.1182 |
| 0.10 | 0.3979 | 0.2196 | 0.2501 | 0.2374 | 0.2644 |

At the highest noise level, widest-interval sampling has the lowest mean NMSE. Relational curvature is significantly better than widest-interval sampling in only two high-noise conditions and significantly worse in seven. Noisy finite-difference relationships can become unreliable, especially when intervals become small.

## Interpreting the score ablations

The results support three conclusions about the original heuristic.

### 1. Coverage is indispensable

Pure gradient and pure curvature perform poorly. Width-only sampling is strong. Any future relational mechanism should therefore be compared with systematic coverage as a mandatory baseline.

### 2. Curvature is not merely redundant with coverage

Relational curvature significantly beats widest-interval sampling in 39 conditions, especially in the narrow-feature and smooth-mixed families. It also has the lowest aggregate error at budget 36. Coverage alone therefore does not explain every relational benefit.

### 3. The `0.20` offset has a context-dependent effect

Compared with weighted curvature without the offset, full relational curvature is significantly better in 20 conditions and significantly worse in 15. It is particularly helpful in oscillatory conditions, where it significantly outperforms weighted curvature in 18 conditions and loses in none. It more often reduces performance in smooth and narrow-feature conditions.

The offset appears to trade local relational selectivity for additional coverage pressure. That trade-off should be investigated explicitly rather than assumed to be universally beneficial.

## Supported conclusion

A defensible summary for the paper is:

> Across the tested synthetic environments, relational-curvature sampling consistently improved reconstruction relative to repeated initial measurements, uniform random exploration, pure gradient selection, and pure curvature selection. However, deterministic interval coverage was competitive and sometimes superior. Relational curvature was most advantageous in smooth and narrow-feature landscapes and at the largest tested budget, whereas widest-interval sampling was generally stronger in oscillatory and high-noise conditions. These results identify a conditional interaction between coverage and relational guidance rather than a universal advantage for either mechanism.

Pilot 3b still tests reconstruction of predefined functions. It does not demonstrate relational generation, recursive representation development, expansion of physical degrees of freedom, or the broader Generative Framework.

## Recommended next steps

1. **Freeze the strategies and test unseen landscape families.** Include discontinuous, piecewise-linear, multiscale, and deliberately deceptive periodic environments. Avoid tuning on these held-out families.
2. **Retain widest-interval and weighted-curvature controls in future pilots.** They are necessary for separating coverage, curvature, and the offset’s contribution.
3. **Test the resolution hypothesis directly.** Vary measurement density over a wider range and determine whether relational guidance predictably becomes more valuable as local slope estimates improve.
4. **Develop noise-aware relational sampling separately.** High-noise results suggest that repeated observations, uncertainty estimates, or regularized slope estimates may be necessary.
5. **Carry the methodological discipline into Pilot 4.** Use equal-information baselines, matched resources, generic feature constructors, held-out tasks, and ablations. Do not interpret reconstruction performance as evidence of representational generation.

## Reproduction

Run:

```bash
python3 generative_geometry_pilot3b.py --replicates 60 --output-dir ./pilot3b_output
```

A quick validation can be run with `--replicates 3`. All seeds are deterministic. See `pilot3b_metadata.json` for configuration and software versions.

## Files

- [Revised experiment script](generative_geometry_pilot3b.py)
- [Raw replicate-level results](pilot3b_raw_results.csv)
- [Condition summaries](pilot3b_condition_summary.csv)
- [Paired comparisons](pilot3b_paired_comparisons.csv)
- [Exact condition winners](pilot3b_condition_winners.csv)
- [Aggregate results](pilot3b_aggregate.csv)
- [Family figure](pilot3b_family_nmse.png)
- [Nested-budget figure](pilot3b_budget_nmse.png)
- [Noise figure](pilot3b_noise_nmse.png)
- [Run metadata](pilot3b_metadata.json)
