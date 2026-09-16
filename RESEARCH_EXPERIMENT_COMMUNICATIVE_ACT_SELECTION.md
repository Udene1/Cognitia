# Research Experiment: Communicative Act Selection

## Status

**Active research experiment — build toward this direction.**

This experiment is the first concrete investigation under `RESEARCH_COMMUNICATIVE_COGNITION.md`.

Cognitia is a research project. We do not know in advance what the final communication architecture should be. This experiment exists to produce evidence that can tell us what to build next.

We should not optimize for polished answers. We should not assume that a fixed taxonomy, template system, or language generator is the correct solution. We will construct the smallest controlled experiment that can distinguish genuine communicative cognition from surface answer production, inspect the results, and integrate only what survives.

---

## Research question

> **Given the same underlying cognitive state, can Cognitia select different communicative acts according to communicative objective and interaction context, while preserving the epistemic commitments of the underlying cognition across different representations?**

This is the first operational test of the larger hypothesis:

> **Can Cognitia learn a representation-independent model of communicative intent and interaction, such that it can discover how internal cognitive states should be transformed into appropriate actions for different recipients and objectives, while preserving epistemic truth across representations?**

The first experiment intentionally tests only a small part of that larger question.

---

## What we are trying to distinguish

The experiment must distinguish between two very different capabilities.

### Surface answer production

```text
question → answer template / generated text
```

versus:

### Communicative cognition

```text
internal cognitive state
        ↓
epistemic state
        ↓
interaction state + objective
        ↓
communicative alternatives
        ↓
communicative act selection
        ↓
representation projection
        ↓
communication consequence
```

The second is the research target.

A fluent answer is not evidence by itself.

---

# Experiment 1 — Fixed cognitive state, changing objective

## Principle

Hold the underlying cognitive state constant.

Change only the communicative objective.

Observe whether Cognitia selects different communicative acts while preserving the same epistemic commitments.

This prevents us from confusing changes in the underlying problem with changes in communication.

---

## Controlled cognitive state

Use a deliberately unresolved problem.

Example:

```text
Question:
Why did system X fail?

Candidate explanations:

H1 = resource exhaustion
    Evidence E1 supports H1.

H2 = dependency failure
    Evidence E2 weakly supports H2.

H3 = configuration error
    No current supporting evidence.

Current epistemic state:
No explanation is established.

Available evidence:
E1, E2

Missing evidence:
Evidence that discriminates among H1, H2 and H3.
```

The important property is that the state contains:

- multiple hypotheses
- unequal evidence
- unresolved uncertainty
- enough information to communicate something useful
- insufficient information for an unconditional root-cause assertion

This creates a meaningful epistemic constraint.

---

# Experimental condition A — Inform

Objective:

```text
inform the recipient about the current state of knowledge
```

Expected communicative behavior:

- report supported candidates
- distinguish evidence strength
- state that the root cause remains unresolved
- avoid presenting a candidate as established fact

Possible communicative structure:

```text
ACT = REPORT_CURRENT_STATE

claims:
    H1 → supported candidate
    H2 → weak candidate
    H3 → unsupported

commitment:
    root cause unresolved

uncertainty:
    explicit
```

The exact wording is not the primary test.

The selected act and commitments are.

---

# Experimental condition B — Investigate

Objective:

```text
help determine what should be investigated next
```

The underlying epistemic state remains identical.

Expected communicative behavior may instead be:

```text
ACT = PROPOSE_DISCRIMINATING_TEST

current leading candidates:
    H1, H2

uncertainty:
    H1 vs H2 unresolved

next evidence:
    identify observation that distinguishes H1 from H2
```

The system should communicate the uncertainty in a way that advances investigation rather than merely reporting it.

---

# Experimental condition C — Decision support

Objective:

```text
help an operator decide what to do now
```

The same epistemic state may produce:

```text
ACT = DECISION_SUPPORT

known:
    root cause unresolved

supported possibility:
    H1

possible action:
    investigate / mitigate H1

constraint:
    action must not be represented as proof that H1 is the established cause
```

The communicative act can therefore change without changing the underlying belief state.

---

# Experimental condition D — Teach

Objective:

```text
help a learner understand the situation
```

The system may need to:

```text
ACT = EXPLAIN_UNCERTAINTY

explain:
    what a hypothesis is
    why E1 supports H1
    why support is not proof
    why H2 remains possible
    what evidence would discriminate them
```

Again, the epistemic state remains unchanged.

The communication structure changes because the objective changes.

---

# Experimental condition E — Clarification required

Introduce an underspecified recipient or objective.

For example:

```text
recipient = unknown
objective = ambiguous
required detail = unknown
```

A meaningful system should have the possibility of selecting:

```text
ACT = REQUEST_CLARIFICATION
```

rather than being forced to generate an arbitrary answer.

This tests whether communication can include **interaction management**, not merely information transmission.

---

# Experimental condition F — Insufficient capability

Give Cognitia a question for which its current capabilities cannot establish the requested conclusion.

The expected behavior is not:

```text
STOP
```

and not:

```text
ASSERT_UNSUPPORTED_CONCLUSION
```

Instead, the candidate behavior is:

```text
ACT = REPORT_LIMITATION + PROVIDE_BEST_SUPPORTED_PARTIAL_RESULT
```

with:

```text
uncertainty → lower commitment
capability limitation → higher verification requirement
```

This directly tests Cognitia's existing principle that uncertainty should constrain confidence rather than become an excuse not to tackle the problem.

---

# Primary measurements

Every experimental run should record the internal communicative decision before surface realization.

At minimum:

```text
cognitive_state_id
objective
recipient/context
selected_act
alternative_acts_considered
claims_selected
claims_omitted
claim_epistemic_status
evidence_references
uncertainty
requested_action
verification_requirement
surface_representation
```

The exact schema is itself experimental and may change.

---

# The most important test: epistemic preservation

For every generated representation, compare the surface commitment against the originating cognitive state.

We need to detect transformations such as:

```text
candidate → fact

weak evidence → strong evidence

uncertain → certain

unknown → known

possible cause → established cause
```

Any such silent upgrade is a failure even if the resulting answer sounds excellent.

Conversely, excessive weakening should also be observable:

```text
validated → "maybe"

strong evidence → "we have no idea"
```

Communication should preserve the appropriate epistemic status rather than simply becoming more cautious.

---

# Representation-transfer experiment

Once communicative act selection works in a structured form, test representation independence.

Start with one communicative structure:

```text
objective = inform
claim = H1
status = supported_candidate
evidence = E1
alternatives = H2, H3
root_cause_established = false
```

Project it onto multiple surfaces:

```text
natural language
structured record
machine-readable message
```

Later, potentially:

```text
code/comment
mathematical representation
diagram
agent-to-agent protocol
```

Then compare the underlying commitments rather than the strings.

The test is:

> **Did each representation preserve the communicative act and epistemic state?**

---

# Consequence-learning extension

The controlled experiment tests selection.

The next experiment tests learning.

Introduce an interaction environment:

```text
cognitive state
      ↓
communicative act selection
      ↓
surface realization
      ↓
recipient
      ↓
recipient response / environment consequence
      ↓
observation
      ↓
communication experience
      ↓
policy/model revision
```

Example:

```text
Cognitia communicates:
"Resource exhaustion is the cause."

Recipient interprets this as established.

Observed consequence:
    operator stops investigating alternatives.

Analysis:
    communicative commitment exceeded epistemic state.
```

The important learning target is not merely:

```text
"Do not use that sentence."
```

but potentially:

```text
For unresolved competing hypotheses,
when communicating to this recipient/context,
asserting a single candidate without explicit uncertainty
has a high risk of causing false certainty.
```

This is the beginning of a learned communication policy.

---

# Child-like development hypothesis

The system should be allowed to begin with imperfect communicative behavior.

A developmental sequence might look like:

```text
primitive communicative attempts
        ↓
repeated interaction
        ↓
observed consequences
        ↓
recognition of communicative patterns
        ↓
composition of primitive acts
        ↓
context adaptation
        ↓
more reliable communication
```

The goal is not to manually encode the final behavior and call it learning.

We should determine which structures must be innate/architectural and which can emerge through experience.

That boundary is itself a research question.

---

# What counts as evidence of success?

A useful early success would require all of the following:

1. **Same underlying cognitive state.**
2. **Different communicative objective or interaction context.**
3. **Different communicative act selected where appropriate.**
4. **Selection is traceable to the cognitive + epistemic + interaction state.**
5. **Epistemic commitments remain correct.**
6. **The act can be projected into more than one representation.**
7. **The surface does not manufacture additional knowledge.**

A later success additionally requires:

8. **Consequences are observed.**
9. **Communication experience is retained.**
10. **Future communicative decisions change appropriately because of experience.**
11. **The learned pattern transfers beyond the exact training interaction.**

---

# What does NOT count as success

The following are insufficient by themselves:

- grammatically correct prose
- longer answers
- more human-like wording
- better-looking templates
- a large predefined communication taxonomy
- memorized example responses
- LLM-generated explanations
- high similarity to human reference answers
- simply adding confidence labels to generated text

These may be useful surface capabilities, but they do not establish the research hypothesis.

---

# Failure taxonomy

Every failed run should attempt to identify where the failure occurred.

### Cognition failure

The underlying problem representation was incorrect or incomplete.

### Epistemic failure

The system's representation of evidence or uncertainty was incorrect.

### Objective failure

The communicative objective was misunderstood.

### Interaction failure

The recipient/context model was missing or incorrect.

### Act-selection failure

The system had the relevant state but selected the wrong communicative action.

### Composition failure

The selected primitive acts could not be assembled into a coherent communication structure.

### Projection failure

The underlying communicative structure was correct but the target representation distorted it.

### Consequence-interpretation failure

The system observed an interaction consequence but inferred the wrong lesson from it.

### Learning failure

A valid communication experience did not produce an appropriate model/policy revision.

This taxonomy should remain provisional and can be revised as experiments reveal new failure modes.

---

# Research loop

This experiment should be developed through:

```text
hypothesis
   ↓
controlled experiment
   ↓
observation
   ↓
failure/success analysis
   ↓
revised hypothesis
   ↓
next experiment
   ↓
candidate abstraction
   ↓
validation
   ↓
integration into Cognitia
```

Do not prematurely turn an interesting observation into architecture.

---

# Integration rule

A new communication component should enter Cognitia's core only when experiments provide evidence that it represents a reusable cognitive capability rather than a narrow solution to one benchmark.

The preferred progression is:

```text
experiment
→ observation
→ candidate model
→ independent reproduction
→ transfer test
→ validation
→ integration
```

Existing systems should not be discarded merely because a new capability produces regressions. The regression becomes evidence to investigate whether the capabilities can coexist and under what conditions.

---

# Long-term target

This experiment is not intended to end with an answer generator.

The longer-term target is a system where:

```text
world / problem
      ↓
internal cognition
      ↓
epistemic state
      ↓
interaction state
      ↓
communicative objective
      ↓
communicative act
      ↓
representation-independent structure
      ↓
surface/action
      ↓
interaction consequence
      ↓
experience
      ↓
learning
```

If this works, natural-language communication becomes one surface of a more general capability.

The same underlying communicative cognition could potentially be expressed through:

- natural language
- programming languages
- mathematics
- structured messages
- diagrams
- reports
- APIs
- agent protocols
- other representations not yet anticipated

---

# Current next step

**Do not build the complete communication system.**

Build the smallest controlled implementation capable of running **Experiment 1: fixed cognitive state, changing communicative objective**.

The first milestone is not fluent communication.

It is evidence that Cognitia can separate:

```text
WHAT I KNOW
from
WHAT I WANT TO ACCOMPLISH THROUGH COMMUNICATION
from
WHAT COMMUNICATIVE ACTION IS WARRANTED
from
HOW THAT ACTION IS REPRESENTED
```

If the experiment fails, that failure tells us what Cognitia is missing.

If it succeeds, the next experiment should introduce recipient/context variation and then consequence-driven learning.

**We are not implementing an answer to the research question. We are building experiments that allow Cognitia to discover the answer.**
