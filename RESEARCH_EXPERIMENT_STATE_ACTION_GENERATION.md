# Research Experiment: State-Generated Action Space

## Question

Can Cognitia construct candidate intermediate actions from its current cognitive state and permitted operations, rather than receiving a researcher-authored vocabulary of intermediate search facets?

## Why this boundary matters

The previous action-space reduction still used `ResearchSearchPlanner` to create the candidate actions. That means the experiment reduced ordering and surface convenience, but the researcher still determined the vocabulary Cognitia could choose from.

This experiment removes that hidden control.

The intended boundary is:

`current state -> generated candidates -> selection -> operation -> observation -> updated state -> experience`

The evaluator supplies only:

- the current problem/state;
- the operations the environment permits;
- constraints needed to make the operation legal.

The evaluator does **not** supply an expected action, search facet, or preferred intermediate path.

## Current implementation

`cognitia/state_action_generation.py` introduces:

- `AvailableOperation`: an environment capability, not an expected action;
- `GeneratedAction`: an auditable candidate tied to the state signal that generated it;
- `StateActionGenerator`: deterministic candidate construction from uncertainty, hypotheses, evidence, knowledge, goal, and the problem.

The existing `ResearchSearchPlanner` remains untouched as a control. It is intentionally not used by this experiment.

## Experimental conditions

1. **Training state** — unresolved cause, existing evidence, multiple hypotheses, explicit goal.
2. **Changed surface + conflict** — different problem wording with conflicting observations.
3. **Partial state** — reduced evidence and a narrower hypothesis set.

The experiment records the full generated candidate set and the state signals that produced each candidate.

## Measurements

- whether candidates are generated without an expected action;
- whether changing state changes the generated candidate set;
- whether every candidate has explicit state provenance;
- whether planner-authored search facets were absent.

These are mechanism measurements, not scores of cognition.

## What this does not establish

A state-derived candidate is not automatically useful. A deterministic generator is not automatically learning. Candidate novelty is not evidence of intelligence. This experiment does not establish general cognition, learning, transfer, planning, or real-world usefulness.

## Next reduction

Connect the generated candidates to an auditable selector and then to an operation executor. The executor must return an observed consequence, not an evaluator assertion of success. The resulting state transition and experience record must be preserved.

The next important test is therefore not whether the generator can produce strings. It is whether a generated intermediate action can create new evidence, change the state, survive a failed action, and alter the next action without the evaluator quietly supplying the missing path.

## Research rule

A green CI run is engineering evidence only. The `.ci/state-action-generation-research.json` artifact is the research evidence. Interpret the actual trajectories before drawing conclusions.
