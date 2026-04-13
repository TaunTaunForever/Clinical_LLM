"""Evaluation reporting helpers for grouped planner performance."""

from __future__ import annotations

from typing import Any

from icu_qa.evaluation.benchmark import BenchmarkExample
from icu_qa.evaluation.metrics import exact_plan_match, slot_level_accuracy


def evaluate_plan_predictions(
    benchmark_examples: list[BenchmarkExample],
    predicted_plans: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarize planner performance overall and by metadata bucket."""

    if len(benchmark_examples) != len(predicted_plans):
        raise ValueError("Predicted plans must align 1:1 with benchmark examples.")

    per_example_rows: list[dict[str, Any]] = []
    for example, predicted in zip(benchmark_examples, predicted_plans, strict=True):
        per_example_rows.append(
            {
                "analysis_family": example.metadata.get("analysis_family", "unknown"),
                "complexity_tier": example.metadata.get("complexity_tier", "unknown"),
                "exact_plan_match": exact_plan_match(predicted, example.gold_plan),
                "slot_level_accuracy": slot_level_accuracy(predicted, example.gold_plan),
            }
        )

    def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
        count = len(rows)
        if count == 0:
            return {"count": 0, "exact_plan_match_rate": 0.0, "avg_slot_level_accuracy": 0.0}
        return {
            "count": count,
            "exact_plan_match_rate": sum(bool(row["exact_plan_match"]) for row in rows) / count,
            "avg_slot_level_accuracy": sum(float(row["slot_level_accuracy"]) for row in rows) / count,
        }

    by_family: dict[str, list[dict[str, Any]]] = {}
    by_complexity: dict[str, list[dict[str, Any]]] = {}
    for row in per_example_rows:
        by_family.setdefault(str(row["analysis_family"]), []).append(row)
        by_complexity.setdefault(str(row["complexity_tier"]), []).append(row)

    return {
        "overall": summarize(per_example_rows),
        "by_analysis_family": {family: summarize(rows) for family, rows in by_family.items()},
        "by_complexity_tier": {
            complexity: summarize(rows) for complexity, rows in by_complexity.items()
        },
    }
