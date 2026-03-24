# Novelty Framework

Novelty typology, calibration, decision tree, anti-patterns, and prior work comparison for ML/AI research.

## Novelty Typology

| Type | Description | Minimum Bar for Top Venue |
|------|-------------|--------------------------|
| New paradigm | Fundamentally new way of thinking | Changes how the field frames the area |
| New method | New algorithm or architecture | Clear advantage + insight into WHY it works |
| New formulation | New problem definition or task framing | Must reveal something non-obvious |
| New analysis | Deep understanding of existing methods | Must change practice ("stop doing X") |
| New application | Known method applied to new domain | Requires domain-specific adaptation + insight |
| Combination | Combining known components A + B | Must show emergent properties (A+B > A + B) |
| Engineering | Better implementation, scaling, efficiency | Must be 10x+, not 20% faster |

## Novelty Calibration Scale (1-10)

| Score | Meaning | Landmark Example |
|-------|---------|-----------------|
| 10 | Paradigm shift | Attention Is All You Need (Transformer) |
| 9 | Foundational new capability | GPT-3 (scaling laws + in-context learning) |
| 8 | Major new direction | LoRA, Chain-of-Thought Prompting |
| 7 | Strong novelty, clear gap filled | DPO, Flash Attention |
| 6 | Solid new method with clear advantages | Typical top-venue oral paper |
| 5 | Incremental but with genuine insight | Typical top-venue poster paper |
| 4 | Engineering contribution or application | Solid workshop paper |
| 3 | Trivial combination of known techniques | Likely rejected at top venue |
| 2 | Minor variation, no new insight | Below publication threshold |
| 1 | Already published or trivially derivable | Not a contribution |

## "Is It Novel?" Decision Tree

Five sequential questions. Stop at the first Red flag and resolve before continuing.

1. **Does this exact method or idea exist in published work?**
   YES -- Red flag. Identify how you differ or stop here. NO -- Continue.
2. **Are the individual components all known?**
   YES -- What is the INSIGHT of combining them? No insight = no novelty.
   NO -- Which component is genuinely new? That is your contribution.
3. **Could a competent expert trivially arrive at this?**
   YES -- Need substantially stronger empirical results to justify. NO -- Likely novel.
4. **Does concurrent work exist (arxiv preprints, recent submissions)?**
   YES -- Need to differentiate clearly. See concurrent work protocol below.
   NO -- Good signal, but verify: is nobody working on this because it is not interesting?
5. **Where does the novelty live?**
   Method -- Strongest. Results -- Need impressive margins. Framing -- Weakest, needs strong motivation.

## Novelty Anti-Patterns

| Anti-Pattern | Why It Fails |
|--------------|-------------|
| "Nobody applied X to Y" without domain insight | Application without adaptation is not a contribution |
| "First to evaluate on this dataset" | Using a new dataset is not novelty -- the method must be novel |
| "We added module X to architecture Y" | Incremental bolting-on without motivation or ablation |
| "Better by 0.3%" | Within variance of existing methods -- not a real improvement |

## Concurrent Work Handling Protocol
| Scenario | Flag | Action |
|----------|------|--------|
| Published at top venue, same approach | RED FLAG | Novelty is gone. Pivot or find a different angle. |
| Preprint on arxiv, same approach | YELLOW FLAG | Race condition. Accelerate, differentiate clearly. |
| Preprint on arxiv, different approach | Opportunity | Cite and compare. Evidence the problem matters. |
| Different framing but same core technique | YELLOW FLAG | Must differentiate explicitly. Show framing adds value. |

If no concurrent work: nobody thought of it (good) or nobody finds it interesting (check significance).

## Incremental vs Significant Contribution
An incremental contribution becomes significant when it includes at least one of:
- A new insight explaining WHY the improvement works
- A theoretical analysis that generalizes beyond the specific case
- Results crossing a meaningful threshold (enabling a new capability)
- Evidence the approach changes best practice for the community

Without any of these, the contribution remains incremental regardless of raw metric improvement.

## Top-5 Closest Prior Work Comparison
For each of the 5 most similar works:

```
Paper: [title, authors, venue, year]
Similarity axis: method / task / data / setting
What they share: [specific overlap]
What is different: [specific delta]
Could they trivially extend to cover ours? [yes/no + why]
```

Key question: "Could a competent researcher, reading paper X, arrive at this as an obvious next step in under one day?" YES = weak novelty. NO = novelty has substance.

## Delta Classification
After the Top-5 comparison, classify the primary delta and assign a calibration score.

```
Primary delta type: [from typology table]
Calibration score: [1-10]
Evidence: [why this score -- reference specific prior work gaps]
Concurrent work impact: [none / opportunity / YELLOW FLAG / RED FLAG]
Adjusted score: [after concurrent work adjustment]
```
If adjusted score is below 5, flag as a novelty concern in the assessment.
