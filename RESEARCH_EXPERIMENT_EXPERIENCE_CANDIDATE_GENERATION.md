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

CI run `35236284316` completed successfully and produced the research artifact `.ci/experience-candidate-generation.json`. The engineering result is only the gate; the artifact is the evidence.

Across all three held-out cases, the full 16-candidate pre-selection set was identical under absent, confirmed, and refuted experience. In the confirmed and refuted conditions, the structurally related experience was actually retrieved (`exp-confirmed` / `exp-refuted`), so the invariant is not explained by failure to retrieve the experience.

The generated operation set in every case contained `external-search`, `inspect`, `compute`, and `reason`. Thus the freshness/local-investigation/computation operation candidates were present before downstream scoring or operation selection, regardless of experience outcome.

### Observed result

- `freshness-required`: candidate set unchanged across absent / confirmed / refuted experience.
- `local-uncertainty`: candidate set unchanged across absent / confirmed / refuted experience.
- `computation`: candidate set unchanged across absent / confirmed / refuted experience.

## Interpretation

The tested architecture currently places the experience boundary **after candidate generation**. Experience can be retrieved, but the `StateActionGenerator` receives only the current state, available operations, and candidate limit. Consequently, in this path, experience cannot directly remove a candidate before evaluation.

This is evidence about the implementation boundary, not proof that candidate-generation blindspots are impossible.

In particular, the experiment has **not** established what happens if experience changes cognitive state before candidate generation. That is the remaining route by which experience could indirectly suppress an investigation candidate.

## Relation to the blindspot hypothesis

This is another narrowing of the original blindspot hypothesis.

The evidence now covers three downstream boundaries:

1. **Downstream consequence:** a refuted experience can reach a structurally related held-out problem without forcing the old action.
2. **Operation choice:** experience can alter upstream candidate evaluation without changing the operation indicated by the current information need in the tested cases.
3. **Candidate generation:** experience retrieval/outcome does not directly change the pre-selection candidate set in the current architecture.

Taken together, this makes the original broad claim — “experience causes Cognitia to assume a related new problem is the same and therefore skip investigation” — substantially weaker for the tested path.

It is still too broad to say the blindspot is globally solved. The unresolved route is experience → state change → candidate generation, along with any future learning mechanism that can alter generator inputs.

## Next boundary

Test the state-update route:

> Can an experience-derived update change the inputs from which candidates are generated, without directly prescribing the candidate vocabulary?

The next experiment must first locate an actual implemented experience-to-state transition, if one exists. If none exists, that absence is itself an architectural finding and we should not invent one merely to make the experiment possible.

The experiment should compare the generator's actual inputs and candidate trajectories before and after the real state transition, while keeping the candidate vocabulary researcher-independent.
