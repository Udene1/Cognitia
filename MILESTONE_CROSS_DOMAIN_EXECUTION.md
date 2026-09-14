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
- `cognitia/observation.py` establishes an explicit observation ledger.

## Observation vs learning

An observation is **ingested and retained**. Calling Git, the web, a repository, a filesystem, a running program, or another source an "environment" does not mean throwing away what was observed.

The intended lifecycle is:

`environment -> observation -> experience -> extracted cognition -> candidate knowledge -> validated knowledge`

For Git specifically:

`commit/change -> Git observation -> development episode/experience -> extracted reasoning/lessons -> candidate abstractions -> validated knowledge`

A commit therefore remains available as evidence/provenance, while the cognition extracted from the development episode is what Cognitia learns. We should not put the raw commit into the knowledge store and call it knowledge, but neither should we discard it after extraction.

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
- Persistent storage integration for the observation ledger.
- Multi-observation experience construction from complete development episodes.

## After this milestone

The next phase is to move from a constrained executable bridge to **general transfer experiments**:

1. build a stronger text -> logic extractor for conditional, causal, procedural, and quantitative reasoning;
2. compile the same logic into multiple executable representations;
3. execute generated code against held-out cases;
4. transfer one abstraction into a genuinely different domain (for example engineering -> economics, or mathematics -> code);
5. collect target observations and feed successes/failures back into provenance and learning;
6. test contradiction-driven revision of previously successful abstractions;
7. make observation/experience persistence durable rather than only in-process;
8. expand the benchmark from hand-authored cases to discovered reasoning episodes.

The eventual research question is not "can Cognitia translate text into code?" It is whether Cognitia can discover reusable reasoning structure, instantiate it in a new representation/domain, execute it, observe the result, and revise the abstraction when reality disagrees.
