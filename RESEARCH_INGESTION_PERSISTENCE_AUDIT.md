# Ingestion and persistence audit

This experiment checks a question that should be answered from implementation evidence rather than assumption: what does Cognitia actually retain from the repository and from live web research?

The audit distinguishes CI's ability to see a checked-out repository from Cognitia actually ingesting repository artifacts. It also distinguishes live web observations from promoted durable knowledge.

## Current hypothesis to test

- Repository visibility in CI is not itself codebase ingestion.
- Live web acquisition creates provenance-bearing observations.
- Durable SQLite memory exists and can retain validated knowledge.
- Raw web observations are not necessarily durable merely because the journal exists.

## Evidence rule

The generated `.ci/cognitive-ingestion-persistence-audit.json` artifact is the evidence. Green CI only establishes that the audit executed.

## Next boundary

If the audit confirms the current gap, introduce a real evidence archive for raw environmental observations and a repository/code environment source. Neither should silently promote acquired content into knowledge.
