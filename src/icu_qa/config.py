"""Configuration helpers for local development."""

from __future__ import annotations

import os
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
    planner_model_name: str = field(
        default_factory=lambda: os.getenv("ICU_QA_PLANNER_MODEL", "gpt-4.1-mini")
    )
    training_base_model_name: str = field(
        default_factory=lambda: os.getenv(
            "ICU_QA_TRAINING_BASE_MODEL",
            "Qwen/Qwen2.5-3B-Instruct",
        )
    )
    training_artifact_dir: Path = field(default_factory=lambda: Path("artifacts/finetune"))
    training_output_dir: Path = field(default_factory=lambda: Path("artifacts/training_runs"))
    planner_api_url: str = field(
        default_factory=lambda: os.getenv(
            "ICU_QA_PLANNER_API_URL",
            "https://api.openai.com/v1/chat/completions",
        )
    )
    planner_api_key: str = field(default_factory=lambda: os.getenv("ICU_QA_PLANNER_API_KEY", ""))
    planner_timeout_seconds: float = field(
        default_factory=lambda: float(os.getenv("ICU_QA_PLANNER_TIMEOUT_SECONDS", "60"))
    )
    planner_temperature: float = field(
        default_factory=lambda: float(os.getenv("ICU_QA_PLANNER_TEMPERATURE", "0"))
    )
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

    def resolved_training_artifact_dir(self) -> Path:
        return (self.project_root / self.training_artifact_dir).resolve()

    def resolved_training_output_dir(self) -> Path:
        return (self.project_root / self.training_output_dir).resolve()
