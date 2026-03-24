# Conference Standards

Venue-specific review criteria and acceptance patterns for ML/AI conferences.

## Review Forms by Venue

### NeurIPS

| Dimension | Scale |
|-----------|-------|
| Soundness | 1-4 |
| Contribution | 1-4 |
| Presentation | 1-4 |
| Overall | 1-10 |
| Confidence | 1-5 |

### ICML

| Dimension | Scale |
|-----------|-------|
| Correctness | Qualitative |
| Technical Novelty | Qualitative |
| Experimental Evaluation | Qualitative |
| Clarity | Qualitative |
| Overall | Numeric |

### ICLR (OpenReview)

| Dimension | Scale |
|-----------|-------|
| Soundness | 1-4 |
| Presentation | 1-4 |
| Contribution | 1-4 |
| Rating | 1-10 |
| Confidence | 1-5 |

### ACL / EMNLP

| Dimension | Scale |
|-----------|-------|
| Soundness | Qualitative |
| Substance | Qualitative |
| Overall | Numeric |
| Recommendation | Accept / Reject |

### CVPR

| Dimension | Scale |
|-----------|-------|
| Technical Quality | Qualitative |
| Novelty | Qualitative |
| Significance | Qualitative |
| Clarity | Qualitative |
| Overall | Numeric |

### AAAI

| Dimension | Scale |
|-----------|-------|
| Soundness | Qualitative |
| Novelty | Qualitative |
| Significance | Qualitative |
| Clarity | Qualitative |
| Overall | 1-10 |

## Score Interpretation

Applies to venues using 1-10 overall scales (NeurIPS, ICLR, and similar).

| Range | Meaning |
|-------|---------|
| 1-2 | Fundamentally flawed |
| 3-4 | Below acceptance bar |
| 5 | Borderline |
| 6-7 | Above bar |
| 8+ | Strong accept / oral candidate |

## Acceptance Statistics

| Venue | Acceptance Rate |
|-------|-----------------|
| NeurIPS | ~25-26% |
| ICML | ~25-28% |
| ICLR | ~30-32% |
| ACL | ~20-25% |
| EMNLP | ~22-25% |
| CVPR | ~25% |
| AAAI | ~20-24% |
| Workshop | ~40-60% |

## What Gets Accepted

Venue-specific patterns that correlate with acceptance.

| Venue | Key Acceptance Drivers |
|-------|----------------------|
| NeurIPS | Values novelty + significance; tolerates incomplete experiments for truly novel ideas |
| ICML | Values rigor + soundness; strong baselines expected |
| ICLR | Values novelty + clarity; open review pushes transparency |
| ACL | Values reproducibility + comprehensive evaluation |
| EMNLP | Values empirical rigor + practical NLP contributions; accepts shorter papers |
| CVPR | Values strong visual results + comprehensive ablations; demo/visual quality matters |
| AAAI | Broad AI scope; values interdisciplinary work + real-world applications |
| Workshop | Values novelty of direction over completeness; work-in-progress accepted |

## What Gets Rejected

Common rejection reasons across venues, ordered by frequency.

| Reason | Description |
|--------|-------------|
| Missing strong baselines | Most common -- reviewers expect comparison against current SOTA |
| Incremental contribution | Insufficient novelty over existing work |
| Overclaiming | Claims not supported by experimental evidence |
| Missing related work | Unaware of or ignoring key prior work |
| Poor writing | Unclear contribution statement, hard to follow |
| Statistical issues | No error bars, single runs, no significance tests |

## Area Chair Decision Heuristics

- If 3 reviewers agree -- follow consensus
- If split (accept/reject) -- AC examines specific arguments, not just scores
- Rebuttals that address concrete concerns with evidence move the needle
- Rebuttals that argue with reviewers or dismiss concerns rarely help
- Champion papers (one strong advocate) can survive mixed reviews if the argument is compelling

## Venue-Specific Weight Adjustments

Adjusts the default scoring formula per venue. All rows sum to 1.0.

| Venue | Novelty | Soundness | Experiments | Significance | Clarity | Reproducibility |
|-------|---------|-----------|-------------|--------------|---------|-----------------|
| NeurIPS | 0.30 | 0.15 | 0.15 | 0.20 | 0.10 | 0.10 |
| ICML | 0.20 | 0.25 | 0.25 | 0.15 | 0.10 | 0.05 |
| ICLR | 0.30 | 0.15 | 0.15 | 0.20 | 0.10 | 0.10 |
| ACL | 0.20 | 0.15 | 0.25 | 0.15 | 0.10 | 0.15 |
| EMNLP | 0.20 | 0.15 | 0.25 | 0.15 | 0.10 | 0.15 |
| CVPR | 0.20 | 0.20 | 0.25 | 0.15 | 0.10 | 0.10 |
| AAAI | 0.20 | 0.20 | 0.20 | 0.20 | 0.10 | 0.10 |
| Workshop | 0.30 | 0.15 | 0.15 | 0.10 | 0.15 | 0.15 |

**Usage:** Multiply each dimension score (from the scorecard) by the venue weight, then sum for the venue-adjusted overall score. When computing the multi-venue scorecard, apply each venue's row independently to produce per-venue adjusted scores.

## Stage-Adaptive Scoring Weights

Scoring dimensions and weights change based on research_stage:

### Stage: idea
Primary dimensions (higher weight):
- Novelty: x1.2 (is the idea genuinely new?)
- Experimental Design Quality: x1.0 (replaces "Experiments" -- evaluate design, not results)
- Significance: x1.0 (does this matter?)
- Soundness: x0.8 (is the approach logically sound?)

Secondary dimensions (lower weight):
- Clarity: x0.6 (ideas are rough, penalize less)
- Reproducibility: x0.4 (no experiments to reproduce yet)

Key rule: Do NOT penalize absence of experimental results.
Dimension rename: "Experiments" -> "Experimental Design Quality" for idea stage.
Projected Score is PRIMARY, Current Score is secondary (informational).

### Stage: preliminary_results
All dimensions at standard weight.
Both Current Score and Projected Score shown equally.
Experimental results evaluated but incompleteness noted, not penalized.

### Stage: draft
All dimensions at standard weight.
Current Score is PRIMARY.
Full paper evaluation -- missing experiments ARE penalized.

### Stage weights and venue weights

Stage weights multiply on top of venue weights (NeurIPS, ICML, etc.) -- they are compatible and multiplicative. To compute the final adjusted score for a dimension: `dimension_score * venue_weight * stage_weight`. This ensures that both venue expectations and research maturity are reflected in the scoring.
