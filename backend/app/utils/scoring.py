"""Scoring utility helpers for market analytics modules."""

from __future__ import annotations


def clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    """Clamp a numeric value within bounds."""
    return max(lower, min(upper, value))


def weighted_score(components: list[tuple[float, float]]) -> float:
    """Compute normalized weighted score from (value, weight) pairs."""
    total_weight = sum(weight for _, weight in components)
    if total_weight == 0:
        return 0.0
    score = sum(value * weight for value, weight in components) / total_weight
    return clamp(score)


def score_from_thresholds(value: float, good: float, bad: float, inverse: bool = False) -> float:
    """Map values to 0-100 based on linear good/bad thresholds."""
    if good == bad:
        return 50.0

    if inverse:
        if value <= good:
            return 100.0
        if value >= bad:
            return 0.0
        return clamp(100 * (bad - value) / (bad - good))

    if value >= good:
        return 100.0
    if value <= bad:
        return 0.0
    return clamp(100 * (value - bad) / (good - bad))
