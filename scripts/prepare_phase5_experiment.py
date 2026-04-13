"""Validate and summarize fine-tuning artifacts for a Phase 5 run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from icu_qa.training.artifacts import (
    load_chat_records,
    load_supervised_records,
    summarize_finetune_records,
)
from icu_qa.training.experiment import FineTuneExperimentConfig, validate_experiment_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a Phase 5 fine-tuning experiment.")
    parser.add_argument(
        "--artifact-dir",
        required=True,
        help="Directory containing standardized fine-tuning artifacts",
    )
    parser.add_argument(
        "--model-family",
        default="Qwen/Qwen2.5-3B-Instruct",
        help="Identifier for the base model family you plan to fine-tune",
    )
    parser.add_argument(
        "--format",
        choices=["supervised", "chat"],
        default="supervised",
        help="Fine-tuning artifact format to validate",
    )
    parser.add_argument(
        "--run-name",
        default="planner_finetune_baseline",
        help="Experiment run name",
    )
    args = parser.parse_args()

    config = FineTuneExperimentConfig(
        artifact_dir=Path(args.artifact_dir),
        model_family=args.model_family,
        format_name=args.format,
        run_name=args.run_name,
    )
    split_paths = validate_experiment_artifacts(config)
    print(
        json.dumps(
            {
                "run_name": config.run_name,
                "model_family": config.model_family,
                "format": config.format_name,
                "artifact_paths": {split: str(path.resolve()) for split, path in split_paths.items()},
            },
            indent=2,
        )
    )

    loader = load_supervised_records if args.format == "supervised" else load_chat_records
    for split_name, path in split_paths.items():
        summary = summarize_finetune_records(loader(path), args.format)
        print(f"{split_name} summary:")
        print(
            json.dumps(
                {
                    "num_examples": summary.num_examples,
                    "avg_input_chars": summary.avg_input_chars,
                    "avg_target_chars": summary.avg_target_chars,
                    "complexity_tier_counts": summary.complexity_tier_counts,
                    "analysis_family_counts": summary.analysis_family_counts,
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
