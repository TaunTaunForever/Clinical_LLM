"""Scaffold a Phase 5 fine-tuning run for the selected base model."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from icu_qa.config import Settings
from icu_qa.training.runner import (
    TrainingRunConfig,
    build_training_manifest,
    missing_training_dependencies,
    write_training_manifest,
)


def main() -> None:
    settings = Settings()
    parser = argparse.ArgumentParser(description="Scaffold a Phase 5 fine-tuning run.")
    parser.add_argument(
        "--artifact-dir",
        default=str(settings.resolved_training_artifact_dir()),
        help="Directory containing standardized fine-tuning artifacts",
    )
    parser.add_argument(
        "--output-dir",
        default=str(settings.resolved_training_output_dir()),
        help="Directory where run manifests and checkpoints should be written",
    )
    parser.add_argument(
        "--model-name",
        default=settings.training_base_model_name,
        help="Base model to fine-tune",
    )
    parser.add_argument(
        "--format",
        choices=["supervised", "chat"],
        default="supervised",
        help="Artifact format to use for training",
    )
    parser.add_argument(
        "--run-name",
        default="planner_qwen25_3b_baseline",
        help="Name for this training run",
    )
    parser.add_argument(
        "--disable-qlora",
        action="store_true",
        help="Disable QLoRA-specific dependency checks and manifest settings",
    )
    parser.add_argument(
        "--check-dependencies-only",
        action="store_true",
        help="Only report whether required training dependencies are installed",
    )
    args = parser.parse_args()

    config = TrainingRunConfig(
        artifact_dir=Path(args.artifact_dir),
        output_dir=Path(args.output_dir),
        model_name=args.model_name,
        format_name=args.format,
        run_name=args.run_name,
        use_qlora=not args.disable_qlora,
    )

    missing = missing_training_dependencies(use_qlora=config.use_qlora)
    print(
        json.dumps(
            {
                "model_name": config.model_name,
                "format_name": config.format_name,
                "use_qlora": config.use_qlora,
                "missing_dependencies": missing,
            },
            indent=2,
        )
    )
    if args.check_dependencies_only:
        return

    manifest_path = write_training_manifest(config)
    print("Training manifest:")
    print(json.dumps(build_training_manifest(config), indent=2))
    print(f"Wrote training manifest to {manifest_path.resolve()}")
    print("TODO: execute TRL SFTTrainer in the target training environment.")


if __name__ == "__main__":
    main()
