# Cognitia Web Research Architecture

## What the current discovery search engine does

`DiscoverySearchEngine` is **not an internet search engine**. It searches a bounded space of structural hypotheses generated from a supplied model. Its job is to answer:

> Given an explanatory model and a gap, which candidate explanations should Cognitia investigate next?

It does not fetch URLs, crawl pages, maintain a web index, or call an LLM.

## What internet access should become

Internet access belongs to Cognitia's **environment/evidence layer**, not inside the reasoning engine.

```text
GOAL / INFORMATION GAP
        |
        v
Cognitia forms search objective
        |
        v
WebEnvironmentSource
        |
        v
WebSearchProvider
        |
        +--> live search API
        |    OR
        +--> local/indexed corpus
        |    OR
        +--> future crawler/indexer
        |
        v
EnvironmentObservation
        |
        v
source + content + reliability + metadata
        |
        v
Cognitia evaluates evidence
        |
        v
world/knowledge model update
        |
        v
reasoning / hypothesis / next search
```

This separation is deliberate. A search provider supplies observations; it does not reason for Cognitia.

## Live web search vs internet indexing

These are different capabilities.

### Live web search
Cognitia asks an external provider for results when it has an information objective. This gives freshness without requiring Cognitia to crawl the entire internet itself.

### Internet indexing
Cognitia maintains or consumes a searchable corpus of discovered documents. A serious index would need crawling, canonicalization, deduplication, parsing, metadata extraction, freshness tracking, source reliability, robots/permission handling, incremental updates, and retrieval indexes.

The current `WebSearchProvider` boundary supports either implementation without committing Cognitia's intelligence to either one.

## Research loop

The intended future loop is:

```text
identify gap
  -> formulate search objective
  -> acquire evidence
  -> evaluate source/reliability
  -> extract structured knowledge
  -> compare against current world model
  -> revise hypotheses
  -> identify remaining gaps
  -> search again or run an experiment
```

This means web search is an **epistemic capability**, not Cognitia's brain.

## Current implementation status

Implemented now:

- capability-neutral `EnvironmentSource`
- `EnvironmentObservation` with provenance and reliability
- `WebSearchProvider` interface
- `WebEnvironmentSource` adapter
- explicit null environment
- tests proving the boundary

Not implemented yet:

- live HTTP crawling/search
- search-provider credentials
- web crawler
- distributed web index
- semantic web indexing
- automatic source trust model
- autonomous web research loop

Those should be built incrementally and verified rather than simulated.
