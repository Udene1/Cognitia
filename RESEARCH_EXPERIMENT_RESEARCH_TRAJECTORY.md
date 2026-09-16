# Research Experiment: Adaptive Research Trajectory

## Status

Research direction / instrumentation phase. No behavioral claim is promoted yet.

## Why this experiment exists

Cognitia produced different Roman Empire syntheses across fresh CI executions: one run acquired 149 candidate claims and another acquired 136. The central conclusion remained similar, but the factor landscape changed. We need to understand whether differences arise from the external evidence environment, claim extraction, research planning, evidence interpretation, or synthesis.

The purpose of this work is not to make the answer longer or more stable. It is to make Cognitia's research trajectory observable and eventually test whether it can use what it learns from an earlier research action to choose a better next action.

## Current observation

The current research path is bounded but largely front-loaded:

`question -> planner creates bounded actions -> live search/fetch -> claim extraction -> synthesis`

The planner is deterministic. The web evidence is live. The normal `OpenEndedResearch.investigate()` path creates its plan before executing the rounds, rather than using the observations from round 1 to construct round 2.

This means a fresh run can produce a different evidence landscape without Cognitia necessarily having changed its research strategy. We must distinguish those causes before claiming adaptive research.

## Research question

Can Cognitia inspect the evidence and uncertainty produced by an earlier research round and use that information to construct the next research action, rather than merely executing a precomputed collection plan?

A stronger eventual question is:

> Can Cognitia improve its research trajectory by selecting subsequent investigations from observed information gain, unresolved questions, contradictions, source diversity, and discriminating evidence needs?

## Hypotheses

### HRT-1 — trajectory observability

Cognitia can produce a durable, inspectable trace of each research round sufficient to reconstruct why a search action was selected, what was observed, what claims were extracted, what remained unresolved, and what information need motivated the next action.

### HRT-2 — adaptive round selection

Given the same initial question and bounded research budget, Cognitia can use observations from an earlier round to select a materially different and evidence-motivated next search action.

### HRT-3 — adaptive selection is not merely collection

The next action is selected because of information discovered in the previous round, rather than because that action was already present in the original plan.

### HRT-4 — bounded adaptive research can improve evidence discrimination

A small number of adaptive rounds can target unresolved alternatives, contradictions, or missing independent evidence more directly than a fixed collection plan.

## Important distinction

A changing answer is not itself evidence of learning.

A smaller claim count is not a failure.

A larger claim count is not a success.

The experiment must explain the causal path between:

`observation -> interpretation -> information need -> next action -> new evidence -> revised interpretation`

## Proposed research shape

Do not begin with a large autonomous planner.

Start with a small number of rounds, likely 2–3, where the first round is deliberately broad and subsequent rounds are selected from the first round's actual observations.

Example:

```text
Round 1
  broad investigation
  ↓
  claims / conflicts / source origins / uncertainty
  ↓
  identify strongest unresolved information need
  ↓
Round 2
  targeted investigation selected from Round 1
  ↓
  update evidence landscape
  ↓
Round 3 (optional)
  discriminate remaining alternative or verify missing evidence
```

The key change is that Round 2 must not simply execute a query that was already waiting in the initial plan unless Cognitia can show that Round 1 independently selected or justified it.

## Required trajectory record

Each round should eventually expose at least:

- action selected
- action purpose
- parent/preceding observation or information need
- expected information gain
- search query and terms
- search observations
- documents selected/fetched
- claims extracted
- claim clusters / conflicts
- source-origin diversity
- unresolved questions
- evidence gaps
- why this action was selected
- what changed after the action
- whether the action reduced an identified uncertainty
- whether the next action was generated from the resulting state

This record is research evidence. It should be inspectable without reconstructing behavior from raw CI logs.

## Experimental controls

### Fixed-question control

Run the same question with a fixed plan and preserve its complete evidence trajectory.

### Adaptive treatment

Run the same question with the same initial acquisition budget, but require later actions to be selected from the state produced by earlier rounds.

### Replay control

Replay the recorded first-round state and verify that the same adaptive decision can be reconstructed from the recorded state.

### No-op / irrelevant-evidence control

Introduce an observation that does not materially affect unresolved information needs. The planner should not treat every new observation as a reason to change direction.

### Contradiction control

If the first round exposes genuinely conflicting claims, the next action should be capable of targeting the conflict rather than simply collecting more generic material.

## What would count as evidence

Evidence supporting adaptive research would require all of the following in a controlled case:

1. Round 1 produces an identifiable evidence state.
2. That state contains a concrete unresolved information need or discriminating question.
3. The next action is generated from that state.
4. The selected action was not merely copied from a precomputed plan.
5. The reason for selection is inspectable.
6. The resulting evidence changes the research state in an observable way.
7. The process can repeat for another round without hard-coding the exact question-specific path.

## What would weaken or falsify the hypothesis

- Later actions are always the original plan in disguise.
- The planner changes queries without using any information from previous observations.
- Every observation causes a new search regardless of relevance.
- The system cannot identify why an action was selected.
- Adaptive behavior requires question-specific hand-written rules.
- The apparent adaptation disappears when the exact state identifier is changed.
- More searches occur but do not improve discrimination of competing explanations.

## Relationship to communication research

Communication research remains active and important, but it is not necessary to finish the entire communication route before investigating research trajectory.

The communication work has already established useful controlled findings:

- objective can change communicative act;
- recipient/context can change act while preserving epistemic commitments;
- representations can preserve epistemic content through direct or recoverable evidence encoding;
- communication consequences can revise an inspectable policy;
- experience can transfer from one interaction state to a structurally related held-out state under the current hand-specified policy abstraction.

The unresolved communication question remains whether Cognitia can discover the transferable representation/rearrangement itself rather than being handed the abstraction.

That route should remain recorded and revisitable. We should return to it when research trajectory evidence reveals that the cognitive content / evidence state is sufficiently observable to test representation rearrangement at a deeper level.

## Current interpretation

The Roman Empire runs currently provide evidence of **variation in acquired evidence landscapes**, not yet evidence of adaptive research learning.

The immediate research priority is therefore observability followed by a small adaptive-round experiment.

We should learn how Cognitia researches before asking it to research more broadly.

## Research discipline

- Do not record ordinary engineering/import/test failures as research findings.
- Record only failures that reveal something about Cognitia's research behavior or a research hypothesis.
- Do not treat CI green/red as the conclusion; inspect actual traces and outputs.
- Preserve previous observations even when later experiments revise their interpretation.
- Do not replace the broader roadmap with a single experiment; use evidence to determine sequencing.
- Before starting a new experiment, ensure no open PR remains.
