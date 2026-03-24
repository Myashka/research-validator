# Research Principles

## Iterative Deep Research Protocol

Each agent performs 5-8 searches minimum across four rounds:

| Round | Focus | Goal |
|-------|-------|------|
| **1. Broad Overview** | Main keywords, method type, task category | Map the landscape: 15-20 potentially relevant papers |
| **2. Drill-Down** | Citation mining, forward/backward refs from top-5 hits | Find work that keyword search misses |
| **3. Cross-Reference** | Validate key claims across 2-3 sources, resolve conflicts | Confirm or refute major findings |
| **4. Reality Check** | Edge cases, concurrent work, negative results | Stress-test assumptions, detect blind spots |

Do NOT stop after Round 1. Broad search alone misses critical work.

## Source Quality Tiers

| Tier | Sources | Trust Level |
|------|---------|-------------|
| **Tier 1** | Peer-reviewed papers (NeurIPS, ICML, ICLR, ACL, CVPR, AAAI), official benchmarks (PapersWithCode) | High -- cite directly |
| **Tier 2** | Reputable preprints (arxiv with high citation/discussion), tech blogs from major labs (Google AI, Meta AI, DeepMind) | Medium -- cite with `[Preprint]` label |
| **Tier 3** | Blog posts, tweets, social media, unreviewed claims | Low -- never cite as evidence |

A Tier 3 source claiming SOTA is NOT reliable without Tier 1/2 confirmation.

## Cross-Referencing Rules

- **Never trust a single source** for key claims (SOTA numbers, novelty assertions, benchmark results)
- **2-3 independent sources** required for every major finding
- **Sources agree:** note convergence, cite all sources
- **Sources disagree:** note both positions, explain discrepancy, state which to trust and why

## Tool Usage Protocol

Priority order -- use higher-priority tools first, fall back as needed:

| Priority | Tool | Use For |
|----------|------|---------|
| **Primary** | Python scripts (`arxiv_search.py`, `semantic_scholar.py`, `openalex_client.py`) | Structured search with verified results |
| **Secondary** | AlphaXiv MCP (`mcp__alphaxiv`) | Semantic search, paper Q&A |
| **Tertiary** | `WebSearch` | Broad discovery, Google Scholar fallback |
| **Verification** | `validate_citations.py` | Check DOI/arxiv ID resolution before final output |
| **Enrichment** | `WebFetch` | PapersWithCode leaderboards, OpenReview pages, arxiv abstracts |

## Search Patterns by Task

Copy-pasteable commands for common operations:

```bash
# Paper discovery
python scripts/arxiv_search.py '{keywords}' --category cs.LG --limit 20

# SOTA check
# WebFetch paperswithcode.com/task/{task-slug}
# Then verify top results via arxiv

# Citation graph (forward + backward)
python scripts/semantic_scholar.py citations --paper-id {arxiv_id_or_doi}

# Concurrent work (recent, sorted by date)
python scripts/arxiv_search.py '{topic}' --category cs.LG --sort date --limit 30

# Venue search
# WebSearch "{venue} {year} {topic} accepted papers"

# Author tracking
python scripts/openalex_client.py author --name "{name}"
```

## Anti-Hallucination Integration

- API scripts return **only real papers** as structured JSON with IDs -- no fabrication possible
- Every cited paper MUST have an `arxiv:{id}` or `DOI:{doi}` identifier
- Before final output: run `python scripts/validate_citations.py` on all references
- If a paper cannot be verified, mark it `[Unverified]` and note the failed lookup

## Data Freshness Rules

ML/AI moves fast. Outdated evidence leads to wrong conclusions.

| Rule | Threshold |
|------|-----------|
| **Staleness flag** | Papers older than 12 months: flag as potentially outdated for SOTA claims |
| **SOTA verification** | Always verify current SOTA via API/web -- never rely on memory or cached knowledge |
| **Conference patterns** | Check last 2-3 years of target venue proceedings for acceptance trends |

## Handling Research Failures

When searches return insufficient results:

1. **Try 3+ alternative queries** (synonyms, broader terms, related subfields) before declaring a gap
2. **Use proxy data** if exact data is unavailable (broader field results to estimate subfield trends)
3. **Declare gaps explicitly:** `DATA GAP: Could not find reliable data on [X]`
4. **Never fabricate:** an honest "unknown" is infinitely more valuable than a made-up citation
5. **Suggest how to fill:** recommend specific databases to check or authors/labs to contact
