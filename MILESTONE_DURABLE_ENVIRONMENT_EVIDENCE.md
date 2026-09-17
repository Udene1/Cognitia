# Milestone: Durable Environment Evidence

## Research question

Can Cognitia retain the raw evidence from the environments in which it operates, with enough provenance to reinterpret that evidence later, without silently converting it into knowledge?

## Boundary established

This milestone adds two evidence paths:

- `DurableEvidenceArchive` persists raw observations using the existing SQLite observation store.
- `GitRepositoryObserver` observes tracked repository state and source with commit identity, path, language, source URI, and content digest.

The repository observer does not infer what a source file means. It only exposes an auditable source artifact.

## Why this follows the transfer work

Cognitia already has experiments where structure moves between representations and domains. The next missing substrate is the ability to retain the evidence from which those abstractions can later be reconstructed. Without that substrate, an observation can disappear at process or CI boundaries even when a derived result survives.

The intended chain is:

`environment -> observation -> durable evidence -> experience -> abstraction -> validated knowledge`

The archive deliberately stops at durable evidence.

## Held-out direction

The next experiment should give Cognitia a sequence of repository states rather than a human explanation of the change. It should receive the evidence of what changed and what happened after the change, then determine whether a development episode or causal hypothesis is warranted.

Do not provide the intended reason for a commit. Do not provide a named design pattern. Do not collapse the source diff into a pre-interpreted lesson.
