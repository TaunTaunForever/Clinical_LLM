"""JSON schema contract for planner output."""

from __future__ import annotations

ALLOWED_ANALYSIS_TYPES = {
    "descriptive_summary",
    "outcome_rate",
    "cohort_comparison",
    "top_risk_groups",
    "feature_difference",
    "distribution_query",
}

ALLOWED_FILTER_OPERATORS = {"eq", "ne", "gt", "gte", "lt", "lte", "in"}
ALLOWED_AGGREGATIONS = {
    "count",
    "mean",
    "median",
    "std",
    "min",
    "max",
    "proportion",
    "mortality_rate",
    "survival_rate",
}
ALLOWED_SORT_DIRECTIONS = {"asc", "desc"}

ANALYSIS_PLAN_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
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
    ],
    "properties": {
        "intent": {"type": "string"},
        "analysis_type": {"type": "string", "enum": sorted(ALLOWED_ANALYSIS_TYPES)},
        "select": {"type": "array", "items": {"type": "string"}},
        "filters": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["column", "operator", "value"],
                "properties": {
                    "column": {"type": "string"},
                    "operator": {"type": "string", "enum": sorted(ALLOWED_FILTER_OPERATORS)},
                    "value": {},
                },
            },
        },
        "group_by": {"type": "array", "items": {"type": "string"}},
        "aggregations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "column", "alias"],
                "properties": {
                    "name": {"type": "string", "enum": sorted(ALLOWED_AGGREGATIONS)},
                    "column": {"type": "string"},
                    "alias": {"type": "string"},
                },
            },
        },
        "comparisons": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["left_filters", "right_filters", "metric"],
                "properties": {
                    "left_filters": {"type": "array"},
                    "right_filters": {"type": "array"},
                    "metric": {"type": "string"},
                },
            },
        },
        "order_by": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["column", "direction"],
                "properties": {
                    "column": {"type": "string"},
                    "direction": {"type": "string", "enum": sorted(ALLOWED_SORT_DIRECTIONS)},
                },
            },
        },
        "limit": {"type": ["integer", "null"], "minimum": 1},
        "requires_clarification": {"type": "boolean"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "notes": {"type": "array", "items": {"type": "string"}},
    },
}
