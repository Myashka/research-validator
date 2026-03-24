# Research Validator

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Honest, critical validation of ML/AI research ideas before conference submission. If your idea has fatal flaws, it will tell you.

Works with [Claude Code](https://claude.ai/claude-code) and any agent that supports skills.

## Available Skills

| Skill | What you get |
| --- | --- |
| [research-design](research-design/) | 10-phase research proposal validation: consider agents at intake, 3-wave literature search (7 parallel agents), novelty gate, verification, methodology review, contribution framing, agent-isolated mock peer review (4 personas), multi-venue scorecard, Go/No-Go verdict with action plan. |

## Usage

Describe your research idea -- the skill triggers automatically:

> _"I have a paper idea about using LoRA for continual learning. Is it worth pursuing?"_

**-> `research-design`** runs the full 10-phase validation (defaults to idea stage)

---

> _"Evaluate my research proposal -- I have preliminary results on efficient attention pruning"_

**-> `research-design`** evaluates at preliminary_results stage (both current and projected scores)

---

> _"Will this get into NeurIPS? I want to combine retrieval-augmented generation with..."_

**-> `research-design`** evaluates novelty, methodology, and multi-venue fit (NeurIPS + recommended alternatives)

Or invoke directly: `/research:research-design`

> **Token usage:** Full mode launches 16 agents (4 consider + 7 research + 1 verification + 4 mock reviewers). Fast Track launches 10 (2 + 5 + 1 + 2). For the best experience, use [Claude Max 5x](https://claude.ai/upgrade). If a session hits the limit, ask Claude to resume -- it picks up where it left off.

## Roadmap

- [x] Research idea validation (pitch to Go/No-Go verdict)
- [ ] Paper review mode (review a written draft, not just a pitch)

## Installation

```bash
claude plugin marketplace add myashka/research-validator
claude plugin install research@research-validator
```

### Python Dependencies

```bash
uv sync
```

Optional environment variables for higher API rate limits:

```bash
export S2_API_KEY="your-key"              # Semantic Scholar
export OPENALEX_EMAIL="you@example.com"   # OpenAlex polite pool
```

### AlphaXiv MCP (Optional)

```bash
claude mcp add alphaxiv --transport sse https://api.alphaxiv.org/mcp/v1
```

The skill automatically detects and uses AlphaXiv when available, falling back to API-based search otherwise.

## Attribution

- **[taches-cc-resources](https://github.com/glittercowboy/taches-cc-resources)** -- planning framework and development tooling
- **[startup-skill](https://github.com/ferdinandobons/startup-skill)** -- plugin structure, radical honesty philosophy
- **[claude-scientific-skills](https://github.com/anthropics/claude-scientific-skills)** -- `arxiv_search.py`, `openalex_client.py`, `validate_citations.py`, `extract_metadata.py`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
