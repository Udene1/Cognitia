# Cognitia

Cognitia is an experimental artificial cognitive system.

The goal is not to recreate an existing LLM. Cognitia explores a different question:

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
Update state
  ↓
Reason again
```

### Core concepts

- **World state** — the system's current structured representation of entities, relationships, facts, beliefs, and uncertainty.
- **Evidence** — observations with provenance, timestamps, reliability, and scope.
- **Memory** — semantic, episodic, and procedural information.
- **Reasoning** — transforming a structured cognitive state into hypotheses and candidate actions.
- **Planning** — selecting the next action based on the goal, state, uncertainty, and available tools.
- **State transition** — updating the world model when new evidence or action consequences arrive.

## Design principle

Cognitia must distinguish between:

1. what was observed,
2. what is believed,
3. why it is believed, and
4. what happened after acting on that belief.

This gives us a foundation for testing whether persistent state actually improves problem solving.

## v0.01 scope

The initial implementation will be deliberately small and testable. It will provide:

- typed world-state objects;
- evidence and provenance;
- explicit beliefs with confidence;
- memory records;
- deterministic state transitions;
- a reasoning boundary that can later connect to a neural model;
- a small simulated environment;
- end-to-end tests proving that new evidence can change future decisions.

We are intentionally **not** starting with large-scale model training. The cognitive architecture comes first.

## Research direction

The long-term question is whether a system can accumulate knowledge without merely accumulating text — by constructing and revising useful internal representations of the world and using those representations to solve new problems.
