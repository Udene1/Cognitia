# Cognitia Discovery Research Agenda

Cognitia is not being designed as an LLM, an LLM wrapper, or a conventional agent framework. We do not assume that the eventual cognitive architecture needs a name yet. We are investigating what mechanisms are required for a machine to reason, investigate, learn, and potentially discover knowledge beyond what it was explicitly given.

## Core research question

> Can an artificial cognitive system investigate problems beyond the immediate capabilities of any individual model, construct genuinely novel hypotheses, test them, learn from failure, and progressively convert surviving hypotheses into reproducible knowledge?

## What "novel" means here

Novelty is not a measure of how many existing concepts were recombined. A recombination may be useful, but it is not sufficient evidence of discovery.

For Cognitia, discovery research is interested in hypotheses or explanatory structures that are not already represented in the system's current knowledge and that introduce a genuinely new explanatory or predictive claim.

A generated idea is not a discovery merely because it is unfamiliar to Cognitia. It must survive increasingly strong evidence.

## Discovery epistemic ladder

```text
candidate idea
    ↓
novel relative to current knowledge
    ↓
plausible / internally coherent
    ↓
falsifiable prediction
    ↓
controlled test or simulation
    ↓
internal evidence
    ↓
independent reproduction
    ↓
external validation
    ↓
accepted scientific knowledge
```

Cognitia must never collapse these states into a single confidence number.

## Unknown-space exploration

The target is not simply to search harder for known answers.

Cognitia should eventually be able to recognize:

1. what its current models explain;
2. what observations remain unexplained;
3. which assumptions constrain its current hypothesis space;
4. where alternative representations may be required;
5. which plausible hypotheses are absent from its current knowledge;
6. what observations would distinguish competing hypotheses;
7. which experiment, calculation, simulation, or information acquisition would most reduce uncertainty.

The difficult research problem is therefore **hypothesis-space expansion**, not random idea generation.

## Discovery loop

```text
observe
  ↓
model current knowledge
  ↓
identify anomaly / explanatory gap
  ↓
construct candidate hypothesis space
  ↓
explore alternatives
  ↓
derive predictions
  ↓
select discriminating test
  ↓
experiment / simulate / acquire evidence
  ↓
observe outcome
  ↓
revise beliefs and representations
  ↓
retain, challenge, revise, or reject
  ↓
formalize surviving result
```

## Research experiments

### D1 — Anomaly recognition

Can Cognitia distinguish an ordinary unknown from an observation that conflicts with its current explanatory models?

### D2 — Hypothesis-space expansion

When existing explanations fail, can Cognitia construct alternatives that are not simply retrieved from existing knowledge?

### D3 — Novel prediction

Can a newly generated hypothesis produce a prediction that was not explicitly supplied as an observation?

### D4 — Discriminating experiment selection

Can Cognitia choose an experiment because it separates competing hypotheses rather than merely because it is easy to perform?

### D5 — Discovery under capability limits

When Cognitia cannot perform the ideal experiment, can it construct a qualified approximation, state the epistemic limitation, and identify the verification path?

### D6 — Failed-discovery learning

Can Cognitia learn from a failed hypothesis without simply memorizing that the exact hypothesis was wrong?

### D7 — Independent reproduction

Can an independently implemented verifier reproduce a Cognitia-generated result without relying on Cognitia's internal reasoning trace as proof?

## Completed foundation milestones

### Discovery gap representation

Cognitia now has an explicit workspace for observations, explanation assessments, explanatory gaps, and hypothesis candidates. Contradicted or unexplained observations become investigation targets without automatically generating an answer. This preserves the distinction between an anomaly and a solution.

### Bounded hypothesis-space construction

Cognitia can now construct a traceable alternative space from an explicit explanatory model. The initial transformations are:

- relax an assumption;
- reverse an assumption;
- partition by an existing context variable;
- introduce an explicitly identified missing variable.

Each alternative retains its source model, transformation, changed element, epistemic status, and unassessed novelty status. This is deliberately a **search primitive**, not a claim of autonomous scientific creativity.

### Falsifiable prediction contracts

A hypothesis can now be paired with a condition, expected outcome, and explicit falsifier. Cognitia does not infer that a prose proposition is scientifically testable merely because it sounds plausible.

### Discriminating experiment selection

Cognitia can select a test when competing hypotheses make different predictions under the same condition. Information gain is derived from the prior entropy of the competing hypotheses rather than a fixed placeholder.

### Bounded structural search and research artifacts

Cognitia now has a canonical structural discovery IR plus a bounded search engine over structural alternatives. The IR removes model-specific identifiers from comparison and produces stable fingerprints; similarity remains evidence rather than semantic equivalence.

The search engine now supports bounded multi-step transformation paths with deterministic deduplication, explicit derivation traces, learned transformation utility, and learned failure pressure. Search depth and candidate count remain hard budgets. Multi-step candidates remain hypotheses until independently tested.

### Behavioral verification

Independent code representations can now be followed by held-out behavioral verification. Structural similarity remains an inference; agreement across held-out cases upgrades the epistemic status to `verified-on-held-out-cases`, while mismatches explicitly challenge the structural inference.

### Discovery investigation and web boundary

Cognitia now has an environment/evidence boundary. A search provider can supply observations, while Cognitia retains responsibility for interpretation and hypothesis revision. Evidence is deduplicated, provenance-preserving, reliability-gated, and temporally qualified before investigation uses it. There is still no built-in live crawler or LLM dependency.

### Failure-driven search learning

Discovery failures can be classified using the existing failure-analysis taxonomy and accumulated as evidence about search transformations. Failed investigations penalize future search utility rather than deleting the failed hypothesis or pretending the failure proves the underlying proposition false.

### Durable discovery lifecycle

Discovery artifacts can now survive process restart with links to observations, models, hypotheses, predictions, experiments, outcomes, epistemic status, and reproduction status. Persistence is an evidence record, not a truth claim.

### Validated-knowledge persistence invariant

This is now a hard architectural rule:

> **Cognitia may remember candidates, observations, experiences, hypotheses, and failures freely. It promotes something to durable knowledge only after it has survived explicit tests meeting the validation policy, and it persists that validated knowledge with its provenance and test identities.**

A failed test cannot be promoted. A restart cannot strengthen a proposition. Persistence records what survived the test process; it does not make an untested proposition true.

The durable knowledge path is:

```text
candidate / observation
        ↓
      test
        ↓
  pass + reliability
        ↓
validation gate
        ↓
persisted knowledge
        ↓
restart / replay
        ↓
usable prior knowledge
```

## Current architectural consequence

The existing knowledge, memory, hypothesis, verification, capability, failure-analysis, candidate, and durable-state systems are foundations for discovery. The discovery layers must remain connected to those systems rather than becoming a separate idea-generation subsystem.

In particular, durable cognitive state must be replayable into active cognition. A remembered hypothesis or capability outcome is useful only when a fresh process can reconstruct the state and use it in a subsequent decision.

## Next research attack

The next difficult step is to remove more hand-written transformation mappings and make the canonical representation itself richer enough that useful transformations can operate on assumptions, variables, dependencies, constraints, predictions, and outcomes generically. Search should learn which transformations are useful from consequences, while behavioral verification and independent reproduction protect against seductive but wrong abstractions.

The progression is:

```text
explicit model
→ explanatory gap
→ alternative hypothesis space
→ prediction
→ discriminating experiment
→ observed result
→ hypothesis revision
→ learned search strategy
→ durable validated knowledge
```

The key research question is whether the final arrows can become learned cognition rather than a collection of manually encoded heuristics.

## Non-goals

- Do not call an LLM to supply Cognitia's intelligence.
- Do not equate novelty with random recombination.
- Do not call an internally generated hypothesis a scientific law.
- Do not treat persistence as evidence of truth.
- Do not treat a successful single experiment as universal proof.
- Do not optimize for impressive-looking generated papers before the underlying discovery process is defensible.

## Long-term objective

The strongest future demonstration would be a problem for which the relevant answer is absent from Cognitia's starting knowledge, followed by a complete trace showing:

```text
unexplained observation
→ novel hypothesis
→ novel prediction
→ discriminating experiment
→ result
→ belief revision
→ independent reproduction
→ durable knowledge
```

Only then should Cognitia claim that it has demonstrated a meaningful form of machine discovery.
