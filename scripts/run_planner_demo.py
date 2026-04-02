"""Run the Phase 1 stub planner demo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from icu_qa.data.schema import build_sepsis_survival_schema
from icu_qa.planning.planner import PlannerRequest, StubPlanner


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Phase 1 stub planner demo.")
    parser.add_argument(
        "--split",
        choices=["training", "evaluation", "heldout"],
        default="evaluation",
        help="Dataset split label to mention in the demo question context",
    )
    parser.add_argument(
        "--question",
        default="What is the mortality rate?",
        help="Question to send to the stub planner",
    )
    args = parser.parse_args()

    schema = build_sepsis_survival_schema()
    request = PlannerRequest(
        question=f"[dataset_split={args.split}] {args.question}",
        schema=schema,
    )
    planner = StubPlanner()

    print("Messages:")
    for message in planner.build_messages(request):
        print(message)

    print("\nStub plan:")
    print(planner.plan(request).plan)


if __name__ == "__main__":
    main()
