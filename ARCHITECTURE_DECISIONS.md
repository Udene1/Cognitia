# Cognitia — Architecture Decisions and Challenges

This document records places where the original ambition is intentionally narrowed, reordered, or challenged. Cognitia should not accumulate impressive-sounding subsystems merely because they are possible.

## 1. Capability acquisition is now a first-class loop

A failure should not end at `failure -> report`.

The preferred path is:

```text
Attempt
  ↓
Failure / limitation
  ↓
Failure classification
  ↓
Smallest actionable capability gap
  ↓
Existing capability composition?
  ↓
Procedure learning / transfer?
  ↓
Controlled construction?
  ↓
Candidate
  ↓
Benchmark
  ↓
Verify
  ↓
Regression / compatibility evaluation
  ↓
Promote OR hold for balancing
```

A gap diagnosis is not permission to construct code. Construction remains explicitly gated.

## 2. Regression does not delete cognition

A candidate that improves one capability but damages another remains valuable evidence.

The system should retain the candidate, record the regression, and search for coexistence, selective activation, composition, boundary conditions, or another balancing strategy.

Therefore:

> Regression is a promotion blocker, not a capability deletion command.

## 3. Candidate state is not enough

A mutable/current candidate registry cannot by itself represent intellectual history. Cognitia needs an append-only evaluation history containing benchmark comparisons, verification outcomes, holds, regressions, and promotions.

The current implementation is intentionally in-memory. Durable storage is a later infrastructure step; the conceptual model must exist before persistence is added.

## 4. Challenge: specialized programming languages are not a near-term milestone

The earlier roadmap treated a specialized language as a fairly direct continuation of code generation. That is premature.

Cognitia first needs to demonstrate that its internal representations actually outperform ordinary program representations for some class of cognitive tasks. Until that evidence exists, Python/ordinary programming languages and well-defined intermediate representations are sufficient.

A specialized language is therefore **research-gated**, not a committed implementation phase.

Before pursuing it, Cognitia should demonstrate:

- a recurring computational bottleneck;
- a representation that captures the bottleneck better than existing languages;
- measurable gains in reasoning, search, verification, or efficiency;
- a clear compiler/interpreter semantics.

## 5. Challenge: machine-code generation is not part of Cognitia's intelligence milestone

Generating machine code would prove that Cognitia can generate machine code. It would not prove that Cognitia understands, reasons, learns, or improves.

The near-term target is structured computational planning and verified execution. Lower-level compilation is infrastructure that can be delegated to established toolchains until Cognitia has a demonstrated reason to replace them.

## 6. Challenge: philosophical traditions are methods, not personalities or doctrines

Cognitia should not become a database of philosophers or a system that chooses "the Stoic answer" to a question.

Instead, philosophical reasoning should be represented as reusable argument/questioning frameworks with explicit assumptions, goals, premises, counterarguments, and validity conditions.

For example, a consequentialist framework can evaluate outcomes without making consequentialism Cognitia's universal value system.

## 7. Challenge: thousands of possibilities does not mean enumerating thousands of possibilities

The possibility-space architecture must be search-based and constraint-driven.

Cognitia should represent branching alternatives compactly, prune using constraints/evidence, and expand branches when their expected information or decision value justifies the cost.

The objective is not maximum branching. It is efficient coverage of decision-relevant possibilities.

## 8. Challenge: physics should remain a testbed, not become the product

Physics is valuable because it provides explicit models, quantitative predictions, observations, assumptions, and falsifiable discrepancies.

After the core scientific loop is strong enough, the architecture should generalize to other domains rather than accumulating an enormous physics library first.

A large formula catalog without stronger general cognition is not progress.

## 9. Language comes later than cognition, but not infinitely later

The no-LLM constraint does not mean Cognitia should avoid language indefinitely. A semantic language interface is necessary to expose the cognitive substrate to people.

However, language parsing must translate user input into structured goals, entities, constraints, claims, and context. It must not become a hidden replacement for reasoning.

The test is simple:

> If the language component is removed, the cognitive substrate should still be able to reason over structured problems.

## 10. Current priority order

When choosing between competing work, prefer:

1. durable and auditable cognitive state;
2. epistemic representations and belief revision;
3. reasoning mechanisms that operate on structured state;
4. failure -> capability-gap -> acquisition loop;
5. benchmark / verification / regression evidence;
6. persistent cognitive memory;
7. causal and possibility reasoning;
8. action and experimentation;
9. language interface;
10. broader domains;
11. specialized computational representations only when evidence demands them.

This ordering is deliberately different from a conventional AI product roadmap. Cognitia is being built to investigate independent cognition, not to maximize demo quality as quickly as possible.
