"""Deterministic validation for planner output."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from icu_qa.data.schema import DatasetSchema
from icu_qa.planning.json_schema import (
    ALLOWED_AGGREGATIONS,
    ALLOWED_ANALYSIS_TYPES,
    ALLOWED_FILTER_OPERATORS,
    ALLOWED_SORT_DIRECTIONS,
)


class PlanValidationError(ValueError):
    """Raised when a planner output is invalid or unsupported."""


@dataclass(slots=True)
class ValidationResult:
    """Structured validation response."""

    is_valid: bool
    errors: list[str]


def _validate_column_names(columns: list[str], allowed_columns: set[str], field_name: str) -> list[str]:
    errors: list[str] = []
    for column in columns:
        if column not in allowed_columns:
            errors.append(f"Unsupported column in {field_name}: {column}")
    return errors


def validate_plan_dict(plan: dict[str, Any], schema: DatasetSchema) -> ValidationResult:
    """Validate a plan dictionary against the dataset schema and allowed operations."""

    errors: list[str] = []
    required_fields = {
        "intent",
        "analysis_type",
        "select",
        "filters",
        "group_by",
        "aggregations",
        "comparisons",
        "order_by",
        "limit",
        "requires_clarification",
        "confidence",
        "notes",
    }
    missing = required_fields.difference(plan)
    if missing:
        errors.append(f"Missing required fields: {sorted(missing)}")
        return ValidationResult(is_valid=False, errors=errors)

    allowed_columns = set(schema.column_names())
    aggregation_aliases = {
        aggregation.get("alias") for aggregation in plan.get("aggregations", []) if aggregation.get("alias")
    }

    analysis_type = plan.get("analysis_type")
    if analysis_type not in ALLOWED_ANALYSIS_TYPES:
        errors.append(f"Unsupported analysis_type: {analysis_type}")

    for select_item in plan.get("select", []):
        if select_item not in allowed_columns and select_item not in aggregation_aliases:
            errors.append(f"Unsupported column in select: {select_item}")
        elif select_item in allowed_columns:
            column_schema = schema.get_column(select_item)
            if column_schema is not None and not column_schema.supports_select:
                errors.append(f"Column does not support select: {select_item}")
    errors.extend(_validate_column_names(plan.get("group_by", []), allowed_columns, "group_by"))
    for group_item in plan.get("group_by", []):
        column_schema = schema.get_column(group_item)
        if column_schema is not None and not column_schema.supports_group_by:
            errors.append(f"Column does not support group_by: {group_item}")

    for filter_spec in plan.get("filters", []):
        column = filter_spec.get("column")
        operator = filter_spec.get("operator")
        if column not in allowed_columns:
            errors.append(f"Unsupported filter column: {column}")
        else:
            column_schema = schema.get_column(column)
            if column_schema is not None and not column_schema.supports_filter:
                errors.append(f"Column does not support filter: {column}")
        if operator not in ALLOWED_FILTER_OPERATORS:
            errors.append(f"Unsupported filter operator: {operator}")

    for aggregation in plan.get("aggregations", []):
        name = aggregation.get("name")
        column = aggregation.get("column")
        alias = aggregation.get("alias")
        if name not in ALLOWED_AGGREGATIONS:
            errors.append(f"Unsupported aggregation: {name}")
        if column not in allowed_columns:
            errors.append(f"Unsupported aggregation column: {column}")
        else:
            column_schema = schema.get_column(column)
            if column_schema is not None and name not in column_schema.supported_aggregations:
                errors.append(f"Aggregation {name} is not supported for column: {column}")
        if not alias:
            errors.append("Aggregation alias is required")

    for comparison in plan.get("comparisons", []):
        metric = comparison.get("metric")
        if metric not in ALLOWED_AGGREGATIONS:
            errors.append(f"Unsupported comparison metric: {metric}")
        for side_name in ("left_filters", "right_filters"):
            for filter_spec in comparison.get(side_name, []):
                column = filter_spec.get("column")
                operator = filter_spec.get("operator")
                if column not in allowed_columns:
                    errors.append(f"Unsupported comparison filter column: {column}")
                else:
                    column_schema = schema.get_column(column)
                    if column_schema is not None and not column_schema.supports_filter:
                        errors.append(f"Column does not support filter: {column}")
                if operator not in ALLOWED_FILTER_OPERATORS:
                    errors.append(f"Unsupported comparison filter operator: {operator}")

    for order_spec in plan.get("order_by", []):
        column = order_spec.get("column")
        direction = order_spec.get("direction")
        if column not in allowed_columns and column not in aggregation_aliases:
            errors.append(f"Unsupported order_by column: {column}")
        if direction not in ALLOWED_SORT_DIRECTIONS:
            errors.append(f"Unsupported sort direction: {direction}")

    confidence = plan.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
        errors.append("Confidence must be a number between 0 and 1")

    limit = plan.get("limit")
    if limit is not None and (not isinstance(limit, int) or limit < 1):
        errors.append("Limit must be null or a positive integer")

    if plan.get("comparisons") and plan.get("aggregations"):
        errors.append("Plans cannot mix top-level aggregations and comparisons in the same request")

    return ValidationResult(is_valid=not errors, errors=errors)


def assert_valid_plan(plan: dict[str, Any], schema: DatasetSchema) -> None:
    """Raise an exception if the plan is invalid."""

    result = validate_plan_dict(plan, schema)
    if not result.is_valid:
        raise PlanValidationError("; ".join(result.errors))
