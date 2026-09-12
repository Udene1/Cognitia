# Cognitia — Working Plan for ChatGPT

This is the durable working contract for Cognitia development. Before substantial work, inspect the repository and challenge this plan where necessary. The plan is subordinate to Cognitia's actual architectural goal; a checklist item is never a reason to build an unnecessary subsystem.

## 1. Vision

Cognitia is an experimental artificial cognitive system intended to represent reality, locate relevant information, reason over alternatives, compare perspectives, challenge conclusions, act, observe consequences, learn, and revise its internal models.

The central research target is **independent cognition**. Cognitia must not become an LLM wrapper, and language must be an interface to cognition rather than the source of cognition.

It should eventually exploit machine advantages: persistent memory, explicit representations, searchable state, reproducibility, parallelism, computation, and long-running background processes.

## 2. Non-negotiable principles

- **No LLM dependency.** Cognitia must be useful and cognitively functional without an LLM. External models may be optional capabilities, never hidden cognitive substrate.
- **Architecture before scale.** Establish explicit cognitive mechanisms before pursuing large model training.
- **No false certainty.** Stored information is not automatically truth. Track epistemic status, evidence, assumptions, provenance, and uncertainty.
- **Capability limitation does not terminate investigation.** Attempt → qualify → verify. Inability to establish a claim is not inability to investigate it.
- **No silent belief mutation.** Preserve why beliefs/models changed.
- **Failure is evidence.** Failed predictions and failed reasoning attempts should diagnose missing knowledge, representations, primitives, algorithms, assumptions, precision, context, search, or capability interactions where possible.
- **Regression is a promotion blocker, not capability deletion.** Retain useful candidates, investigate interactions, balance or selectively compose them, and promote only when the resulting build passes its gates.
- **Production-quality engineering.** Deterministic, explicit, typed, testable primitives. No mocks pretending capabilities exist. Never claim CI is green without evidence.
- **Small primitives, composable architecture.** Avoid giant frameworks and duplicate abstractions.

## 3. Current cognitive loop

```text
Goal → Problem framing → Current world state → Relevant memory/knowledge/evidence
→ Hypotheses/possibility space → Reasoning method selection → Reasoning
→ Plan/action/investigation → Observation → Consequence → Learning
→ Belief/model/capability revision → Updated state → Repeat
```

Eventually this must support foreground reasoning and background cognition: unresolved hypotheses, contradictions, old predictions, knowledge gaps, and capability weaknesses can be revisited without requiring a new user request.

## 4. Cognitive architecture

### Foundation
- World model
- Working and long-term memory
- Knowledge representation
- Evidence/provenance
- Experience memory
- Goals/context

### Epistemic system
- Claims/propositions
- Assumptions
- Knowledge gaps
- Belief/model revision history
- Uncertainty beyond one confidence number
- Contradictions
- Evidence comparison and provenance weighting
- Epistemic result classes: established, supported, prediction, inference, hypothesis, approximation, heuristic, analogy, speculation, unresolved, capability-limited

### Reasoning portfolio
Cognitia should eventually support multiple mechanisms rather than one universal reasoner: deduction, induction, abduction, analogy, constraints, graph reasoning, probabilistic inference, causal inference, temporal reasoning, optimization, simulation, search, argumentation, counterfactuals, decision theory, game theory, scientific reasoning, and normative/ethical reasoning.

A meta-reasoner should choose mechanisms based on the problem rather than invoking every mechanism every time.

### Model and possibility space
Represent competing hypotheses, possible states, candidate causes, predictions, alternative models, and counterfactual worlds. Distinguish possible, plausible, probable, and supported. Search/prune the space; do not blindly enumerate every permutation.

### Multi-perspective and dialectical reasoning
Perspectives should encode emphasized variables, assumptions, evidence preferences, and omissions. Philosophical methods are lenses to compare, not doctrines to adopt blindly. Disagreements should be decomposed into facts, assumptions, terminology, domain boundaries, or causal level.

### Self-criticism and self-model
For important conclusions:
```text
claim → evidence → assumptions → strongest objection → alternatives → falsifier → uncertainty → verification
```
Cognitia should remember its own capability strengths, weaknesses, failed attempts, strategy performance, and belief revisions.

### Decision and values
Keep descriptive, predictive, normative, strategic, and ethical reasoning distinct. Do not derive an ought directly from a prediction.

## 5. Efficiency / deep thinking

Intelligence includes knowing where the solution is likely to be found and therefore avoiding unnecessary computation.
- Retrieve using goal + state + hypothesis + uncertainty + required action, not similarity alone.
- Reuse validated models and derivations with provenance.
- Prune impossible branches with constraints.
- Parallelize independent branches when worthwhile.
- Use reasoning budgets for time, search breadth, simulation, evidence cost, and required confidence.
- Estimate value of information before expensive investigation.
- Stop when additional computation is unlikely to change the decision; investigate deeply when uncertainty and consequences justify it.

## 6. Capability acquisition

A capability gap should trigger diagnosis, not immediate code generation:
```text
Failure → diagnose smallest missing machinery → approximate if valid
→ otherwise compose / learn procedure / generalize / construct
→ verify → benchmark → regression analysis → balance/repair → immutable build
```

Capability acquisition includes knowledge, representations, procedures, algorithms, executable code, tools, and eventually specialized computational representations. Code generation is only one acquisition mechanism.

Construction remains controlled: proposal → formal checks → sandbox → tests → benchmarks → regression checks → policy/review gate → versioned deployment.

## 7. Evaluation and build integrity

Every meaningful capability should have explicit representation, tests, benchmark cases, verification criteria, baseline comparison, protected-capability regression checks, retained evaluation history, and immutable build identity.

A failed candidate remains research material. Never erase evidence merely because integration regressed another capability.

## 8. Physics as first serious reality model

Physics is a proving ground, not the whole intelligence architecture. Current direction:
1. dimension-aware quantities;
2. Newtonian force relationships;
3. force → acceleration → kinematics derivation;
4. prediction error, tolerances, and uncertainty;
5. model/domain/assumption abstraction;
6. multi-force systems;
7. energy and momentum;
8. simulation;
9. experiment design and discriminating hypotheses;
10. anomaly/model-limit investigation.

Physical laws remain explicit models with assumptions and domains of validity.

## 9. Scientific reasoning

```text
Model → prediction → observation → discrepancy/agreement → investigation
→ alternative hypothesis → discriminating test → evidence → model revision
```
Do not fake statistical rigor. Numeric physics should eventually use tolerances and uncertainty rather than naive exact equality.

## 10. Environment capabilities

Eventually Cognitia can use web search, files, databases, APIs, execution environments, and sensors as **observation sources**:
```text
information gap → objective → capability → observation → provenance/reliability → structured update → reasoning
```
Never use an external tool as a substitute for Cognitia's cognition.

## 11. Computational self-construction

Long-term:
```text
cognitive intention → structured computational plan → executable representation → execution → observation
```
If repeated evidence shows existing representations are inadequate, Cognitia may research specialized intermediate representations or languages. This is a consequence of demonstrated capability needs, not an early goal.

Uncontrolled self-modification is explicitly out of scope. Future self-improvement remains versioned, sandboxed, tested, benchmarked, and gated.

## 12. Deliberate pruning of the roadmap

These are **not automatic build commitments**:
- implementing every named reasoning paradigm as a separate module;
- building a philosophy engine before argument/epistemic machinery works;
- implementing every physics formula before prediction/error handling is sound;
- building a specialized language merely because it is interesting;
- adding web search before Cognitia can represent and evaluate observations;
- adding a conversational shell before the substrate can produce structured conclusions;
- pursuing literal human-brain imitation for its own sake.

A roadmap item survives only if it creates a demonstrable cognitive capability or is necessary infrastructure for one.

## 13. Revised roadmap

### Stage A — Cognitive substrate (current)
- [x] World state, evidence, beliefs
- [x] Knowledge and experience memory
- [x] Context-conditioned learning
- [x] Scientific hypothesis/testing primitives
- [x] Physics quantities and kinematics
- [x] Capability self-model and capability-aware routing
- [x] Failure diagnosis and capability-gap diagnosis
- [x] Candidate acquisition, benchmarking, verification, regression gates
- [x] Immutable cognitive builds
- [x] Candidate evaluation history foundation
- [x] Newtonian force/acceleration
- [x] Force → acceleration → kinematics bridge
- [ ] Prediction error/tolerance/uncertainty
- [ ] Stronger model/assumption abstraction

### Stage B — Epistemic substrate
- [ ] First-class claims/propositions
- [ ] Explicit assumptions
- [ ] Durable belief revision history
- [ ] Rich uncertainty representation
- [ ] Contradiction objects + investigation
- [ ] Evidence comparison/provenance weighting

### Stage C — Model search
- [ ] Hypothesis spaces
- [ ] Possible-state representation
- [ ] Search/pruning
- [ ] Counterfactual states
- [ ] Causal hypotheses/graphs
- [ ] Prediction generation
- [ ] Domain-specific prediction error

### Stage D — General reasoning
- [ ] Argument representation
- [ ] Counterarguments/dialectic
- [ ] Self-criticism/adversarial reasoning
- [ ] Perspective representation/comparison
- [ ] Descriptive/predictive/normative separation in executable reasoning
- [ ] Philosophical methods only where they provide measurable reasoning value

### Stage E — Meta-cognition
- [ ] Reasoning-method selection
- [ ] Goal-directed retrieval
- [ ] Reasoning budgets
- [ ] Value-of-information estimation
- [x] Initial capability self-model
- [ ] Strategy-performance learning
- [ ] Background cognitive work

### Stage F — Action and environment
- [ ] Planner
- [ ] Experiment design
- [ ] Discriminating experiments
- [ ] Consequence evaluation
- [ ] Closed-loop model revision
- [ ] Tool/environment interfaces

### Stage G — Computational construction
- [ ] Structured program synthesis
- [ ] Execution/verification loop
- [ ] Internal computational representation
- [ ] Specialized representation research only when demonstrated necessary
- [ ] Versioned safe self-improvement

### Stage H — Cross-domain intelligence
Add domains only after the substrate demonstrates transfer: economics, biology, software/system reasoning, social systems, philosophy/ethics, and others as justified by capability gaps.

## 14. Definition of progress

Do not optimize for files, formulas, stored text, LLM calls, or demos.

Progress means Cognitia gains a **reliable, testable cognitive capability** that composes with existing capabilities.

For every substantial feature ask:
1. What capability does it add?
2. What representation does it require?
3. What can Cognitia do now that it could not do before?
4. How is it tested?
5. What uncertainty/limitations remain?
6. What existing capability could it regress?
7. Is this actually necessary, or merely interesting?

## 15. Working agreement

When continuing Cognitia:
1. Inspect current repository state; do not trust stale descriptions.
2. Read this plan before substantial architectural changes.
3. Challenge the plan when evidence shows an item is unnecessary, premature, redundant, or harmful.
4. Prefer large coherent implementation batches with tests.
5. Reuse canonical modules; do not recreate concepts under new names.
6. Preserve failed candidates and evaluation history.
7. Keep capability acquisition independent from LLMs.
8. Never silently substitute an unavailable capability.
9. Never claim CI is green without checking current workflow state.
10. Update this plan when architecture materially changes.
11. Surface genuinely strong public-building/post ideas when the work produces one, without derailing engineering.

## 16. Immediate next priorities

After the Newtonian bridge, the highest-value work is to make Cognitia's predictions and beliefs **epistemically measurable**: prediction error, tolerance, uncertainty, model assumptions, and revision evidence. Then strengthen claims/contradictions and model search. Do not jump prematurely to philosophy modules, web search, conversation, specialized languages, or large collections of formulas.
