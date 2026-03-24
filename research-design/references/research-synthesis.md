# Research Synthesis Protocol

How to synthesize raw agent output (Waves 1-3) into two deliverables: `literature-review.md` and `novelty-assessment.md`.

**When to read:** After waves complete (Wave 1+2+3 in Full mode, Wave 1+2 in Fast Track), before writing synthesis deliverables.

## Synthesis Flow
1. **Collect** -- read all raw files from `{project}/01-discovery/raw/`:
   - `core-predecessors.md` (A1), `methodological-relatives.md` (A2), `concurrent-work.md` (A3)
   - `sota-analysis.md` (B1), `open-problems.md` (B2)
   - `venue-analysis.md` (C1), `reviewer-landscape.md` (C2)
2. **Patterns** -- identify recurring themes, methods, datasets, and claims across agents
3. **Contradictions** -- flag where agents disagree (e.g., A1 says novel, A3 finds concurrent work)
4. **Implications** -- what do the patterns and contradictions mean for the proposal?
5. **Confidence** -- rate each synthesis claim using the confidence dashboard below

---

## Template: literature-review.md
```markdown
# Literature Review
**Phase:** 3 — Literature Research | **Project:** {project-name} | **Date:** {date} | **Confidence:** {High/Medium/Low}
---
## 1. Executive Summary
<!-- 5 sentences: (1) field context, (2) dominant approaches, (3) SOTA status, (4) where proposal fits, (5) overall opportunity assessment -->

## 2. Top-5 Closest Prior Work (from A1)
| # | Paper [Verified ID] | Year | Similarity | Key Difference | Threat Level |
|---|---------------------|------|------------|----------------|--------------|
| 1 | | | | | {High/Med/Low} |

## 3. Methodological Landscape (from A2)
- **Method:** {method_name}
- **Applications found:** {domains/tasks where method is used}
- **Success patterns:** {when it works} | **Failure patterns:** {when it doesn't}
- **Transferable lessons:** {key takeaways for proposal}

## 4. Concurrent Work Status (from A3)
**Novelty Race Status:** {No race / Emerging competition / Active race}
**Most threatening paper:** {title} -- {why}
**URGENT:** {N} | **WARNING:** {N} | **INFO:** {N}
**Recommended response:** {proceed / accelerate / pivot / differentiate}

## 5. SOTA Summary (from B1)
| Benchmark | Metric | SOTA Method | Score | Trend | Proposal Target |
|-----------|--------|-------------|-------|-------|-----------------|
| | | | | {improving/plateau/saturated} | |
**What counts as competitive:** {minimum bar description}

## 6. Open Problems Alignment (from B2)
| Open Problem | Community Priority | Proposal Addresses? | Evidence |
|--------------|--------------------|---------------------|----------|
| | {High/Med/Low} | {Direct/Partial/No} | |
**Community priority match:** {High/Medium/Low}

## 7. Venue Fitness (from C1, C2)
- **Topic traction at {venue}:** {growing/stable/declining} | **Papers (2-3 yr):** {N}
- **Quality bar:** {minimum novelty and experimental scope expected}
- **Reviewer preferences:** {what reviewers value, common complaints}
- **Fit assessment:** {strong fit / acceptable / marginal / poor fit}

## 8. Data Gaps
- [ ] {gap}: {what is missing, where to look}
---
## Flags
**Red Flags:** {list or "None identified"}
**Yellow Flags:** {list or "None identified"}
```

---

## Template: novelty-assessment.md
```markdown
# Novelty Assessment
**Phase:** 3 — Literature Research | **Project:** {project-name} | **Date:** {date} | **Confidence:** {High/Medium/Low}
---
## 1. Novelty Classification
**Type:** {New method / New theory / Empirical study / New application / New dataset / Analysis / Combination}
**Justification:** {1-2 sentences}

## 2. Top-5 Prior Work Comparison
| # | Paper [Verified ID] | Their Approach | Their Result | Shared | Different |
|---|---------------------|----------------|--------------|--------|-----------|
| 1 | | | | | |

## 3. Delta Analysis
**Genuinely new:** {delta with evidence}
**NOT new (existing components):** {what exists, where, reference}

## 4. Concurrent Work Impact
**Active competitors:** {count from A3 URGENT + WARNING}
**Impact on novelty:** {no impact / weakens but survivable / potentially fatal}
**Differentiation strategy:** {how to position against concurrent work}

## 5. Novelty Score
**Score: {1-10}** <!-- 10=paradigm shift, 8=major direction, 6=solid method, 5=incremental+insight, 4=engineering, 3=trivial combo, 1=published -->
**Evidence:** {2-3 sentences justifying score}

## 6. Risk Factors
- {risk}: {description, likelihood, mitigation}

## 7. Data Gaps
- [ ] {gap}: {what is missing, impact on novelty claim}
---
## Flags
**Red Flags:** {list or "None identified"}
**Yellow Flags:** {list or "None identified"}
```

---

## Cross-Document Connections Protocol
When writing both deliverables, link insights across files:
- **Prior work (lit-review sec 2)** feeds **comparison table (novelty sec 2)** -- same papers, different lens
- **Concurrent work (lit-review sec 4)** feeds **concurrent impact (novelty sec 4)**
- **SOTA (lit-review sec 5)** sets the bar for **novelty score (novelty sec 5)**
- **Open problems (lit-review sec 6)** validates **novelty type (novelty sec 1)**
- **Data gaps** from both documents merge into the **gap aggregation** below

Use `see literature-review.md sec N` / `see novelty-assessment.md sec N` for cross-references.

---

## Confidence Dashboard Template
| Claim | Source Agent | Source Tier | Confidence | Data Age |
|-------|-------------|-------------|------------|----------|
| {claim} | {A1/A2/B1/etc.} | {Published/Preprint/Verified/Unverified} | {High/Med/Low} | {months old} |

Flag claims with Low confidence or data older than 12 months for re-verification.

---

## Gap Aggregation
Collect ALL data gaps from every raw file and both synthesis documents:
| # | Gap | Source File | Impact | Suggested Action |
|---|-----|-------------|--------|------------------|
| 1 | {description} | {raw file or synthesis doc} | {High/Med/Low} | {what to do} |

High-impact gaps MUST be resolved before the Novelty Gate (Phase 4). Medium gaps go in the action plan. Low gaps are documented but non-blocking.
