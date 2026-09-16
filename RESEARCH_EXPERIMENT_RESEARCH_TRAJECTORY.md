# Research Experiment: Research Trajectory

## Status

**Differential trajectory experiment — protocol implemented; observation pending.**

No claim has been promoted that Cognitia can adapt its research trajectory. This phase is designed to let the observed trajectory determine whether a controlled evidence perturbation changes what happens next.

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

The differential experiment must not encode its expected scientific result into its assertions. CI assertions protect experimental integrity; the generated artifact records the actual outcome. Both divergence and non-divergence are informative observations.

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

## Experiment 2: differential trajectory observation

This is the next experiment after trajectory observability. It is intentionally narrower than a claim of adaptive cognition.

### Research question

> When the research question is held constant but the first acquired evidence differs, does the subsequent research trajectory change?

### Hypothesis

A change in the evidence state **may** change the subsequent research trajectory. The direction, specific information need, and specific research objective are not specified in advance.

This wording is deliberate. We are testing whether a difference emerges, not implementing a predetermined A → X and B → Y result.

### Controlled conditions

Three executions are run through the same `AdaptiveOpenResearch` controller:

- **Condition A:** first evidence state contains one controlled service-failure observation;
- **Condition B:** first evidence state contains a different controlled service-failure observation;
- **Same-evidence control:** repeats Condition A exactly.

Across all three:

- the research question is identical;
- the controller is identical;
- the round limit is identical;
- acquisition limits are identical;
- the first search/action is identical;
- only the first acquired evidence content differs between A and B.

The control is not a scientific conclusion. It checks that repeating the same controlled input reproduces the same subsequent behavior under the deterministic implementation.

### Required observations

The CI artifact records the complete two-round trajectory for each condition, including:

- question;
- acquired first evidence;
- action identity and parent action;
- search objective;
- information need;
- source claim/document identifiers for the information need;
- decision rationale;
- claims and documents entering each step;
- whether the second information need changed;
- whether the second objective changed;
- whether source-claim references changed;
- whether the same-evidence control reproduced the result.

### What CI is allowed to assert

CI asserts experimental integrity only:

- the controlled question and first action are equal;
- A and B actually differ in first evidence;
- each second step is linked to its own preceding action;
- information need and provenance are present;
- the same-evidence control reproduces the A trajectory under the deterministic implementation.

CI does **not** assert that A and B must diverge.

### What the observation means

If the second trajectories differ, the observation supports the narrower statement that the implemented controller is sensitive to this changed evidence state.

If the second trajectories do not differ, the observation shows that this particular evidence perturbation did not change the subsequent trajectory.

Neither outcome establishes learned cognition. The current adaptive controller contains researcher-authored deterministic routing rules. Therefore the observed result is evidence about the implemented research mechanism, not evidence of an independently learned research policy.

## CI and research-record method

The communication experiment established the useful pattern we are reusing:

1. define the research question before the result;
2. encode the controlled experiment in executable code;
3. run it through GitHub Actions;
4. preserve the actual behavioral output as an artifact;
5. update the research history from the observation;
6. state the evidence boundary explicitly;
7. derive the next experiment from what was observed rather than from a fixed roadmap.

For the differential trajectory experiment, the dedicated workflow is `differential-research-trajectory`. It executes `tests/ci/differential_trajectory.py` and uploads `.ci/differential-trajectory.json` even when the experiment fails, so the research record is not reduced to a green/red status.

This mirrors the communication record's distinction between behavioral evidence, persistence/continuity evidence, and regression evidence. CI success itself remains an implementation fact, not a cognitive finding.

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
- Did the controlled evidence perturbation alter the next trajectory?

The last question is deliberately open.

## What would support HRT-1

The recorded trajectory is faithful to the executed research episode and does not invent hidden cognitive causes.

## What would weaken HRT-1

- trajectory records disagree with actual execution;
- important executed evidence cannot be reconstructed;
- records silently infer reasoning that the system never represented;
- the same execution cannot be reproduced from the recorded state;
- later adaptive experiments cannot identify the evidence state available before an action.

## What would support the narrower differential observation

The controlled runs produce a reproducible record showing whether and how the subsequent action changes when only the first evidence changes.

The result is useful whether the trajectories diverge or remain equal, provided the perturbation and controls are valid and the observation is preserved.

## What would be a stronger future result

A later experiment would need to vary the question and/or evidence structure without changing the researcher-authored routing rules. The purpose would be to determine whether the observed evidence-to-action relationship survives outside the exact scenario used here.

Only after such transfer/generalization evidence should we consider whether the implemented mechanism is expressing a broader research capability. Learning would require an additional discriminator showing that experience changes future behavior and that the change transfers beyond the exact experience that produced it.

## Research record

### 2026-09-16 — initial trajectory direction

The Roman Empire CI runs motivated this route. The English answer changed because live evidence and extracted claim composition changed, but the current implementation did not establish that Cognitia changed its search plan because of what it learned during an earlier round.

### 2026-09-16 — observability implementation started

A standalone trajectory reconstruction layer was added without changing search behavior. This deliberately separates **observing research** from **changing research**.

Current interpretation: **insufficient evidence for adaptive research.**

### 2026-09-16 — differential experiment protocol corrected

The first version of the differential experiment encoded the expected result into the test: resource-exhaustion evidence was expected to produce one second objective and dependency-failure evidence another. That was implementation-led rather than discovery-led.

After comparing it with the communication experiment's method, the protocol was changed so that:

- the hypothesis no longer names the expected second action;
- CI protects controls and provenance rather than requiring divergence;
- the CI artifact records the actual relationship between the changed evidence and subsequent trajectory;
- the research history is updated only after the observation exists.

Current interpretation remains **unknown pending CI observation**.

## Relationship to communication research

Communication research remains active and unresolved. Its current supported boundary is that communication experience can transfer a consequence across structurally related held-out states while preserving epistemic commitments, but the abstraction used for that transfer remains researcher-specified.

We are pausing that route at this boundary while making Cognitia's research/evidence trajectory observable. We will return to communication when the cognitive/evidence state is sufficiently explicit to test whether representation rearrangement can itself be discovered rather than supplied.
