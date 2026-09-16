# Experience-Conditioned Future Behavior v2

## Status

Experiment implementation in progress. The result must be taken from the generated CI artifact, not from test completion alone.

## Research question

Does recorded experience alter future action selection on a held-out problem while remaining structurally specific and defeasible when contradictory evidence arrives?

This is the next discriminator after the structural-transfer experiment and the first experience-blindspot implementation. The objective is to test whether experience is actually part of the future decision state rather than merely retrievable metadata.

## Protocol

The researcher supplies only:

- a cognitive state structure;
- a set of operations the environment permits;
- the experimental conditions;
- the observables.

`StateActionGenerator` constructs candidate actions from the state. No condition supplies an expected winning action.

`ExperienceGeneratedActionSelector` ranks those generated actions using experience as defeasible evidence. It compares structural state signals and operation overlap; it does not contain scenario-specific problem -> action mappings.

Conditions:

1. experience absent baseline;
2. confirmed prior experience present;
3. the same prior experience contradicted by refuting experience;
4. held-out surface problem with the same structural state;
5. specificity control with a different structural state;
6. recovery episode after contradiction;
7. later independent episode to test persistence.

## Required observations

- **Influence:** baseline and experience-present behavior differ.
- **Defeasibility:** contradiction can change behavior relative to confirmed experience.
- **Transfer:** the effect survives a changed surface problem with the same structural state.
- **Specificity:** an unrelated structural state does not inherit the experience-driven change.
- **Recovery:** contradictory experience produces the new behavior on another held-out surface.
- **Persistence:** the post-contradiction behavior survives into a later episode.
- **Novelty:** after refutation, selection is not simply a repeat of the previously successful operation.

## Anti-handholding boundary

The harness must not encode `if experience X then action Y`.

The previous action is recorded as an observed event. The next selector receives the ledger and independently ranks generated candidates. The experiment therefore measures the implemented mechanism's trajectory instead of comparing it against researcher-provided expected actions.

## Interpretation boundary

Even if the discriminators are observed, the result establishes only that this deterministic mechanism can use structured prior experience as defeasible evidence for future action selection under the tested conditions. It does not establish general cognition, autonomous learning, or cross-domain abstraction.

The next research decision must be made from the actual trajectory, especially any failures of specificity, defeasibility, transfer, or recovery.
