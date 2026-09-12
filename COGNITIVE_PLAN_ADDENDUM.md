# Cognitia — Cognitive Plan Addendum

This addendum records architectural principles and requirements discovered after the original `CHATGPT.md` plan. It is part of the durable Cognitia plan and must be consulted alongside `CHATGPT.md` until these sections are merged into the main plan.

## 1. Epistemic self-awareness

Cognitia must model not only the world and what it knows, but its own cognitive capabilities and limitations.

It should distinguish:

- knows;
- does not know;
- knows that it does not know;
- does not know whether it knows;
- lacks sufficient evidence;
- has insufficient reasoning machinery;
- has a partial capability that can still produce a useful approximation;
- cannot currently produce a meaningful attempt.

The dangerous state is not simply ignorance. It is **unknown ignorance**: Cognitia does not realize that the required knowledge or capability is absent and therefore silently substitutes an unrelated or weaker mechanism.

## 2. Capability self-model

Cognitia needs an explicit model of its own cognitive capabilities.

A capability should eventually describe at least:

- capability identity;
- domain;
- maturity;
- reliability;
- prerequisites;
- supported problem classes;
- known limitations;
- known failure modes;
- required inputs;
- verification method;
- historical performance;
- contexts in which performance changes.

The self-model must itself be evidence-based and revisable. Cognitia should learn where it is strong and where it systematically fails.

## 3. Capability-gap detection

Before reasoning deeply, Cognitia should identify the capabilities required by the problem and compare them with its current capability inventory.

```text
Problem
  ↓
Required capabilities
  ↓
Self-model
  ↓
Capability assessment
  ↓
Sufficient / Partial / Missing
```

A capability gap is not automatically a reason to stop. It is an epistemic fact that affects how the resulting conclusion must be represented.

## 4. Attempt, qualify, verify

**Capability limitation changes epistemic status; it does not automatically terminate investigation.**

When a required capability is missing or immature, Cognitia should:

1. determine whether existing capabilities can produce useful partial information;
2. explicitly record the substitution or approximation;
3. produce the strongest justified hypothesis or estimate available;
4. label the result with an appropriate epistemic status;
5. expose assumptions and capability limitations;
6. state what could make the conclusion wrong;
7. identify a verification path;
8. pursue verification when its expected value justifies the cost.

Core principle:

> **Never confuse inability to establish with inability to investigate.**

A weaker capability may generate hypotheses or approximations, but it must not silently masquerade as a stronger capability.

## 5. Epistemic result classes

Cognitia should eventually distinguish at least:

- established result;
- supported conclusion;
- prediction;
- inference;
- hypothesis;
- approximation;
- heuristic;
- analogy;
- speculation;
- unresolved question;
- capability-limited result.

A confidence number alone is insufficient. A conclusion should carry its epistemic class, reasoning method, evidence, assumptions, limitations, and verification requirements.

## 6. Transparent capability substitution

If Cognitia needs causal inference but only has correlation analysis, it may use correlation to generate candidate explanations, but must record:

```text
Required capability: causal inference
Available capability: correlation analysis
Substitution: correlation used for hypothesis generation
Validity: insufficient to establish causality
Result: candidate explanation
Verification: required
```

This prevents a weaker mechanism from silently impersonating a stronger one while preserving useful forward progress.

## 7. Cognitive routing

Cognitia should learn to select reasoning mechanisms based on the structure of the problem.

```text
Problem
  ↓
Problem classification
  ↓
Relevant domain
  ↓
Required models
  ↓
Required reasoning mechanism
  ↓
Required evidence
  ↓
Investigation / reasoning
```

The routing system should eventually learn which reasoning mechanism and information source are most useful for particular problem classes.

## 8. Three-model architecture

Cognitia should maintain three interacting representations:

### World model

What is happening outside Cognitia?

### Knowledge model

What does Cognitia know, why does it believe it, and what evidence supports it?

### Self model

What can Cognitia currently determine, how reliable are its capabilities, where does it fail, and what machinery is missing?

These models should influence one another through the meta-reasoner.

```text
World model
Knowledge model
Self model
      ↓
Meta-reasoner
      ↓
Reasoning method
      ↓
Conclusion / action / investigation
      ↓
Observation
      ↓
Update world + knowledge + self models
```

## 9. Verification-aware conclusions

Important conclusions should eventually be able to expose a structured verification plan:

```text
Claim
Epistemic status
Reasoning method
Evidence
Supporting evidence
Contradicting evidence
Assumptions
Capability limitations
Confidence
What would change the conclusion?
Recommended verification
Expected value of verification
```

This is preferable to either false certainty or refusing to reason whenever certainty is unavailable.

## 10. Capability acquisition

Capability acquisition is a first-class cognitive process, not synonymous with generating source code.

```text
Capability gap
    ↓
Inspect existing operations
    ↓
Can existing operations solve it?
    ├─ yes → compose
    └─ no
         ↓
   Did Cognitia repeatedly solve it through the same procedure?
    ├─ yes → learn reusable procedure
    └─ no
         ↓
   Is controlled construction authorized?
    ├─ yes → construct candidate implementation
    └─ no → retain unresolved capability gap
```

A capability candidate consists of more than code. It carries its representation, procedure/operations, provenance, and (when constructed) a code artifact. Candidates are immutable research artifacts until evaluation succeeds.

Capability acquisition must not silently modify the active cognitive build. Construction is candidate generation; benchmark evidence determines whether the candidate is useful; cross-capability regression determines whether it can be promoted.

## 11. Candidate evaluation and cognitive builds

Cognitia must distinguish **software version** from **cognitive build**.

A cognitive build is an immutable manifest of capabilities, maturity, status, parent build, and notes. Candidate capabilities may exist in a candidate/held build without becoming active.

```text
Gap
 ↓
Acquisition plan
 ↓
Candidate capability
 ↓
Deterministic benchmark
 ↓
Compare against baseline
 ↓
Check protected capabilities
 ↓
 ┌───────────────┐
 │ no regression │ → eligible for promotion
 └───────────────┘
        │
        └→ regression → HOLD_FOR_BALANCING
                         ↓
                   repair / compose / selective integration
                         ↓
                      benchmark again
```

**Regression is a promotion blocker, not a capability deletion command.** A useful new capability must be retained even when its first integration is harmful. Cognitia should attempt to balance capabilities, alter their interaction, or selectively integrate them before giving up on the candidate.

## 12. New implementation roadmap

The following work is now a priority in the architecture:

### Epistemic foundations

- [x] Capability representation
- [x] Capability profile / self-model
- [x] Capability-gap representation
- [x] Epistemic result classes
- [x] Transparent capability substitution
- [x] Verification-plan representation

### Meta-reasoning

- [x] Capability-aware reasoning routing
- [ ] Problem-to-reasoning-method mapping
- [x] Self-performance history
- [x] Failure-mode learning
- [ ] Value-of-information for verification

### Capability acquisition

- [x] Executable composition of existing operations
- [x] Reusable procedure learning from repeated traces
- [x] Controlled candidate construction
- [x] Automatic acquisition-mode selection
- [x] Candidate benchmark pipeline
- [x] Immutable cognitive build manifest
- [ ] Persistent candidate registry
- [ ] Automated capability synthesis/repair loop
- [ ] Formal verification and sandbox execution for constructed code

### Long-term

- [ ] Learn cognitive topology: where useful information and reasoning structures are likely to reside
- [ ] Detect architecture-level capability failures
- [ ] Propose new cognitive capabilities when repeated failures reveal missing machinery
- [ ] Benchmark successive cognitive builds against identical tasks
- [ ] Maintain reproducible historical cognitive builds

## 13. Permanent design laws added by this addendum

1. **Do not pretend to possess a capability that Cognitia does not possess.**
2. **Do not stop merely because a capability is incomplete if a useful, explicitly qualified attempt is possible.**
3. **A weaker capability may approximate or generate hypotheses for a stronger required capability only when the substitution is explicit.**
4. **Every important conclusion should carry enough epistemic metadata to understand how it was produced and how it could be wrong.**
5. **Uncertainty should trigger investigation, not automatic paralysis.**
6. **Cognitia must learn about its own failures, not only failures in the external world.**
7. **Capability acquisition is broader than code generation: knowledge, representation, composition, procedures, algorithms, tools, and code can all create capability.**
8. **Regression blocks promotion before it deletes capability.**
9. **Cognitive builds are immutable capability configurations, distinct from ordinary software versions.**
10. **A constructed capability must remain a candidate until it survives tests, benchmarks, and protected-capability regression checks.**
11. **When user observations expose an important capability gap or architectural insight, record it in the durable plan before continuing so future work does not silently forget it.**
