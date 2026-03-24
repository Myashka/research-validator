# Contributing

## Adding Reference Files

Reference files live in `research-design/references/` and are loaded progressively by phase.

**Naming convention:** Name files by their function, not phase number (e.g., `novelty-framework.md`, not `phase-2.5-criteria.md`).

**Structure:** Each reference file should contain structured guidelines, checklists, or templates that the skill phases consume. Use markdown with clear sections.

**Registration:** After adding a reference file, update the Reference Files table in `research-design/SKILL.md`:

```markdown
| `references/your-file.md` | Phase N | ~Lines | Purpose description |
```

## Adding New Skills

1. Create a new directory under the plugin root (e.g., `your-skill/`)
2. Add a `SKILL.md` with proper frontmatter (`name`, `description`)
3. Register the skill in `.claude-plugin/marketplace.json` under the `skills` array
4. Add reference files in `your-skill/references/` as needed

## Testing

Run evaluation cases to verify skill behavior:

1. Test with sample research pitches across different domains (NLP, CV, RL)
2. Verify all phases produce expected output structure
3. Check that agent waves launch and synthesize correctly
4. Confirm Go/No-Go verdicts are well-calibrated against known-good/bad proposals

## Commit Conventions

This project uses conventional commits:

- `feat(scope): message` — new feature or capability
- `fix(scope): message` — bug fix
- `docs(scope): message` — documentation changes
- `refactor(scope): message` — code restructuring without behavior change

Scope examples: `skill`, `scripts`, `references`, `plugin`

## Python Scripts

Scripts in `research-design/scripts/` follow these conventions:

- Prefer standard library where possible
- External dependencies: `requests` and `pyalex` (see `pyproject.toml`)
- Each script should be independently runnable via CLI
- Use structured JSON output for API responses (anti-hallucination)
- Include error handling for API rate limits and timeouts
