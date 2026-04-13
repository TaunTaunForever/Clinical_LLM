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
    semantic_type: str = "attribute"
    synonyms: list[str] = field(default_factory=list)
    supports_filter: bool = True
    supports_group_by: bool = True
    supports_select: bool = True
    supported_aggregations: list[str] = field(default_factory=list)
    is_derived: bool = False
    derivation: str | None = None


@dataclass(slots=True)
class DatasetSchema:
    """Dataset metadata exposed to the planner."""

    name: str
    columns: list[ColumnSchema]
    description: str = ""
    cohort_role: str = "unspecified"
    entity_grain: str = "row"
    planner_guidance: list[str] = field(default_factory=list)

    def column_names(self) -> list[str]:
        return [column.name for column in self.columns]

    def get_column(self, name: str) -> ColumnSchema | None:
        for column in self.columns:
            if column.name == name:
                return column
        return None

    def to_prompt_payload(self) -> dict[str, Any]:
        return {
            "dataset_name": self.name,
            "dataset_description": self.description,
            "cohort_role": self.cohort_role,
            "entity_grain": self.entity_grain,
            "planner_guidance": self.planner_guidance,
            "columns": [
                {
                    "name": column.name,
                    "dtype": column.dtype,
                    "description": column.description,
                    "allowed_values": column.allowed_values,
                    "semantic_type": column.semantic_type,
                    "synonyms": column.synonyms,
                    "supports_filter": column.supports_filter,
                    "supports_group_by": column.supports_group_by,
                    "supports_select": column.supports_select,
                    "supported_aggregations": column.supported_aggregations,
                    "is_derived": column.is_derived,
                    "derivation": column.derivation,
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
                supported_aggregations=["count"],
            )
            for column in frame.columns
        ],
    )


def build_sepsis_survival_schema(split_name: str = "evaluation") -> DatasetSchema:
    """Return the schema metadata for the bound sepsis survival dataset."""

    dataset_name_by_split = {
        "training": "sepsis_survival_primary_cohort",
        "evaluation": "sepsis_survival_study_cohort",
        "heldout": "sepsis_survival_validation_cohort",
    }

    return DatasetSchema(
        name=dataset_name_by_split.get(split_name, "sepsis_survival_study_cohort"),
        description=(
            "Retrospective sepsis survival cohort with one row per episode. "
            "The dataset is narrow and supports demographic, episode-level, "
            "and hospital survival outcome analysis."
        ),
        cohort_role=split_name,
        entity_grain="episode",
        planner_guidance=[
            "Treat each row as a retrospective sepsis episode record.",
            "Do not infer diagnosis, treatment effects, or causality.",
            "Use derived flags for mortality and survival outcomes when possible.",
            "Prefer grouping by sex_label over the raw sex encoding for user-facing plans.",
            "episode_number is an identifier-like episode field and is usually better for counts than means.",
        ],
        columns=[
            ColumnSchema(
                name="age_years",
                dtype="int64",
                description="Patient age in years at cohort entry for the sepsis episode.",
                semantic_type="demographic_numeric",
                synonyms=["age", "patient_age", "age_in_years"],
                supported_aggregations=["count", "mean", "median", "std", "min", "max"],
            ),
            ColumnSchema(
                name="sex_0male_1female",
                dtype="int64",
                description="Raw binary sex encoding where 0=male and 1=female.",
                allowed_values=["0", "1"],
                semantic_type="categorical_code",
                synonyms=["sex_code", "gender_code", "raw_sex"],
                supported_aggregations=["count", "proportion"],
            ),
            ColumnSchema(
                name="episode_number",
                dtype="int64",
                description="Episode identifier/count field from the source dataset.",
                semantic_type="identifier",
                synonyms=["episode", "encounter_number", "episode_id"],
                supports_group_by=False,
                supported_aggregations=["count"],
            ),
            ColumnSchema(
                name="hospital_outcome_1alive_0dead",
                dtype="int64",
                description="Raw binary hospital outcome where 1=alive and 0=dead.",
                allowed_values=["0", "1"],
                semantic_type="outcome_code",
                synonyms=["hospital_outcome", "survival_outcome", "alive_dead_flag"],
                supported_aggregations=["count", "proportion", "mean"],
            ),
            ColumnSchema(
                name="sex_label",
                dtype="category",
                description="Derived categorical sex label mapped from the raw binary encoding.",
                allowed_values=["male", "female"],
                semantic_type="categorical_label",
                synonyms=["sex", "gender", "sex_group"],
                supported_aggregations=["count", "proportion"],
                is_derived=True,
                derivation="Mapped from sex_0male_1female with 0->male and 1->female.",
            ),
            ColumnSchema(
                name="survival_flag",
                dtype="int64",
                description="Derived binary survival indicator where 1=alive and 0=dead.",
                allowed_values=["0", "1"],
                semantic_type="binary_outcome",
                synonyms=["survived", "alive", "survival"],
                supported_aggregations=["count", "proportion", "survival_rate", "mean"],
                is_derived=True,
                derivation="Copied from hospital_outcome_1alive_0dead.",
            ),
            ColumnSchema(
                name="mortality_flag",
                dtype="int64",
                description="Derived binary mortality indicator where 1=dead and 0=alive.",
                allowed_values=["0", "1"],
                semantic_type="binary_outcome",
                synonyms=["died", "death", "mortality", "in_hospital_mortality"],
                supported_aggregations=["count", "proportion", "mortality_rate", "mean"],
                is_derived=True,
                derivation="Computed as 1 - survival_flag.",
            ),
        ],
    )
