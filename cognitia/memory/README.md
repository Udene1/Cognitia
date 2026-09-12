# Experience Memory

Cognitia treats **every consequence as learning material**.

A successful action is useful because it reveals what worked. A failed action is equally useful because it reveals what did not work under a particular context.

The v0.01 experience record is:

```text
context + action + observation + outcome
```

Outcomes are explicitly classified as:

- `positive`
- `negative`
- `neutral`

The system must not discard failures. A failed action can later change a procedure, reduce confidence in a hypothesis, or prevent the same action from being selected in a similar context.

The current store is append-only and in-memory. A later learning layer will transform accumulated experiences into updated beliefs and procedural knowledge.
