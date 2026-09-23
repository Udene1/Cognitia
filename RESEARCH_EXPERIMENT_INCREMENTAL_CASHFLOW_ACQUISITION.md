# Incremental Cashflow acquisition

## Question

Does Cognitia consume the Cashflow observation stream incrementally while retaining
older observations, rather than treating Cashflow's latest 200-record response as
its current memory?

## Boundary

Cashflow exposes a `since` timestamp and returns `nextSince`. Its endpoint limits
responses to 200 observations. Cognitia now treats that timestamp as acquisition
state and its SQLite observation store as durable observation memory.

## Intended invariant

A later acquisition may add observations, replay observations, or advance the
source boundary, but a moving Cashflow window must not remove previously retained
observations or their derived claims.

## Implementation under test

- Recover the durable SQLite observation ledger before acquisition.
- Use the ledger's latest Cashflow `observed_at` timestamp as the next `since`
  boundary.
- Fetch repeatedly while a full 200-record batch advances the timestamp.
- Ingest observations idempotently into the existing ledger.
- Derive the research artifact's claims from the complete retained Cashflow
  observation ledger, not only the newest response batch.
- Persist the resulting SQLite state through the existing CI state archive.

## Prior evidence

The preceding live observation comparison found 200 observations in both runs,
but only 118 were shared. The moving window changed claims from 352 to 272:
151 claims belonged to observations that left the window and 71 to newly entered
observations. The shared 118 observations produced exactly the same 201 claims,
establishing deterministic extraction.

That result exposed an acquisition-boundary problem rather than an extractor
problem.

## Success criteria

1. The second acquisition sends the previously retained timestamp as `since`.
2. Existing observation IDs/content remain unchanged.
3. New source observations are appended rather than replacing the ledger.
4. Replayed observations remain idempotent.
5. The cumulative observation count does not decrease.
6. The cumulative claim count does not decrease merely because source records
   leave Cashflow's latest-200 window.
7. The artifact records acquisition batches and both the starting and ending
   timestamps.

## Remaining source-level question

Cashflow currently applies the `since` timestamp independently to each source
table, limits each table, merges the results, and then applies the global 200
limit. This experiment therefore establishes Cognitia's incremental acquisition
boundary, but it does not yet prove that the Cashflow endpoint itself provides a
complete cursor under every high-volume or equal-timestamp condition. That is a
separate source-pagination experiment.
