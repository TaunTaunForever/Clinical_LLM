"""Experiment configuration and validation for Phase 5 fine-tuning."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from icu_qa.evaluation.finetune import default_finetune_artifact_paths


@dataclass(slots=True)
class FineTuneExperimentConfig:
    """Configuration for a planner fine-tuning experiment."""

    artifact_dir: Path
    model_family: str
    format_name: str = "supervised"
    run_name: str = "planner_finetune_baseline"


def validate_experiment_artifacts(config: FineTuneExperimentConfig) -> dict[str, Path]:
    """Ensure the required fine-tuning artifacts exist for an experiment."""

    required_paths: dict[str, Path] = {}
    for split_name in ("training", "evaluation", "heldout"):
        candidate = default_finetune_artifact_paths(config.artifact_dir, split_name)[config.format_name]
        if not candidate.exists():
            raise FileNotFoundError(
                f"Missing {config.format_name} fine-tuning artifact for split {split_name}: {candidate}"
            )
        required_paths[split_name] = candidate
    return required_paths
