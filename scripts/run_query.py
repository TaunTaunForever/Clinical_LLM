"""Run a validated plan against a local CSV dataset."""

from __future__ import annotations

import argparse
import json
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
from icu_qa.data.schema import ColumnSchema, DatasetSchema
from icu_qa.execution.engine import execute_plan
from icu_qa.planning.validator import assert_valid_plan


def infer_schema_from_frame_columns(columns: list[str]) -> DatasetSchema:
    """Build a minimal dataset schema from known column names.

    TODO: Replace with richer schema metadata extraction.
    """

    return DatasetSchema(
        name="local_csv_dataset",
        columns=[
            ColumnSchema(name=column, dtype="unknown", description=f"Column {column}")
            for column in columns
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a JSON analysis plan on a local CSV.")
    parser.add_argument("plan_path", help="Path to a JSON plan file")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--csv-path", help="Path to the CSV dataset")
    group.add_argument(
        "--split",
        choices=["training", "evaluation", "heldout"],
        help="Configured dataset split to run the plan against",
    )
    args = parser.parse_args()

    settings = Settings()
    if args.csv_path:
        dataset_label = str(Path(args.csv_path).resolve())
        frame = basic_preprocess(load_csv_dataset(args.csv_path))
    elif args.split == "training":
        dataset_label = str(settings.resolved_training_data_path())
        frame = load_training_dataset(settings)
    elif args.split == "evaluation":
        dataset_label = str(settings.resolved_evaluation_data_path())
        frame = load_evaluation_dataset(settings)
    else:
        dataset_label = str(settings.resolved_heldout_data_path())
        frame = load_heldout_dataset(settings)

    schema = infer_schema_from_frame_columns(list(frame.columns))
    with Path(args.plan_path).open("r", encoding="utf-8") as handle:
        plan = json.load(handle)

    assert_valid_plan(plan, schema)
    result = execute_plan(frame, plan)
    print("Dataset:", dataset_label)
    print(result.result_frame.to_string(index=False))
    print("\nMetadata:", result.metadata)


if __name__ == "__main__":
    main()
