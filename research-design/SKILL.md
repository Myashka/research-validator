---
name: research-design
description: >
  Validates ML/AI research ideas before writing a paper. Covers literature research,
  novelty assessment, methodology review, contribution framing, mock peer review,
  and action planning. Trigger when the user has a research idea to evaluate,
  wants to check if a paper idea is novel, needs to assess experimental design,
  asks about research feasibility, or says anything like "I have a paper idea",
  "is this worth researching", "will this get into NeurIPS", "evaluate my research
  proposal". Also handles resuming from a previous checkpoint.
---

# Research Design

Structured multi-phase skill that takes a verbal research idea (pitch) and validates it through literature research, novelty assessment, methodology review, contribution framing, mock peer review, and action planning. Produces an honest Go/No-Go verdict with a concrete improvement plan.

## How It Works

Read `references/output-guidelines.md` at the start of every run for formatting rules, file headers/footers, and the Final Assessment Dashboard template.

**Pipeline:**
```
INTAKE -> PRE-CHECK -> LITERATURE -> NOVELTY GATE -> VERIFICATION -> METHODOLOGY -> CONTRIBUTION -> MOCK REVIEW -> ACTION PLAN
Phase 1     Phase 2     Phase 3       Phase 4         Phase 5         Phase 6         Phase 7         Phase 8        Phase 9
```

**Two modes:**
- **Full** -- all phases, 7 research agents across 3 waves, 4 mock reviewers
- **Fast Track** -- compressed: 2 consider agents, Wave 1 + Wave 2 only (skip Wave 3), 2 mock reviewers, streamlined action plan

**Language:** Respond in the language the user uses. Default to English if unclear.

**Progressive references:** Only read reference files when needed by the current phase. Each phase header lists which files to load.

**State tracking:** PROGRESS.md in the project directory tracks current phase and can resume interrupted runs.

### Fast Track Mode Summary

Fast Track compresses the assessment for quicker go/no-go. All differences from Full mode:
- **Phase 1 (Intake):** 2 consider agents (5 Whys + First Principles) instead of 4
- **Phase 3 (Literature):** Wave 1 + Wave 2 only (skip Wave 3 venue analysis). Reduces research agents from 7 to 5
- **Phase 8 (Mock Review):** 2 reviewers (R1 Domain Expert + R2 Methodology Skeptic) instead of 4
- **Phase 9 (Action Plan):** Top-3 improvements only, no Eisenhower matrix

All other phases run identically in both modes.

## Radical Honesty Protocol

> Load `references/honesty-protocol.md` once at Phase 1 and apply throughout all phases.
> Core principle: tell the truth, even when it is uncomfortable. Label every claim. Never fabricate citations.

## Phase 0: Resume Check

Check if `PROGRESS.md` exists in the current directory.

**If PROGRESS.md exists:**
1. Read it and display the current state to the user (phase, project name, last update)
2. Ask: "Found a previous session for **{project-name}** at Phase {N}. Continue from where you left off, or start fresh?"
3. If continue: jump to the recorded phase, re-read its required references
4. If start fresh: archive old PROGRESS.md as `PROGRESS.pre-restart.md`, proceed to Phase 1

**If PROGRESS.md does not exist:**
Proceed directly to Phase 1.

## Phase 1: Intake Interview

> Reference: `references/honesty-protocol.md` -- load for claim labels and anti-pattern awareness.

### 1.1 Mode Selection

Use the AskUserQuestion tool:
- question: "Choose assessment mode for this research proposal:"
- options:
  - "Full Assessment -- All phases, 3 research waves (7 agents), 4 consider agents, 4 mock reviewers (~30-60 min)"
  - "Fast Track -- Compressed go/no-go: 2 research waves (5 agents), 2 consider agents, 2 mock reviewers (~15-25 min)"

Record the choice. It affects Phases 1, 3, 8, and 9.

### 1.2 Core Questions

Present all 4 core questions in a single message. The user answers all at once:

1. **Research Question:** "What are you trying to show, prove, or discover? What is your hypothesis and proposed approach?"
2. **Prior Work:** "What existing work are you building on? What has been tried before and why is it insufficient?"
3. **Experimental Setup:** "What experiments do you plan? What datasets, baselines, and metrics will you use? What compute do you have?"
4. **Target & Timeline:** "Which venue are you targeting? When is the deadline? What stage are you at (idea / preliminary results / draft)?"

### 1.3 Critical Analysis (Consider Agents)

After user answers core questions, launch parallel consider agents. Each agent applies one critical thinking framework to the proposal independently.

**Full Mode** -- launch 4 agents in parallel:
1. Agent: 5 Whys -- read `references/consider-5-whys.md`
2. Agent: First Principles -- read `references/consider-first-principles.md`
3. Agent: Inversion -- read `references/consider-inversion.md`
4. Agent: Occam's Razor -- read `references/consider-occams-razor.md`

**Fast Track Mode** -- launch 2 agents in parallel:
1. Agent: 5 Whys -- read `references/consider-5-whys.md`
2. Agent: First Principles -- read `references/consider-first-principles.md`

**Each agent receives:** its framework reference file + user's 4 core answers + context: "You are critically analyzing an ML/AI research proposal. Apply the framework below to identify weaknesses, hidden assumptions, and gaps. Produce a structured analysis followed by 2-3 targeted hard questions for the researcher."

**Each agent does NOT receive:** other agents' analyses, SKILL.md, PROGRESS.md, or any other reference files.

**After all agents complete:** Collect outputs. Synthesize into framework analysis summary + top 3-5 hard questions (deduplicated, sharpest formulations). Present to user. User responds. Save everything to `{project}/00-intake/intake.md`.

### 1.4 Project Setup

Derive `{project}` from the research topic. Use lowercase-hyphenated format (e.g., `jepa-text2weights`, `efficient-attention-pruning`). Create the directory and all subdirectories:

`{project}/` with subdirectories: `00-intake/`, `01-discovery/` (with `raw/`), `02-assessment/`, `03-mock-review/`, `04-action/`.

**Research Stage:** Capture `research_stage` from core question 4. Values: `idea` (default -- evaluate POTENTIAL, not completeness), `preliminary_results` (evaluate design + early evidence), `draft` (evaluate as finished submission). Propagates to Phase 8 (reviewer prompts), Phase 9 (verdict), and Assessment Dashboard. Save in `{project}/00-intake/intake.md` header.

### 1.5 Output

Create `{project}/00-intake/intake.md` (standard header from `references/output-guidelines.md`) with: formalized research question, hypothesis, prior work summary, known gaps, planned experiments/datasets/baselines/metrics, target venue and deadline, key assumptions (labeled per honesty protocol), Red/Yellow flags.

Create `PROGRESS.md`: Project name, mode (Full/Fast Track), current phase (1 -- Intake Complete), last updated date.

## Phase 2: Quick Novelty Pre-Check

Lightweight pre-check before full research. Saves tokens if the idea is obviously already published.

**Steps:**
1. Run 1-2 quick searches based on the user's research question:
   - `python scripts/arxiv_search.py "{exact topic keywords}" --limit 5`
   - `WebSearch "{exact topic} arxiv 2024 2025 2026"`
2. Scan results for exact matches (same problem + same approach + published).

**Outcomes:**
- **RED** -- Exact match found (same problem + same approach + published). Stop early. Present the finding to the user with citation. Suggest pivot: different angle, different method, or extension. Ask user: "Continue with full research anyway, or pivot?"
- **YELLOW** -- Similar work found but different angle. Note for research agents (pass as additional context to Wave 1). Proceed to Phase 3.
- **GREEN** -- Nothing obvious found. Proceed to Phase 3.

**Important:** This is NOT a replacement for the full Novelty Gate (Phase 4). It is a fast pre-filter only. A GREEN here does not mean the idea is novel.

Update PROGRESS.md: `**Current Phase:** 2 (Pre-Check Complete)`

## Phase 3: Literature Research

> Reference: Read `references/research-principles.md` FIRST -- load before any wave for search protocol, source tiers, and anti-hallucination rules.

### 3.1 Environment Detection

Detect available tools before launching research. Check: (1) Agent tool -- parallel vs sequential agents, (2) AlphaXiv MCP (`mcp__alphaxiv`) -- semantic search vs keyword fallback (see `references/alphaxiv-mcp-guide.md`), (3) Python scripts (`python scripts/arxiv_search.py --help`) -- structured API search vs WebSearch-only. Log capabilities in `{project}/01-discovery/environment.md`.

### 3.2 Wave 1: Direct Related Work

Read `references/research-wave-1-literature.md` for agent templates and tool sequences.

**Venue-agnostic search:** Wave 1 searches by topic and method. Do NOT filter by venue. The goal is comprehensive coverage across all venues and preprint servers.

Launch 3 agents (parallel if Agent tool available, sequential otherwise):
- **A1: Core Predecessors** -- papers solving the same problem with the same or similar method
- **A2: Methodological Relatives** -- papers using the same method for different tasks
- **A3: Concurrent Work** -- recent preprints (last 6 months) on the same topic

Each agent follows the search depth and tool sequence defined in the reference file. Every cited paper MUST have a `[Verified]` tag with arxiv ID or DOI.

Raw output saved to:
- `{project}/01-discovery/raw/core-predecessors.md` (A1)
- `{project}/01-discovery/raw/methodological-relatives.md` (A2)
- `{project}/01-discovery/raw/concurrent-work.md` (A3)

Wait for all Wave 1 agents to complete before proceeding.

### 3.3 Wave 2: Landscape & Gap Analysis

Read `references/research-wave-2-landscape.md` for agent templates and tool sequences.

**Venue-agnostic search:** Wave 2 searches by topic and method. Do NOT filter by venue. SOTA and open problems span the entire research community, not a single conference.

Launch 2 agents (uses Wave 1 output as context):
- **B1: SOTA Analysis** -- current state-of-the-art on relevant benchmarks, verified against 2+ sources
- **B2: Open Problems & Surveys** -- survey papers, workshop reports, community-recognized gaps

Raw output saved to:
- `{project}/01-discovery/raw/sota-analysis.md` (B1)
- `{project}/01-discovery/raw/open-problems.md` (B2)

Wait for all Wave 2 agents to complete before proceeding.

### 3.4 Wave 3: Multi-Venue Fitness (Full mode only)

Read `references/research-wave-3-venue.md` for multi-venue C1/C2 agent templates and tool sequences.

Wave 3 analyzes fit for the target venue + 1-2 recommended alternatives (2-3 venues total). This is where venue-specific analysis begins -- Waves 1-2 are venue-agnostic.

Launch 2 agents (uses Wave 1 + Wave 2 output):
- **C1: Multi-Venue Fitness Analysis** -- analyze target + 1-2 alternative venues: topic coverage, quality bar, fit assessment (Strong/Moderate/Weak Fit), and best-fit recommendation
- **C2: Multi-Venue Reviewer Landscape** -- reviewer preferences, common complaints, bias patterns per venue (public data only), with cross-venue comparison

Raw output saved to:
- `{project}/01-discovery/raw/venue-analysis.md` (C1)
- `{project}/01-discovery/raw/reviewer-landscape.md` (C2)

### 3.5 Synthesis

Read `references/research-synthesis.md` for synthesis protocol, templates, and cross-document connection rules.

Collect all raw files from `{project}/01-discovery/raw/`. Identify recurring themes, contradictions across agents, and implications for the proposal. Generate two deliverables:

- `{project}/01-discovery/literature-review.md` -- structured review with executive summary, top-5 closest prior work, SOTA summary, open problems alignment, venue fitness, and data gaps
- `{project}/01-discovery/novelty-assessment.md` -- novelty classification, delta analysis, concurrent work impact, novelty score (1-10), and risk factors

Both files use the standard header/footer from `references/output-guidelines.md`.

**Fast Track:** Run Wave 1 + Wave 2 only (skip Wave 3). Simplified synthesis: shorter literature-review.md (skip venue fitness section), same novelty-assessment.md.

### 3.6 Sequential Fallback (No Agent Tool)

When the Agent tool is unavailable (e.g., Claude.ai), run each agent's search sequence one at a time within each wave. Same structure, same output files, same quality -- just slower.

Update PROGRESS.md: `**Current Phase:** 3 (Literature Research Complete)`

## Phase 4: Novelty Gate

> Reference: Read `references/novelty-framework.md` for novelty typology, decision tree, anti-patterns, and prior work comparison template.

Go/No-Go checkpoint based on literature findings. Can halt the process early if novelty is insufficient.

### 4.1 Decision Tree

Walk through the five questions in `references/novelty-framework.md` ("Is It Novel?" Decision Tree) using the literature search results. For each question, cite specific papers found in Phase 3.

### 4.2 Prior Work Delta

Using the Top-5 Closest Prior Work template from the reference file, compare the proposal against the 5 most similar papers. Classify the primary delta type (new paradigm / method / formulation / analysis / application / combination / engineering) and assign a calibration score (1-10).

### 4.3 Critical Thinking: Inversion + Opportunity Cost

Apply two frameworks from `references/critical-thinking-frameworks.md`:

**Inversion** -- "What would guarantee rejection for lack of novelty?" List specific failure modes (prior work overlap, trivial combination, concurrent work). For each: is it present? If yes, what is the avoidance plan?

**Opportunity Cost** -- "Is this the best use of 6 months?" Resources required, best alternative directions from literature search, expected value comparison.

### 4.4 Anti-Pattern Check

Check against all four novelty anti-patterns in the reference file. If any match, flag explicitly and explain why it fails.

### 4.5 Gate Decision

| Signal | Condition | Action |
|--------|-----------|--------|
| **GREEN** | Clear novelty, gap confirmed, no blocking concurrent work | Proceed confidently to Phase 5 |
| **YELLOW** | Novelty is incremental, or concurrent work exists | Note caveats, suggest differentiation angles, continue |
| **RED** | Work already exists, or contribution is too thin | Present findings, suggest pivots, ask researcher: "Continue anyway or redirect?" |

If RED: pause and wait for researcher's decision before proceeding. Do not skip this gate.

### 4.6 Output

Create `{project}/01-discovery/novelty-gate.md` with: verdict (Green/Yellow/Red), decision tree walkthrough, Top-5 prior work comparison, delta classification with calibration score, anti-pattern results, and (if Yellow/Red) specific pivot suggestions.

Update PROGRESS.md: `**Current Phase:** 4 (Novelty Gate Complete)`

## Phase 5: Verification (V1 Agent)

> Reference: Read `references/verification-agent.md` for the V1 agent protocol, 7-point checklist, and output format.

After novelty gate, launch V1 Verification Agent to catch errors before assessment and mock review build on them.

### 5.1 Agent Launch

1. Launch Verification Agent using the Agent tool.
2. Agent receives: `references/verification-agent.md` protocol + all files in `{project}/00-intake/` and `{project}/01-discovery/`.
3. Agent checks the 7-point checklist: unlabeled claims, internal contradictions, citation consistency, data gaps declared, flags present, stage-appropriate assessment, synthesis completeness.
4. Agent produces: `{project}/01-discovery/verification-report.md`

### 5.2 On Results

- **PASS** -- proceed to Phase 6.
- **PASS WITH WARNINGS** -- note warnings in PROGRESS.md, proceed to Phase 6.
- **FAIL** -- pause. Fix critical issues before proceeding to Phase 6. Address each FAIL item, re-run verification if needed.

Update PROGRESS.md: `**Current Phase:** 5 (Verification Complete)`

## Phase 6: Methodology Review

> References: Read `references/experimental-design.md` for baseline rules, statistical checklist, ablation patterns, and claims-evidence template. Read `references/conference-standards.md` for venue-specific rigor expectations.

Systematic review of the proposed methodology.

### 6.1 Logical Chain Audit

Trace the chain: Problem Statement -> Gap in Prior Work -> Proposed Approach -> Why It Should Work -> Expected Results. Check each link. A break in any link is a weakness to flag.

### 6.2 Assumption Mining (First Principles)

Apply First Principles from `references/critical-thinking-frameworks.md`: list all explicit and implicit assumptions (training stability, generalization, scale). Challenge each: supported by evidence, or convention? Flag unsupported assumptions that create risk.

### 6.3 Method-Specific Checks

Use the method-type checklist in `references/experimental-design.md` (Common Experimental Pitfalls, Fair Comparison Guidelines). Check compute cost, stability, hyperparameter sensitivity, and whether complexity adds value for the specific method type.

### 6.4 Counter-Argument Generation

For each major claim, generate the strongest counter-argument a skeptical reviewer would raise. If a counter-argument cannot be refuted with available evidence, flag it as a weakness.

### 6.5 Baseline Sufficiency Matrix (Occam's Razor)

Apply Occam's Razor from `references/critical-thinking-frameworks.md`: "Has the simplest reasonable baseline been tried?" Fill the Baseline Sufficiency Matrix from `references/experimental-design.md` -- check SOTA methods, simple-but-strong baselines, and ablation variants for inclusion, fair comparison, and currency.

### 6.6 Ablation Design (Via Negativa)

Apply Via Negativa from `references/critical-thinking-frameworks.md`: for each method component, determine what happens when it is removed. Flag untested components as "MUST TEST." Identify the minimal set of components that explain most of the results.

### 6.7 Claims-Evidence Gap Analysis

For each major claim, fill the Claims-Evidence template from `references/experimental-design.md`: required evidence, currently available evidence, gap description, effort to close (S/M/L), and impact on score. Any claim with a non-empty gap is a vulnerability.

### 6.8 Feasibility Check

Assess whether experiments are realistic given: compute resources, timeline to deadline, team expertise, data availability, and technical risks from steps 6.1-6.7.

### 6.9 Output

Create two files:
- `{project}/02-assessment/methodology-review.md` -- full methodology assessment with specific recommendations per step
- `{project}/02-assessment/claims-matrix.md` -- one Claims-Evidence block per major claim

Update PROGRESS.md: `**Current Phase:** 6 (Methodology Review Complete)`

## Phase 7: Contribution Framing

> Reference: Read `references/contribution-types.md` for contribution taxonomy, venue expectations, framing strategies, title/abstract patterns, and the 5-second test.

Position the research for maximum impact at the target venue.

### 7.1 Contribution Type Classification

Classify the contribution using the 7-type taxonomy in the reference file (new method, new theory, new dataset, empirical study, analysis, negative result, position/survey). Check venue expectations for that type.

### 7.2 Positioning Strategy

Select the best framing approach from the reference file (taxonomy, contrast, evolution, or gap). Justify the choice based on the literature landscape from Phase 3.

### 7.3 Alternative Framings

Brainstorm 2-3 alternative ways to frame the same work. For each: describe the framing angle, its strengths, and its risks. Recommend the strongest option with rationale.

### 7.4 Title Suggestions

Generate 2-3 candidate titles following the type-specific patterns in the reference file. Each title must pass the 5-second test: a reader scanning it should instantly understand (1) what area this is in and (2) what the contribution is.

### 7.5 Abstract Draft

Draft a structured abstract following the template in the reference file: Problem (1 sentence) -> Gap (1 sentence) -> Approach (1-2 sentences) -> Result with numbers (1-2 sentences) -> Implication (optional, 1 sentence).

### 7.6 Output

Create `{project}/02-assessment/contribution-framing.md` with: contribution type and venue fit, recommended framing with rationale, alternative framings, title candidates with 5-second test results, and abstract draft.

Update PROGRESS.md: `**Current Phase:** 7 (Contribution Framing Complete)`

## Phase 8: Mock Review

> References: Read `references/mock-review-templates.md` for reviewer personas, scoring format, and aggregate protocol. Read `references/conference-standards.md` for venue-specific weights and acceptance patterns.

Simulate conference peer review with 4 personas (Fast Track: R1 + R2 only).

### 8.1 Launch Mock Reviewers

> Reference: Read `references/mock-review-templates.md` (Agent Launch Protocol section FIRST, then persona sections)

Launch each reviewer as a SEPARATE Agent using the Agent tool. Each agent gets ONLY its persona prompt + assessment materials. Agents do NOT see each other's reviews (blind review).

Full Mode: 4 agents in parallel (R1 Domain Expert, R2 Methodology Skeptic, R3 Big Picture, R4 Newcomer)
Fast Track: 2 agents in parallel (R1, R2)

After all agents complete, synthesize reviews into scorecard (main context, not agent). See Agent Launch Protocol in `references/mock-review-templates.md` for full specification.

### 8.2 Stage-Adaptive Review

Read research_stage from `{project}/00-intake/intake.md`. Apply stage-adaptive prompt prefix from `references/mock-review-templates.md` (Stage-Adaptive Review Prefixes section).
- **idea:** Evaluate POTENTIAL, not completeness. "Experimental Design Quality" replaces "Experiments". Projected Score is PRIMARY.
- **preliminary_results:** Note incomplete experiments but do not penalize. Both Current and Projected Score shown.
- **draft:** Standard evaluation, no prefix applied.

### 8.3 Aggregate Assessment

After all reviews, follow the 5-step aggregate protocol from `references/mock-review-templates.md`:
1. **Consensus detection** -- strengths/weaknesses cited by 3+ reviewers
2. **Weighted scores** -- per-dimension averages weighted by reviewer confidence
3. **AC decision simulation** -- Strong Accept / Accept / Borderline / Reject / Strong Reject
4. **Disagreement handling** -- map split patterns to specific actions (see reference file)
5. **Key action** -- single most impactful improvement from the synthesis

Apply venue-specific weight adjustments from `references/conference-standards.md` to compute the venue-adjusted overall score.

### 8.4 Multi-Venue Scorecard

Show scores for multiple venues (target + alternatives from Wave 3):
- Apply venue-specific weights from `references/conference-standards.md` for each venue
- Indicate best-fit venue with reasoning
- If best-fit differs from target, flag this in the dashboard
- In Fast Track mode (no Wave 3), apply weights for the target venue only and note that multi-venue comparison was skipped

### 8.5 Output

Save individual reviews and aggregate scorecard:
- `{project}/03-mock-review/r1-domain-expert.md`
- `{project}/03-mock-review/r2-methodology.md`
- `{project}/03-mock-review/r3-big-picture.md` (Full mode only)
- `{project}/03-mock-review/r4-newcomer.md` (Full mode only)
- `{project}/03-mock-review/scorecard.md` -- aggregate scores, consensus, AC decision

Update PROGRESS.md: `**Current Phase:** 8 (Mock Review Complete)`

## Phase 9: Action Plan

> References: Apply frameworks from `references/critical-thinking-frameworks.md`: Pareto (prioritize improvements), One Thing (single highest-leverage action), Eisenhower (urgency/importance matrix).

Synthesize all phases into a verdict and concrete next steps.

### 9.1 Stage-Adaptive Verdict

Read research_stage from `{project}/00-intake/intake.md`. Verdict question changes per stage:
- **idea:** "Is this proposal worth pursuing?" Projected Score drives verdict. GO = strong question + sound design + clear novelty. CONDITIONAL = needs refinement before experiments. NO-GO = fundamental issues.
- **preliminary_results:** "Is this on track for a strong submission?" Both Current and Projected Score inform verdict. Focus on trajectory.
- **draft:** "Is this paper ready for submission?" Current Score drives verdict. Full paper evaluation.

### 9.2 Verdict

Three possible outcomes:

**GO** -- clear path to acceptance:
- Prioritized improvement list (Pareto: which 20% of fixes yield 80% of score increase)
- The ONE Thing: single most impactful action that makes everything else easier
- Eisenhower matrix: Q1 do first (reviewer will reject without this), Q2 schedule (strengthens paper), Q3 minimize (minor fixes), Q4 skip (diminishing returns)
- Experiment priorities with effort estimates (S/M/L)
- Timeline to submission with milestones

**Fast Track:** Top-3 improvements only, no Eisenhower matrix.

**CONDITIONAL** -- fixable issues block acceptance:
- Critical experiments or evidence needed before proceeding
- Risk assessment: what happens if experiments fail?
- Minimum viable paper: smallest set of results that clears the acceptance bar
- Decision point: "Run experiment X. If result > Y, GO. Otherwise, NO-GO."

**NO-GO** -- fundamental problems:
- Honest explanation of why (novelty, feasibility, contribution thickness)
- Pivot suggestions: alternative directions using existing work
- Salvageable elements: what can be reused in a different project
- Alternative venues: where this might fit (e.g., workshop instead of main conference)

### 9.3 Kill Criteria

Define 5-7 specific, measurable conditions under which the researcher should stop and redirect (e.g., "Baseline X outperforms your method on 2+ benchmarks after fair tuning"). If ANY kill criterion triggers, pause and reassess.

### 9.4 Output

Create three files:
- `{project}/04-action/action-plan.md` -- verdict, prioritized improvements, timeline
- `{project}/04-action/improvement-checklist.md` -- checklist items with effort estimates (S/M/L)
- `{project}/04-action/kill-criteria.md` -- numbered kill criteria with trigger conditions

Update PROGRESS.md: `**Current Phase:** 9 (Action Plan Complete)`

## Final Deliverable

After Phase 9, produce:

1. **Assessment Dashboard** -- print the dashboard from `references/output-guidelines.md` in conversation. Fill: novelty (Phase 4), soundness/experiments/reproducibility (Phase 6), significance (Phase 7), clarity (Phase 1 + 7), overall (Phase 8 aggregate), verdict (Phase 9).
2. **Project README** -- `{project}/README.md` with executive summary, key findings, verdict, and links to all generated files.
3. **Anti-Pattern Check** -- scan all outputs against anti-patterns in `references/honesty-protocol.md`. Revise if any match.
4. **Citation Validation** -- run `python scripts/validate_citations.py {project}/`. Fix any `[Unverified]` citations.

## Reference Files

Progressive loading: only read files when needed by the current phase.

| File | When to Read | ~Lines | Purpose |
|------|-------------|--------|---------|
| `references/output-guidelines.md` | Start of run | ~136 | File headers/footers, dashboard template, quality examples |
| `references/honesty-protocol.md` | Phase 1 onward | ~109 | Claim labels, anti-hallucination, anti-patterns |
| `references/critical-thinking-frameworks.md` | Phase 1, 4, 6, 8, 9 | ~115 | 10 frameworks mapped to specific phases |
| `references/research-principles.md` | Phase 3 (before waves) | ~95 | Search protocol, source tiers, anti-hallucination rules |
| `references/consider-5-whys.md` | Phase 1.3 (consider agent prompt) | ~49 | 5 Whys framework for root motivation analysis |
| `references/consider-first-principles.md` | Phase 1.3 (consider agent prompt) | ~50 | First Principles framework for hidden assumptions |
| `references/consider-inversion.md` | Phase 1.3 (consider agent prompt, Full only) | ~60 | Inversion framework for rejection failure modes |
| `references/consider-occams-razor.md` | Phase 1.3 (consider agent prompt, Full only) | ~54 | Occam's Razor framework for complexity audit |
| `references/alphaxiv-mcp-guide.md` | Phase 3 (if MCP available) | ~145 | AlphaXiv MCP setup, tools, fallback |
| `references/research-wave-1-literature.md` | Phase 3.2 | ~188 | Wave 1 agent templates and tool sequences |
| `references/research-wave-2-landscape.md` | Phase 3.3 | ~152 | Wave 2 agent templates and tool sequences |
| `references/research-wave-3-venue.md` | Phase 3.4 (Full mode) | ~238 | Multi-venue Wave 3 agent templates and tool sequences |
| `references/research-synthesis.md` | Phase 3.5 (Synthesis) | ~139 | Synthesis protocol and cross-document rules |
| `references/novelty-framework.md` | Phase 4 | ~100 | Novelty typology, decision tree, anti-patterns |
| `references/experimental-design.md` | Phase 6 | ~104 | Baseline rules, statistics, ablation, claims-evidence |
| `references/conference-standards.md` | Phase 6, 8 | ~175 | Venue review forms, weights, acceptance patterns |
| `references/contribution-types.md` | Phase 7 | ~83 | Contribution taxonomy, framing strategies, 5-second test |
| `references/mock-review-templates.md` | Phase 8 | ~281 | 4 reviewer personas, scoring format, aggregate protocol |
| `references/verification-agent.md` | Phase 5 (verification agent prompt) | ~73 | V1 verification agent protocol and checklist |
