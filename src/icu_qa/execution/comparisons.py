"""Cohort comparison helpers."""

from __future__ import annotations

from typing import Any

import pandas as pd


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
