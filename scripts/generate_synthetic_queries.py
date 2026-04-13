"""Generate starter semi-synthetic query examples."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from icu_qa.config import Settings
from icu_qa.data.loader import load_evaluation_dataset, load_heldout_dataset, load_training_dataset
from icu_qa.evaluation.benchmark import (
    benchmark_summary,
    default_benchmark_artifact_path,
    generate_benchmark_examples,
    save_benchmark_examples,
    save_split_benchmark_artifacts,
)


def load_split_frame(split: str):
    settings = Settings()
    if split == "training":
        return load_training_dataset(settings)
    if split == "evaluation":
        return load_evaluation_dataset(settings)
    return load_heldout_dataset(settings)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate semi-synthetic benchmark examples.")
    parser.add_argument(
        "--split",
        choices=["training", "evaluation", "heldout"],
        default="training",
        help="Dataset split to generate examples from",
    )
    parser.add_argument(
        "--output-path",
        help="Optional output JSON path for benchmark examples",
    )
    parser.add_argument(
        "--artifact-dir",
        help="Optional directory to write standardized benchmark artifacts",
    )
    parser.add_argument(
        "--all-splits",
        action="store_true",
        help="Generate standardized benchmark artifacts for training, evaluation, and heldout",
    )
    args = parser.parse_args()

    if args.all_splits:
        split_examples = {
            "training": generate_benchmark_examples(load_split_frame("training"), split_name="training"),
            "evaluation": generate_benchmark_examples(load_split_frame("evaluation"), split_name="evaluation"),
            "heldout": generate_benchmark_examples(load_split_frame("heldout"), split_name="heldout"),
        }
        if not args.artifact_dir:
            raise ValueError("--artifact-dir is required when using --all-splits")
        output_paths = save_split_benchmark_artifacts(split_examples, args.artifact_dir)
        for split_name, examples in split_examples.items():
            print(f"{split_name} summary:")
            print(json.dumps(benchmark_summary(examples), indent=2))
            print(f"Artifact: {output_paths[split_name].resolve()}")
        return

    frame = load_split_frame(args.split)
    examples = generate_benchmark_examples(frame, split_name=args.split)
    summary = benchmark_summary(examples)

    print(json.dumps(summary, indent=2))
    if args.output_path:
        save_benchmark_examples(examples, args.output_path)
        print(f"Wrote benchmark examples to {Path(args.output_path).resolve()}")
    elif args.artifact_dir:
        output_path = default_benchmark_artifact_path(args.artifact_dir, args.split)
        save_benchmark_examples(examples, output_path)
        print(f"Wrote benchmark examples to {output_path.resolve()}")
    else:
        print(json.dumps([example.to_record() for example in examples], indent=2))


if __name__ == "__main__":
    main()
