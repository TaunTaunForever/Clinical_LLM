"""Planner interfaces and a local stub implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from icu_qa.data.schema import DatasetSchema
from icu_qa.planning.prompt_templates import (
    build_planner_system_prompt,
    build_planner_user_prompt,
)


@dataclass(slots=True)
class PlannerRequest:
    """Structured input to the planning layer."""

    question: str
    schema: DatasetSchema
    few_shot_examples: list[dict[str, object]] = field(default_factory=list)


@dataclass(slots=True)
class PlannerResponse:
    """Structured output from the planning layer."""

    raw_text: str
    plan: dict[str, Any] | None = None


class StubPlanner:
    """A non-LLM stub used to exercise the planning interface in Phase 1.

    TODO: Replace with a real remote planner client.
    """

    def build_messages(self, request: PlannerRequest) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": build_planner_system_prompt()},
            {
                "role": "user",
                "content": build_planner_user_prompt(
                    question=request.question,
                    schema=request.schema,
                    few_shot_examples=request.few_shot_examples,
                ),
            },
        ]

    def plan(self, request: PlannerRequest) -> PlannerResponse:
        placeholder_plan = {
            "intent": "unsupported_stub",
            "analysis_type": "descriptive_summary",
            "select": [],
            "filters": [],
            "group_by": [],
            "aggregations": [],
            "comparisons": [],
            "order_by": [],
            "limit": None,
            "requires_clarification": True,
            "confidence": 0.0,
            "notes": ["TODO: integrate remote planner service."],
        }
        return PlannerResponse(raw_text=str(placeholder_plan), plan=placeholder_plan)
