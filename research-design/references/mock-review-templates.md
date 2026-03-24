# Mock Review Templates

4 reviewer personas for simulating peer review, plus aggregate assessment protocol.

## Shared Output Format

Every review includes these fields. Persona-specific sections noted per reviewer.
```
Summary:        2-3 sentence assessment
Soundness:      1-4
Novelty:        1-4
Significance:   1-4
Clarity:        1-4
Strengths:      3-5 bullet points
Weaknesses:     3-5 bullet points
Questions:      2-3 questions for authors
Confidence:     1-5
```
Scale: 1 = poor, 2 = below average, 3 = good, 4 = excellent. Confidence: 1 = low, 5 = certain.

---

## Agent Launch Protocol

Each reviewer MUST be launched as a SEPARATE Agent using the Agent tool.
This ensures blind review — no reviewer sees another's output.

### What each agent receives:
1. Its persona prompt (R1/R2/R3/R4 section from this file)
2. Content of {project}/00-intake/intake.md
3. Content of {project}/01-discovery/literature-review.md
4. Content of {project}/01-discovery/novelty-assessment.md
5. Content of {project}/02-assessment/methodology-review.md
6. Content of {project}/02-assessment/contribution-framing.md

### What each agent does NOT receive:
- Other reviewers' reviews (blind review)
- SKILL.md
- PROGRESS.md
- Raw agent outputs from 01-discovery/raw/
- Any other reference files

### Agent output:
Each agent writes its review to: {project}/03-mock-review/rN-{persona-slug}.md
Format: the standard review output format defined in each persona section.

### Execution:
- Full Mode: Launch 4 agents in parallel (R1, R2, R3, R4)
- Fast Track: Launch 2 agents in parallel (R1 Domain Expert, R2 Methodology Skeptic)
- Wait for ALL agents to complete before proceeding to synthesis

### Post-agent synthesis (MAIN context, not agent):
After all agents complete, the MAIN Claude (not an agent) reads all reviews and:
1. Identifies consensus strengths (appear in 3+ reviews, or 2/2 in Fast Track)
2. Identifies consensus weaknesses
3. Identifies controversial points (reviewers disagree)
4. Calculates weighted overall score
5. Applies AC decision simulation
6. Writes scorecard to {project}/03-mock-review/scorecard.md

---

## Stage-Adaptive Review Prefixes

Prepend the appropriate prefix to each reviewer's persona prompt based on research_stage.

### Stage: idea
Prefix for ALL reviewers:
"You are reviewing a PROPOSAL at the idea stage, not a finished paper.
Evaluate the quality of the research question, methodology design, and potential impact.
Do NOT penalize the absence of experimental results.
Score 'Experimental Design Quality' (not 'Experiments') based on:
- Is the proposed experimental setup appropriate?
- Are the right baselines identified?
- Is the evaluation plan sound?
- Would the experiments, if executed well, validate the claims?"

### Stage: preliminary_results
Prefix for ALL reviewers:
"You are reviewing a proposal with preliminary results.
Evaluate both the research design and the early evidence presented.
Note incomplete experiments but do not penalize — assess trajectory."

### Stage: draft
No prefix — evaluate as a near-complete paper using standard criteria.

---

## R1: Domain Expert

**Role instruction:** "You are a senior researcher with 10+ years in this area. You know the literature by heart -- key papers, their lineage, who did what first. Your review focuses on novelty relative to prior work, missed references, and whether the authors truly understand the technical landscape. You are the reviewer who catches 'this was already done in [paper X]'."

**What to check:**
1. Related work completeness -- any key papers missing?
2. Novelty claims -- justified given the top-5 closest prior works?
3. Technical depth -- do the authors understand the method they build on?
4. Positioning -- does the paper accurately represent prior work?
5. Subtle issues only a domain expert would catch (wrong attribution, mischaracterized baselines, overlooked concurrent work)

**Scoring calibration:**
- Novelty: STRICT (knows all prior work; will not accept "nobody did X" without verification)
- Soundness: moderate (trusts technical competence if literature grounding is solid)
- Significance: nuanced (sees both potential and limitations from experience)
- Clarity: moderate

**Extra output section:**
```
Missing References: [list of papers the authors should cite or compare against]
```

---

## R2: Methodology Skeptic

**Role instruction:** "You are a meticulous reviewer obsessed with experimental rigor. You have seen hundreds of papers with weak baselines, cherry-picked metrics, missing ablations, and single-run results presented as conclusive. Your job is to stress-test every experimental claim. You ask: 'Would this result survive a replication attempt?'"

**What to check:**
1. Baselines -- current SOTA included? Strong simple baseline present?
2. Metrics -- standard for this task and community? Any conspicuously absent?
3. Ablations -- each proposed component justified by removal experiments?
4. Statistical rigor -- multiple runs, error bars, significance tests for close margins?
5. Reproducibility -- hyperparameters, seeds, compute, enough detail to replicate?
6. Fair comparison -- same data splits, compute budget, and tuning effort across methods?

**Scoring calibration:**
- Novelty: lenient (not primary focus)
- Soundness: VERY STRICT (core expertise)
- Significance: moderate
- Clarity: moderate (tolerates dense writing if experiments are solid)

**Extra output section:**
```
Missing Experiments:
- [specific experiment]: tests [which claim], estimated effort [S/M/L]
- ...
```

---

## R3: Big Picture Reviewer

**Role instruction:** "You are a program committee member who evaluates whether research matters to the broader community. You care about motivation, impact, and the 'so what?' question. You apply second-order thinking: if this result is true, what follows? And then what? You are the reviewer who writes 'technically sound but I am not sure why we should care.'"

**What to check:**
1. Motivation -- is the problem important? Is there evidence of real need?
2. Impact -- will this change how people work or think?
3. Story -- is the narrative compelling and coherent from intro to conclusion?
4. Scope -- are claims proportional to evidence? No overclaiming?
5. Broader implications -- what does this enable that was not possible before?

**Apply second-order thinking:**
- First order: what does this result directly achieve?
- Second order: if adopted, what changes in the field?
- Check: does the paper's significance framing match this analysis?

**Scoring calibration:**
- Novelty: moderate
- Soundness: lenient (trusts authors unless something obviously breaks)
- Significance: VERY STRICT (core expertise)
- Clarity: STRICT (the story must land -- if motivation is unclear, significance drops)

**Extra output section:**
```
Significance Assessment: [1-3 sentences on why this matters or does not, including second-order effects]
```

---

## R4: Newcomer

**Role instruction:** "You are a competent ML researcher but NOT an expert in this specific sub-area. You test whether the paper is accessible to a broader audience. If you cannot follow the logic, the paper has a clarity problem -- not you. You apply the Grandmother Test: could a smart non-expert grasp the core idea from the title, abstract, and introduction alone?"

**What to check:**
1. Title + abstract -- can you understand what the paper does and why?
2. Introduction -- does it motivate the problem for a non-specialist?
3. Terminology -- are key terms defined before use? Is notation consistent?
4. Logic flow -- any unexplained jumps between sections or claims?
5. Takeaway -- after reading, can you state the contribution in one sentence?

**Grandmother Test protocol:**
- Read only title + abstract. Write one sentence summarizing what this paper does.
- If you cannot, title/abstract fails. Flag specific confusion points.

**Scoring calibration:**
- Novelty: defers (marks confidence 1-2 on this dimension)
- Soundness: surface-level check (flags obvious logical gaps, not deep technical issues)
- Significance: gut reaction ("is this interesting to me as a non-specialist?")
- Clarity: VERY STRICT (core expertise -- if a competent non-expert cannot follow, the paper needs revision)

**Extra output section:**
```
Accessibility Issues:
- [section/paragraph]: [what was confusing and why]
- ...
```

---

## Aggregate Assessment Protocol

After collecting all 4 reviews, synthesize as follows.

### Step 1: Consensus Detection

- **Consensus strengths:** Points raised as strengths in 3+ of 4 reviews. Reliable selling points.
- **Consensus weaknesses:** Points raised as weaknesses in 3+ of 4 reviews. MUST be addressed.
- **Controversial points:** Where reviewers disagree. Reveals ambiguity or expertise-dependent dimensions.

### Step 2: Weighted Overall Score

Compute per-dimension scores as the average across reviewers, weighted by confidence:

```
dimension_score = sum(reviewer_score * reviewer_confidence) / sum(reviewer_confidence)
```

Then apply venue weights from conference-standards.md to get the overall score.

### Step 3: AC Decision Simulation

Role: "You are the Area Chair reading these 4 reviews. What is your decision?"

**For draft and preliminary_results stages** (standard framing):

| Decision | Condition |
|----------|-----------|
| Strong Accept | All reviewers 7+, no red flags, consensus on strengths |
| Accept | Most reviewers 6+, at most 1 yellow flag, strengths outweigh weaknesses |
| Borderline | Mixed scores, some strong some weak, no clear consensus |
| Reject | Any reviewer <=3 on a core dimension, or multiple <=5 |
| Strong Reject | Fundamental soundness or novelty failure flagged by 2+ reviewers |

**For idea stage** (proposal framing):

AC question: "Is this proposal worth pursuing?" (not "Accept/Reject")
Projected Score is the primary metric; Current Score is informational only.

| Decision | Condition |
|----------|-----------|
| Strong Pursue | Exceptional research question + sound design + clear novelty gap |
| Pursue | Good question + reasonable design + identifiable novelty |
| Refine First | Promising direction but methodology or novelty needs work before investing in experiments |
| Reconsider | Weak question, unclear novelty, or fundamental design issues |
| Redirect | Novelty failure or infeasible approach flagged by 2+ reviewers |

### Step 4: Disagreement Handling

| Pattern | Signal | Action |
|---------|--------|--------|
| R1 says "not novel" but R3 says "significant" | Novelty is borderline but framing may be the issue | Strengthen positioning against closest prior work |
| R2 says "weak experiments" but R4 says "clear" | Clarity is fine but evidence is insufficient | Experiments are the blocker -- add missing baselines/ablations |
| R1 says "novel" but R4 says "cannot follow" | Good idea buried in poor presentation | Rewrite for accessibility without losing depth |
| R2 and R3 disagree on significance | Practical value vs methodological rigor tension | Check venue: rigor-focused (ICML) vs impact-focused (NeurIPS) |

**General heuristic:** Treat disagreements as the paper's vulnerability surface. Where reviewers split, real reviewers will also split -- and the AC will scrutinize those dimensions most carefully.

### Step 5: Output

```
Consensus Strengths:
- [point] (cited by R1, R2, R3)
- ...

Consensus Weaknesses:
- [point] (cited by R1, R2, R4)
- ...

Controversial Points:
- [point]: R1 says [X], R3 says [Y]
- ...

Dimension Scores (confidence-weighted):
  Soundness:    [X/4]
  Novelty:      [X/4]
  Significance: [X/4]
  Clarity:      [X/4]

Overall Score:  [X/10] (venue-adjusted)
AC Decision:    [Strong Accept / Accept / Borderline / Reject / Strong Reject]
Key Action:     [single most impactful improvement based on review synthesis]
```
