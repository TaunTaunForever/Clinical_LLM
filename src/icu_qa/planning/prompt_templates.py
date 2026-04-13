"""Prompt-building helpers for the remote planning service."""

from __future__ import annotations

import json
from textwrap import dedent

from icu_qa.data.schema import DatasetSchema
from icu_qa.planning.json_schema import ALLOWED_AGGREGATIONS, ANALYSIS_PLAN_JSON_SCHEMA


def build_planner_system_prompt() -> str:
    """Return the system prompt for the planner."""

    return dedent(
        """
        You are a structured analytics planner for retrospective ICU/sepsis tabular data.
        Return JSON only.
        Do not perform numerical computation.
        Do not reference unsupported columns.
        Ask for clarification by setting requires_clarification=true when the question is ambiguous.
        Do not provide diagnosis, treatment advice, or causal claims.
        """
    ).strip()


def build_planner_user_prompt(
    question: str,
    schema: DatasetSchema,
    few_shot_examples: list[dict[str, object]] | None = None,
) -> str:
    """Build the user prompt payload for structured planning."""

    examples = few_shot_examples or []
    payload = {
        "question": question,
        "schema_metadata": schema.to_prompt_payload(),
        "allowed_aggregations": sorted(ALLOWED_AGGREGATIONS),
        "allowed_operations": [
            "filter",
            "group_by",
            "aggregate",
            "sort",
            "limit",
            "compare_cohorts",
        ],
        "json_output_contract": ANALYSIS_PLAN_JSON_SCHEMA,
        "few_shot_examples": examples,
    }
    return json.dumps(payload, indent=2, sort_keys=True)
