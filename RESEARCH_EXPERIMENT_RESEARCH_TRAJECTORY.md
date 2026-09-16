# Research Experiment: Research Trajectory

## Status

**Differential trajectory experiment — observed; interpretation recorded; generalization remains unresolved.**

No claim has been promoted that Cognitia can learn or generally adapt its research trajectory. The controlled experiment established that the current researcher-authored adaptive controller changes its next research objective/information need when the first evidence state is changed. The same-evidence control reproduced the corresponding trajectory. The next question is whether this relationship survives changed questions and evidence structures without question-specific routing.

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

The CI artifact from 2026-09-16 recorded the following:

- the initial question and action were identical across A, B, and the same-evidence control;
- the first acquired evidence differed between A and B;
- the same-evidence control reproduced A's information need, objective, and second search query;
- after the evidence perturbation, the second information need changed;
- the second research objective changed;
- the second search query changed;
- the source-claim references feeding the second action changed;
- the second-round document itself was the same controlled follow-up content in this harness, so the observed difference is specifically in the action selected after the first evidence state, not a difference in the second acquired document.

Thus the narrower experimental observation is:

> Under this controlled implementation, changing the first evidence state changed the subsequent research action state, while repeating the same evidence reproduced the corresponding action state.

This is evidence that the implemented `AdaptiveOpenResearch` controller is sensitive to the changed evidence state.

It is **not** evidence that Cognitia learned the relationship. The controller contains researcher-authored deterministic routing rules that inspect the current evidence structures and choose an action. The experiment therefore establishes an implementation-level evidence-conditioned transition, not learned cognition.

## CI malfunction discovered during analysis

The dedicated differential-research workflow completed successfully and produced the research artifact. The ordinary `test` workflow for the same PR failed with **190 passed, 1 failed, 1 warning**.

The failing test was `tests/test_adaptive_open_research.py::test_differential_experiment_harness_preserves_controls`. Its control assertion incorrectly required the complete web-call sequence for Conditions A and B to be identical. That assertion contradicted the experimental question because the second call is itself the trajectory variable being observed.

The failure exposed a test-harness malfunction, not a failed Cognitia research result. The corrected test now asserts that the initial question/action is controlled, while allowing the second call to differ and continuing to assert provenance, parent linkage, and same-evidence reproducibility.

This distinction is important: a red CI result can be evidence about the research instrumentation or implementation, but it must not be silently treated as evidence about cognition.

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

The last question is deliberately open for each future perturbation.

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

## Next discriminator: structural transfer of evidence-conditioned research

The observed effect is currently tied to a small controlled scenario and a deterministic controller. The next experiment must therefore change the surface problem while preserving the underlying experimental mechanism.

Do not replace the current strings with another hand-authored pair and call that generalization.

The next discriminator should use multiple held-out questions and structurally different evidence states, including at least:

- an evidence state with a supported claim;
- an evidence state with competing/conflicting claims;
- an evidence state with weak or uncertain support;
- an evidence state where no usable claim is extracted.

The controller and acquisition budget should remain fixed. The experiment should record the complete pre-action evidence state and the selected next action, then compare whether the action is systematically conditioned on the structural state across held-out questions.

The interpretation boundary remains strict: successful transfer would establish that the implemented mechanism generalizes its evidence-conditioned routing beyond the original scenario. It would still not establish learning.

A subsequent learning experiment would need an explicit experience-to-policy mechanism and a held-out evaluation showing that experience changes future behavior and that the change transfers beyond the cases that produced the experience.

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

### 2026-09-16 — differential experiment observed

The dedicated workflow completed successfully and produced the raw trajectory artifact. The controlled observation showed that changing the first evidence changed the second information need, objective, and search query, while the same-evidence control reproduced A. The second-round follow-up document was held constant, so the observed divergence occurred at the action-selection boundary.

Current interpretation: **the implemented adaptive controller is evidence-state sensitive in this controlled case; there is insufficient evidence for learned or general adaptive research.**

### 2026-09-16 — regression/test harness malfunction identified

The ordinary test workflow reported 190 passing tests and one failure. Inspection showed that the failing assertion required A and B's complete search-call sequences to remain identical, which conflicts with the experiment's purpose of observing whether the second action changes. The test was corrected to constrain only the intended controls. This is an engineering/instrumentation correction, not a cognitive result.

## Relationship to communication research

Communication research remains active and unresolved. Its current supported boundary is that communication experience can transfer a consequence across structurally related held-out states while preserving epistemic commitments, but the abstraction used for that transfer remains researcher-specified.

We are pausing that route at this boundary while making Cognitia's research/evidence state explicit enough to run stronger experiments. We will return to communication when the cognitive/evidence state is sufficiently explicit to test whether representation rearrangement can itself be discovered rather than supplied.
