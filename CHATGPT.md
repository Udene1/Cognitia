# Cognitia — Working Plan for ChatGPT

> This file is the durable working contract for Cognitia development. Before proposing or implementing a substantial change, read this file and check the change against the vision, architecture, roadmap, and non-negotiable constraints below.

## 1. Vision

Cognitia is an experimental artificial cognitive system whose goal is to become a system that can **represent reality, find where relevant information is, reason over many possible explanations, compare perspectives, challenge its own conclusions, act, observe consequences, learn, and revise its internal models**.

The ambition is not to build another chatbot or a thin wrapper around an LLM. Cognitia should become useful through its own cognitive architecture first.

The long-term aspiration is a system that can:

- maintain a persistent model of the world;
- know what it knows, what it does not know, and why it believes something;
- efficiently find where useful information is likely to exist;
- construct and compare hypotheses rather than immediately choosing one explanation;
- reason across many possible states without exhaustively exploring irrelevant branches;
- reason causally and counterfactually;
- use multiple professional and philosophical perspectives on the same problem;
- detect contradictions and investigate them instead of silently averaging them away;
- distinguish truth-seeking from prediction, decision-making, strategy, and values;
- criticize its own conclusions and identify what would change its mind;
- remember the history of its reasoning and belief revisions;
- choose appropriate reasoning methods and allocate computation intelligently;
- eventually construct or generate executable computational machinery, including code and potentially new programming representations when existing ones are inadequate.

The goal is not to reproduce the human brain literally. Cognitia should exploit advantages available to machines: persistent memory, explicit representations, parallelism, searchable state, reproducibility, computation, and long-running background processes.

## 2. Non-negotiable principles

### 2.1 No LLM dependency

Cognitia must **not** require an LLM to maintain its world model, reason, learn, plan, test hypotheses, or make decisions.

External models may eventually be optional capabilities for language, translation, perception, code assistance, or other useful tasks. They must not secretly become Cognitia's cognitive substrate.

Never solve an architectural problem by replacing it with `call_llm(...)`.

### 2.2 Architecture before scale

Build explicit, testable cognitive primitives before pursuing large-scale model training.

### 2.3 No false certainty

Stored information does not become truth merely because it is stored.

Cognitia must distinguish, at minimum:

- observation;
- measurement;
- evidence;
- interpretation;
- assumption;
- inference;
- hypothesis;
- model;
- prediction;
- expert opinion;
- consensus;
- established result;
- speculation;
- contradiction;
- unknown.

Confidence must be connected to evidence and reasoning history where possible.

### 2.4 Correlation is not causation

Conditional patterns may reveal useful relationships but must not automatically be represented as causal laws.

### 2.5 Failed predictions are information

A failed prediction should trigger investigation of measurement error, hidden variables, omitted assumptions, model limitations, domain boundaries, alternative models, or genuinely falsifying evidence. One failed observation must not automatically destroy a strongly supported model.

### 2.6 No silent belief mutation

When a belief changes, Cognitia should be able to preserve why it changed: previous state, evidence, reasoning, prediction, consequence, and revision.

### 2.7 Production-quality engineering

Prefer deterministic, explicit, typed, testable primitives. Do not use mocks to pretend an architectural capability exists. Do not claim CI is green without checking it.

### 2.8 Small primitives, composable architecture

Avoid prematurely building a giant framework. Each cognitive primitive should have a clear responsibility and compose with the others.

## 3. Current cognitive loop

The foundational loop is:

```text
Goal
  ↓
Problem framing
  ↓
Current world state
  ↓
Relevant memory / knowledge / evidence
  ↓
Hypothesis and possibility space
  ↓
Reasoning
  ↓
Plan / next action / investigation
  ↓
Action
  ↓
Observation
  ↓
Consequence
  ↓
Learning
  ↓
Belief / model revision
  ↓
Updated world state
  ↓
Repeat
```

The loop must eventually support both **foreground reasoning** and **background cognition** such as revisiting unresolved hypotheses, checking contradictions, evaluating old predictions, and identifying knowledge gaps.

## 4. Cognitive architecture

The architecture should grow toward these interacting layers.

### Foundation

- World model
- Working memory
- Long-term memory
- Knowledge representation
- Evidence and provenance
- Experience / episodic memory
- Goals and context

### Epistemic layer

- Claims and propositions
- Evidence relationships
- Assumptions
- Uncertainty
- Confidence
- Belief provenance
- Belief revision
- Knowledge gaps

### Reasoning layer

Reasoning is not one algorithm. It should become a portfolio of mechanisms, including where useful:

- deduction;
- induction;
- abduction;
- analogy;
- constraint solving;
- graph reasoning;
- probabilistic inference;
- causal inference;
- temporal reasoning;
- optimization;
- simulation;
- search;
- argumentation;
- counterfactual reasoning;
- decision theory;
- game-theoretic reasoning;
- scientific reasoning;
- normative / ethical reasoning.

### Model-space layer

Cognitia should represent a branching space of:

- hypotheses;
- possible states;
- candidate causes;
- predicted consequences;
- alternative models;
- counterfactual worlds;
- competing explanations.

The system must distinguish **possible**, **plausible**, **probable**, and **supported**.

### Multi-perspective layer

A problem can be modeled through different disciplinary or philosophical lenses. A perspective should describe what variables it emphasizes, what assumptions it uses, what evidence it prioritizes, and what it tends to omit.

Potential perspectives include:

- physics;
- economics;
- psychology;
- history;
- sociology;
- engineering;
- law;
- biology;
- game theory;
- philosophy;
- ethics;
- systems thinking.

Cognitia should compare perspectives, identify disagreements, and determine whether disagreements arise from facts, assumptions, terminology, domain boundaries, or different levels of causality.

### Dialectical / philosophical layer

Cognitia should learn and use philosophical methods rather than merely store names and quotations.

Important traditions and methods include:

- Socratic questioning;
- Aristotelian categories and causes;
- Stoic analysis of control and judgment;
- consequentialist reasoning;
- deontological reasoning;
- virtue-oriented reasoning;
- existential questions of freedom, meaning, and responsibility;
- epistemology;
- ontology;
- philosophy of science;
- philosophy of mind;
- logic and argumentation.

These are lenses to compare, not doctrines Cognitia must blindly adopt.

### Meta-reasoning layer

Cognitia must eventually reason about **how it should reason**.

It should learn:

- which reasoning method fits which problem;
- where useful information is likely to be found;
- which branches are worth exploring;
- when more computation is justified;
- when additional evidence would change a decision;
- which reasoning strategies perform well in particular domains;
- where its own reasoning is systematically weak.

This is essential for speed. Intelligence includes knowing where to look and where not to spend computation.

### Self-criticism layer

After forming a conclusion, Cognitia should be able to ask:

```text
What is the claim?
What evidence supports it?
What assumptions are required?
What is the strongest opposing argument?
What alternative explanation exists?
What evidence would falsify it?
What uncertainty remains?
How could my reasoning be wrong?
```

### Values and decision layer

Keep these distinct:

- descriptive: what is happening?
- predictive: what is likely to happen?
- normative: what ought to happen?
- strategic: what should be done given an objective?
- ethical: what action is justified?

Do not derive an ought directly from a prediction.

### Intellectual memory

Cognitia should eventually remember not just facts but reasoning history:

```text
I believed X.
I believed X because of A and B.
I considered C and rejected it because of D.
Evidence E contradicted assumption B.
I revised X to X'.
The revision changed prediction P.
The later consequence was Y.
```

This creates an auditable intellectual history rather than a pile of disconnected facts.

## 5. Computational efficiency and deep thinking

Cognitia should become fast without becoming shallow.

Principles:

1. Do not recompute from zero when existing models or reasoning structures apply.
2. Retrieve based on goal + current state + hypothesis + uncertainty + required action, not semantic similarity alone.
3. Use constraints to prune impossible branches early.
4. Parallelize independent reasoning branches where useful.
5. Cache reusable models and derivations while preserving provenance.
6. Maintain background cognitive processes for unresolved problems.
7. Use a reasoning budget: time, search breadth, simulation count, evidence cost, and required confidence should influence whether to continue.
8. Estimate the value of additional information before spending large amounts of computation.
9. Stop when additional computation is unlikely to materially change the decision, but investigate deeply when uncertainty and consequence justify it.

## 6. Physics as the first reality-model domain

Physics is not the entire Cognitia architecture. It is the first serious domain in which Cognitia can construct models, make quantitative predictions, compare predictions to observations, and investigate anomalies.

Current physics direction:

1. quantities and dimensional consistency;
2. Newtonian force relationships;
3. prediction error and physical tolerances / uncertainty;
4. physical laws as falsifiable models;
5. multi-force systems;
6. energy and momentum conservation;
7. simulation;
8. experiment design and discriminating hypotheses;
9. anomaly detection and model-limit investigation;
10. broader physical domains.

Physics primitives must remain explicit models with assumptions and domains of validity, not unquestionable axioms.

## 7. Scientific reasoning

The scientific layer should support:

```text
Existing model
      ↓
Prediction
      ↓
Observation
      ↓
Agreement / discrepancy
      ↓
Investigate discrepancy
      ↓
Alternative hypotheses
      ↓
Discriminating test
      ↓
Evidence
      ↓
Confidence / model revision
```

Generic scientific evaluation should not fake domain-specific statistical rigor. Numeric physics comparisons should eventually use tolerances, uncertainty, and domain-specific evaluators rather than naive exact equality.

## 8. Programming and computational self-construction

Long-term, Cognitia should be able to construct executable solutions.

The progression should be:

```text
Cognitive intention
      ↓
Structured computational plan
      ↓
Existing programming language / execution environment
      ↓
Compiler / interpreter
      ↓
Executable computation
```

Later, if Cognitia repeatedly encounters limitations in existing representations, it may be able to design a specialized language or intermediate representation for a class of problems.

A future self-modification pipeline must be safe and testable:

```text
Proposed change
      ↓
Formal checks
      ↓
Sandbox
      ↓
Tests
      ↓
Benchmarks / regression checks
      ↓
Review / policy gate
      ↓
Versioned deployment
```

Do not build uncontrolled self-modification as a shortcut.

## 9. Environment and capability direction

Eventually Cognitia should treat external capabilities as environments/evidence sources:

- web search;
- files;
- databases;
- APIs;
- code execution;
- local/system information;
- sensors or other external observations where appropriate.

The pattern should be:

```text
Cognitia identifies information gap
        ↓
forms objective
        ↓
uses capability
        ↓
receives observation
        ↓
evaluates provenance/reliability
        ↓
updates structured knowledge/world state
        ↓
reasons again
```

Not:

```text
Cognitia → LLM → tool → LLM → answer
```

## 10. Roadmap

### Phase A — Cognitive foundations (current)

- [x] World state
- [x] Evidence and provenance
- [x] Beliefs
- [x] Knowledge representation
- [x] Experience memory
- [x] Context-conditioned learning
- [x] Scientific hypothesis/testing primitives
- [x] Physics quantities and dimensional reasoning
- [x] Initial kinematics model
- [ ] Newtonian force / acceleration model
- [ ] Stronger model/assumption abstraction

### Phase B — Epistemic reasoning

- [ ] First-class claims and propositions
- [ ] Assumption representation
- [ ] Explicit knowledge gaps
- [ ] Belief revision history
- [ ] Uncertainty representation beyond a single confidence number
- [ ] Contradiction objects and investigation
- [ ] Evidence comparison and provenance weighting

### Phase C — Model and possibility reasoning

- [ ] Hypothesis spaces
- [ ] Branching possible-state representation
- [ ] Search and pruning
- [ ] Counterfactual states
- [ ] Causal graphs / causal hypotheses
- [ ] Prediction generation
- [ ] Domain-specific prediction error

### Phase D — Multi-perspective and philosophical reasoning

- [ ] Perspective representation
- [ ] Argument representation
- [ ] Counterargument / dialectic
- [ ] Philosophical reasoning methods
- [ ] Cross-perspective comparison
- [ ] Normative vs descriptive separation
- [ ] Self-criticism / adversarial reasoning

### Phase E — Meta-reasoning

- [ ] Reasoning-method selection
- [ ] Goal-directed retrieval
- [ ] Reasoning budgets
- [ ] Value-of-information estimation
- [ ] Reasoning strategy evaluation
- [ ] Self-model of cognitive strengths and weaknesses
- [ ] Background cognitive work

### Phase F — Action and experimentation

- [ ] Planner using models and uncertainty
- [ ] Experiment design
- [ ] Discriminating experiments
- [ ] Action consequence evaluation
- [ ] Closed-loop model revision
- [ ] Environment/tool interfaces

### Phase G — Computational construction

- [ ] Structured code generation from internal plans
- [ ] Code verification and execution loop
- [ ] Program synthesis primitives
- [ ] Computational representation / intermediate representation
- [ ] Specialized language research
- [ ] Safe compiler/interpreter construction
- [ ] Versioned, tested self-improvement proposals

### Phase H — Broader intelligence

- [ ] Multiple domain models beyond physics
- [ ] Economics
- [ ] Biology
- [ ] Social systems
- [ ] Software/system reasoning
- [ ] Philosophy and ethics
- [ ] Cross-domain synthesis

## 11. Definition of progress

Progress is not measured primarily by:

- number of files;
- number of formulas;
- amount of stored text;
- number of LLM calls;
- flashy demos.

Progress means Cognitia gains a new **reliable cognitive capability** that composes with existing capabilities and can be tested.

A new feature should ideally answer:

1. What cognitive capability does this add?
2. What representation does it require?
3. What can Cognitia do after this that it could not do before?
4. How can we test that capability?
5. What assumptions or limitations remain?
6. How does it fit the long-term architecture?

## 12. Anti-derailment rules

Before adding a substantial feature, ask:

- Does this strengthen Cognitia's independent cognition?
- Does it introduce hidden dependence on an LLM or external intelligence?
- Does it improve representation, reasoning, learning, planning, action, observation, or self-correction?
- Are we adding a real cognitive primitive or merely adding content?
- Can the capability be tested independently?
- Are we prematurely optimizing for a demo?
- Are we confusing retrieval with reasoning?
- Are we confusing correlation with causation?
- Are we turning a useful model into an unquestionable truth?
- Are we adding complexity before establishing the underlying abstraction?

If the answer suggests architectural drift, stop and reconsider before implementing.

## 13. Current next build target

At the time this plan was established, the immediate implementation target is:

**Build Newtonian force relationships on top of the existing dimension-aware quantity system.**

Requirements:

- mass must have `MASS` dimension;
- forces must have `FORCE` dimension;
- net force must be composable explicitly;
- acceleration must be derived as `F_net / m`;
- invalid dimensions must be rejected;
- zero/negative mass must be rejected;
- assumptions and model identity must be explicit;
- tests must prove the behavior;
- the law should remain a model that can later be tested and challenged, not an unquestionable axiom.

After that, prioritize **prediction error/tolerance/uncertainty** before adding a large collection of physics formulas.

## 14. Working agreement for future ChatGPT sessions

When continuing Cognitia:

1. Read this file first.
2. Inspect the current repository state rather than relying on an old description.
3. Preserve the vision and constraints.
4. Implement real changes when asked to build.
5. Add tests with each meaningful capability.
6. Check CI/status before claiming success.
7. Update this file when the roadmap, architecture, or major design decisions materially change.
8. Do not remove a roadmap item merely because implementation is difficult; redesign the path if necessary while preserving the underlying capability.
9. When a new discovery changes the architecture, record the discovery here so future work does not lose it.
10. Flag genuinely strong public-writing ideas that emerge from Cognitia's engineering discoveries, especially ideas that reveal a non-obvious technical or philosophical principle.

## 15. Current architectural north star

The system should increasingly approach:

```text
                    GOAL
                      ↓
               PROBLEM FRAMING
                      ↓
                WORLD STATE
                      ↓
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
    MEMORY         EVIDENCE       KNOWLEDGE
       └──────────────┼──────────────┘
                      ↓
             POSSIBILITY SPACE
                      ↓
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
    CAUSAL         COUNTER-       PREDICTIVE
    MODELS         FACTUALS         MODELS
       └──────────────┼──────────────┘
                      ↓
             MULTI-PERSPECTIVE
                      ↓
                 REASONING
                      ↓
               SELF-CRITIQUE
                      ↓
               META-REASONING
                      ↓
             PLAN / DECISION
                      ↓
                    ACTION
                      ↓
                 OBSERVE
                      ↓
                 CONSEQUENCE
                      ↓
               LEARN / REVISE
                      ↓
              INTELLECTUAL MEMORY
                      ↺
```

The ultimate direction is not “make Cognitia answer more questions.”

It is:

> **Build a system that can construct models, search its cognitive space intelligently, challenge those models, learn from reality, and progressively become better at deciding what to think about and how to think about it.**
