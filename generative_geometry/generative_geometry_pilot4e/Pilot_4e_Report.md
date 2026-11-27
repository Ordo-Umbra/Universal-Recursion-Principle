# Generative Geometry — Pilot 4e Report

## Descendant Value, Neutral Drift, and Symmetry-Diverse Persistence

### Executive result

Pilot 4e produces a **negative primary result for symmetry-diverse persistence, a positive result for sampled descendant value, and an inconclusive primary-endpoint result for bounded neutral drift**.

At the pre-specified budget of 200 final-task training configurations:

- **Diversity archive versus greedy:** the paired log-error difference was -0.047636, with 95% interval [-0.123447, 0.028174]. The primary persistence-based scaffolding hypothesis therefore failed.
- **Sampled lookahead versus greedy:** the difference was 0.048499, with interval [0.021899, 0.075099]. Lookahead won in 17 of 20 replicates. Together with 245 accepted non-improving parent moves based on sampled descendant value, this satisfies the pre-specified positive descendant-value criterion.
- **Neutral drift versus greedy:** the difference was 0.035024, with interval [-0.001280, 0.071328]. Neutral drift also won in 17 of 20 replicates, but the interval crossed zero, so the pre-specified neutral-tolerance criterion was not met.
- **Independent search** had the lowest mean log error among searched representations. It significantly outperformed the archive, but its interval over lookahead included zero.
- **Supplied exact area** remained far superior to every discovered representation.

The archive's failure was not caused by insufficient exploration. Every archive run occupied all four symmetry classes, 74 of 80 selected outputs were structurally distant from the root, and exact area was encountered in 37 runs. Yet exact area remained the selected output in only one run, and rare ratio-constructor failures produced severe held-out errors. Breadth of exploration and persistence of alternative parents did not imply robust final integration.

The central positive finding is narrower and more precise:

> Explicit sampled evaluation of descendants can give a temporarily unrewarded constructor enough value to be retained as a parent, and this mechanism improved held-out performance relative to fixed-budget greedy search. This does not establish a general advantage over independent sampling, open-ended discovery, or reliable permutation-invariant learning.

## Experimental design

Pilot 4e used only the permuted environment introduced in Pilot 4d. Six point labels were independently permuted within every configuration, preserving point multisets and all geometric targets. Search used hull perimeter, compactness, and hull vertex count as development targets; convex-hull area remained the held-out final target.

All searches began from `dot` and used the same finite grammar, numerical validity gates, stability gates, and robust development score. The exact-area reference, `abs(cross)`, required at least two mutations from the root. Compactness remained acknowledged area-related development guidance.

Six search mechanisms received exactly **500 proposal evaluations per run**:

1. greedy immediate improvement;
2. bounded neutral drift;
3. a four-class symmetry-diversity archive;
4. sampled two-step lookahead;
5. independent expression sampling;
6. unscaffolded direct-root search.

For lookahead, each sampled child received the value

\[
V(c)=\max\left(U(c),\max_{g\in G(c)}U(g)\right),
\]

where \(G(c)\) contains up to four sampled grandchildren. A child could become the next parent when \(V(c)\) exceeded the current parent's score, even if the child's own score did not improve. A valuable grandchild did not replace that child as parent. Every child and grandchild consumed budget, and all methods retained the highest development-scoring valid expression encountered, including the root.

The full design contained 20 replicates, four held-out-family folds, 80 runs per search condition, 240,000 search proposals, and 4,800 final model evaluations. Final fitting budgets were nested at 25, 50, 100, 200, 500, and 1000 configurations. The protocol, hypotheses, thresholds, primary comparison, and interpretation rules were fixed before implementation and testing.

## Performance at the primary endpoint

Budget-200 held-out hull-area performance:

| Representation | Mean \(R^2\) | Median \(R^2\) | 10th-percentile \(R^2\) | Mean log error |
|---|---:|---:|---:|---:|
| supplied area | 0.733554 | 0.828701 | 0.433276 | 0.394025 |
| independent search | -0.162471 | 0.337872 | -2.516223 | 0.628791 |
| sampled lookahead | -0.221696 | 0.313882 | -2.607448 | 0.657625 |
| neutral drift | -0.381660 | 0.268844 | -2.648062 | 0.671101 |
| greedy | -0.365089 | 0.256100 | -2.672394 | 0.706124 |
| unscaffolded | -0.386134 | 0.212836 | -2.277786 | 0.725322 |
| diversity archive | -7.073295 | 0.219380 | -2.812973 | 0.753761 |
| initial | -0.534445 | 0.174513 | -2.814678 | 0.744448 |
| pairwise | -0.438824 | 0.216863 | -2.605589 | 0.724567 |
| raw quadratic | -4.552301 | -3.629599 | -9.442515 | 1.148172 |

Log error is \(\log(1+\mathrm{NRMSE})\); lower values are better. Mean \(R^2\) is retained to expose heavy-tailed failures, while the pre-specified paired inference uses the bounded-growth log transformation. The searched representations generally had positive median \(R^2\), but their negative means show that substantial family-specific failures remained.

## Pre-specified paired comparisons at budget 200

For each focus method \(M\) and comparator \(C\), the reported difference is

\[
D=L_C-L_M,
\]

so positive values favor the focus method. Intervals are two-sided 95% Student-\(t\) intervals over 20 replicate means, with four test-family folds averaged within each replicate.

| Focus method | Comparator | Difference | 95% interval | Replicate wins | Exact sign \(p\) | Result |
|---|---|---:|---:|---:|---:|---|
| diversity archive | greedy | -0.047636 | [-0.123447, 0.028174] | 0.50 | 1.000000 | **Primary hypothesis fails** |
| sampled lookahead | greedy | 0.048499 | [0.021899, 0.075099] | 0.85 | 0.002577 | **Positive descendant-value result** |
| neutral drift | greedy | 0.035024 | [-0.001280, 0.071328] | 0.85 | 0.002577 | Interval criterion not met |
| diversity archive | neutral drift | -0.082660 | [-0.171573, 0.006252] | 0.30 | 0.115318 | No archive advantage |
| diversity archive | sampled lookahead | -0.096135 | [-0.179801, -0.012469] | 0.10 | 0.000402 | Lookahead superior |
| independent search | diversity archive | 0.124969 | [0.034373, 0.215566] | 0.90 | 0.000402 | Independent search superior |
| independent search | sampled lookahead | 0.028834 | [-0.010409, 0.068076] | 0.65 | 0.263176 | No significant interval advantage |
| unscaffolded | diversity archive | 0.028438 | [-0.052094, 0.108971] | 0.30 | 0.115318 | No significant interval advantage |
| diversity archive | supplied area | -0.359735 | [-0.442185, -0.277286] | 0.00 | 0.000002 | Supplied area superior |
| sampled lookahead | supplied area | -0.263600 | [-0.298355, -0.228845] | 0.00 | 0.000002 | Supplied area superior |
| greedy | initial | 0.038324 | [0.018563, 0.058085] | 1.00 | 0.000002 | Greedy improves on the root |

Secondary comparisons were not adjusted for multiplicity. Exact sign tests and win fractions are supporting summaries; they do not replace the interval-based interpretation criteria. In particular, neutral drift's consistent replicate wins do not convert its zero-crossing primary-endpoint interval into a positive result.

## Search activity and structural dependency

| Condition | Accepted moves per run | Non-improving moves per run | Moves worse by more than \(10^{-4}\) per run | Exact terminal area | Exact area encountered | Outputs at root distance \(\geq2\) |
|---|---:|---:|---:|---:|---:|---:|
| greedy | 1.5500 | 0.0000 | 0.0000 | 0 / 80 | 5 / 80 | 40 / 80 |
| neutral drift | 137.4250 | 135.4625 | 0.6250 | 1 / 80 | 5 / 80 | 79 / 80 |
| diversity archive | 6.5000 | 3.5625 | 1.1000 | 1 / 80 | 37 / 80 | 74 / 80 |
| sampled lookahead | 4.8375 | 3.0625 | 1.0500 | 2 / 80 | 21 / 80 | 79 / 80 |
| independent search | 5.7125 | 0.0000 | 0.0000 | 3 / 80 | 77 / 80 | 79 / 80 |
| unscaffolded | 1.8625 | 0.0000 | 0.0000 | 0 / 80 | 0 / 80 | 0 / 80 |

Root distance is capped at zero, one, or two, where two includes all greater distances. It measures whether the selected expression lies outside the direct root neighborhood, not the number of historical revisions. Deep outputs demonstrate structural activity, but they do not by themselves establish causal scaffolding or good held-out performance.

### Symmetry-diverse persistence: active exploration without an advantage

The archive mechanism operated as intended:

- all 80 runs occupied all four symmetry classes;
- 240 acceptances filled previously empty class slots;
- 280 acceptances improved an occupied class;
- 285 accepted moves did not improve the immediate parent score by more than the tolerance;
- 88 accepted moves were worse than the parent by more than \(10^{-4}\).

Thus, the failed primary comparison cannot be attributed to an inactive archive or a failure to populate its descriptors. The archive preserved alternative parents and accepted non-improving moves, but this did not produce a held-out advantage over greedy search.

Exact-area encounters make the distinction especially clear. The archive encountered `abs(cross)` in 37 runs but selected it in only one. In the other area-encountering runs, either another expression had a higher robust development score or lexical tie-breaking selected a different expression. The archive's broad exploration therefore did not ensure that a geometrically apt constructor became the final output.

The final representation also contained only one selected 20-component constructor block alongside the 15 pairwise features. Maintaining four parent classes during search did not provide four simultaneous constructor blocks at final integration. Archive diversity must therefore not be conflated with multi-block representational integration.

### Archive instability and heavy tails

No extreme observations were removed. The archive's budget-200 mean \(R^2=-7.073295\) was strongly affected by a small number of catastrophic ratio constructors:

- the worst result was `abs(divide(w2,dot))`, with \(R^2=-508.954728\) and NRMSE 22.582177;
- `abs(divide(cross,dot))` produced \(R^2=-18.471495\) in another run;
- ten archive outputs contained division and had mean \(R^2=-53.688341\), compared with -0.414003 for the 70 non-division outputs.

These division-stratified summaries are descriptive and post hoc; they are not a new exclusion criterion. They identify the same stability problem seen in earlier pilots: development usefulness and valid gating do not guarantee robust downstream integration.

The instability was not merely a cosmetic property of mean \(R^2\). The archive also had worse mean log error than greedy at budget 200, and its pre-specified comparison against lookahead was significantly negative. Its median \(R^2\), however, remained positive, showing why means, medians, log errors, and complete raw results must all be retained.

### Sampled lookahead: descendant value crosses immediate-score valleys

Lookahead accepted 387 children as new parents. Every accepted parent move had the child role; no grandchild was incorrectly promoted directly to parent. Among these accepted children:

- 245 did not improve the immediate parent score by more than \(10^{-4}\);
- 84 were worse than the immediate parent by more than \(10^{-4}\);
- all 245 non-improving moves passed acceptance through sampled descendant value.

These are direct lineage records of the mechanism the experiment was designed to test. A child could be retained because a sampled grandchild was valuable even when strict greedy improvement would have rejected the child.

Descendants also contributed directly to final outputs. The selected expression was encountered as a grandchild only in 54 runs, as both child and grandchild in 18, and as a child only in eight. This pattern is consistent with the two-step proposal distribution supplying many of the best archived expressions. It also means the positive result concerns the complete sampled-lookahead mechanism, not solely the long-term benefit of changing parents.

Lookahead's advantage was not explained solely by rediscovering exact area:

- exact area was encountered in 21 lookahead runs and selected terminally in only two;
- runs encountering exact area had mean log error 0.656956;
- runs not encountering exact area had mean log error 0.657864.

The nearly identical means show that exact-area encounters do not account for the overall lookahead result. Other discovered constructors and descendant-guided paths supplied the benefit. This stratification is descriptive; it does not identify which individual accepted move caused a particular final gain.

### Neutral drift: substantial movement, qualified performance evidence

Neutral drift accepted 10,994 moves in total, averaging 137.425 per run. Of these, 50 were worse than the immediate parent by more than \(10^{-4}\). Its tabu rule rejected 65.405% of proposals as previously visited expressions; those proposals still consumed the fixed budget.

At budget 200, neutral drift beat greedy in 17 of 20 replicates and had a positive mean paired difference. The 95% interval, however, was [-0.001280, 0.071328]. Under the protocol, this is not a positive neutral-tolerance result. The contrast between the sign test and interval is preserved rather than resolved by changing the criterion after seeing the data.

At larger fitting budgets, neutral drift's intervals did exclude zero: the differences were 0.039858 [0.012037, 0.067679] at budget 500 and 0.041970 [0.012768, 0.071172] at budget 1000. These are supporting secondary results, not replacements for the inconclusive primary endpoint.

### Independent search remains competitive

Independent search encountered exact area in 77 of 80 runs, although it selected exact area terminally in only three. It significantly outperformed the diversity archive and had numerically lower mean log error than lookahead at every final fitting budget. Its budget-200 advantage over lookahead, 0.028834, had interval [-0.010409, 0.068076] and therefore was not statistically resolved.

Consequently, Pilot 4e supports a specific advantage of sampled lookahead over its greedy baseline, but **not a general superiority of developmental parent chaining over direct independent sampling**. The methods have different proposal distributions by design, and proposal count is matched rather than runtime or memory.

## Transfer to unseen environment families

Mean hull-area \(R^2\) at budget 200:

| Unseen family | Greedy | Neutral drift | Diversity archive | Lookahead | Independent | Unscaffolded | Supplied area |
|---|---:|---:|---:|---:|---:|---:|---:|
| convex radial | 0.3408 | 0.2987 | -25.1597 | 0.4147 | 0.2354 | 0.1702 | 0.4242 |
| interior points | 0.2997 | -0.4209 | -0.1579 | 0.2342 | 0.4958 | 0.2997 | 0.8307 |
| irregular radial | 0.2764 | 0.6239 | -0.4892 | 0.6009 | 0.6818 | 0.2087 | 0.8389 |
| elongated | -2.3773 | -2.0284 | -2.4864 | -2.1366 | -2.0629 | -2.2232 | 0.8403 |

Mean log error at budget 200, where lower is better:

| Unseen family | Greedy | Neutral drift | Diversity archive | Lookahead | Independent | Unscaffolded | Supplied area |
|---|---:|---:|---:|---:|---:|---:|---:|
| convex radial | 0.5891 | 0.5988 | 0.7265 | 0.5659 | 0.6145 | 0.6377 | 0.5625 |
| interior points | 0.6070 | 0.6650 | 0.6609 | 0.6263 | 0.5014 | 0.6070 | 0.3443 |
| irregular radial | 0.6052 | 0.4493 | 0.5782 | 0.4581 | 0.4274 | 0.6353 | 0.3370 |
| elongated | 1.0232 | 0.9714 | 1.0494 | 0.9802 | 0.9719 | 1.0213 | 0.3324 |

These family summaries are supporting descriptive analyses rather than additional confirmatory tests.

Lookahead had lower mean log error than greedy on convex-radial, irregular-radial, and elongated families, but not on interior points. Neutral drift showed the same qualitative direction on elongated and irregular-radial families, while performing worse on convex-radial and interior-points families. The archive had lower mean log error than greedy only on irregular-radial configurations; its extreme convex-radial mean \(R^2\) reflects the ratio-constructor failures described above.

Elongated configurations remained the dominant common failure case. Every searched representation had strongly negative mean \(R^2\) there, whereas supplied area retained mean \(R^2=0.8403\). Supplied area also had the lowest mean log error in every family. Search-mechanism improvements therefore did not remove the underlying family-transfer and representation-integration bottleneck.

## Stability and sample efficiency across budgets

Mean log error across nested final-task budgets:

| Budget | Greedy | Neutral drift | Diversity archive | Lookahead | Independent | Unscaffolded | Supplied area |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 25 | 1.1930 | 1.1838 | 1.2407 | 1.0295 | 1.0143 | 1.3722 | 0.5967 |
| 50 | 0.9094 | 0.8883 | 1.0114 | 0.8412 | 0.7909 | 0.9615 | 0.5693 |
| 100 | 0.7543 | 0.7165 | 0.8149 | 0.6961 | 0.6643 | 0.7783 | 0.4306 |
| 200 | 0.7061 | 0.6711 | 0.7538 | 0.6576 | 0.6288 | 0.7253 | 0.3940 |
| 500 | 0.6814 | 0.6416 | 0.6964 | 0.6387 | 0.6120 | 0.6958 | 0.3776 |
| 1000 | 0.6742 | 0.6323 | 0.6805 | 0.6313 | 0.6030 | 0.6870 | 0.3713 |

Lookahead's paired advantage over greedy was positive with an interval excluding zero at **every** budget. The differences were 0.163581 at budget 25, 0.068218 at 50, 0.058253 at 100, 0.048499 at 200, 0.042736 at 500, and 0.042990 at 1000. The effect was largest at the smallest fitting budget, although all searched methods remained unstable there.

Neutral drift did not have a zero-excluding interval at budgets 25, 50, 100, or 200, but did at 500 and 1000. The archive did not have a positive zero-excluding interval over greedy at any budget. Independent search retained the lowest numerical mean log error among searched methods at every budget, without a resolved interval advantage over lookahead.

Untransformed low-budget means expose additional instability. At budget 25, archive mean \(R^2\) was -1887.037975 and neutral-drift mean \(R^2\) was -33.5653; even lookahead and independent search had negative means of -4.3896 and -6.1266. At budget 1000, mean \(R^2\) remained negative for every searched representation, while supplied area reached 0.7652. More final-task data reduced error but did not fully repair weak or unstable discovered features.

## Interpretation for the Generative Framework

Pilot 4e separates four notions that should not be collapsed:

1. **Encounter:** an expression is proposed during search.
2. **Parent retention:** an expression remains available for later mutations.
3. **Output selection:** an expression has the highest development score encountered.
4. **Robust integration:** the selected expression improves held-out learning without catastrophic failures.

The archive was strong on encounter and structural exploration, but this did not yield output selection or robust integration. Lookahead explicitly valued reachable descendants and outperformed greedy search, yet remained below supplied area and did not significantly outperform independent search. Neutral drift generated extensive parent movement, but activity alone did not satisfy the primary performance criterion.

The positive lookahead result gives a concrete computational interpretation of option or descendant value: the development value of an expression need not equal its immediate score, because an expression also changes which later expressions become accessible. In this experiment, making that value explicit through sampled grandchildren helped cross immediate-score valleys.

This is evidence for the specified mechanism in a finite synthetic grammar, not evidence for unrestricted open-endedness. The descendants, grammar, development tasks, descriptors, gates, and learner were researcher-supplied. The experiment also did not isolate descendant-guided parent acceptance from the broader child-and-grandchild proposal distribution; that would require a separate ablation.

Most importantly, the result does not show that permutation-invariant aggregation or multi-block representational integration has been solved. Those remain distinct bottlenecks. A future test of permutation-invariant aggregation should manipulate the downstream learner or feature aggregation directly rather than infer such integration from search archives.

## What Pilot 4e does and does not support

A defensible conclusion is:

> Under a matched 500-proposal budget in the permuted geometric environment, sampled two-step descendant evaluation improved held-out performance over greedy parent chaining and produced documented non-improving parent moves accepted for their descendant value. Bounded neutral drift showed a consistent directional benefit at the primary endpoint but failed its interval criterion. Symmetry-diverse persistence produced broad exploration without an overall performance advantage, while independent search remained highly competitive. Constructor encounter, developmental retention, final selection, and robust integration are therefore experimentally distinct stages.

The experiment does not establish:

- positive persistence-based scaffolding from the symmetry archive;
- a positive primary-endpoint neutral-drift interval;
- general superiority of lineage search over independent sampling;
- reliable exact-area discovery or selection;
- robust transfer to elongated configurations;
- permutation-invariant downstream aggregation;
- simultaneous integration of multiple discovered constructors;
- open-ended discovery, autonomous environmental design, or metaphysical conclusions.

## Validation and reproduction

Pre-run descriptor checks confirmed the exact endpoint-exchange convention and coordinate-scaling interpretation. In particular, `cross` was antisymmetric with homogeneity degree two, `abs(cross)` was symmetric nonnegative with degree two, and `sqrt_abs(cross)` was symmetric nonnegative with degree one.

The two-replicate smoke run logged 24,000 proposals, exactly 500 per run. All eight smoke archive runs occupied all four classes, and all accepted lookahead parents were children. No exact-area terminal discoveries occurred in smoke; no thresholds or hypotheses were changed in response.

Final-output validation confirmed:

- 240,000 proposal rows and 4,800 final-result rows;
- 480 search summaries, with 80 runs per condition;
- exactly 500 consecutively numbered proposals in every run;
- 12,631 accepted-move rows reconciled with accepted-move totals;
- unique representation/budget/replicate/family final rows;
- finite MSE, NRMSE, \(R^2\), and log-error values throughout;
- exact agreement between selected search outputs and final evaluation expressions;
- all 387 accepted lookahead parent moves recorded in the child role;
- all 80 full-run archives at four-class occupancy.

Run:

```bash
python3 generative_geometry_pilot4e.py --replicates 20 --output-dir ./pilot4e_output
```

All seeds are deterministic. Proposal count is matched, not runtime or memory. Software versions and parameter values are recorded in `pilot4e_metadata.json`.

## Files

- [Pre-run protocol](Pilot_4e_Protocol.md)
- [Experiment script](generative_geometry_pilot4e.py)
- [Raw final evaluations](pilot4e_raw_results.csv)
- [Complete proposal history](pilot4e_proposal_history.csv)
- [Accepted moves](pilot4e_accepted_moves.csv)
- [Search summaries and terminal expressions](pilot4e_search_summary.csv)
- [Terminal-constructor summary](pilot4e_constructor_summary.csv)
- [Overall summaries](pilot4e_summary_overall.csv)
- [Family summaries](pilot4e_summary_by_family.csv)
- [Paired comparisons](pilot4e_paired_comparisons.csv)
- [Sample-efficiency figure](pilot4e_sample_efficiency.png)
- [Family-transfer figure](pilot4e_family_transfer.png)
- [Structural-depth figure](pilot4e_structural_depth.png)
- [Valley-activity figure](pilot4e_valley_activity.png)
- [Run metadata](pilot4e_metadata.json)
- [Full execution log](pilot4e_full_run.log)
