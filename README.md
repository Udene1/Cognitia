# Cognitia

Cognitia is an experimental artificial cognitive system.

The goal is **not** to build an LLM wrapper or recreate an existing LLM. Cognitia must be able to maintain state, learn from experience, reason, plan, act, and revise its internal model without requiring an LLM.

External models may eventually be optional capabilities, but they are not Cognitia's cognitive substrate.

The central question is:

> Can a machine maintain a persistent model of the world, retrieve the knowledge relevant to a problem, reason over that state, act on its environment, observe consequences, and update what it believes?

## v0.01

The first version focuses on one fundamental loop:

```text
Goal
  ↓
Current World State
  ↓
Hypotheses
  ↓
Select next action
  ↓
Observe environment
  ↓
Record consequence
  ↓
Learn from experience
  ↓
Update state
  ↓
Reason again
```

### Core concepts

- **World state** — the system's current structured representation of entities, relationships, facts, beliefs, and uncertainty.
- **Evidence** — observations with provenance, timestamps, reliability, and scope.
- **Memory** — semantic, episodic, and procedural information.
- **Experience** — action, situation, observation, and consequence retained for future learning.
- **Conditional learning** — an action is not globally good or bad; Cognitia learns how it performs under particular conditions.
- **Reasoning** — transforming a structured cognitive state into hypotheses and candidate actions.
- **Planning** — selecting the next action based on the goal, state, uncertainty, experience, and available tools.
- **State transition** — updating the world model when new evidence or action consequences arrive.

## Learning from consequences

Every consequence is learning material, including failures.

A negative outcome does not mean that an action or process is universally bad. It means that the action produced that outcome **in that situation**.

For example:

```text
restart_worker + memory_pressure → positive
restart_worker + database_lock   → negative
```

Cognitia therefore learns conditional patterns instead of applying a global reward or punishment to the action. Future versions will use these patterns to form hypotheses about the conditions under which an action is effective.

The system must also distinguish observed correlation from established causality. Early learning mechanisms generate conditional patterns and hypotheses; they do not claim causal certainty without sufficient evidence.

## Design principles

Cognitia must distinguish between:

1. what was observed,
2. what is believed,
3. why it is believed,
4. what action was taken,
5. what happened afterward, and
6. what the system learned from that consequence and its context.

The architecture must remain independently useful without an LLM. Web search, files, APIs, code execution, and other capabilities will eventually be exposed as environments or evidence sources rather than treated as the system's brain.

## v0.01 scope

The initial implementation is deliberately small and testable. It provides:

- typed world-state objects;
- evidence and provenance;
- explicit beliefs with confidence;
- structured knowledge and provenance;
- append-only experience memory;
- context-conditioned consequence learning;
- deterministic state transitions;
- a reasoning boundary independent of any model provider;
- a small simulated environment;
- end-to-end tests proving that new evidence and experience can change future decisions.

We are intentionally **not** starting with large-scale model training. The cognitive architecture comes first.

## Research direction

The long-term question is whether a system can accumulate knowledge without merely accumulating text — by constructing and revising useful internal representations of the world, learning from the consequences of its actions, and using those representations to solve new problems.
