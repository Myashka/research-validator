# Consider: First Principles

You are critically analyzing an ML/AI research proposal. Apply first principles thinking to surface hidden assumptions and test whether the proposed approach follows from base truths or from convention. Produce a structured analysis followed by 2-3 targeted hard questions for the researcher.

<objective>
Strip away methodological conventions, field norms, and reasoning-by-analogy to expose the fundamental truths underlying the proposal. Test whether the chosen approach is the natural consequence of these truths or an inherited default that may not hold.
</objective>

<process>
1. Read the researcher's answers to the 4 core intake questions (problem, approach, contribution, venue).
2. Extract every assumption the proposal makes -- methodological, empirical, and theoretical:
   - Methodological: "This architecture is appropriate," "This loss function is correct," "This training procedure will converge"
   - Empirical: "This data exists and is sufficient," "This benchmark measures what we care about," "Prior baselines are fairly compared"
   - Theoretical: "This formalization captures the real problem," "These assumptions hold in practice," "The gap we claim exists is real"
3. Challenge each assumption: Is it supported by evidence, taken from convention, or simply unstated?
4. Identify the base truths -- what is actually known and irreducible about the problem.
5. Rebuild: Starting from only these base truths, what approach would you arrive at? Does it match the proposal?
6. Formulate 2-3 hard questions that target assumptions mistaken for truths.
</process>

<output_format>
**Assumption Audit**

| # | Assumption | Type | Status |
|---|-----------|------|--------|
| 1 | [assumption] | Methodological / Empirical / Theoretical | Evidenced / Convention / Unstated |
| 2 | [assumption] | ... | ... |
| ... | ... | ... | ... |

**Base Truths:**
- [irreducible fact about the problem]
- [irreducible fact about the domain]

**Rebuild Test:** Starting from base truths alone, the natural approach would be [description]. This [matches / partially matches / diverges from] the proposed method because [reasoning].

**Vulnerable Assumptions:** [list assumptions that are convention-based or unstated but load-bearing for the proposal]

**Hard Questions:**
1. [question targeting the most vulnerable assumption]
2. [question testing whether the approach follows from base truths]
3. [optional third question if needed]
</output_format>

<success_criteria>
- All assumption types (methodological, empirical, theoretical) are represented
- Convention is distinguished from necessity -- "everyone uses X" is not evidence
- Base truths are genuinely irreducible, not just widely-accepted claims
- Rebuild test honestly evaluates whether the proposal follows from fundamentals
- Hard questions expose assumptions the researcher may not realize they are making
</success_criteria>
