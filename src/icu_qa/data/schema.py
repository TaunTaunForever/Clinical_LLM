"""Schema objects used by the planner and validator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass(slots=True)
class ColumnSchema:
    """Metadata for a single dataset column."""

    name: str
    dtype: str
    description: str
    allowed_values: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DatasetSchema:
    """Dataset metadata exposed to the planner."""

    name: str
    columns: list[ColumnSchema]

    def column_names(self) -> list[str]:
        return [column.name for column in self.columns]

    def to_prompt_payload(self) -> dict[str, Any]:
        return {
            "dataset_name": self.name,
            "columns": [
                {
                    "name": column.name,
                    "dtype": column.dtype,
                    "description": column.description,
                    "allowed_values": column.allowed_values,
                }
                for column in self.columns
            ],
        }


def infer_schema_from_frame(frame: pd.DataFrame, name: str) -> DatasetSchema:
    """Infer a lightweight dataset schema from dataframe columns and dtypes."""

    return DatasetSchema(
        name=name,
        columns=[
            ColumnSchema(
                name=column,
                dtype=str(frame[column].dtype),
                description=f"Column {column}",
            )
            for column in frame.columns
        ],
    )


def build_sepsis_survival_schema() -> DatasetSchema:
    """Return the schema metadata for the bound sepsis survival dataset."""

    return DatasetSchema(
        name="sepsis_survival_study_cohort",
        columns=[
            ColumnSchema(
                name="age_years",
                dtype="int64",
                description="Patient age in years at cohort entry.",
            ),
            ColumnSchema(
                name="sex_0male_1female",
                dtype="int64",
                description="Binary sex encoding where 0=male and 1=female.",
                allowed_values=["0", "1"],
            ),
            ColumnSchema(
                name="episode_number",
                dtype="int64",
                description="Episode count identifier from the source dataset.",
            ),
            ColumnSchema(
                name="hospital_outcome_1alive_0dead",
                dtype="int64",
                description="Binary hospital outcome where 1=alive and 0=dead.",
                allowed_values=["0", "1"],
            ),
            ColumnSchema(
                name="sex_label",
                dtype="category",
                description="Derived categorical sex label from source encoding.",
                allowed_values=["male", "female"],
            ),
            ColumnSchema(
                name="survival_flag",
                dtype="int64",
                description="Derived binary survival indicator where 1=alive and 0=dead.",
                allowed_values=["0", "1"],
            ),
            ColumnSchema(
                name="mortality_flag",
                dtype="int64",
                description="Derived binary mortality indicator where 1=dead and 0=alive.",
                allowed_values=["0", "1"],
            ),
        ],
    )
