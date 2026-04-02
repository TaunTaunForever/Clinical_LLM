"""Deterministic preprocessing helpers."""

from __future__ import annotations

import pandas as pd


def normalize_column_names(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with standardized snake_case-like column names."""

    normalized = frame.copy()
    normalized.columns = [
        column.strip().lower().replace(" ", "_").replace("-", "_")
        for column in normalized.columns
    ]
    return normalized


def basic_preprocess(frame: pd.DataFrame) -> pd.DataFrame:
    """Apply lightweight preprocessing steps used across local workflows."""

    return normalize_column_names(frame)


def preprocess_sepsis_survival_dataset(frame: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the bound sepsis survival dataset into analysis-ready columns."""

    processed = basic_preprocess(frame)

    required_columns = {
        "age_years",
        "sex_0male_1female",
        "episode_number",
        "hospital_outcome_1alive_0dead",
    }
    missing = required_columns.difference(processed.columns)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Dataset is missing required sepsis survival columns: {missing_list}")

    processed["sex_label"] = processed["sex_0male_1female"].map({0: "male", 1: "female"})
    processed["survival_flag"] = processed["hospital_outcome_1alive_0dead"].astype(int)
    processed["mortality_flag"] = 1 - processed["survival_flag"]
    return processed
