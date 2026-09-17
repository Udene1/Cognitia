"""Reconstruct development episodes from repository-state evidence.

This module deliberately separates observed temporal relationships from causal
explanations. It can establish that a repository change preceded an observed
consequence when the evidence carries ordered state identities, but it does not
assign an intended reason to the change.
"""
from __future__ import annotations

from dataclasses import dataclass

from .observation import Observation


@dataclass(frozen=True)
class DevelopmentEpisode:
    before: Observation
    after: Observation
    consequence: Observation
    changed: bool
    temporal_relation: str
    causal_explanation: str | None


class DevelopmentEpisodeReconstructor:
    """Recover the smallest defensible episode from raw evidence."""

    def reconstruct(
        self,
        before: Observation,
        after: Observation,
        consequence: Observation,
    ) -> DevelopmentEpisode:
        if before.environment != "git" or after.environment != "git":
            raise ValueError("development states must come from git observations")
        if before.kind != "repository_state" or after.kind != "repository_state":
            raise ValueError("development states must be repository_state observations")

        before_commit = dict(before.metadata).get("commit", before.subject)
        after_commit = dict(after.metadata).get("commit", after.subject)
        changed = before_commit != after_commit

        return DevelopmentEpisode(
            before=before,
            after=after,
            consequence=consequence,
            changed=changed,
            temporal_relation="change_precedes_consequence" if changed else "no_change_observed",
            causal_explanation=None,
        )
