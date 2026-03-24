# Output Guidelines

## Standard File Header

```
# [Document Title]
**Phase:** [phase number and name]
**Project:** [project-name]
**Date:** [generation date]
**Confidence:** [High / Medium / Low]
---
```

## Standard File Footer

```
---
## Flags
**Red Flags:**
- [list or "None identified"]
**Yellow Flags:**
- [list or "None identified"]
## Sources
- [key sources with verification status]
```

## Cross-Phase Referencing

Good: `See 01-discovery/synthesis.md > "BERT variants dominate" [Published]` -- explicit path, specific finding, label.

Bad: "As mentioned earlier, there are related works." -- no path, no specifics, no label.

## Quality Examples

**Literature review -- BAD:**
> Several papers address this problem. The area is well-studied with many approaches.

**Literature review -- GOOD:**
> 3 papers directly address cross-lingual transfer for low-resource NER:
> - Bari et al. (2020) achieve 71.2 F1 on WikiAnn using zero-shot transfer [Published]
> - Wu & Dredze (2019) show mBERT underperforms by 15+ F1 on distant languages [Published]
> - No work found combining adapter tuning with cross-lingual NER [Verified via Semantic Scholar, 2024-01]

**Scorecard -- BAD:**
> Novelty: Good. The approach seems new and interesting.

**Scorecard -- GOOD:**
> Novelty: 6/10. Core idea (adapter-based transfer) exists [Pfeiffer et al., 2020, Published]. Novel combination with language-family clustering has no direct precedent [Verified]. Incremental over MAD-X [Pfeiffer et al., 2021] rather than fundamentally new. [Assessment]

## Final Assessment Dashboard

Print in conversation at skill completion. Use the stage-appropriate template below.

### Dashboard: draft and preliminary_results stages

```
═══════════════════════════════════════════════
 RESEARCH PROPOSAL ASSESSMENT
═══════════════════════════════════════════════
 Title:           [from intake]
 Target Venue:    [venue + year]
 Research Stage:  [preliminary_results / draft]
 Novelty:         [X/10] [rationale]
 Soundness:       [X/10] [rationale]
 Experiments:     [X/10] [rationale]
 Significance:    [X/10] [rationale]
 Clarity:         [X/10] [rationale]
 Reproducibility: [X/10] [rationale]
 OVERALL:         [X/10]
 VERDICT:         [GO / CONDITIONAL / NO-GO]
 CONFIDENCE:      [High / Medium / Low]
 Top Strength:    [one line]
 Top Weakness:    [one line]
 Critical Action: [one line]
 Files generated: [N]
 Directory:       [path]
═══════════════════════════════════════════════
```

### Dashboard: idea stage

For idea stage, the dashboard evaluates POTENTIAL, not completeness.
"Experiments" is replaced with "Experimental Design Quality."
Projected Score is PRIMARY; Current Score is secondary/informational.

```
═══════════════════════════════════════════════
 RESEARCH PROPOSAL ASSESSMENT
═══════════════════════════════════════════════
 Title:           [from intake]
 Target Venue:    [venue + year]
 Research Stage:  idea
 Novelty:                      [X/10] [rationale]
 Soundness:                    [X/10] [rationale]
 Experimental Design Quality:  [X/10] [rationale]
 Significance:                 [X/10] [rationale]
 Clarity:                      [X/10] [rationale]
 Reproducibility:              [X/10] [rationale]
 ───────────────────────────────────────────
 Projected Score: [X/10]  ← PRIMARY
 Current Score:   [X/10]  (informational — idea stage)
 ───────────────────────────────────────────
 VERDICT:         [GO / CONDITIONAL / NO-GO]
                  [GO = worth pursuing]
                  [CONDITIONAL = refine before experiments]
                  [NO-GO = fundamental issues]
 CONFIDENCE:      [High / Medium / Low]
 Top Strength:    [one line]
 Top Weakness:    [one line]
 Critical Action: [one line]
 Files generated: [N]
 Directory:       [path]
═══════════════════════════════════════════════
```

**Field definitions:**
- **Novelty** -- how new is this vs existing work (from Phase 4 novelty assessment)
- **Soundness** -- is the methodology correct and claims supported (from Phase 6)
- **Experiments** -- are experiments sufficient to validate claims (from Phase 6); for idea stage, replaced by **Experimental Design Quality** (evaluate proposed design, not results)
- **Significance** -- does this matter to the field (from Phase 7 contribution framing)
- **Clarity** -- can the idea be communicated clearly (from Phase 1 intake + Phase 7)
- **Reproducibility** -- can others replicate this (from Phase 6 methodology review)
- **Projected Score** -- estimated score if experiments succeed as designed (idea stage PRIMARY)
- **Current Score** -- score based on what exists now (draft stage PRIMARY, idea stage informational)
- **VERDICT** -- GO (submit/pursue), CONDITIONAL (fix specific issues first), NO-GO (fundamental problems)
- **CONFIDENCE** -- how certain we are in this assessment given available evidence

## Handling Pivots

When the user changes direction mid-assessment:
- Do NOT restart from scratch
- Update intake with `## Pivot Notes` section documenting what changed and why
- Re-run only affected phases (novelty, methodology, or both)
- Keep old output as `[filename].pre-pivot.md`
- Log pivot in PROGRESS.md with timestamp
