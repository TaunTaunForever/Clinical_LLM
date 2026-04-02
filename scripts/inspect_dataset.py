"""Inspect a local ICU/sepsis CSV dataset."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from icu_qa.config import Settings
from icu_qa.data.loader import (
    load_csv_dataset,
    load_evaluation_dataset,
    load_heldout_dataset,
    load_training_dataset,
)
from icu_qa.data.preprocessing import basic_preprocess


def load_named_split(split: str) -> tuple[str, object]:
    """Load one of the configured dataset splits."""

    settings = Settings()
    if split == "training":
        return str(settings.resolved_training_data_path()), load_training_dataset(settings)
    if split == "evaluation":
        return str(settings.resolved_evaluation_data_path()), load_evaluation_dataset(settings)
    if split == "heldout":
        return str(settings.resolved_heldout_data_path()), load_heldout_dataset(settings)
    raise ValueError(f"Unsupported split: {split}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a local CSV dataset.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--path", help="Path to the CSV dataset")
    group.add_argument(
        "--split",
        choices=["training", "evaluation", "heldout"],
        help="Configured dataset split to inspect",
    )
    args = parser.parse_args()

    if args.path:
        dataset_label = str(Path(args.path).resolve())
        frame = basic_preprocess(load_csv_dataset(args.path))
    else:
        dataset_label, frame = load_named_split(args.split)

    print("Dataset:", dataset_label)
    print("Rows:", len(frame))
    print("Columns:", list(frame.columns))
    print(frame.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
