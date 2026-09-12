# Knowledge Layer

Cognitia does not treat raw text as knowledge.

The first knowledge layer stores structured propositions with:

- subject
- predicate
- value
- provenance
- source reliability
- scope
- learning time

Knowledge is deliberately distinct from belief. A proposition can be known from a source while its confidence in a particular world state is still determined by the reasoning system.

## Acquisition path

The v0.01 contract is:

```text
human / document extractor / environment
                    |
                    v
             structured proposition
                    |
                    v
               provenance
                    |
                    v
              knowledge store
```

The `teach()` API is intentionally explicit. Later document and environment adapters must produce the same `KnowledgeItem` contract instead of bypassing provenance.

This store is currently in-memory. Persistence and richer extraction are separate milestones so the semantics of knowledge can be tested before infrastructure is added.
