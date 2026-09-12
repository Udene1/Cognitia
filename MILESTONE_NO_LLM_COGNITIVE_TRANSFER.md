# Milestone: Cognitive Transfer Without an LLM

## Why this milestone matters

Cognitia has now demonstrated a small but important property of its architecture:

> It can retain a computational solution across processes and transfer that solution to a different problem without calling an LLM.

The first experiment was intentionally hand-guided. We supplied the computational logic, implementation label, and structured problem signature. That proved persistence and transfer, but it did not prove that Cognitia could derive the useful abstraction itself.

This milestone records the next step: removing that handholding.

## What the new experiment does

Training provides Cognitia with:

1. a human-readable problem statement;
2. actual Python source code that solves the problem;
3. the observed outcome that the implementation passed its held-out tests.

It does **not** provide:

- the intended algorithm name;
- the computational logic;
- a manually written problem signature;
- an LLM-generated explanation of the code;
- an LLM call of any kind.

Cognitia parses the source with Python's AST, extracts structural operations, control flow, keyed state updates, and data flow, and infers a bounded computational family. That representation is converted into a reusable solution pattern and persisted as knowledge.

A fresh process then receives a differently worded problem:

> Calculate total spending for each customer from a new set of purchases.

Cognitia derives a problem signature from the language, retrieves the persisted computational pattern, selects the corresponding executable capability, runs it on a new dataset, and verifies the result.

## The architecture demonstrated

```text
Human problem
      |
      v
Actual source code + observed outcome
      |
      v
Code interpreter
      |
      v
Computational representation
      |
      v
Candidate solution pattern
      |
      v
Persistent knowledge
      |
      |  fresh process
      v
New problem statement
      |
      v
Problem-structure interpretation
      |
      v
Retrieve transferable pattern
      |
      v
Select executable capability
      |
      v
Execute on new data
      |
      v
Verify consequence
```

## What has actually been proven

The experiment proves a controlled form of representation transfer:

- source code can be converted into a structured computational representation without an LLM;
- the inferred representation can become persistent solution knowledge;
- the knowledge survives process boundaries;
- a differently worded target problem can be mapped to the learned computational family;
- the learned family can be selected and executed on new data;
- the transferred result can be verified.

The important point is not that this particular aggregation algorithm is difficult. It is that the **intelligence path is owned by Cognitia** rather than delegated to a language model.

## What has NOT been proven

This is not general human-level code understanding.

The current interpreter is deliberately bounded. It recognizes a small set of structural patterns such as group-by/reduce, filtering, and linear search. Its natural-language problem interpreter is also deliberately bounded.

Therefore this milestone should be described honestly as:

> **A controlled no-LLM cognitive-transfer experiment in which Cognitia infers a computational pattern from executable code and transfers it to a new problem.**

It is not evidence that Cognitia can yet understand arbitrary programs, arbitrary natural language, or arbitrary domains.

## Why we are doing it this way

Cognitia should not become another LLM wrapper.

An LLM can eventually be an optional capability or information source, but Cognitia's reasoning, memory, world model, hypothesis management, planning, learning, and capability acquisition must remain meaningful without one.

The language interface should be a surface of cognition, not the source of cognition.

Code is particularly valuable as an early learning environment because it is human problem-solving logic expressed in an executable representation. Cognitia should learn both:

```text
code
  <-> algorithm
  <-> computational logic
  <-> problem-solving pattern
  <-> human explanation
```

The long-term test is whether Cognitia can move between these representations and transfer what is invariant while discarding what is incidental.

## Next bar

The next experiment should increase the difficulty rather than simply add more hand-written rules:

1. train on several code variants of the same computational pattern;
2. separate incidental syntax from invariant data flow;
3. learn multiple patterns and distinguish them;
4. introduce negative and mixed outcomes;
5. test transfer across different data schemas and domains;
6. generate or compose an implementation from the learned representation rather than relying only on a pre-registered executor;
7. use failures to revise the representation instead of silently forcing a match;
8. benchmark against protected capabilities so new learning cannot silently damage old ones.

The goal is not to make the demo look intelligent. The goal is to make the underlying cognitive machinery progressively earn the right to be called intelligent.

## Historical record

### Stage 1 — hand-guided transfer

Cognitia learned a solution pattern from explicitly supplied logic and transferred it in a fresh process. This established durable knowledge and cross-process transfer.

### Stage 2 — code-derived transfer

Cognitia now receives the executable implementation instead of its explanation. It derives a computational representation, persists the resulting pattern, interprets a new problem, retrieves the pattern, executes it, and verifies the result.

This is the first milestone where the experiment removes the explicit solution-logic label from training.

### Stage 3 — Git-environment source discovery

Cognitia no longer needs the training source to be handed directly to the learning script. The Git environment observer discovers tracked Python source through `GitRepositoryObserver.python_sources()`. The discovered source is then interpreted and persisted.

A fresh process subsequently solves the target problem using only the persisted Git-derived knowledge; it does not reload the training source.

The observed CI path was:

```text
Git repository
    -> GitRepositoryObserver.python_sources()
    -> PythonCodeInterpreter
    -> computational representation
    -> persistent knowledge
    -> fresh process
    -> retrieve pattern
    -> execute on new data
    -> verify result
```

The CI experiment produced `GIT_SOURCE_LEARNING_SUCCESS` followed by `GIT_DERIVED_TRANSFER_SUCCESS`.

This matters because the repository has now become an environment Cognitia can observe rather than a fixture from which the test directly hands Cognitia its source.

### Stage 4 — cross-domain conceptual transfer

The next experiment raises the bar beyond numeric aggregation.

The training source is an engineering decision policy about balancing a newly acquired capability against a regression. Cognitia discovers that source through the Git observer and extracts an abstract decision pattern:

```text
evaluate competing outcomes
    -> preserve the baseline when an improvement carries a regression
    -> adopt the improvement when the regression is resolved
```

A fresh process is then given an economics problem involving a policy that improves growth but worsens inflation risk. The source code and engineering domain are unavailable in that process. Cognitia maps the new problem to the learned abstract family and applies the transferred decision structure.

The test also includes held-out cases so agreement is not established from only one scenario.

The intended CI evidence is:

```text
SOURCE_DISCOVERY_PATH: GitRepositoryObserver.python_sources
INFERRED_FAMILY: tradeoff_balance
CROSS_DOMAIN_CONCEPT_LEARNED
TARGET_SIGNATURE: ('tradeoff_balance',)
ECONOMIC_DECISION: hold_for_balancing
HELD_OUT_CASES: 2
CROSS_DOMAIN_TRANSFER_SUCCESS
```

This is a more meaningful test than asking Cognitia to repeat the same arithmetic in a different wording. It tests whether a computational decision structure learned in one domain can be applied to a structurally analogous problem in another domain.

It is still a controlled experiment, not proof of general reasoning. The target-domain interpreter and decision executor remain bounded and explicitly engineered. The next challenge is to make those abstractions increasingly discoverable and verifiable rather than adding domain-specific mappings.

## Principle

> **Do not give Cognitia the abstraction if Cognitia is supposed to learn the abstraction. Give it evidence from which the abstraction can be earned.**

And the stronger version now guiding the next phase:

> **Do not test whether Cognitia remembers the answer. Test whether it can recover the underlying structure and transfer that structure where the surface changes.**
