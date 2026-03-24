# AlphaXiv MCP Integration Guide

AlphaXiv provides an MCP (Model Context Protocol) server for semantic paper search, content retrieval, and Q&A against arXiv papers. This is an **optional enhancement** -- the research-design skill works without it.

---

## MCP Server Configuration

**Endpoint:** `https://api.alphaxiv.org/mcp/v1`

Add to your project `.mcp.json` or Claude Code settings to enable AlphaXiv tools.

### Example `.mcp.json` Snippet

```json
{
  "mcpServers": {
    "alphaxiv": {
      "type": "sse",
      "url": "https://api.alphaxiv.org/mcp/v1"
    }
  }
}
```

Place this file in your project root. Claude Code will detect it automatically on startup.

To add via CLI instead:

```bash
claude mcp add alphaxiv --transport sse https://api.alphaxiv.org/mcp/v1
```

On first use, Claude Code will open a browser window for OAuth 2.0 authentication.

---

## Available MCP Tools

AlphaXiv exposes 6 tools through its MCP server:

### 1. `embedding_similarity_search`

Semantic paper discovery using embedding similarity. Returns up to 25 results ranked by relevance to a natural-language query.

- **Use for:** Finding conceptually related papers even when terminology differs
- **Advantage over keyword search:** Captures semantic meaning, not just lexical overlap
- **Limit:** 25 results per query

### 2. `full_text_papers_search`

Keyword-based search across full paper text. Useful when you need exact term matching or specific technical phrases.

- **Use for:** Finding papers that use specific method names, dataset names, or exact phrases
- **Complements:** `embedding_similarity_search` (keyword vs semantic)

### 3. `agentic_paper_retrieval`

Multi-turn autonomous retrieval that iteratively refines search results. Currently in beta.

- **Use for:** Complex queries that benefit from iterative refinement
- **Status:** Beta -- may change or be unavailable
- **Note:** Higher latency due to multi-turn nature

### 4. `get_paper_content`

Retrieves paper content as either an AI-generated report (summary, key findings, methodology) or raw extracted text.

- **Use for:** Getting paper summaries without reading full PDFs, extracting methodology details
- **Modes:** AI-generated report or raw text extraction

### 5. `answer_pdf_queries`

Q&A against specific papers. Ask questions about a paper and get answers grounded in its content.

- **Use for:** Targeted questions about methodology, results, limitations of a specific paper
- **Input:** Paper identifier + question

### 6. `read_files_from_github_repository`

Check code implementations linked from papers. Reads files directly from GitHub repositories.

- **Use for:** Verifying that paper implementations exist, checking code quality, understanding implementation details

---

## When to Use AlphaXiv vs Scripts

### AlphaXiv MCP -- Best For

| Task | Tool | Why |
|------|------|-----|
| Semantic paper discovery | `embedding_similarity_search` | Finds conceptually related work even with different terminology |
| Paper content analysis | `get_paper_content` | Get summaries or raw text without PDF download |
| Targeted paper Q&A | `answer_pdf_queries` | Ask specific questions grounded in paper content |
| Implementation checks | `read_files_from_github_repository` | Verify code exists and check details |
| Complex discovery | `agentic_paper_retrieval` | Multi-turn refinement for hard queries |

### Python Scripts -- Best For

| Task | Script | Why |
|------|--------|-----|
| Structured metadata | `arxiv_search.py`, `semantic_scholar.py` | Returns JSON with IDs, DOIs, citation counts |
| Citation graphs | `semantic_scholar.py citations/references` | Forward/backward citation traversal |
| SOTA verification | `semantic_scholar.py search`, WebSearch | Benchmark leaderboards, recent results |
| Batch operations | `semantic_scholar.py batch` | Look up 500 papers in one request |
| Citation validation | `validate_citations.py` | Verify papers exist via DOI resolution |
| Author analysis | `semantic_scholar.py author` | Author profiles, h-index, paper lists |
| Bibliometric trends | `openalex_client.py` | Publication trends, institutional analysis |

### Combined Strategy (Recommended)

Use AlphaXiv for **discovery**, scripts for **verification**:

1. **Discover** with `embedding_similarity_search` -- find semantically related papers
2. **Verify** with `semantic_scholar.py paper` -- get structured metadata and citation counts
3. **Deep-dive** with `get_paper_content` or `answer_pdf_queries` -- understand key papers
4. **Validate** with `validate_citations.py` -- confirm all references resolve to real papers
5. **Cross-reference** with `arxiv_search.py` -- ensure nothing missed in arXiv-specific search

---

## Fallback: When AlphaXiv Is Unavailable

The skill MUST work without AlphaXiv MCP. It is an enhancement, not a requirement.

If AlphaXiv tools are not available (MCP not configured, server down, network issues):

| AlphaXiv Tool | Fallback | Notes |
|---------------|----------|-------|
| `embedding_similarity_search` | `semantic_scholar.py search` + `arxiv_search.py` | Keyword search instead of semantic; use multiple query variations |
| `full_text_papers_search` | `arxiv_search.py` + WebSearch | arXiv API for preprints, WebSearch for broader coverage |
| `agentic_paper_retrieval` | Multiple rounds of `semantic_scholar.py search` | Manual iteration instead of autonomous |
| `get_paper_content` | WebFetch on arXiv abstract page | Less detail but gets abstract and metadata |
| `answer_pdf_queries` | Read paper via WebFetch + manual analysis | More token-intensive but functional |
| `read_files_from_github_repository` | WebFetch on GitHub URLs | Direct URL access to repository files |

### Degradation Priority

When adapting to missing tools:

1. **Always available:** WebSearch, WebFetch (built-in Claude tools)
2. **If Python + requests available:** All scripts in `scripts/` directory
3. **If AlphaXiv MCP configured:** Full semantic search and paper Q&A
4. **Best case:** All three tiers combined

The research quality scales with available tools but remains functional with just WebSearch + WebFetch.
