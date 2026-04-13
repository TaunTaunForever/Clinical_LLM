"""Aggregation helpers used by the execution engine."""

from __future__ import annotations

from typing import Callable

import pandas as pd


def mortality_rate(series: pd.Series) -> float:
    """Return the share of positive outcome rows in a binary mortality column."""

    if len(series) == 0:
        return 0.0
    return float(series.astype(float).mean())


def survival_rate(series: pd.Series) -> float:
    """Return one minus the mortality rate for a binary outcome column."""

    return 1.0 - mortality_rate(series)


AGGREGATION_FUNCTIONS: dict[str, Callable[[pd.Series], float | int]] = {
    "count": lambda series: int(series.count()),
    "mean": lambda series: float(series.mean()),
    "median": lambda series: float(series.median()),
    "std": lambda series: float(series.std()),
    "min": lambda series: float(series.min()),
    "max": lambda series: float(series.max()),
    "proportion": lambda series: float(series.astype(float).mean()),
    "mortality_rate": mortality_rate,
    "survival_rate": survival_rate,
}
