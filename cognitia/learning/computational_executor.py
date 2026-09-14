"""Execute bounded computational families without depending on source language."""
from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any


def execute_family(
    family: str,
    records: Iterable[dict[str, Any]],
    *,
    key_field: str,
    value_field: str,
    reducer: Callable[[Any, Any], Any] | None = None,
) -> dict[Any, Any]:
    """Execute a learned family against a fresh dataset.

    The executor consumes the abstract family name, not Python/JavaScript/SQL
    source. It is deliberately small: the research question is whether a
    computational abstraction survives language boundaries, not whether this
    function is a general-purpose runtime.
    """
    if family != "group_by_reduce":
        raise ValueError(f"unsupported computational family: {family}")
    combine = reducer or (lambda left, right: left + right)
    result: dict[Any, Any] = {}
    for record in records:
        key = record[key_field]
        value = record[value_field]
        result[key] = value if key not in result else combine(result[key], value)
    return result
