"""Run starter evaluation utilities."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from icu_qa.config import Settings
from icu_qa.evaluation.metrics import json_validity_rate


def main() -> None:
    parser = argparse.ArgumentParser(description="Run starter evaluation utilities.")
    parser.add_argument(
        "--split",
        choices=["evaluation", "heldout"],
        default="evaluation",
        help="Dataset split to treat as the evaluation target",
    )
    args = parser.parse_args()

    settings = Settings()
    dataset_path = (
        settings.resolved_evaluation_data_path()
        if args.split == "evaluation"
        else settings.resolved_heldout_data_path()
    )
    sample_flags = [True, True, False]
    print("Evaluation split:", args.split)
    print("Dataset path:", dataset_path)
    print("Sample JSON validity rate:", json_validity_rate(sample_flags))


if __name__ == "__main__":
    main()
