# Experimental Design

Evaluation methodology, baseline selection, and statistical rigor requirements for ML/AI experiments.

## Baseline Selection Rules

1. Always include current SOTA on the benchmarks you use
2. Include a "simple but strong" baseline (linear model, bag-of-words, etc.)
3. For new datasets: show the task is non-trivial (random baseline, majority class)
4. If improving method X: include X as a baseline under fair comparison
5. Use identical conditions across all methods (data splits, preprocessing, compute budget)

## Statistical Rigor Checklist

| # | Requirement |
|---|-------------|
| 1 | Multiple runs (min 3, preferred 5) with different random seeds |
| 2 | Report mean +/- std for all results |
| 3 | Significance tests (paired t-test, bootstrap) for close results |
| 4 | Confidence intervals reported |
| 5 | Improvement falls outside variance range |
| 6 | Hyperparameter sensitivity analysis reported |
| 7 | No train/test data leakage |
| 8 | Consistent evaluation protocol across all methods |

**Scoring:** <4/8 = weak | 4-6/8 = adequate | 7-8/8 = strong

## Ablation Design Patterns

- Vary one component at a time
- Compare full model vs each "without-X" variant
- If N components, minimum N+1 rows in ablation table
- Every component must be shown necessary (removing it hurts performance)

## Reproducibility Checklist

**Theory / Proofs:** assumptions stated, complete proofs provided, steps independently verifiable

**Experiments:** hyperparameters listed, training details (optimizer, LR, schedule), preprocessing described, data splits specified, random seeds fixed, hardware reported, number of runs stated, error bars included

**Code and Data:** code available or release planned, data available or access described, library versions specified

## Common Experimental Pitfalls

| # | Pitfall | Why It Kills a Paper |
|---|---------|---------------------|
| 1 | Unfair comparison (different compute, data augmentation) | Reviewers reject on soundness |
| 2 | Data leakage between train/test | Invalidates all results |
| 3 | Hyperparameter tuning on test set | Inflated numbers, no generalization |
| 4 | Cherry-picked qualitative examples | Hides failure modes |
| 5 | Reporting best run instead of mean | Masks variance, overstates gains |
| 6 | Missing error analysis / failure cases | Suggests lack of understanding |

## Fair Comparison Guidelines

- Same data splits across all methods
- Same preprocessing pipeline
- Same compute budget (or normalize results by compute)
- Same hyperparameter search budget
- Re-run baselines in your setup -- do not copy numbers from other papers

## Metric Selection by Task Type

| Task Type | Standard Metrics |
|-----------|-----------------|
| Classification | accuracy, F1, precision/recall, AUC-ROC |
| Generation | BLEU, ROUGE, BERTScore, human eval |
| Retrieval | MRR, NDCG, Recall@K |
| Regression | MSE, MAE, R-squared |
| Detection | mAP, IoU |

Always report standard metrics for the task even if proposing custom ones.

## Baseline Sufficiency Matrix

```
                    Included?   Fair Comparison?   Current?
SOTA method 1       [ ]            [ ]               [ ]
SOTA method 2       [ ]            [ ]               [ ]
Strong simple BL    [ ]            [ ]               [ ]
Ablation (no X)     [ ]            [ ]               [ ]
Ablation (no Y)     [ ]            [ ]               [ ]
Random baseline     [ ]            [ ]               [ ]
```

- Missing SOTA = automatic weakness
- Missing simple baseline = reviewer suspicion
- Missing ablation = cannot prove components are necessary
- Unfair comparison = methodology flaw

## Claims-Evidence Gap Analysis

```
CLAIM: "[claim text]"
Required Evidence:
  - [what evidence is needed]
Currently Available:
  - [ ] [evidence item]: YES/NO
GAP: [what's missing]
EFFORT TO CLOSE: [S/M/L]
IMPACT ON SCORE: [how much fixing this gap helps]
```

Fill one block per major claim. Any claim with GAP = non-empty is a vulnerability reviewers will target.
