# Cognitia — Durable Working Contract for ChatGPT

This file is the durable operating contract for continuing Cognitia if conversational state is lost. It is not merely a roadmap. It records the research philosophy, engineering rules, evidence discipline, current research state, terminology, workflow, and the standard for deciding what Cognitia has actually learned.

If this file conflicts with stale conversational memory, inspect the repository and current experiments first. If repository evidence conflicts with this file, update the file rather than preserving an obsolete belief.

## 1. What Cognitia is

Cognitia is an experimental artificial cognitive system. The research target is not a better chatbot, answer generator, prompt framework, or LLM wrapper. The target is a system that can maintain explicit cognitive state, represent evidence and uncertainty, construct and discriminate hypotheses, investigate reality, choose actions, observe consequences, learn from those consequences, revise models, and transfer useful abstractions across problems and representations.

The long-term question is whether a machine can develop increasingly general cognitive machinery from explicit representations, computation, memory, evidence, experimentation, and learning rather than taking an LLM as the cognitive substrate.

Cognitia should exploit machine advantages: persistent memory, explicit state, reproducibility, search, computation, parallelism, durable history, and long-running background work.

## 2. Non-negotiable mode of work

### No mocks / no pretend capabilities

Do not create mocks, fake integrations, placeholder intelligence, toy outputs presented as real capability, or throwaway demos merely to make a test pass. A controlled test fixture is allowed only when it isolates a research variable and its artificial nature is explicit. A fixture must never be confused with real capability.

### No LLM as cognition

Cognitia's cognitive behavior must remain inspectable without an LLM. External models may eventually be optional tools/capabilities, but they must not silently become the mechanism responsible for cognition, research decisions, epistemic judgments, or unexplained behavior.

### Research before assumption

We do not assume that a proposed cognitive mechanism works because it sounds intelligent. We construct a hypothesis, design a controlled experiment, observe actual behavior, analyze what happened, preserve the evidence, and keep only what survives.

The core scientific loop is:

```text
question
→ hypothesis
→ controlled experiment
→ observation
→ interpretation
→ surviving / rejected hypothesis
→ revised hypothesis
→ next experiment
```

A feature existing in code is not evidence that the corresponding cognitive capability exists.

### CI green is not research information

A passing CI run establishes that the tested engineering checks passed. It does **not** establish that Cognitia learned, generalized, reasoned, researched adaptively, communicated appropriately, or acquired a cognitive capability.

After every meaningful CI run, inspect what actually happened: logs, outputs, traces, artifacts, state transitions, trajectories, claims, evidence, selected actions, and persistence/recovery behavior. Explain the causal behavior where possible.

The question is always:

> What did Cognitia actually do, why did it do it, what changed, and what does that observation justify?

### Failure classification

Not every failure belongs in research history.

- **Engineering failure:** import error, broken fixture, stale test, serialization bug, CI setup defect, incorrect field access, infrastructure failure, etc. Fix it. Do not record it as evidence about cognition.
- **Research/behavioral failure:** Cognitia behaves differently from the hypothesis in a way that reveals something about its cognitive mechanism, representation, epistemic boundary, adaptation, transfer, reasoning, or interaction. Preserve it as research evidence.

Engineering defects may explain why an experiment did not execute, but they are not themselves research findings.

### Preserve failures and regressions

A failed research hypothesis is valuable. Do not erase it merely because a later implementation works. Preserve the original observation, interpretation, boundary, and what changed.

A capability regression is not automatically a reason to delete the new capability. Investigate whether the capabilities can coexist, compose, balance, or require a new abstraction. Promote only after regression gates are understood.

### No silent epistemic upgrades

Never turn unknown into known, hypothesis into fact, weak evidence into strong evidence, candidate cause into established cause, or uncertain into certain merely because another component needs a convenient answer.

Every important conclusion should expose, where applicable:

```text
claim → evidence → provenance → assumptions → alternatives → strongest objection
→ falsifier / discriminating test → uncertainty → verification requirement
```

### Capability limitation does not terminate investigation

If Cognitia cannot establish an answer, it should still investigate the question with the capabilities available. It must state what it could establish, what remains uncertain, why the limitation occurred, and what evidence or capability would be needed for verification.

## 3. What counts as real progress

Do not optimize for number of files, formulas, tests, lines of code, stored text, LLM calls, demos, or green CI badges.

Progress means a **reliable, inspectable, testable cognitive capability** has been demonstrated and survives controlled testing.

For every substantial change ask:

1. What cognitive capability is being tested or added?
2. What representation does it require?
3. What did Cognitia actually do before the change?
4. What does it actually do after the change?
5. Which variable changed in the experiment?
6. What remained controlled?
7. What observation supports the claim?
8. What alternative explanation remains?
9. What does the result *not* establish?
10. Does the behavior transfer beyond the exact hand-built case?
11. What existing capability could regress?
12. What should be tested next to distinguish competing explanations?

## 4. Core cognitive loop

```text
Goal
→ Problem framing
→ Current state / world model
→ Relevant memory + evidence
→ Information gaps / hypotheses / possibility space
→ Select reasoning or investigation method
→ Act / investigate / compute
→ Observe consequence
→ Interpret evidence
→ Revise hypothesis / model / strategy
→ Updated cognitive state
→ Repeat
```

The important transition is not simply `input → answer`. It is state-conditioned action followed by consequence and learning.

## 5. Cognitive architecture

### Foundation
- World state/model
- Working and long-term memory
- Knowledge representation
- Evidence and provenance
- Experience memory
- Goals and context
- Capability self-model

### Epistemic substrate
- Claims/propositions
- Assumptions
- Evidence relationships
- Knowledge gaps
- Contradictions
- Uncertainty
- Belief/model revision history
- Source/provenance comparison
- Verification requirements

Useful epistemic result classes include established, supported, prediction, inference, hypothesis, approximation, heuristic, analogy, speculation, unresolved, and capability-limited.

### Reasoning portfolio
Eventually support multiple reasoning mechanisms rather than one universal procedure: deduction, induction, abduction, analogy, constraints, graph reasoning, probabilistic inference, causal inference, temporal reasoning, optimization, simulation, search, argumentation, counterfactual reasoning, decision theory, game theory, scientific reasoning, and normative/ethical reasoning.

A future meta-reasoner should select mechanisms according to the problem instead of blindly invoking every mechanism.

### Model and possibility space
Represent competing hypotheses, candidate causes, possible states, predictions, alternative models, and counterfactual states. Distinguish possible, plausible, probable, supported, and established. Search and prune rather than blindly enumerating every permutation.

### Self-model
Cognitia should eventually remember its own capability strengths, weaknesses, failed strategies, successful strategies, uncertainty patterns, and model revisions. A failure should help diagnose whether the missing machinery is knowledge, representation, algorithm, precision, context, search, computation, or capability interaction.

## 6. Scientific research discipline

Research is itself a cognitive capability and must be studied as behavior.

```text
Question
→ Round 1 observation
→ inspect discoveries / uncertainty / contradictions
→ identify information need
→ choose next action
→ Round 2 observation
→ revise state
→ targeted discrimination if justified
→ synthesis
→ record trajectory and surviving interpretation
```

Do not call continuous execution of a precomputed search list “adaptive research.” If later research actions were planned before earlier evidence existed, that is bounded collection, not evidence-conditioned research.

A genuine adaptive transition requires evidence that:

1. an earlier state was observed;
2. an unresolved information need existed in that state;
3. the next action was generated from that state;
4. the next action was not merely copied from a precomputed plan;
5. the reason for selection is inspectable;
6. the new observation changes the cognitive state;
7. the process can repeat;
8. the mechanism survives controlled changes in evidence.

## 7. Current research trajectory work

The Roman Empire research investigation exposed a key issue. Cognitia produced a cautious multi-factor synthesis, but repeated runs changed the extracted factor landscape (for example, 149 versus 136 claims) while retaining a similar central conclusion. The existing investigation path used a deterministic precomputed planner followed by live search/fetch and deterministic claim extraction. The normal `investigate()` path did not use planner `follow_up()` to adapt from intermediate observations.

Therefore the current interpretation is:

> Changing output across Roman Empire runs is evidence of a changing evidence/extraction environment, not yet evidence that Cognitia learned a new research path from Round 1.

This led to the research trajectory program.

### Trajectory observability

`cognitia/research_trajectory.py` records actual trajectory lineage, including sequence, action ID, parent action ID, purpose, objective, rationale, expected information gain, information need, source claim/document IDs, observations, clusters/conflicts, and source origins where exposed by the system.

Observability comes before making the planner “smart.” We must first be able to see the causal trajectory.

### Evidence-conditioned adaptive research

The adaptive research experiment introduced:

- `ResearchInformationNeed`
- `AdaptiveResearchEpisode`
- evidence-conditioned subsequent actions
- parent action IDs
- source claim/document IDs
- inspectable rationale

The controlled mechanism currently derives later information needs using researcher-specified rules:

```text
conflict → conflict_resolution
clusters → independent_evidence
claims → claim_verification
otherwise → evidence_acquisition
```

The experiment established a controlled evidence-conditioned transition, but **did not establish that Cognitia discovered the abstraction itself**. The information-need abstraction and selection policy were hand-specified.

That limitation is important and must not be forgotten.

### Differential trajectory experiment — current frontier

Commit `8895717bdd1221f165cebc1117748be1f09da5f5` adds `tests/test_differential_research_trajectory.py`.

It uses a deterministic web source and holds the question constant while changing only the first evidence:

- Case A: resource exhaustion caused the service failure.
- Case B: dependency failure caused the service failure.

The experiment asks whether the second research objective changes accordingly, rather than remaining fixed.

The intended research observation is stronger than “the test passes”: inspect both trajectories and determine whether the changed first evidence actually propagates through information-need formation into a different next action/objective.

Current CI status for this exact commit must be checked before treating the experiment as executed. A GitHub lookup currently reports **no workflow run associated with commit `8895717...`**, so there is currently no CI result for that commit to interpret. Do not infer execution from the commit existing.

## 8. Communication research

Communication is also treated as cognition, not merely text formatting.

The central question is:

> Can Cognitia learn a representation-independent model of communicative intent and interaction, such that it can transform internal cognitive states into appropriate actions for different recipients and objectives while preserving epistemic truth across representations?

The research abstraction is:

```text
cognitive state + epistemic state + interaction state + objective + recipient
→ communicative alternatives
→ act selection
→ representation/surface
→ interaction consequence
→ experience
→ policy/model revision
```

The deeper shared structure with research trajectory is:

```text
what I know / observed
→ what is unresolved
→ what action is warranted
→ consequence
→ learning
```

For communication this becomes:

```text
what I know
→ communicative objective / recipient state
→ warranted communicative act
→ representation
→ consequence
```

### Communication evidence already obtained

Controlled experiments established the following limited findings:

- Objective-conditioned communicative act selection works in controlled deterministic cases.
- Recipient/context changes can alter selected communicative action while preserving epistemic commitments.
- A representation-preserving boundary was tested. Direct evidence exposure was not necessary in the tested case if exact machine-observable recovery remained possible; silently lossy omission was rejected.
- Communication consequences can be stored as experience and used to revise a communication policy; a later decision can change without changing epistemic commitments.
- A controlled experience-generalization experiment transferred an adapted communication policy from one structurally related cognitive state to a held-out state while preserving epistemic commitments.

None of these results establishes general learned communication. In particular, the tested transferable abstractions were researcher-designed.

### Communication remains intentionally unresolved

Do not declare the communication route finished. The deeper unresolved problem is whether Cognitia can itself discover how to rearrange the same underlying content into another representation, rather than being handed the representation mapping.

The route should resume when the underlying cognitive/evidence state is mature enough to test representation rearrangement meaningfully.

## 9. Roman Empire answer-core evidence

The Roman Empire research path previously produced a deterministic synthesis with:

- candidate multi-factor synthesis;
- six factors;
- economic, demographic, political, and military domains;
- competing explanations and distinguishing tests;
- explicit caveats that extraction is not automatically established knowledge.

The English answer was constructed by Cognitia's deterministic synthesis/rendering path, not by post-processing from ChatGPT.

Important limitation: this demonstrates deterministic research synthesis and cautious rendering, not learned general natural-language communication or adaptive research by itself.

## 10. Evidence and research-history rules

Every research experiment should distinguish:

- **Hypothesis:** what we think may be true.
- **Experiment:** controlled procedure intended to discriminate hypotheses.
- **Observation:** what the system actually did.
- **Interpretation:** what the observation supports.
- **Boundary:** what the experiment cannot establish.
- **Rejected hypothesis:** what failed and why.
- **Surviving hypothesis:** what remains supported after the experiment.
- **Next discriminator:** what should be tested to distinguish remaining explanations.

Never write “implemented X, therefore Cognitia learned X.”

Never write a research-history entry merely because CI is green.

Research history should be updated when an experiment yields information about Cognitia's behavior. Pure implementation failures belong in engineering history/commits, not research conclusions.

If an important research history file is referenced by memory but does not exist in the repository, do not recreate its supposed contents from memory. Verify the repository and explicitly treat the documentation discrepancy as a documentation/state-integrity issue.

## 11. Evaluation and build integrity

Every meaningful cognitive capability should have:

- explicit representation;
- controlled experiment or benchmark;
- baseline behavior;
- changed variable(s);
- verification criteria;
- protected-capability regression tests;
- inspectable outputs/traces;
- retained research evidence;
- immutable build identity.

For a research result, the minimum useful report is not “N tests passed.” It is:

```text
experiment
→ controls
→ treatment
→ observed trajectory
→ actual outputs/state changes
→ causal interpretation
→ alternative explanations
→ epistemic boundary
→ next discriminator
```

## 12. Current engineering workflow

Before substantial work:

1. Inspect the repository tree and current branch/commit.
2. Read `CHATGPT.md`.
3. Read the relevant research MD files, especially the active route and prior experiment records.
4. Check open PRs and ensure the previous experiment is integrated before beginning another.
5. Inspect current CI for the exact commit.
6. If CI fails, inspect logs and classify each failure as engineering or research.
7. If CI passes, inspect outputs/artifacts/trajectories anyway.
8. Only then interpret the experiment.
9. Record the research finding if there is genuine research information.
10. Choose the next experiment from the surviving uncertainty, not from a desire to keep adding code.

### No-open-PR rule

Before starting a new experiment, the preceding PR should not remain open. Merge a validated experiment or close it when it is stale/invalid. Do not stack uncontrolled research branches and lose causal clarity.

### Large batches

When the research question is clear, implementation should be done in coherent batches rather than fragmented micro-commits. However, large batches must remain experimentally disciplined: each batch should have a clear research purpose, controlled variables, tests, and inspectable evidence.

## 13. Capability acquisition

A capability gap triggers diagnosis, not automatic code generation:

```text
failure
→ diagnose smallest missing machinery
→ approximate only if epistemically valid
→ compose / learn procedure / generalize / construct
→ verify
→ benchmark
→ regression analysis
→ balance / repair
→ immutable build
```

Code generation is only one acquisition mechanism. New representations, procedures, algorithms, tools, executable artifacts, and learned strategies may all be appropriate depending on evidence.

## 14. Long-term architecture

### Epistemic substrate
Claims, assumptions, provenance, contradictions, uncertainty, belief revision, and verification requirements.

### Model/possibility system
Competing hypotheses, candidate causes, predictions, counterfactuals, possible states, causal structures, and search/pruning.

### Reasoning portfolio
Deduction, induction, abduction, analogy, constraints, graph reasoning, probability, causality, temporal reasoning, optimization, simulation, search, argumentation, counterfactuals, decision theory, game theory, scientific reasoning, and normative reasoning where justified.

### Meta-cognition
Reasoning-method selection, goal-directed retrieval, strategy-performance learning, value-of-information estimation, reasoning budgets, and background cognitive work.

### Action/environment
Planning, experiment design, discriminating experiments, tool use, consequence evaluation, and closed-loop revision.

### Computational construction
Structured program synthesis, execution/verification, internal computational representations, and eventually safe versioned self-improvement. Specialized representations/languages are justified only by demonstrated cognitive need.

### Cross-domain transfer
Add economics, biology, software/system reasoning, social systems, philosophy/ethics, and other domains only when they test or expose meaningful transfer/capability gaps.

## 15. Physics

Physics is a proving ground, not the whole intelligence architecture.

Current sequence:

1. dimension-aware quantities;
2. Newtonian force relationships;
3. force → acceleration → kinematics;
4. prediction error, tolerances, uncertainty;
5. model/domain/assumption abstraction;
6. multi-force systems;
7. energy and momentum;
8. simulation;
9. experiment design and discriminating hypotheses;
10. anomaly/model-limit investigation.

Physical laws are explicit models with assumptions and domains of validity.

## 16. Deliberate pruning

Do not automatically build:

- every named reasoning paradigm as a separate module;
- a philosophy engine before argument/epistemic machinery works;
- every physics formula before prediction/error handling is sound;
- a specialized language because it is interesting;
- web search merely because external information is useful;
- a conversational shell before the cognitive substrate warrants it;
- human-brain imitation for its own sake;
- large infrastructure whose only purpose is to make a demo look complete.

A roadmap item survives only when evidence shows it creates a useful cognitive capability or is necessary infrastructure for one.

## 17. Roadmap state

### Cognitive substrate
- [x] World state, evidence, beliefs
- [x] Knowledge/experience memory
- [x] Context-conditioned learning
- [x] Scientific hypothesis/testing primitives
- [x] Capability self-model/routing
- [x] Failure and capability-gap diagnosis
- [x] Candidate acquisition/verification/regression gates
- [x] Immutable cognitive builds
- [x] Newtonian force/acceleration
- [x] Force → acceleration → kinematics bridge
- [ ] Prediction error/tolerance/uncertainty
- [ ] Stronger model/assumption abstraction

### Epistemic substrate
- [ ] First-class claims/propositions
- [ ] Explicit assumptions
- [ ] Durable belief revision history
- [ ] Rich uncertainty representation
- [ ] Contradiction objects/investigation
- [ ] Evidence comparison/provenance weighting

### Model search
- [ ] Hypothesis spaces
- [ ] Possible-state representation
- [ ] Search/pruning
- [ ] Counterfactual states
- [ ] Causal hypotheses/graphs
- [ ] Prediction generation
- [ ] Domain-specific prediction error

### General reasoning
- [ ] Argument representation
- [ ] Counterarguments/dialectic
- [ ] Self-criticism/adversarial reasoning
- [ ] Perspective representation/comparison
- [ ] Descriptive/predictive/normative separation
- [ ] Philosophical methods only where measurable value is demonstrated

### Meta-cognition
- [ ] Reasoning-method selection
- [ ] Goal-directed retrieval
- [ ] Reasoning budgets
- [ ] Value-of-information estimation
- [x] Initial capability self-model
- [ ] Strategy-performance learning
- [ ] Background cognitive work

### Action/environment
- [ ] Planner
- [ ] Experiment design
- [ ] Discriminating experiments
- [ ] Consequence evaluation
- [ ] Closed-loop model revision
- [ ] Tool/environment interfaces

### Computational construction
- [ ] Structured program synthesis
- [ ] Execution/verification loop
- [ ] Internal computational representation
- [ ] Specialized representation research only when demonstrated necessary
- [ ] Versioned safe self-improvement

### Cross-domain intelligence
- [ ] Demonstrated transfer across increasingly different domains

## 18. Immediate research priority

The immediate frontier is **research trajectory cognition**, not simply adding more search sources.

The sequence is:

1. execute and inspect the differential trajectory experiment at commit `8895717...`;
2. determine whether changed first evidence actually changes the next selected research action;
3. record the observation and its boundary;
4. if supported, test structural transfer with a different question/state rather than repeating the exact service-failure case;
5. then test whether Cognitia can discover or revise the information-need abstraction instead of receiving it from researcher-written rules;
6. only after that expand adaptive research breadth.

Communication research remains a parallel but paused route. Return to representation rearrangement when the cognitive/evidence substrate is mature enough to make that experiment meaningful.

The broader roadmap remains active. Evidence-driven sequencing does **not** mean abandoning the roadmap; it means choosing the next step using what survived.

## 19. Standard report format for Cognitia work

When reporting an experiment, use this order whenever practical:

**Experiment:** what question was tested.

**Controls:** what was held constant.

**Treatment:** what was changed.

**Execution:** exact commit/workflow/run and whether the experiment actually executed.

**Observed behavior:** what Cognitia selected, produced, changed, stored, or recovered.

**Trace:** the causal chain from input/state to action to observation to subsequent state.

**Interpretation:** what the behavior supports.

**Alternative explanations:** what else could explain it.

**Boundary:** what it does not establish.

**Research record:** what should be written into the appropriate MD/history file.

**Next discriminator:** the smallest experiment that separates the remaining explanations.

Never substitute “CI passed” for this report.

## 20. Final operating principle

We are not building the story of Cognitia. We are building Cognitia and discovering what it actually is.

We should be willing to be wrong about the architecture, the mechanism, the roadmap, and our interpretation. The repository is a laboratory record. Code expresses hypotheses; experiments expose behavior; observations constrain interpretation; failed hypotheses remain evidence; surviving abstractions earn their place.

The goal is not to prove that our original idea was correct.

The goal is to discover, as rigorously as we can, what cognitive machinery actually survives contact with evidence.
