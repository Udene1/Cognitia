# Milestone: Development Episode Reconstruction

## Research question

Can Cognitia reconstruct a minimal development episode from repository-state evidence and observed test consequences without being handed the intended reason for a change?

## First boundary

The first experiment deliberately establishes only the weakest defensible relation:

```text
repository state A
      ↓
repository state B
      ↓
observed test consequence
```

The reconstruction may identify that a repository state changed before the observed consequence. It must not convert that temporal relation into an intended causal explanation.

## Experiment

`tests/ci/development_episode_reconstruction.py` uses two actual repository states surrounding the durable-environment-evidence change and executes the environment-evidence tests as the observed consequence.

The experiment reports:

- exact before/after commit identities
- changed files
- actual consequence status
- reconstructed temporal relation
- causal explanation field

## Result criterion

A successful run requires:

- state identities differ
- changed files are observed from Git
- the actual test consequence is captured
- the relation is `change_precedes_consequence`
- `causal_explanation` remains `None`

This is intentionally not yet causal inference.

## Next experiment

Once this boundary is validated, provide multiple candidate explanations supported by different evidence and test whether Cognitia can discriminate among them rather than treating temporal precedence as causation.

Only after that should the research return to communication and ask whether Cognitia can communicate development episodes while preserving the distinction between observation, hypothesis, and established explanation.
