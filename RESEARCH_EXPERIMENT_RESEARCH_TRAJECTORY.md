# Research Experiment: Research Trajectory

## Status

**Active research route — observability experiment in progress.**

No claim has been promoted that Cognitia can adapt its research trajectory. This phase records the behavior needed to test that claim without assuming the answer.

## Why this experiment exists

The Roman Empire research runs changed between executions: the evidence landscape moved from 149 extracted claims / 6 factor categories to 136 extracted claims / 8 factor categories, while the central synthesis remained cautious and multi-factor. Inspection showed that `OpenEndedResearch.investigate()` constructs a bounded plan before executing its rounds. The normal path does not currently call `ResearchSearchPlanner.follow_up()`.

Therefore the changing output is evidence of a changing acquired evidence landscape, not evidence that Cognitia noticed Round 1 and deliberately changed Round 2.

We need to distinguish:

1. environmental variation;
2. extraction variation;
3. interpretation variation;
4. search-policy variation;
5. synthesis variation.

The first build step is therefore **trajectory observability**, not a smarter planner.

## Research question

Can Cognitia expose enough of its own research trajectory that we can determine what it observed, what information need remained, why an action was selected, and what changed after the action?

The stronger later question is:

> Can Cognitia use the evidence state produced by one investigation round to construct the next investigation rather than executing a precomputed collection plan?

We do not assume the answer is yes.

## Experimental discipline

The research route follows the same discipline used for communication:

`hypothesis → controlled experiment → observation → interpretation → revised hypothesis → next experiment`

For research:

`question → investigation → evidence state → information need → next investigation → revised evidence state`

A changing answer is not itself evidence of learning. We require an inspectable causal path from an observed state to a subsequent research action.

Engineering failures are not research findings. They are fixed and excluded from the research history unless they reveal a property of Cognitia's research behavior itself.

## Experiment 1: trajectory reconstruction

### Hypothesis HRT-1

A bounded research episode can be represented as an inspectable trajectory containing the selected action, search observations, acquired documents, extracted claims, conflicts, source origins, and unresolved information needs without inventing causal explanations that the current system does not expose.

### Controlled variables

- research question;
- existing search planner;
- existing live web acquisition;
- existing claim extraction;
- existing synthesis path.

### New observation layer

`cognitia/research_trajectory.py` introduces:

- `ResearchTrajectoryStep`
- `ResearchTrajectory`
- `reconstruct_trajectory(...)`

The reconstruction records:

- sequence;
- action identity;
- purpose;
- search objective;
- recorded decision rationale;
- expected information gain;
- search observation IDs;
- document IDs;
- claim IDs;
- cluster count;
- conflict count;
- source origins;
- unresolved information needs.

### Important boundary

The current system does **not** expose a true internal information-need state. The trajectory recorder therefore leaves `unresolved_information_needs` empty at the per-step level rather than deriving one from the query and pretending it was Cognitia's internal reasoning.

Likewise, `decision_rationale` is recorded exactly as the existing system provides it. It is not treated as proof that the action was causally selected from previous observations.

This is intentional. The experiment must show us what the system actually exposes before we claim more.

## Expected observation

We should be able to reconstruct a research episode and answer:

- What did Cognitia search?
- What did it observe?
- What documents entered the evidence state?
- What claims entered the state?
- What conflicts were visible?
- What source origins were represented?
- What action did the planner select?
- What rationale did the system actually record?
- What information remains unobservable?

## What would support HRT-1

The recorded trajectory is faithful to the executed research episode and does not invent hidden cognitive causes.

## What would weaken HRT-1

- trajectory records disagree with actual execution;
- important executed evidence cannot be reconstructed;
- records silently infer reasoning that the system never represented;
- the same execution cannot be reproduced from the recorded state;
- later adaptive experiments cannot identify the evidence state available before an action.

## Next experiment — not yet started

After trajectory reconstruction is validated, run a small controlled two-round experiment:

**Round 1:** broad investigation.

**Round 2:** Cognitia must choose the next action from the actual Round-1 evidence state.

Compare against a precomputed-plan control.

The adaptive hypothesis is only supported if the next action is demonstrably generated from the preceding evidence state, its information need, contradiction, uncertainty, or evidence gap — and this behavior survives a changed question/state without question-specific hardcoding.

## Research record

### 2026-09-16 — initial trajectory direction

The Roman Empire CI runs motivated this route. The English answer changed because live evidence and extracted claim composition changed, but the current implementation did not establish that Cognitia changed its search plan because of what it learned during an earlier round.

### 2026-09-16 — observability implementation started

A standalone trajectory reconstruction layer was added without changing search behavior. This deliberately separates **observing research** from **changing research**.

Current interpretation: **insufficient evidence for adaptive research.**

Next decision must be made from the trajectory experiment's observed behavior, not from the roadmap alone.

## Relationship to communication research

Communication research remains active and unresolved. Its current supported boundary is that communication experience can transfer a consequence across structurally related held-out states while preserving epistemic commitments, but the abstraction used for that transfer remains researcher-specified.

We are pausing that route at this boundary while making Cognitia's research/evidence trajectory observable. We will return to communication when the cognitive/evidence state is sufficiently explicit to test whether representation rearrangement can itself be discovered rather than supplied.
