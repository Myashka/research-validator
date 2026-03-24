# Research Wave 3: Multi-Venue Fitness

Wave 3 deploys 2 agents in parallel to calibrate the proposal against multiple suitable venues. Consumes Wave 1 and Wave 2 output to assess venue-specific fit, reviewer expectations, and topic traction across the target venue and 1-2 recommended alternatives.

**When to read:** Phase 3 (Literature Research), after Wave 2 completes.

## Agent C1: Multi-Venue Fitness Analysis

**Role:** Assess fit for the target venue AND 1-2 recommended alternative venues. Determine where this work fits BEST.

**Expertise blocks:** E (search) + A (conference standards)

**Search depth:** 4-6 searches per venue, covering last 2-3 years

### Step 1: Start with User's Target Venue

Use the target venue from intake (Phase 1.2, core question 4). This is always analyzed first.

### Step 2: Recommend 1-2 Alternative Venues

Based on contribution type (from Wave 1-2 output) and topic, recommend 1-2 alternative venues:

| Contribution / Topic | Recommended Alternatives |
|-----------------------|--------------------------|
| Methods paper (general ML) | NeurIPS, ICML, ICLR |
| NLP-focused | ACL, EMNLP, NAACL |
| Vision-focused | CVPR, ICCV, ECCV |
| Applied / domain-specific | Relevant workshops, AAAI |
| Theoretical | NeurIPS, ICML, COLT |
| Systems / efficiency | MLSys, NeurIPS (systems track) |

Choose alternatives that differ meaningfully from the target (e.g., if target is NeurIPS, consider a domain venue like ACL or CVPR if the topic fits, not just ICML).

### Step 3: Analyze EACH Venue (Target + Alternatives)

For EACH venue (target + 1-2 alternatives), run the following searches:

1. **WebSearch for accepted papers:**
   - `"{venue} {year-1} {year-2} {topic} accepted papers"`
   - `"{venue} {year} oral spotlight {topic}"` for high-impact papers

2. **WebSearch for OpenReview data** (ICLR, NeurIPS, and venues with public reviews):
   - `"openreview.net {venue} {topic}"` to find accepted and rejected submissions
   - Compare accepted vs rejected to identify the quality bar

3. **OpenAlex venue-specific search:**
   ```bash
   python scripts/openalex_client.py search "{topic}" --filter-venue "{venue}" --years 3
   ```

4. **AlphaXiv venue-specific papers** (if MCP available):
   - `embedding_similarity_search` filtered to venue proceedings
   - Identifies papers similar to the proposal within the venue

### Step 4: Compare Venues

After analyzing all venues, compare: where would this work fit BEST? Consider topic traction, contribution type alignment, quality bar relative to the proposal's strength, and reviewer culture.

### Output Format

Produce one block per venue, then a comparative summary:

```
## Venue: {venue_name}

**Topic coverage (last 2-3 years):**
- Total papers on topic: {N}
- Oral/Spotlight: {N} | Poster: {N} | Rejected (if visible): {N}

**Common contribution types:**
- [ ] New method
- [ ] New dataset/benchmark
- [ ] Empirical analysis
- [ ] Theoretical contribution
- [ ] Position/survey

**Quality bar:**
- Minimum novelty expected: [description]
- Typical experimental scope: [N benchmarks, N baselines]
- Writing/presentation standard: [description]

**Topic traction:**
- Trend: [growing / stable / declining] at this venue
- Evidence: [paper counts by year, oral/spotlight ratio]
- Peak year: {year} | Direction: [up/down/flat]

**Notable recent papers:**
- {title} ({year}) -- [Verified: arxiv:{id}] -- {why notable}
(repeat for top 3-5 papers)

**Fit assessment:** [Strong Fit / Moderate Fit / Weak Fit]
**Recommendation:** [why this venue is/isn't a good target for this work]
```

After all venue blocks, add a comparative summary:

```
## Venue Comparison

| Dimension | {target_venue} | {alt_venue_1} | {alt_venue_2} |
|-----------|----------------|---------------|---------------|
| Topic traction | [growing/stable/declining] | ... | ... |
| Contribution type match | [yes/partial/no] | ... | ... |
| Quality bar vs proposal | [above/at/below] | ... | ... |
| Fit assessment | [Strong/Moderate/Weak] | ... | ... |

**Best-fit venue:** {venue} -- [reasoning]
**If best-fit differs from target:** [explanation of tradeoff and recommendation]
```

### Key Question

> "Across 2-3 suitable venues, where would this work have the strongest fit? Is the user's target venue the best choice?"

If the target venue is not the best fit, recommend the alternative with clear reasoning.

---

## Agent C2: Multi-Venue Reviewer Landscape

**Role:** What do reviewers at each analyzed venue value? What common complaints arise? What biases exist? Compare reviewer expectations across venues.

**Expertise blocks:** E (search) + A (conference standards)

**Search depth:** 4-6 searches per venue, focused on publicly available review data

**Privacy constraint:** This agent uses ONLY publicly available data (OpenReview, published meta-analyses, official reviewer guidelines). No private or leaked review data.

**Venue scope:** Analyze the same set of venues as C1 (target + 1-2 alternatives). C1 and C2 run in parallel, so use the same venue recommendation logic from Step 2 above.

### Tool Sequence (repeat for EACH venue)

1. **WebSearch for public reviews:**
   - `"openreview.net {venue} {year} {topic} reviews"` for public review text
   - Extract common praise and criticism patterns from 5-10 reviews

2. **WebSearch for reviewer guidelines and criteria:**
   - `"{venue} reviewer guidelines {year}"` for official criteria
   - `"{venue} area chair guidelines"` for AC decision patterns

3. **WebSearch for review meta-analyses:**
   - `"{venue} review analysis" OR "{venue} acceptance statistics {topic}"`
   - `"peer review bias" "{venue}" {topic}` for documented bias patterns

### Output Format

Produce one block per venue, then a comparative summary:

```
## Reviewer Landscape: {venue_name} / {topic}

**Common reviewer praise (from public reviews):**
- [pattern 1, with frequency if known]
- [pattern 2]

**Common reviewer complaints (from public reviews):**
- [complaint 1, with frequency if known]
- [complaint 2]

**Reviewer preferences at this venue:**
- Novelty weight: [high/medium/low]
- Reproducibility expectations: [description]
- Experimental rigor standard: [description]
- Writing quality sensitivity: [description]

**Observed bias patterns:**
- Positive: [e.g., preference for theoretical contributions, novelty-loving ACs]
- Negative: [e.g., methods-only reviewers ignoring applications, dismissal of incremental work]

**Actionable insights for the proposal:**
- [specific recommendation based on reviewer patterns]
- [specific recommendation based on common complaints]
```

After all venue blocks, add a comparative summary:

```
## Reviewer Expectations Comparison

| Dimension | {target_venue} | {alt_venue_1} | {alt_venue_2} |
|-----------|----------------|---------------|---------------|
| Novelty emphasis | [high/medium/low] | ... | ... |
| Rigor emphasis | [high/medium/low] | ... | ... |
| Common praise | [summary] | ... | ... |
| Common complaint | [summary] | ... | ... |
| Bias risk for this proposal | [high/medium/low] | ... | ... |

**Most favorable reviewer culture for this work:** {venue} -- [reasoning]
```

### Key Question

> "What would a typical reviewer at EACH venue praise or criticize about this proposal? Where would it receive the fairest evaluation?"

Use reviewer patterns to preemptively address likely concerns at the chosen venue.

---

## Anti-Hallucination (All Agents)

- Every paper MUST have a `[Verified]` tag with arxiv ID or DOI
- If verification fails, mark `[Unverified]` and note the failed lookup
- Run `python scripts/validate_citations.py` before finalizing output
- NEVER cite from memory -- only cite what API/search returned
- Reviewer data MUST come from public sources only (OpenReview, official guidelines)

---

## Wave 3 Completion Criteria

- [ ] Both agents (C1, C2) finished with minimum search depth met for EACH venue
- [ ] Every cited paper has `[Verified]` tag with arxiv ID or DOI
- [ ] Target venue + 1-2 alternatives analyzed (2-3 venues total)
- [ ] Per-venue fit assessment provided (Strong Fit / Moderate Fit / Weak Fit)
- [ ] Venue comparison summary with best-fit recommendation
- [ ] Raw output saved to `{project}/01-discovery/raw/`:
  - `raw/venue-analysis.md` (C1)
  - `raw/reviewer-landscape.md` (C2)
- [ ] Key findings extracted for synthesis:
  - Topic traction trend per venue (growing/stable/declining)
  - Venue quality bar per venue (minimum novelty, experimental scope)
  - Reviewer preference patterns and common complaints per venue
  - Best-fit venue recommendation with reasoning
- [ ] All 3 waves complete -> proceed to `research-synthesis.md` for final deliverables:
  - Wave 1 (literature) + Wave 2 (landscape) + Wave 3 (venue) = full research context
  - Synthesize into: `literature-review.md` + `novelty-assessment.md`

## Flags

**Red Flags:**
- Topic is clearly declining at ALL analyzed venues
- No venue shows Strong Fit -- contribution type mismatch across the board
- Venue explicitly discourages the type of contribution the proposal makes

**Yellow Flags:**
- Target venue shows Weak Fit but an alternative shows Strong Fit
- No papers on this exact topic at any venue (could be novel or off-target)
- Reviewer patterns show strong bias against the proposal's approach type at the target venue
