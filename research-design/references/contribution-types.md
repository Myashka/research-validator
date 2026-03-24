# Contribution Types

Taxonomy of ML/AI research contributions, venue expectations, framing strategies, and presentation patterns.

## Contribution Taxonomy

| Type | Description |
|------|-------------|
| New method / algorithm / architecture | Novel technique solving an existing or new problem |
| New theoretical result / proof / bound | Formal analysis with provable guarantees |
| New dataset / benchmark | Resource enabling new evaluation or research direction |
| Empirical study / large-scale analysis | Systematic experiments revealing new understanding |
| Analysis of existing methods | "Why does X work?" — mechanistic or empirical explanation |
| Negative result / failure analysis | Important hypothesis disproven through rigorous testing |
| Position paper / survey | Structured overview or argument shaping community direction |

## Venue Expectations by Type

| Type | What Top Venues Expect |
|------|----------------------|
| Method | Strong baselines, ablations, multiple datasets, clear improvement, insight into WHY it works |
| Theory | Realistic assumptions, tight bounds, empirical validation connecting theory to practice |
| Dataset | Clear gap filled, baseline evaluations on the new resource, demonstrated community need |
| Empirical | Surprising findings, sufficient scale, reproducibility, actionable takeaways |
| Analysis | Actionable insights that change practice ("stop doing X", "do Y instead") |
| Negative | Thorough experiments, important hypothesis, honest reporting, lessons for future work |

## Framing Strategies

**Taxonomy approach** — Group related work into categories, show where your contribution fits.
"Methods for X fall into three families: A, B, C. We introduce a fourth approach that..."

**Contrast approach** — Explicitly differentiate from the closest prior work.
"Unlike X which does A, we do B because C — enabling D."

**Evolution approach** — Build a clear lineage showing your work as a natural progression.
"Building on X (which showed P), Y (which added Q), and Z (which extended R), we..."

**Gap approach** — Identify what the field is missing and fill it.
"Despite progress in X, nobody has addressed Y — which matters because Z."

## Title and Abstract Patterns

**Method paper:** "[Name]: [What It Does] via [How]"
Example: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"

**Analysis paper:** "[Finding]: [What We Discovered About X]"
Example: "Scaling Data-Constrained Language Models: On the Role of Repeated Data"

**Dataset paper:** "[Name]: A Benchmark for [Task]"
Example: "MMLU: Measuring Massive Multitask Language Understanding"

## 5-Second Test

A reader scanning the title should instantly understand:
1. What area this is in
2. What the contribution is

If the title requires domain context to parse, it fails. Jargon-heavy or overly clever titles lose readers at the first filter — and reviewers ARE the first filter.

## Contribution Falsifiability Test

For each stated contribution, verify:

| Question | Bad Example | Good Example |
|----------|------------|--------------|
| Is it specific enough to be proven wrong? | "A novel framework for..." | "Achieves X% on benchmark Y" |
| Is it measurable? | "Improves understanding of..." | "Reduces compute by Nx on task Z" |
| Does it match what's demonstrated? | Claims generality, tests one dataset | Claims and evidence aligned |

Vague contributions signal weak thinking. Specific contributions signal confidence.

## Abstract Structure

| Sentence | Purpose | Length |
|----------|---------|--------|
| 1 | Problem — what challenge exists | ~1 sentence |
| 2 | Gap — why current solutions fall short | ~1 sentence |
| 3-4 | Approach — what you do and how | 1-2 sentences |
| 5-6 | Result — concrete outcomes with numbers | 1-2 sentences |
| 7 | Implication — why this matters beyond your paper | ~1 sentence (optional) |

Every sentence earns its place. Cut anything that doesn't serve one of these five roles.
