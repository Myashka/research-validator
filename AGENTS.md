# Research Validator

## Overview

- **Plugin:** research (namespace: `research:*`)
- **Skill:** research-design
- **License:** MIT

Validates ML/AI research ideas with radical honesty before writing a paper. Input is a verbal pitch (no document), output is Go/No-Go verdict with scorecard, mock reviews, and action plan.

## Repository Structure

```
.claude-plugin/
  marketplace.json                    # Plugin manifest
research-design/
  SKILL.md                            # Main skill definition (10 phases)
  references/                         # Reference files loaded progressively by phase
    alphaxiv-mcp-guide.md             # AlphaXiv MCP setup and fallback strategy
    conference-standards.md           # Venue review forms, acceptance rates, scoring weights
    consider-5-whys.md                # Consider agent: root motivation (Phase 1.3)
    consider-first-principles.md      # Consider agent: hidden assumptions (Phase 1.3)
    consider-inversion.md             # Consider agent: failure modes (Phase 1.3, Full only)
    consider-occams-razor.md          # Consider agent: simplest baseline (Phase 1.3, Full only)
    contribution-types.md             # Contribution taxonomy, framing strategies
    critical-thinking-frameworks.md   # Frameworks mapped to phases
    experimental-design.md            # Baselines, statistical rigor, ablation
    honesty-protocol.md               # Claim labels, anti-hallucination rules
    mock-review-templates.md          # 4 reviewer personas, agent isolation, stage-adaptive prefixes
    novelty-framework.md              # Novelty typology, calibration scale
    output-guidelines.md              # File templates, assessment dashboard
    research-principles.md            # Search protocol, source quality tiers
    research-synthesis.md             # Synthesis flow, literature-review templates
    research-wave-1-literature.md     # Wave 1: predecessors, methods, concurrent work
    research-wave-2-landscape.md      # Wave 2: SOTA analysis, open problems
    research-wave-3-venue.md          # Wave 3: multi-venue fitness analysis
    verification-agent.md             # V1 verification agent (7-point checklist)
  scripts/                            # Python scripts for literature search
    arxiv_search.py                   # arXiv API client
    extract_metadata.py               # DOI/PMID/arxiv metadata extraction
    openalex_client.py                # OpenAlex API client
    paperswithcode.py                 # Papers With Code API client
    query_helpers.py                  # Compound OpenAlex queries
    semantic_scholar.py               # Semantic Scholar API client
    validate_citations.py             # Citation validation pipeline
```

## Research Architecture

```
INTAKE → PRE-CHECK → LITERATURE → NOVELTY GATE → VERIFICATION → METHODOLOGY → CONTRIBUTION → MOCK REVIEW → ACTION PLAN
```

- **10 phases** (0 = resume check, 1-9 = pipeline)
- **Two modes:** Full (16 agent launches) / Fast Track (10 agent launches)
- **Stage-adaptive:** research_stage (idea / preliminary_results / draft) adjusts scoring, review prompts, and verdict framing
- **Waves 1-2** search venue-agnostically; **Wave 3** analyzes multi-venue fit
- **Mock review:** 4 isolated agents (blind review), each with its own persona

## Key Conventions

- **Progressive reference loading:** read reference files only when needed
- **Radical honesty:** no sugar-coating fatal flaws
- **Agent isolation:** mock reviewers and consider agents run in separate contexts
- **Verbal pitch only:** no document upload required

## Git Workflow

Conventional commits: `feat(scope): message`, `fix(scope): message`, `docs(scope): message`

**Never use `git add -f` or `git add --force`.** If a file is gitignored, it must not be committed. The `.gitignore` uses a whitelist — only plugin source files are tracked.
