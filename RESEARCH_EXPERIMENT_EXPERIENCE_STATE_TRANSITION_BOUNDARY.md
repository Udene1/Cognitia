# Research experiment: experience state-transition boundary

## Research question

Does a recorded `Experience.state_update` currently reach active cognition as a state transition?

## Why this boundary matters

The preceding experiments established two narrow facts:

1. retrieved experience can affect downstream candidate evaluation;
2. retrieved experience does not currently change the complete pre-selection candidate set.

Those results leave an earlier architectural possibility open: experience might change the cognitive state before candidate generation. If that route exists, candidate-generation invariance under direct experience input is not sufficient to establish that experience cannot create an investigation blindspot.

## Method

This experiment does **not** add a state-transition mechanism. It performs a source-level AST audit of Python under `cognitia/` for references to `state_update`.

The purpose is to distinguish:

- a state update being recorded as data inside an experience record;
- a state update actually being consumed by another component and used as the next `CognitiveState`.

No expected candidate set, selected operation, or desired transition is encoded.

## Evidence

The CI artifact `.ci/experience-state-transition-boundary.json` records every `state_update` reference found by the audit and separates references inside `cognitia/experience.py` from external consumers.

## Interpretation rule

If there are no external consumers, the result is:

> `Experience.state_update` is currently recorded but is not an implemented experience-to-state transition mechanism.

That is an architectural observation, not evidence that experience-derived state updates are impossible or unnecessary.

If external consumers exist, those consumers must be inspected before making any claim about the boundary.

## Research constraint

Do not silently introduce a transition mechanism just to test whether experience can affect state. A future state-transition capability should be designed and tested as its own research boundary, with provenance and evidence handling explicit.

## Next boundary

If a state-transition mechanism is deliberately introduced, test whether experience-derived state can change subsequent cognition while preserving the distinction between:

- what the world established;
- what the experience suggested;
- what remains uncertain;
- and what Cognitia independently investigates next.
