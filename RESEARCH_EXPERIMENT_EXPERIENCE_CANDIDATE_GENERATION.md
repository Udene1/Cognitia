# Experience → Candidate Generation Boundary

## Research question

Can a structurally related prior experience prevent a necessary investigation candidate from being generated at all?

This follows the earlier experience downstream-consequence and operation-choice experiments. Those experiments showed that experience can reach downstream candidate evaluation without making a held-out problem identical to the prior problem or preventing the operation selected from following the current information need. The next earlier boundary is candidate generation itself.

## Experimental discipline

The experiment does **not** add experience as an input to `StateActionGenerator`. That would change the architecture before observing whether the existing architecture already permits the hypothesized influence.

For each held-out problem, candidate generation is run under three ledger conditions:

1. no stored experience;
2. a structurally related confirmed experience;
3. a structurally related refuted experience.

The complete pre-selection candidate sets are recorded. Experience retrieval is also recorded separately so that retrieval is not confused with causal influence on generation.

The cases cover:

- a freshness/current-status problem;
- unresolved local uncertainty;
- a computational problem.

The available operations are external search, local inspection, computation, and reasoning. No expected candidate is asserted by the harness; the observed generated set is the primary evidence.

## Boundary inspected

`StateActionGenerator.generate(...)` currently consumes only:

- the current `CognitiveState`;
- the operations available from the environment;
- the maximum candidate count.

The implementation derives candidate signals from uncertainty, hypotheses, evidence, knowledge, and goal. The experience ledger is not an argument to this generator.

Therefore, if the generated sets remain identical while relevant experience is retrieved, the narrow result is architectural: **the current tested path does not allow the experience ledger to suppress candidate generation directly.**

That is not a general claim that experience can never create a candidate-generation blindspot. A future mechanism could first transform cognitive state using experience and then pass the transformed state to the generator. That route is not tested here.

## Result

The result is written to `.ci/experience-candidate-generation.json` by the CI experiment harness. The artifact is the research record; CI success itself is only an engineering gate.

### Interpretation rule

- If candidate sets differ across experience conditions, we have evidence of a genuine pre-selection influence and must investigate that route before proceeding.
- If candidate sets are invariant, we have evidence that the current generator boundary is downstream of neither direct experience retrieval nor experience outcome. The next question becomes whether **experience-derived state change** can alter the generator inputs.

## Relation to the blindspot hypothesis

This experiment narrows the blindspot question again. The prior evidence already showed that structural relatedness does not, by itself, make a new problem inherit an old action. The operation-choice experiment further showed that experience could alter upstream action evaluation without preventing an operation selected from the current information need.

This experiment asks whether experience can act even earlier by removing an action before evaluation begins.

A negative result here should therefore be recorded as a boundary finding, not as proof that the broader blindspot problem is solved.

## Next boundary

If invariant, test the state-update route:

> Can an experience-derived update change the inputs from which candidates are generated, without directly prescribing the candidate vocabulary?

That experiment should distinguish a genuine experience-to-state mechanism from simply passing an experience object into the generator and teaching the harness the desired answer.
