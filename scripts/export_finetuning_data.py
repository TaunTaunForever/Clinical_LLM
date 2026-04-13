"""Export fine-tuning-ready planner artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from icu_qa.data.loader import load_evaluation_dataset, load_heldout_dataset, load_training_dataset
from icu_qa.config import Settings
from icu_qa.evaluation.benchmark import generate_benchmark_examples, load_benchmark_examples
from icu_qa.evaluation.finetune import (
    benchmark_to_finetune_examples,
    default_finetune_artifact_paths,
    save_finetune_split_artifacts,
)


def load_split_benchmarks_from_data() -> dict[str, list]:
    settings = Settings()
    return {
        "training": generate_benchmark_examples(load_training_dataset(settings), split_name="training"),
        "evaluation": generate_benchmark_examples(load_evaluation_dataset(settings), split_name="evaluation"),
        "heldout": generate_benchmark_examples(load_heldout_dataset(settings), split_name="heldout"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export fine-tuning-ready planner artifacts.")
    parser.add_argument(
        "--benchmark-dir",
        help="Optional directory containing standardized benchmark JSON artifacts",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write fine-tuning artifacts into",
    )
    args = parser.parse_args()

    if args.benchmark_dir:
        benchmark_dir = Path(args.benchmark_dir)
        benchmark_examples = {
            split: load_benchmark_examples(benchmark_dir / f"{split}_benchmark.json")
            for split in ("training", "evaluation", "heldout")
        }
    else:
        benchmark_examples = load_split_benchmarks_from_data()

    finetune_examples = {
        split: benchmark_to_finetune_examples(examples, split_name=split)
        for split, examples in benchmark_examples.items()
    }
    output_paths = save_finetune_split_artifacts(finetune_examples, args.output_dir)

    for split_name, split_paths in output_paths.items():
        print(f"{split_name} fine-tuning artifacts:")
        print(json.dumps({name: str(path.resolve()) for name, path in split_paths.items()}, indent=2))
        print(
            json.dumps(
                {
                    "num_examples": len(finetune_examples[split_name]),
                    "suggested_paths": {
                        name: str(path)
                        for name, path in default_finetune_artifact_paths(args.output_dir, split_name).items()
                    },
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
