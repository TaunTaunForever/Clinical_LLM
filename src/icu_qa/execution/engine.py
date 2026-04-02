"""Deterministic execution engine for validated plans."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from icu_qa.execution.aggregations import AGGREGATION_FUNCTIONS


@dataclass(slots=True)
class ExecutionResult:
    """Structured execution result."""

    result_frame: pd.DataFrame
    metadata: dict[str, Any]


class ExecutionEngine:
    """Run validated analysis plans against a dataframe."""

    def __init__(self, frame: pd.DataFrame) -> None:
        self.frame = frame.copy()

    def execute(self, plan: dict[str, Any]) -> ExecutionResult:
        working = self._apply_filters(self.frame, plan.get("filters", []))
        result = self._apply_aggregations(working, plan.get("group_by", []), plan.get("aggregations", []))

        select_columns = plan.get("select", [])
        if select_columns:
            existing_columns = [column for column in select_columns if column in result.columns]
            if existing_columns:
                result = result.loc[:, existing_columns]

        result = self._apply_order_by(result, plan.get("order_by", []))

        limit = plan.get("limit")
        if limit is not None:
            result = result.head(limit)

        metadata = {
            "input_rows": len(self.frame),
            "filtered_rows": len(working),
            "output_rows": len(result),
        }
        return ExecutionResult(result_frame=result.reset_index(drop=True), metadata=metadata)

    def _apply_filters(self, frame: pd.DataFrame, filters: list[dict[str, Any]]) -> pd.DataFrame:
        filtered = frame.copy()
        for filter_spec in filters:
            column = filter_spec["column"]
            operator = filter_spec["operator"]
            value = filter_spec["value"]
            if operator == "eq":
                filtered = filtered[filtered[column] == value]
            elif operator == "ne":
                filtered = filtered[filtered[column] != value]
            elif operator == "gt":
                filtered = filtered[filtered[column] > value]
            elif operator == "gte":
                filtered = filtered[filtered[column] >= value]
            elif operator == "lt":
                filtered = filtered[filtered[column] < value]
            elif operator == "lte":
                filtered = filtered[filtered[column] <= value]
            elif operator == "in":
                filtered = filtered[filtered[column].isin(value)]
            else:
                raise ValueError(f"Unsupported filter operator at execution time: {operator}")
        return filtered

    def _apply_aggregations(
        self,
        frame: pd.DataFrame,
        group_by: list[str],
        aggregations: list[dict[str, str]],
    ) -> pd.DataFrame:
        if not aggregations:
            if group_by:
                return frame.loc[:, group_by].drop_duplicates().reset_index(drop=True)
            return frame.reset_index(drop=True)

        if group_by:
            grouped = frame.groupby(group_by, dropna=False)
            rows: list[dict[str, Any]] = []
            for group_key, group_frame in grouped:
                row = self._group_key_to_row(group_by, group_key)
                for aggregation in aggregations:
                    row[aggregation["alias"]] = self._compute_aggregation(group_frame, aggregation)
                rows.append(row)
            return pd.DataFrame(rows)

        row = {
            aggregation["alias"]: self._compute_aggregation(frame, aggregation)
            for aggregation in aggregations
        }
        return pd.DataFrame([row])

    def _compute_aggregation(self, frame: pd.DataFrame, aggregation: dict[str, str]) -> Any:
        name = aggregation["name"]
        column = aggregation["column"]
        function = AGGREGATION_FUNCTIONS[name]
        return function(frame[column])

    def _apply_order_by(self, frame: pd.DataFrame, order_by: list[dict[str, str]]) -> pd.DataFrame:
        if not order_by:
            return frame
        by = [item["column"] for item in order_by]
        ascending = [item["direction"] == "asc" for item in order_by]
        return frame.sort_values(by=by, ascending=ascending)

    @staticmethod
    def _group_key_to_row(group_by: list[str], group_key: Any) -> dict[str, Any]:
        if len(group_by) == 1:
            if isinstance(group_key, tuple):
                group_key = group_key[0]
            return {group_by[0]: group_key}
        return dict(zip(group_by, group_key, strict=True))


def execute_plan(frame: pd.DataFrame, plan: dict[str, Any]) -> ExecutionResult:
    """Convenience wrapper for one-off execution."""

    return ExecutionEngine(frame).execute(plan)
