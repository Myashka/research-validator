# Research Wave 1: Direct Related Work

Wave 1 deploys 3 agents in parallel to map the immediate literature landscape. Each agent searches from a different angle for comprehensive coverage.

**When to read:** Phase 3 (Literature Research), before launching Wave 1 agents.

## Agent A1: Core Predecessors

**Role:** Find papers solving the SAME problem with the SAME or similar method.

**Expertise blocks:** E (search) + C (novelty) + F (honesty)

**Search depth:** 8-10 searches minimum, 4 rounds

### Tool Sequence

1. **AlphaXiv semantic search** (if MCP available):
   - `embedding_similarity_search` with the research description from intake
   - Finds papers by meaning, not just keywords

2. **arxiv structured search:**
   ```bash
   python scripts/arxiv_search.py "{problem + method keywords}" --category cs.LG --limit 20
   ```

3. **Semantic Scholar discovery:**
   ```bash
   python scripts/semantic_scholar.py search "{topic}" --limit 15
   ```

4. **Citation mining** (for top 3 most relevant papers found):
   ```bash
   python scripts/semantic_scholar.py references --paper-id {id}
   python scripts/semantic_scholar.py citations --paper-id {id}
   ```

5. **Cross-reference via OpenAlex:**
   ```bash
   python scripts/openalex_client.py search "{title}" --cited-by
   ```

### Output Format

```
**Paper:** [title]
**Authors:** [names]
**Venue:** [venue, year]
**ID:** [Verified: arxiv:{id}] or [Verified: DOI:{doi}]
**Core contribution:** [1-2 sentences]
**Relevance:** [High/Medium/Low]
**Similarity to proposal:** [what they share]
**Difference from proposal:** [what's different]
**Could they extend to cover ours?** [yes/no + explanation]
```

---

## Agent A2: Methodological Relatives

**Role:** Find papers using the SAME method for DIFFERENT tasks.

**Expertise blocks:** E (search) + B (methodology)

**Search depth:** 6-8 searches

### Tool Sequence

1. **arxiv with method-specific keywords:**
   ```bash
   python scripts/arxiv_search.py "{method name} {method type}" --category cs.LG --limit 20
   ```

2. **Semantic Scholar recommendations:**
   ```bash
   python scripts/semantic_scholar.py recommendations --paper-id {id_of_most_relevant}
   ```

3. **OpenAlex topic analysis:**
   ```bash
   python scripts/openalex_client.py search "{method}" --filter-topic
   ```

### Output Format

Same per-paper format as A1, plus:

```
**Methodological insight:** [what this application reveals about the method]
**Transferable lesson:** [what the proposal can learn from this usage]
```

### Key Question

> "Has this technique been tried in adjacent domains? What happened?"

Assess: did the method succeed or fail? Why? Are there domain-specific adaptations that inform the proposal?

---

## Agent A3: Concurrent Work

**Role:** Find RECENT preprints (last 6 months) on the same topic.

**Expertise blocks:** E (search) + C (novelty)

**Search depth:** 5-8 searches

### Tool Sequence

1. **arxiv recent papers:**
   ```bash
   python scripts/arxiv_search.py "{topic}" --category cs.LG --sort date --limit 30
   ```

2. **AlphaXiv full-text search** (if MCP available):
   - `full_text_papers_search` catches papers that keyword search misses
   - Search by core concept, not just title keywords

3. **Author tracking:**
   - Identify key authors from A1 findings
   - Check their latest submissions via Semantic Scholar or OpenAlex

4. **WebSearch for very recent work:**
   - `"{topic}" "{method}" arxiv 2025 2026`
   - `"{topic}" submitted {venue} {year}`
   - Catches papers not yet indexed by APIs

### Urgency Flags

Every paper gets exactly one flag:

| Flag | Meaning | Criteria |
|------|---------|----------|
| `[URGENT]` | Same idea, same approach | Published or under review. Potential scoop. |
| `[WARNING]` | Similar idea, different approach | Validates the problem but creates comparison pressure. |
| `[INFO]` | Related but clearly different | Good to cite, no threat to novelty. |

### Output Format

Same per-paper format as A1, plus:

```
**Urgency:** [URGENT] / [WARNING] / [INFO]
**Submission date:** [date if known]
**Overlap with proposal:** [specific overlap description]
**Differentiation strategy:** [how to position against this work]
```

### Novelty Race Assessment

After all concurrent work is reviewed, produce:

```
## Concurrent Work Summary
**Novelty Race Status:** [No race / Emerging competition / Active race]
**Most threatening paper:** [title + why]
**Recommended response:** [proceed / accelerate / pivot / differentiate]
```

---

## Anti-Hallucination (All Agents)

- Every paper MUST have a `[Verified]` tag with arxiv ID or DOI
- If verification fails, mark `[Unverified]` and note the failed lookup
- Run `python scripts/validate_citations.py` before finalizing output
- NEVER cite from memory -- only cite what API/search returned

---

## Wave 1 Completion Criteria

- [ ] All 3 agents (A1, A2, A3) finished with minimum search depth met
- [ ] Every cited paper has `[Verified]` tag with arxiv ID or DOI
- [ ] Raw output saved to `{project}/01-discovery/raw/`:
  - `raw/core-predecessors.md` (A1)
  - `raw/methodological-relatives.md` (A2)
  - `raw/concurrent-work.md` (A3)
- [ ] Key findings extracted for Wave 2:
  - Top 5 predecessors (for B1 SOTA comparison)
  - Open questions (for B2 gap analysis)
  - Concurrent work urgency status

## Flags
**Red Flags:**
- None identified
**Yellow Flags:**
- None identified
