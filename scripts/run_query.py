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
from icu_qa.data.schema import ColumnSchema, DatasetSchema, build_sepsis_survival_schema
from icu_qa.execution.engine import execute_plan
from icu_qa.planning.planner import (
    PlannerTransportError,
    StaticJSONPlannerTransport,
    StructuredPlanner,
    build_default_planner,
)
from icu_qa.planning.validator import assert_valid_plan
from icu_qa.query_flow import QueryFlowService


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
    parser = argparse.ArgumentParser(
        description="Run a JSON plan or end-to-end natural-language query on a dataset."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--csv-path", help="Path to the CSV dataset")
    group.add_argument(
        "--split",
        choices=["training", "evaluation", "heldout"],
        help="Configured dataset split to run the plan against",
    )
    query_mode = parser.add_mutually_exclusive_group(required=True)
    query_mode.add_argument("--plan-path", help="Path to a JSON plan file")
    query_mode.add_argument("--question", help="Natural-language analytics question")
    parser.add_argument(
        "--planner-output-path",
        help="Path to a JSON planner response to use for deterministic end-to-end runs",
    )
    parser.add_argument(
        "--repair-attempts",
        type=int,
        default=1,
        help="Maximum planner repair attempts for malformed or invalid planner outputs",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Include an explanation grounded in the computed result",
    )
    args = parser.parse_args()

    settings = Settings()
    if args.csv_path:
        dataset_label = str(Path(args.csv_path).resolve())
        frame = basic_preprocess(load_csv_dataset(args.csv_path))
        schema = infer_schema_from_frame_columns(list(frame.columns))
    elif args.split == "training":
        dataset_label = str(settings.resolved_training_data_path())
        frame = load_training_dataset(settings)
        schema = build_sepsis_survival_schema()
    elif args.split == "evaluation":
        dataset_label = str(settings.resolved_evaluation_data_path())
        frame = load_evaluation_dataset(settings)
        schema = build_sepsis_survival_schema()
    else:
        dataset_label = str(settings.resolved_heldout_data_path())
        frame = load_heldout_dataset(settings)
        schema = build_sepsis_survival_schema()

    print("Dataset:", dataset_label)

    if args.plan_path:
        with Path(args.plan_path).open("r", encoding="utf-8") as handle:
            plan = json.load(handle)

        assert_valid_plan(plan, schema)
        result = execute_plan(frame, plan)
        print("Plan mode: direct JSON plan")
        print(result.result_frame.to_string(index=False))
        print("\nMetadata:", result.metadata)
        return

    if args.planner_output_path:
        with Path(args.planner_output_path).open("r", encoding="utf-8") as handle:
            planner_output = handle.read()
        planner = StructuredPlanner(
            transport=StaticJSONPlannerTransport(planner_output),
            max_repair_attempts=args.repair_attempts,
        )
    else:
        try:
            planner = build_default_planner(
                settings=settings,
                max_repair_attempts=args.repair_attempts,
            )
        except PlannerTransportError as exc:
            raise ValueError(
                "Live planner transport is not configured. Set ICU_QA_PLANNER_API_KEY "
                "or provide --planner-output-path for deterministic runs."
            ) from exc

    flow = QueryFlowService(planner)
    flow_result = flow.run(
        question=args.question,
        schema=schema,
        frame=frame,
        include_explanation=args.explain,
    )

    print("Query mode: natural-language question")
    print("Question:", args.question)
    print("Planner attempts:", flow_result.planner_response.attempts)
    print("Planned JSON:", json.dumps(flow_result.plan, indent=2))
    if flow_result.requires_clarification:
        print("\nPlanner requires clarification. No execution was performed.")
        return

    assert flow_result.execution_result is not None
    print("\nResult:")
    print(flow_result.execution_result.result_frame.to_string(index=False))
    print("\nMetadata:", flow_result.execution_result.metadata)
    if flow_result.explanation:
        print("\nExplanation:")
        print(flow_result.explanation)


if __name__ == "__main__":
    main()
