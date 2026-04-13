"""Cohort comparison helpers."""

from __future__ import annotations

from typing import Any

import pandas as pd

from icu_qa.execution.aggregations import AGGREGATION_FUNCTIONS


def compare_cohort_means(
    left_frame: pd.DataFrame,
    right_frame: pd.DataFrame,
    column: str,
) -> dict[str, Any]:
    """Compute a simple mean comparison between two cohorts."""

    left_mean = float(left_frame[column].mean())
    right_mean = float(right_frame[column].mean())
    return {
        "column": column,
        "left_mean": left_mean,
        "right_mean": right_mean,
        "difference": left_mean - right_mean,
    }


def compare_cohort_metric(
    left_frame: pd.DataFrame,
    right_frame: pd.DataFrame,
    metric: str,
    column: str,
    left_label: str,
    right_label: str,
) -> dict[str, Any]:
    """Compute a deterministic cohort comparison for a supported metric."""

    function = AGGREGATION_FUNCTIONS[metric]
    left_value = function(left_frame[column])
    right_value = function(right_frame[column])
    return {
        "metric": metric,
        "column": column,
        "left_label": left_label,
        "right_label": right_label,
        "left_value": left_value,
        "right_value": right_value,
        "difference": left_value - right_value,
    }
