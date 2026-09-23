# Research Experiment: Open-Ended Experience Retrieval

## Question

Can Cognitia receive an open-ended research question and autonomously select relevant
prior observations from its durable experience store, rather than being handed a
history slice by the experiment?

## Why this experiment

The incremental Cashflow acquisition work established that Cognitia can retain an
append-only observation history across a moving source window. The next boundary is
whether that accumulated experience is actually addressable when cognition needs it.

A successful result must therefore contain evidence of retrieval, not merely a
successful final research action.

## Experimental boundary

The experiment supplies only:

- the live Cashflow environment;
- the current open-ended question.

It does **not** supply historical observation IDs, a history list, or a preselected
time range.

Cognitia first acquires the current environment incrementally, then asks its
experience retriever to find relevant retained observations from the durable ledger.
The retrieved evidence is converted into claims and combined with current claims for
research-action selection.

## Question presented to Cognitia

> Which prior prospect-touch events correspond to later stage transitions?

This deliberately changes the vocabulary used to describe the same research target.
The stored Cashflow observations are expected to use terms such as outreach, lead,
and state changes. The experiment therefore does not give the lexical retriever the
original wording as an addressability shortcut.

## Controls

Three trajectories are recorded:

1. **Blind:** current evidence only.
2. **Experience-informed:** current evidence plus observations Cognitia selected
   from durable history.
3. **History-ablated:** current evidence only; all historical claims are withheld.

The experiment compares actions and rationales rather than treating a changed
string alone as proof of cognition.

## Evidence recorded

The artifact records:

- acquisition batches and cursor;
- number of newly acquired observations;
- current observation set;
- which historical observations were retrieved;
- retrieval scores and matched terms;
- claims derived from retrieved experience;
- blind, experience-informed, and history-ablated research decisions;
- whether retrieval changed the selected action or rationale.

## Interpretation

A useful positive result requires all of the following:

1. relevant prior observations are retrieved without being named by the experiment;
2. retrieved observations produce auditable claims;
3. the experience-informed trajectory is materially different from the blind or
   history-ablated trajectory, or its rationale explicitly incorporates retrieved
   evidence;
4. the retrieved evidence is traceable to durable observations.

This experiment does **not** establish semantic understanding or causal reasoning.
The first retrieval mechanism is deterministic lexical matching. If it fails, the
result identifies an addressability boundary rather than hiding that limitation.

## Next boundary

The immediate test is the wording-mismatch run above. A failure is an intended
research result: it would show that the current lexical retriever cannot bridge the
representation gap. If it succeeds, the artifact must be inspected to determine
whether the match came from genuine vocabulary-independent structure or accidental
lexical overlap before strengthening the retriever.
