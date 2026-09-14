# Cross-Domain Execution Milestone

## Why this milestone exists

The previous milestone unified text, code, and mathematics under a representation-neutral logic substrate. The next hard question is whether that substrate can carry reasoning all the way to an executable target and survive verification in a different domain.

The target loop is:

`text-only reasoning -> invariant logic -> executable representation -> execution -> different-domain problem -> transferred reasoning -> target verification`

This milestone is intentionally bounded. It proves the architecture of the loop; it does **not** claim general program synthesis, symbolic mathematics, or arbitrary science-to-science transfer yet.

## What is now implemented

- `cognitia/logic_ir.py` is the shared representation-neutral substrate.
- `cognitia/logic_adapters.py` projects text/code/math into that substrate and keeps provenance attached.
- `cognitia/cross_domain_execution.py` adds an auditable executable target and execution/verification boundary.
- `tests/test_cross_domain_execution.py` exercises successful and falsified target transfers.
- `cognitia/observation.py` establishes the observation ledger.
- `cognitia/memory/observation_sqlite.py` makes observations durable in SQLite across process shutdown/restart.
- `tests/test_sqlite_observation.py` proves that a stored observation can be recovered by a newly opened SQLite store.

## Persistence is part of cognition

An observation is **ingested and retained**. Calling Git, the web, a repository, a filesystem, a running program, or another source an "environment" does not mean throwing away what was observed.

The intended lifecycle is:

`environment -> observation -> experience -> extracted cognition -> candidate knowledge -> validated knowledge`

For Git specifically:

`commit/change -> Git observation -> development episode/experience -> extracted reasoning/lessons -> candidate abstractions -> validated knowledge`

A commit therefore remains available as evidence/provenance, while the cognition extracted from the development episode is what Cognitia learns. We should not put the raw commit into the knowledge store and call it knowledge, but neither should we discard it after extraction.

### What persistence means here

SQLite persistence is real persistence when the SQLite file is on a durable filesystem: Cognitia can close, the process can disappear, and a later process can reopen the same database and recover observations/experience/knowledge.

There is an important distinction in the **current CI-only runtime**. GitHub Actions runners are ephemeral. A database created under `.ci/` during one workflow run survives process restarts within that runner, but it does **not** automatically survive destruction of the runner after the workflow finishes.

### Runner-boundary persistence is now implemented

The CI-only boundary is now explicit and tested:

1. the `test` workflow restores the latest cognitive SQLite snapshot from the durable `cognitia-state` branch;
2. the restored databases are integrity-checked before use;
3. Cognitia records the current CI run and performs the existing process-restart persistence proof;
4. a successful `main` run creates a consistent SQLite snapshot using SQLite backup plus `PRAGMA integrity_check`;
5. the snapshot is uploaded as a workflow artifact;
6. a separate `cognitive-state` workflow, triggered only after a successful `main` test workflow, downloads that artifact and commits it to `cognitia-state`;
7. the next runner retrieves that durable snapshot and verifies that the prior CI run is present.

The state transport is deliberately separate from cognition semantics. The archive is a transport envelope containing SQLite databases plus a manifest of sizes and SHA-256 digests. Restore verifies the manifest and SQLite integrity before replacing state files. Persisting an event does not turn it into knowledge; it remains subject to Cognitia's normal interpretation and validation boundaries.

GitHub Actions artifacts are only the handoff between workflow runs; the `cognitia-state` branch is the durable long-lived state record. This avoids treating the runner filesystem or the artifact retention window as the cognitive memory itself.

## Observation vs learning

The observation ledger exists to preserve the observed artifact/facts so Cognitia can:

1. reinterpret an observation with a better extractor later;
2. trace a learned abstraction back to its evidence;
3. compare later observations and detect contradiction or recurrence;
4. reconstruct the development episode that produced an abstraction;
5. distinguish what was directly observed from what Cognitia inferred.

The same boundary applies to web research: source observations are retained as evidence/provenance; synthesized cognition is derived from them.

## Verification contract

Execution is not automatically proof. The executable target must emit explicit observations, and the transfer verifier requires explicit boolean verification verdicts. A failed target execution therefore becomes evidence against the transfer rather than being silently discarded.

## What remains incomplete

- General natural-language reasoning extraction into executable semantics.
- A richer symbolic math representation and solver-backed execution.
- Target-language code generation with behavioral equivalence testing.
- Cross-domain abstraction selection beyond structural role matching.
- Multi-observation experience construction from complete development episodes.
- A production-grade external cognitive-state backend beyond the current GitHub Actions state transport.

## After this milestone

The next phase is to move from a constrained executable bridge to **general transfer experiments**, while keeping the learning loop genuinely persistent:

1. build a stronger text -> logic extractor for conditional, causal, procedural, and quantitative reasoning;
2. compile the same logic into multiple executable representations;
3. execute generated code against held-out cases;
4. transfer one abstraction into a genuinely different domain (for example engineering -> economics, or mathematics -> code);
5. collect target observations and feed successes/failures back into provenance and learning;
6. test contradiction-driven revision of previously successful abstractions;
7. use retained Git observations to construct multi-commit development episodes rather than treating commits independently;
8. expand the benchmark from hand-authored cases to discovered reasoning episodes;
9. return to the answer problem and investigate communication as a learned cognitive capability.

The eventual research question is not "can Cognitia translate text into code?" It is whether Cognitia can discover reusable reasoning structure, instantiate it in a new representation/domain, execute it, observe the result, retain that experience, and revise the abstraction when reality disagrees.

## Immediate next milestone: communication / answer capability

The persistence boundary is no longer the blocker. The next milestone returns to the **answer problem**. The working hypothesis is changing: the central failure may not be lack of problem understanding. Cognitia may understand a problem sufficiently but lack a learned communication capability—the ability to determine what another agent needs to receive, organize the reasoning into an appropriate communicative structure, express it clearly, expose uncertainty, and adapt the explanation to the interaction.

The next answer milestone will therefore investigate communication as a cognitive capability rather than simply adding more answer templates.
