"""Scaffolding for Phase 5 supervised fine-tuning runs."""

from __future__ import annotations

import importlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from icu_qa.training.experiment import FineTuneExperimentConfig, validate_experiment_artifacts


@dataclass(slots=True)
class LoRASettings:
    """Adapter-tuning hyperparameters for the first Phase 5 run."""

    r: int = 16
    alpha: int = 32
    dropout: float = 0.05
    target_modules: tuple[str, ...] = ("q_proj", "k_proj", "v_proj", "o_proj")


@dataclass(slots=True)
class TrainingRunConfig:
    """Configuration for a concrete fine-tuning run."""

    artifact_dir: Path
    output_dir: Path
    model_name: str
    format_name: str = "supervised"
    run_name: str = "planner_qwen25_3b_baseline"
    use_qlora: bool = True
    max_seq_length: int = 2048
    per_device_train_batch_size: int = 1
    per_device_eval_batch_size: int = 1
    gradient_accumulation_steps: int = 16
    learning_rate: float = 1e-4
    num_train_epochs: int = 3
    weight_decay: float = 0.0
    logging_steps: int = 10
    save_steps: int = 100
    lora: LoRASettings = field(default_factory=LoRASettings)


def required_training_dependencies(*, use_qlora: bool) -> list[str]:
    """Return Python packages required for the selected training mode."""

    packages = ["torch", "transformers", "datasets", "trl", "peft", "accelerate"]
    if use_qlora:
        packages.append("bitsandbytes")
    return packages


def missing_training_dependencies(*, use_qlora: bool) -> list[str]:
    """Return missing runtime dependencies for the training scaffold."""

    missing: list[str] = []
    for package in required_training_dependencies(use_qlora=use_qlora):
        try:
            importlib.import_module(package)
        except ImportError:
            missing.append(package)
    return missing


def resolve_training_artifact_paths(config: TrainingRunConfig) -> dict[str, Path]:
    """Validate and return standardized split artifact paths for a run."""

    experiment = FineTuneExperimentConfig(
        artifact_dir=config.artifact_dir,
        model_family=config.model_name,
        format_name=config.format_name,
        run_name=config.run_name,
    )
    return validate_experiment_artifacts(experiment)


def build_training_manifest(config: TrainingRunConfig) -> dict[str, Any]:
    """Build a manifest describing a planned fine-tuning run."""

    artifact_paths = resolve_training_artifact_paths(config)
    return {
        "run_name": config.run_name,
        "model_name": config.model_name,
        "format_name": config.format_name,
        "use_qlora": config.use_qlora,
        "artifact_paths": {split: str(path.resolve()) for split, path in artifact_paths.items()},
        "output_dir": str(config.output_dir.resolve()),
        "hyperparameters": {
            "max_seq_length": config.max_seq_length,
            "per_device_train_batch_size": config.per_device_train_batch_size,
            "per_device_eval_batch_size": config.per_device_eval_batch_size,
            "gradient_accumulation_steps": config.gradient_accumulation_steps,
            "learning_rate": config.learning_rate,
            "num_train_epochs": config.num_train_epochs,
            "weight_decay": config.weight_decay,
            "logging_steps": config.logging_steps,
            "save_steps": config.save_steps,
        },
        "lora": asdict(config.lora),
        "required_dependencies": required_training_dependencies(use_qlora=config.use_qlora),
        "status": "scaffold_only",
        "notes": [
            "This manifest describes the intended Phase 5 fine-tuning run.",
            "Actual TRL SFTTrainer execution is intentionally deferred to the training environment.",
        ],
    }


def write_training_manifest(config: TrainingRunConfig) -> Path:
    """Write a run manifest to the output directory."""

    output_dir = config.output_dir / config.run_name
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "training_manifest.json"
    manifest_path.write_text(json.dumps(build_training_manifest(config), indent=2), encoding="utf-8")
    return manifest_path
