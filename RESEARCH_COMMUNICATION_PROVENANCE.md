# Communication Capability Acquisition Provenance

## Purpose

This record makes the communication research lineage auditable. It answers a
specific question that ordinary experiment history can leave ambiguous:

> **Did Cognitia learn this capability from experience, or did we put the
> capability into the system and then test it?**

A passing experiment does not change provenance. A capability remains
`developer_specified` when its mechanism, taxonomy, recipient mapping, or
selection rule was supplied by the research implementation.

This document is paired with the executable provenance model in
`cognitia/communication_provenance.py`. The code is deliberately metadata-only;
it does not select communication acts or teach Cognitia how to communicate.

## Provenance vocabulary

| Origin | Meaning |
|---|---|
| `developer_specified` | The capability or rule was explicitly introduced by the implementation/researcher. |
| `experience_derived` | A capability was derived from observed experience rather than supplied as the target behavior. |
| `transfer_derived` | A capability was recovered through transfer from previously acquired structure. |
| `observed` | The record documents an observed behavior without claiming that Cognitia learned it. |
| `unknown` | Provenance has not yet been established. |

`independent_of_handholding` is intentionally separate from `origin`. It must
not be inferred from a green CI run.

## Current communication lineage

### Recipient-sensitive communication

- **origin:** `developer_specified`
- **introduced_by:** PR #9
- **evidence:** PR #9
- **validated_by:** PR #12 as controlled structural transfer
- **later_boundaries:** PR #47
- **independent_of_handholding:** false
- **current_status:** engineered mechanism; not independently learned

PR #9 explicitly introduced recipient-conditioned mappings. PR #12 tested
transfer of that engineered capability to a held-out state. That transfer is
useful evidence about the mechanism, but it is not evidence that Cognitia
discovered recipient sensitivity itself.

PR #47 subsequently showed that the current answering path did not actually
consume interaction context in the way the communication research requires.
That is a boundary finding, not a reason to rewrite the earlier provenance.

### Representation-preserving communication

- **origin:** `developer_specified`
- **introduced_by:** PR #10
- **evidence:** PR #10
- **validated_by:** controlled representation-preservation experiments
- **independent_of_handholding:** false
- **current_status:** engineered representation/projection mechanism; not independently learned

The epistemic-preservation invariant and projection mechanism were supplied by
the research implementation. Successful preservation tests therefore validate
the implementation rather than prove autonomous discovery of the invariant.

### Communication consequence exposure

- **origin:** `observed`
- **introduced_by:** PR #48
- **evidence:** PR #48
- **independent_of_handholding:** false
- **current_status:** consequence reaches the existing revision boundary; no communication-learning capability established

PR #48 deliberately did not provide a communication-learning rule or preferred
response. It exposed a recipient consequence to the existing answering/revision
boundary. The recipient responses were still deterministic test generators,
so this is not yet an independent environment or evidence of learned
communication adaptation.

### Communication adaptation

- **origin:** `unknown`
- **introduced_by:** not yet established
- **evidence:** none establishing independent learning
- **independent_of_handholding:** false
- **current_status:** unresolved research question

No current experiment should label this capability `experience_derived` until
Cognitia itself extracts a reusable communication consequence from interaction,
changes a future communication decision, and survives a held-out transfer test
without the target adaptation being supplied by the experiment.

## Research history rule

For every future communication capability, record:

```text
observation
→ hypothesis
→ experiment
→ result
→ interpretation
→ provenance
→ next hypothesis
```

The provenance entry must identify:

1. capability name;
2. origin;
3. introducing change/experiment;
4. source observations or experiences;
5. validation experiments;
6. later boundary/falsification evidence;
7. whether the evidence was independent of handholding;
8. current status.

## Zero-handholding rule

The provenance record must never be used to smuggle a desired communication
behavior into an experiment. It is an audit trail, not a teaching mechanism.

In particular, a future experiment must not change `origin` to
`experience_derived` merely because:

- CI passes;
- an expected answer was produced;
- a deterministic recipient returned the expected consequence;
- a hand-coded rule generalized to a held-out case;
- a researcher can explain why a communication act was appropriate.

The origin changes only when the acquisition evidence justifies the claim.

## Why this matters for future fixes

If a regression appears, provenance lets us ask whether we are debugging:

- a capability we explicitly engineered;
- a capability transferred from an earlier engineered mechanism;
- a capability that Cognitia actually acquired from experience;
- or a behavior whose provenance is still unknown.

This prevents a later repair from accidentally treating a research hypothesis
as established architecture, and it preserves the distinction between **how we
taught Cognitia** and **what Cognitia learned**.
