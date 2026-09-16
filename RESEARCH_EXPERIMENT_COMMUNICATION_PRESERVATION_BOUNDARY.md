# Experiment 3A: Communication Preservation Boundary

## Status

**Implemented; controlled boundary tests added; awaiting CI observation.**

## Why this experiment exists

Experiment 3 showed a concrete failure: the concise representation preserved the selected act, claims, uncertainty, and verification requirement but omitted observable evidence identity `E1`.

The failure must not be treated as a simple formatting bug. It raises a narrower research question about what it means for a representation to preserve a communication contract.

## Research question

When a representation changes the organization or compression of a communication, what information must remain directly observable, and what information may be represented indirectly, for the representation to remain epistemically and operationally equivalent?

## Competing hypotheses

### H3A-direct
Every communication surface must explicitly expose the evidence identities supporting its claims.

### H3A-recoverable
A communication surface may omit a field from its top-level payload if the omitted information remains losslessly recoverable through a deterministic, machine-observable reference contained in that same surface.

### H3A-lossy
A communication surface may omit evidence identity without another observable recovery mechanism, provided the claims and uncertainty remain unchanged.

The experiment is intended to distinguish these hypotheses rather than assume that the first one is correct.

## Controlled variables

Hold constant:

- cognitive state;
- recipient;
- communicative objective;
- selected communicative act;
- claim set;
- epistemic status;
- evidence identity;
- uncertainty;
- verification requirement.

Vary only the representation's evidence encoding:

1. direct evidence identity;
2. deterministic evidence reference that permits exact recovery;
3. evidence omitted with no recovery mechanism.

## Preservation criterion

A projection preserves the communication contract only if a receiver can recover the same epistemically relevant commitments without inventing information or consulting hidden state that is not referenced by the surface.

In particular, the receiver must not be forced to guess:

- which evidence supports a claim;
- whether evidence exists;
- whether verification is still required;
- whether a candidate is established or unresolved.

This criterion distinguishes **compression** from **loss**. Compression is acceptable only when the compressed information remains recoverable.

## Implementation

The boundary experiment now has an explicit `COMPACT_REFERENCED` representation and a deterministic `assert_observable_evidence_recovery` invariant.

The test suite contains three boundary observations:

1. the existing direct representations preserve the decision contract;
2. `COMPACT_REFERENCED` removes the direct `evidence:` field but carries an explicit `evidence_ref:` that exactly identifies the same evidence;
3. the existing `CONCISE` representation remains a negative control and is rejected because it has neither direct evidence nor a recoverable evidence reference.

The original Experiment 3 failure is therefore not erased or rewritten. The new implementation creates a discriminating experiment around that failure.

## Expected observations

- Direct evidence should preserve the contract.
- A deterministic, explicitly referenced evidence encoding should preserve the contract if exact reconstruction is possible.
- Silent evidence omission should fail preservation.

If the second case fails despite exact recoverability, the evidence-preservation invariant may need to be stricter than recoverability. If the third case passes, the current invariant is too strong and must be revised.

## Research discipline

Do not weaken the existing Experiment 3 failure merely to restore CI. Do not silently repair the concise representation and call that validation. The existing failure remains historical evidence.

Only after this boundary is experimentally resolved should the communication route proceed to observable consequences and learning from communication experience.
