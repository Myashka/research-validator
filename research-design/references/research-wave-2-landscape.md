# Research Wave 2: Landscape & Gap Analysis

Wave 2 deploys 2 agents in parallel to map SOTA and identify open problems. Consumes Wave 1 output to deepen the landscape analysis.

**When to read:** Phase 3 (Literature Research), after Wave 1 completes.

## Agent B1: SOTA Analysis

**Role:** Establish current state-of-the-art on relevant benchmarks and datasets.

**Expertise blocks:** E (search) + B (methodology)

**Search depth:** 5-8 searches per benchmark, verify every number

### Tool Sequence

1. **PapersWithCode leaderboard fetch:**
   ```bash
   python scripts/paperswithcode.py leaderboard "{task}" --dataset "{dataset}"
   ```
   OR WebFetch the leaderboard page directly if script unavailable.

2. **arxiv for latest benchmark papers:**
   ```bash
   python scripts/arxiv_search.py "{benchmark} state-of-the-art" --category cs.LG --sort date --limit 20
   ```

3. **Semantic Scholar for highly-cited recent work:**
   ```bash
   python scripts/semantic_scholar.py search "{task} {dataset}" --limit 15 --sort citations
   ```

4. **Cross-reference verification:**
   - Every SOTA number MUST appear in 2+ independent sources
   - If only 1 source, mark `[Unverified-SingleSource]`

5. **Trend detection:**
   - Compare SOTA progression over last 3 years
   - Identify diminishing returns, ceiling effects, or paradigm shifts

### Output Format

Per benchmark, produce a SOTA table:

```
## Benchmark: {benchmark_name}
**Dataset:** {dataset name} | **Metric:** {primary metric}

| Rank | Method | Score | Paper | Year | Verified |
|------|--------|-------|-------|------|----------|
| 1 | {name} | {score} | [Verified: arxiv:{id}] | {year} | 2+ sources |
| 2 | {name} | {score} | [Verified: DOI:{doi}] | {year} | 2+ sources |

**Trend:** [improving rapidly / plateauing / saturated]
**What defines "strong" here:** [e.g., "within 2% of SOTA is competitive"]
```

### Key Question

> "Where does the proposal need to land on these benchmarks to be taken seriously?"

If SOTA is saturated, incremental improvements may not be publishable.

---

## Agent B2: Open Problems & Surveys

**Role:** What does the community consider unsolved? Does the proposal address a real gap?

**Expertise blocks:** E (search) + D (communication)

**Search depth:** 6-8 searches across surveys, workshops, and challenge papers

### Tool Sequence

1. **WebSearch for surveys and challenge papers:**
   - `"{topic} survey {year}"` OR `"{topic} challenges open problems"`
   - `"{topic} limitations future work"` for gaps noted by authors

2. **arxiv survey search:**
   ```bash
   python scripts/arxiv_search.py "{topic} survey OR open problems" --category cs.LG --limit 15
   ```

3. **AlphaXiv deep-dive on found surveys** (if MCP available):
   - `answer_pdf_queries` on top 3 surveys: "What are the main open problems?"
   - Also ask: "What limitations remain unsolved?"

4. **Workshop and challenge discovery:**
   - WebSearch: `"{venue} workshop {topic} {year}"` for recent workshops
   - WebSearch: `"shared task" OR "challenge" "{topic}" {year}` for competitions

### Output Format

```
## Open Problems Catalogue

### Problem 1: {problem name}
**Priority:** [High/Medium/Low] (based on frequency across sources)
**Evidence:** [list of surveys/papers with Verified IDs]
**Description:** [1-2 sentences]
**Current best attempt:** [what has been tried, with reference]
**Proposal alignment:** [direct / partial / tangential]

(repeat for each identified problem)

## Gap Alignment Summary
**Proposal addresses:** [which open problems, directly or partially]
**Novel gap:** [does the proposal identify a gap NOT in the community catalogue?]
**Community priority match:** [High/Medium/Low]
```

### Key Question

> "Does the proposal align with what the community considers important?"

A problem the community does not recognize may be visionary or irrelevant -- the distinction matters for venue selection.

---

## Anti-Hallucination (All Agents)

- Every paper MUST have a `[Verified]` tag with arxiv ID or DOI
- If verification fails, mark `[Unverified]` and note the failed lookup
- Run `python scripts/validate_citations.py` before finalizing output
- NEVER cite from memory -- only cite what API/search returned
- SOTA numbers MUST be cross-referenced against 2+ independent sources

---

## Wave 2 Completion Criteria

- [ ] Both agents (B1, B2) finished with minimum search depth met
- [ ] Every SOTA number verified against 2+ sources
- [ ] Every cited paper has `[Verified]` tag with arxiv ID or DOI
- [ ] Raw output saved to `{project}/01-discovery/raw/`:
  - `raw/sota-analysis.md` (B1)
  - `raw/open-problems.md` (B2)
- [ ] Key findings extracted for Wave 3:
  - SOTA baselines (for gap analysis in Wave 3)
  - Open problems ranked by priority (for contribution framing)
  - Benchmark saturation status

## Flags

**Red Flags:**
- SOTA is saturated AND proposal claims incremental improvement
- Proposal addresses a problem no survey or workshop mentions

**Yellow Flags:**
- SOTA numbers verified from only 1 source
- Proposal targets a gap not in the community catalogue
