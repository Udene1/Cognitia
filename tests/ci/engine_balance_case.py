"""A real engineering decision policy: balance a new capability against regressions."""


def decide_capability(candidate_gain: float, regression: float, new_capability: bool) -> str:
    """Keep the baseline while a useful but regressing capability is balanced."""
    if new_capability and regression > 0:
        return "hold_for_balancing"
    if new_capability and candidate_gain > 0 and regression <= 0:
        return "promote"
    return "retain_baseline"
