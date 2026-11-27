# Generative Geometry — Pilot 4d Report

## Permutation-Randomized Geometry and Multi-Step Scaffolding

### Executive result

Pilot 4d is a **negative result for the pre-specified overall scaffolding advantage, despite a substantial increase in multi-step refinement**.

Randomly permuting point labels made exact unsigned area unreachable by a single mutation from `dot`, while preserving every geometric target. The manipulation changed lineage behavior substantially:

- multi-step refined lineages increased from 10 of 80 ordered runs to 34 of 80 permuted runs;
- exact `dot → cross → abs(cross)` paths occurred in four permuted runs;
- however, 40 permuted runs accepted no revision at all;
- terminal exact-area discovery did not increase materially: four permuted runs versus three ordered runs;
- refined search did not significantly outperform unscaffolded search in the permuted arm;
- the permuted-minus-ordered interaction interval included zero;
- independent search outperformed refined search under the pre-specified permuted-arm log-error comparison.

The central finding is therefore:

> Making an intermediate constructor structurally necessary is not sufficient to make greedy refinement traverse it. When the first mutation is not independently rewarded, refinement can stall. Multi-step activity increases under permutation, but the overall value of parent chaining does not.

A post hoc lineage-stratified analysis suggests that refined search often helps when multi-step revision actually occurs. This does not rescue the failed primary test, but it identifies a precise mechanism for the next experiment: neutral or temporarily unrewarded intermediates require search beyond strict greedy improvement.

## Experimental design

### Paired arms

Both arms used exactly the same underlying point configurations, rotations, targets, environment families, data splits, and final training orders.

- **Ordered:** reproduced Pilot 4c's input point order.
- **Permuted:** independently permuted the six point labels within every configuration before computing features.

Hull area, perimeter, compactness, and hull vertex count are invariant to this relabeling. Validation confirmed identical targets and identical point multisets across arms.

The ordered arm reproduced every Pilot 4c final result exactly.

### Search and controls

Every search began with `dot` and used Pilot 4c's grammar, depth limit, gates, robust development score, and acceptance threshold. The development targets were perimeter, compactness, and hull count; final hull-area labels were excluded from search.

The four search conditions were:

- refined parent-chained search;
- independent guided expression sampling;
- unscaffolded search restricted to direct variants of `dot`;
- random lineage search without development-label guidance.

Candidate-evaluation counts were matched across controls within every arm/replicate/fold. The complete run contains 160 search runs, 58,424 proposals, 171 accepted refined revisions, and 7,680 final model evaluations.

### Primary statistical endpoint

At budget 200, the primary test was refined versus unscaffolded search in the permuted arm using paired replicate means of:

\[
L=\log(1+\mathrm{NRMSE}).
\]

Differences are comparator minus refined, so positive values favor refinement. Intervals use 20 replicates, averaging four test-family folds within each replicate.

## Performance at budget 200

| Arm | Representation | Mean \(R^2\) | Median \(R^2\) | 10th-percentile \(R^2\) |
|---|---|---:|---:|---:|
| ordered | initial | -0.5118 | 0.1532 | -2.5738 |
| ordered | refined | 0.6320 | 0.7728 | 0.2910 |
| ordered | unscaffolded | 0.6578 | 0.7690 | 0.3338 |
| ordered | supplied area | 0.9684 | 0.9723 | 0.9474 |
| permuted | initial | -0.5344 | 0.1745 | -2.8147 |
| permuted | refined | -0.3888 | 0.1765 | -2.5934 |
| permuted | independent search | -0.2593 | 0.2956 | -2.5172 |
| permuted | unscaffolded | -0.3861 | 0.2128 | -2.2778 |
| permuted | random lineage | -348.8599 | 0.0050 | -154.0536 |
| permuted | supplied area | 0.7336 | 0.8287 | 0.4333 |
| permuted | raw quadratic | -4.5523 | -3.6296 | -9.4425 |

Permutation made the final learning problem substantially harder for most fixed-basis representations. Supplied area remained effective, although its performance was lower than in the ordered arm. Raw quadratic features performed particularly poorly under random relabeling.

## Pre-specified paired comparisons

### Permuted arm at budget 200

| Comparator | Log-error difference | 95% interval | Replicate win fraction | Interpretation |
|---|---:|---:|---:|---|
| initial | 0.0268 | [0.0144, 0.0393] | 1.00 | Refinement improves on the initial constructor |
| random lineage | 0.4584 | [0.2462, 0.6706] | 0.95 | Development guidance is beneficial |
| unscaffolded | 0.0077 | [-0.0069, 0.0223] | 0.45 | **Primary scaffolding test fails** |
| independent search | -0.0541 | [-0.1001, -0.0080] | 0.40 | Independent search has the log-error advantage |
| supplied area | -0.3236 | [-0.3413, -0.3058] | 0.00 | Supplied area remains far superior |
| pairwise | 0.0069 | [-0.0045, 0.0184] | 0.40 | No significant advantage over pairwise |
| raw quadratic | 0.4305 | [0.4159, 0.4452] | 1.00 | Refined search is much better than raw quadratic |

### Arm interaction

The permuted-minus-ordered refinement advantage was:

\[
0.0062,\qquad 95\%\,\mathrm{CI}=[-0.0215,\,0.0339].
\]

The interaction is not significant. Consequently, the stronger claim that permutation increases the overall value of parent chaining is not supported.

## Lineage activity changed, but discovery did not reliably improve

### Revision counts

| Accepted revisions | Ordered runs | Permuted runs |
|---:|---:|---:|
| 0 | 0 | 40 |
| 1 | 70 | 6 |
| 2 | 7 | 30 |
| 3 | 3 | 4 |

Permutation produced a bifurcation: half of permuted runs made no accepted revision, while 34 engaged in two or three revisions. The paired increase in multi-step activity was significant under the pre-specified exact McNemar analysis:

- both arms multi-step: 5 run pairs;
- ordered only: 5;
- permuted only: 29;
- neither: 41;
- exact \(p=3.86\times10^{-5}\).

By contrast, terminal exact-area counts were three in ordered and four in permuted, with no shared area-positive run pairs and exact McNemar \(p=1.0\). Increased revision activity therefore did not translate into increased terminal area discovery.

### Permuted refinement paths

The most frequent paths were:

| Path | Runs |
|---|---:|
| `dot` — no accepted revision | 40 |
| `dot → v2 → sqrt_abs(v2)` | 8 |
| `dot → w2 → sqrt_abs(w2)` | 7 |
| `dot → cross → abs(cross)` | 4 |
| `dot → u2 → sqrt_abs(u2)` | 4 |
| `dot → sqrt_abs(dot) → sqrt_abs(w2)` | 2 |
| `dot → abs_diff(dot,v2)` | 2 |
| `dot → sqrt_abs(dot) → sqrt_abs(u2)` | 2 |
| all other paths | 11 |

Exact area was accepted as an intermediate in five permuted runs and remained terminal in four. In the fifth, refinement continued to `add(abs(cross),u2)`.

Many apparently multi-step lineages still ended in expressions directly accessible from the root, such as `sqrt_abs(v2)`. Revision count alone is therefore not a valid measure of obligatory scaffolding; the terminal expression's dependency on the intermediate path matters.

## Where refined search helped: exploratory lineage stratification

The following analysis is **post hoc** and is not part of the primary claim.

Among 34 permuted multi-step runs:

- refined search had lower log error than unscaffolded search in 26;
- the mean unscaffolded-minus-refined log-error difference was 0.0436;
- the median difference was 0.0255.

Among 40 runs with no accepted revision, the corresponding mean was -0.0216, and refined search won only 20%. Six one-revision runs were exact ties.

All four runs terminating in exact `abs(cross)` had lower refined than unscaffolded log error. Their refined mean \(R^2\) was 0.5352, compared with -0.4374 for non-area terminal constructors. This exactly matched supplied-area performance in the same four folds; it was below supplied area's global mean because exact area was discovered only in a selected subset of runs.

This pattern is consistent with a benefit concentrated in successful multi-step trajectories, offset by frequent stalled or unproductive trajectories. Because the strata are defined by search outcomes, they are selection-dependent and cannot establish the overall causal advantage. They motivate a pre-specified follow-up rather than a revised interpretation of Pilot 4d.

## Why greedy refinement stalls

The intended exact-area path requires:

```text
dot → cross → abs(cross)
```

Under random point relabeling, the sign of `cross` is arbitrary across configurations. The intermediate can therefore be less development-useful than it was under consistent angular ordering. Since Pilot 4d accepts a child only when its robust development score improves by more than \(10^{-4}\), a neutral or temporarily worse `cross` step cannot be retained for its later value.

The 40 no-revision runs are direct evidence that this failure mode is common. Independent search can propose `abs(cross)` directly and found eight terminal area constructors in the permuted arm, compared with four for refined search. This helps explain independent search's significant log-error advantage.

The limitation is therefore not simply an insufficient mutation grammar or evaluation budget. It is the strict local improvement rule: **the search cannot value a parent solely for the descendants it makes reachable.**

## Transfer to unseen families in the permuted arm

Mean hull-area \(R^2\) at budget 200:

| Unseen family | Initial | Refined | Independent | Unscaffolded | Supplied area |
|---|---:|---:|---:|---:|---:|
| convex radial | 0.2545 | 0.3684 | 0.3281 | 0.1702 | 0.4242 |
| interior points | 0.1783 | 0.1783 | 0.2624 | 0.2997 | 0.8307 |
| irregular radial | 0.1895 | 0.2652 | 0.5199 | 0.2087 | 0.8389 |
| elongated | -2.7601 | -2.3671 | -2.1475 | -2.2232 | 0.8403 |

Refinement improved mean performance over the initial constructor in three families but not interior points, where half of permuted runs remained at `dot`. Elongated configurations remained the dominant failure condition for all searched representations. Supplied area was the only consistently strong representation across all four families.

## Stability across budgets

Permuted-arm mean \(R^2\):

| Budget | Initial | Refined | Independent | Unscaffolded | Supplied area |
|---:|---:|---:|---:|---:|---:|
| 25 | -10.3933 | -6.4448 | -7.6004 | -17.2398 | 0.1965 |
| 50 | -1.8295 | -1.1567 | -1.4877 | -1.8994 | 0.3333 |
| 100 | -0.7707 | -0.5140 | -1.1313 | -0.6118 | 0.6733 |
| 200 | -0.5344 | -0.3888 | -0.2593 | -0.3861 | 0.7336 |
| 500 | -0.4254 | -0.3119 | -0.2091 | -0.2597 | 0.7573 |
| 1000 | -0.3813 | -0.2802 | -0.1710 | -0.2200 | 0.7652 |

Permutation reduced stability as well as average performance. Refined search improved with budget but remained negative in mean \(R^2\) even at 1000. The gates continued to exclude trivial and pathological expressions, but they could not compensate for weak constructor discovery or the harder permutation-invariant learning problem.

## What Pilot 4d supports

A defensible conclusion is:

> Random point relabeling significantly increases multi-step refinement activity and occasionally enables the intended two-step path to exact area. However, strict improvement-guided parent chaining frequently stalls when the required intermediate is not independently rewarded. Refined search does not outperform unscaffolded search overall, the refinement advantage does not significantly change across arms, and independent search discovers exact area more often in the permuted setting. Structural necessity alone is therefore insufficient for developmental scaffolding; the search mechanism must also be able to preserve or explore temporarily unrewarded intermediates.

The experiment does not establish:

- an overall causal advantage of parent chaining;
- permutation-enabled scaffolding;
- reliable exact-area rediscovery;
- superiority over independent search;
- robust permutation-invariant learning from discovered constructors;
- open-ended discovery or autonomous environmental design.

## Recommended next stage

The next experiment should directly compare search mechanisms for crossing development-score valleys:

1. **Greedy parent chaining:** the current Pilot 4c/4d rule.
2. **Beam or archive search:** retain several valid parents, including some that do not improve the incumbent immediately.
3. **Two-step lookahead:** evaluate whether a parent enables a valuable grandchild before rejecting it.
4. **Neutral-step allowance:** permit bounded acceptance of equal or slightly worse expressions, with a fixed complexity and evaluation budget.

These mechanisms must receive matched candidate evaluations and the same final held-out evaluation. A stronger scaffolding test should also distinguish terminal constructors that genuinely require an intermediate from multi-step paths that could have been reached directly from the root.

The central hypothesis would be that **developmental value resides not only in a constructor's immediate score, but also in the future constructors it makes accessible**. Pilot 4d makes that hypothesis concrete and shows why greedy selection cannot test it adequately.

## Reproduction

Run:

```bash
python3 generative_geometry_pilot4d.py --replicates 20 --output-dir ./pilot4d_output
```

A two-replicate smoke run is available with `--replicates 2`. All seeds are deterministic. Validation confirmed target and point-multiset invariance across arms, exact-area reachability in two mutations, matched proposal budgets, output counts, and exact numerical replication of Pilot 4c in the ordered arm.

## Files

- [Pre-run protocol](Pilot_4d_Protocol.md)
- [Experiment script](generative_geometry_pilot4d.py)
- [Raw final evaluations](pilot4d_raw_results.csv)
- [Complete proposal history](pilot4d_proposal_history.csv)
- [Accepted refinements](pilot4d_accepted_refinements.csv)
- [Search summaries and terminal expressions](pilot4d_search_summary.csv)
- [Terminal-constructor summary](pilot4d_constructor_summary.csv)
- [Overall summaries](pilot4d_summary_overall.csv)
- [Family summaries](pilot4d_summary_by_family.csv)
- [Paired comparisons](pilot4d_paired_comparisons.csv)
- [Arm interactions](pilot4d_arm_interactions.csv)
- [Paired lineage comparisons](pilot4d_lineage_arm_comparisons.csv)
- [Ordered sample-efficiency figure](pilot4d_sample_efficiency_ordered.png)
- [Permuted sample-efficiency figure](pilot4d_sample_efficiency_permuted.png)
- [Ordered family-transfer figure](pilot4d_family_transfer_ordered.png)
- [Permuted family-transfer figure](pilot4d_family_transfer_permuted.png)
- [Refinement-count figure](pilot4d_revision_counts.png)
- [Ordered revision-path figure](pilot4d_revision_paths_ordered.png)
- [Permuted revision-path figure](pilot4d_revision_paths_permuted.png)
- [Run metadata](pilot4d_metadata.json)
