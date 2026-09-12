"""Learn reusable solution patterns from concrete implementations and their logic.

Code is not treated as mere implementation noise.  A program is an executable
representation of a solution: its control flow, data transformations,
constraints, and invariants can be retained alongside an abstraction that can be
expressed independently of a programming language.

The abstraction is explicit in v0.01.  Cognitia must not infer that a code shape
is universally useful merely because a commit exists or a test passed once.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from cognitia.memory import Experience


@dataclass(frozen=True)
class SolutionPattern:
    """A concrete implementation linked to an abstract computational solution."""

    problem: str
    logic: tuple[str, ...]
    implementation: str
    language: str | None
    context: tuple[tuple[str, object], ...]
    positive: int
    negative: int
    neutral: int

    @property
    def observations(self) -> int:
        return self.positive + self.negative + self.neutral

    @property
    def success_rate(self) -> float:
        if self.observations == 0:
            return 0.0
        return self.positive / self.observations

    def matches(self, context: dict[str, object]) -> bool:
        return all(context.get(key) == value for key, value in self.context)


class SolutionPatternLearner:
    """Learn both executable forms and their language-independent logic.

    An experience opts in with ``solution_problem``, ``solution_logic`` and
    ``solution_implementation`` context fields.  This keeps code learning
    explicit and prevents arbitrary source text or commit messages from becoming
    accidental knowledge.
    """

    problem_key = "solution_problem"
    logic_key = "solution_logic"
    implementation_key = "solution_implementation"
    language_key = "solution_language"

    def learn(self, experiences: Iterable[Experience]) -> tuple[SolutionPattern, ...]:
        groups: dict[
            tuple[str, tuple[str, ...], str, str | None, tuple[tuple[str, object], ...]],
            list[int],
        ] = {}

        for experience in experiences:
            problem = experience.context.get(self.problem_key)
            logic = experience.context.get(self.logic_key)
            implementation = experience.context.get(self.implementation_key)
            if not all(isinstance(value, str) and value.strip() for value in (problem, implementation)):
                continue
            if not isinstance(logic, (tuple, list)) or not logic or not all(
                isinstance(step, str) and step.strip() for step in logic
            ):
                continue

            language = experience.context.get(self.language_key)
            if language is not None and not isinstance(language, str):
                continue

            context = tuple(
                sorted(
                    (key, value)
                    for key, value in experience.context.items()
                    if key not in {
                        self.problem_key,
                        self.logic_key,
                        self.implementation_key,
                        self.language_key,
                    }
                )
            )
            key = (problem, tuple(logic), implementation, language, context)
            counts = groups.setdefault(key, [0, 0, 0])
            counts[{"positive": 0, "negative": 1, "neutral": 2}[experience.outcome.kind]] += 1

        return tuple(
            SolutionPattern(
                problem=problem,
                logic=logic,
                implementation=implementation,
                language=language,
                context=context,
                positive=counts[0],
                negative=counts[1],
                neutral=counts[2],
            )
            for (problem, logic, implementation, language, context), counts in sorted(groups.items())
        )

    def applicable(
        self,
        experiences: Iterable[Experience],
        *,
        problem: str,
        context: dict[str, object],
    ) -> tuple[SolutionPattern, ...]:
        return tuple(
            pattern
            for pattern in self.learn(experiences)
            if pattern.problem == problem and pattern.matches(context)
        )
