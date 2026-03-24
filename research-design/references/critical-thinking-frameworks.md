# Critical Thinking Frameworks

These frameworks are embedded at specific points in the process. Not a generic toolkit -- each is applied where it's maximally effective.

## Framework x Phase Matrix

```
                 INTAKE   NOVELTY  METHOD   SIGNIF.  MOCK     ACTION
5 Whys            *
First Principles  *                 *
Inversion         *F        *                          *
Occam's Razor     *F                *
Via Negativa                        *
Second-Order                                 *
Opportunity Cost           *
Pareto                                                         *
One Thing                                                      *
Eisenhower                                                     *

*F = Full mode only (consider agent)
```

## Intake-Phase Frameworks (Consider Agents)

The following frameworks are applied at Intake by dedicated consider agents. Each has its own reference file with a full agent prompt:

- **5 Whys (Intake):** See `references/consider-5-whys.md`
- **First Principles (Intake):** See `references/consider-first-principles.md`
- **Inversion (Intake):** See `references/consider-inversion.md` (Full mode only)
- **Occam's Razor (Intake):** See `references/consider-occams-razor.md` (Full mode only)

## 2. First Principles (Methodology)

1. List assumptions: ___, ___, ___
2. Challenge each: supported by evidence? Or convention/trend-following?
3. Base truths: what remains after removing unsupported assumptions?
4. Rebuild: given only base truths, what approach follows naturally?

At Methodology: challenge whether complexity is needed.
Key question: "Does the proposed method align with base truths, or is it driven by convention?"

## 3. Inversion (Novelty + Mock Review)

- What would guarantee this paper gets rejected? -> list failure modes
- For each failure mode: is it present? -> avoidance plan
- Anti-Goals: never claim novelty without verifying, never skip strongest baseline, never present best-of-N runs

At Novelty: identify fatal gaps before experiments. At Mock Review: generate worst-case reviewer objections.
Key question: "What is the single most likely reason a reviewer rejects this?"

## 4. Occam's Razor (Methodology)

1. Proposed method: requires assumptions [___]
2. Simpler alternative: requires assumptions [___]
3. Simplest baseline: requires assumptions [___]
4. Evidence check: which assumptions are actually supported?
5. Simplest valid approach: ___

Apply when evaluating whether complexity is justified.
Key question: "Has the simplest reasonable baseline been tried?" If NO, this is experiment #1.

## 5. Via Negativa (Methodology)

For each method component:
- Component ___: remove -> performance change: ___ -> KEEP / REMOVE / MUST TEST
After subtraction: the real contribution is ___, not the full pipeline.

Drives ablation study design.
Key question: "What can we remove without meaningful performance loss?"

## 6. Second-Order Thinking (Significance)

- Action: this research shows ___ works for ___
- 1st order: ___ -> 2nd order: ___ -> 3rd order: ___
- Delayed consequences: ___
- Revised impact: high / medium / low because the chain reaches ___

Assesses whether impact extends beyond the immediate result.
Stop when consequence chain either reaches broad impact or clearly fizzles out.

## 7. Opportunity Cost (Novelty)

- Resources required: ___ months, ___ compute, ___ conference cycles
- Best alternative uses: direction B (___), direction C (___)
- True cost: choosing this means NOT pursuing ___
- Verdict: is expected value of this direction higher than best alternative?

Apply at Novelty gate when deciding whether a direction is worth pursuing.
Key question: "Is this the best use of 6 months of research?"

## 8. Pareto (Action Plan)

Rank improvements by (impact on score x 1/effort):
- Vital few (do FIRST): 1. ___, 2. ___, 3. ___
- Trivial many (defer/skip): ___
- Bottom line: N improvements, ~X weeks, expected score increase: +Y

Key question: "Which 20% of improvements yield 80% of score increase?"

## 9. One Thing (Action Plan)

- Goal: get this paper from ___/10 to ___/10
- Candidate actions: ___
- The ONE domino: ___ -- because doing this makes everything else easier or unnecessary
- Next action: ___

Key question: "If you could fix only one thing before submitting, what would it be?"

## 10. Eisenhower (Action Plan)

- Q1 Do First (important + urgent): ___ (reviewer will reject without this)
- Q2 Schedule (important + can wait): ___ (strengthens paper significantly)
- Q3 Minimize (urgent but not critical): ___ (formatting, minor fixes)
- Q4 Skip (neither): ___ (diminishing returns experiments)

Key question: "What will a reviewer reject without?" -- that goes in Q1.
