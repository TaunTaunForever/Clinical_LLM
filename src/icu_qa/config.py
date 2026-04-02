"""Configuration helpers for local development."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Settings:
    """Project settings for local execution.

    Phase 1 keeps configuration intentionally minimal and file-based.
    """

    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2])
    dataset_dir: Path = field(
        default_factory=lambda: Path("s41598-020-73558-3_sepsis_survival_dataset")
    )
    training_data_path: Path = field(
        default_factory=lambda: Path(
            "s41598-020-73558-3_sepsis_survival_dataset/"
            "s41598-020-73558-3_sepsis_survival_primary_cohort.csv"
        )
    )
    evaluation_data_path: Path = field(
        default_factory=lambda: Path(
            "s41598-020-73558-3_sepsis_survival_dataset/"
            "s41598-020-73558-3_sepsis_survival_study_cohort.csv"
        )
    )
    heldout_data_path: Path = field(
        default_factory=lambda: Path(
            "s41598-020-73558-3_sepsis_survival_dataset/"
            "s41598-020-73558-3_sepsis_survival_validation_cohort.csv"
        )
    )
    training_dataset_name: str = "sepsis_survival_primary_cohort"
    evaluation_dataset_name: str = "sepsis_survival_study_cohort"
    heldout_dataset_name: str = "sepsis_survival_validation_cohort"
    planner_model_name: str = "TODO_REMOTE_PLANNER"
    planner_temperature: float = 0.0
    max_rows_preview: int = 5

    @property
    def resolved_data_path(self) -> Path:
        """Backward-compatible alias for the evaluation dataset path."""

        return self.resolved_evaluation_data_path()

    @property
    def resolved_dataset_dir(self) -> Path:
        return (self.project_root / self.dataset_dir).resolve()

    def resolved_training_data_path(self) -> Path:
        return (self.project_root / self.training_data_path).resolve()

    def resolved_evaluation_data_path(self) -> Path:
        return (self.project_root / self.evaluation_data_path).resolve()

    def resolved_heldout_data_path(self) -> Path:
        return (self.project_root / self.heldout_data_path).resolve()
