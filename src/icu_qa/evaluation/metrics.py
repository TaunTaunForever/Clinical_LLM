"""Evaluation metrics for planner and execution behavior."""

from __future__ import annotations

from typing import Any, Iterable

import pandas as pd


def json_validity_rate(flags: Iterable[bool]) -> float:
    """Return the share of planner outputs that parsed as valid JSON/plans."""

    values = list(flags)
    if not values:
        return 0.0
    return sum(bool(flag) for flag in values) / len(values)


def exact_table_match(left: pd.DataFrame, right: pd.DataFrame) -> bool:
    """Return whether two result tables match exactly after index reset."""

    return left.reset_index(drop=True).equals(right.reset_index(drop=True))


def exact_plan_match(predicted: dict[str, Any], gold: dict[str, Any]) -> bool:
    """Return whether two planner outputs match exactly."""

    return predicted == gold


def slot_level_accuracy(predicted: dict[str, Any], gold: dict[str, Any]) -> float:
    """Return simple slot-level accuracy over gold top-level keys."""

    if not gold:
        return 0.0
    matched = 0
    for key, value in gold.items():
        if predicted.get(key) == value:
            matched += 1
    return matched / len(gold)
