"""Run starter evaluation utilities."""

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
    load_benchmark_examples,
)
from icu_qa.evaluation.metrics import json_validity_rate
from icu_qa.evaluation.reporting import evaluate_plan_predictions


def main() -> None:
    parser = argparse.ArgumentParser(description="Run starter evaluation utilities.")
    parser.add_argument(
        "--split",
        choices=["training", "evaluation", "heldout"],
        default="evaluation",
        help="Dataset split to treat as the evaluation target",
    )
    parser.add_argument(
        "--benchmark-path",
        help="Optional path to a saved benchmark JSON file",
    )
    parser.add_argument(
        "--predictions-path",
        help="Optional path to JSON containing predicted plans aligned to benchmark examples",
    )
    args = parser.parse_args()

    settings = Settings()
    if args.benchmark_path:
        examples = load_benchmark_examples(args.benchmark_path)
        dataset_path = Path(args.benchmark_path).resolve()
    elif args.split == "training":
        dataset_path = settings.resolved_training_data_path()
        examples = generate_benchmark_examples(load_training_dataset(settings), split_name="training")
    elif args.split == "evaluation":
        dataset_path = settings.resolved_evaluation_data_path()
        examples = generate_benchmark_examples(load_evaluation_dataset(settings), split_name="evaluation")
    else:
        dataset_path = settings.resolved_heldout_data_path()
        examples = generate_benchmark_examples(load_heldout_dataset(settings), split_name="heldout")

    sample_flags = [True, True, False]
    print("Evaluation split:", args.split)
    print("Dataset path:", dataset_path)
    if not args.benchmark_path:
        print("Suggested artifact path:", default_benchmark_artifact_path("artifacts/benchmarks", args.split))
    print("Sample JSON validity rate:", json_validity_rate(sample_flags))
    print("Benchmark summary:")
    print(json.dumps(benchmark_summary(examples), indent=2))
    if args.predictions_path:
        predicted_plans = json.loads(Path(args.predictions_path).read_text(encoding="utf-8"))
        print("Planner performance by family and complexity:")
        print(json.dumps(evaluate_plan_predictions(examples, predicted_plans), indent=2))



if __name__ == "__main__":
    main()
