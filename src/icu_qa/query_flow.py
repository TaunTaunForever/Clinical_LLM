"""End-to-end natural-language query orchestration."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from icu_qa.execution.engine import ExecutionResult, execute_plan
from icu_qa.explanation.summarizer import summarize_result
from icu_qa.planning.planner import PlannerClient, PlannerRequest, PlannerResponse


@dataclass(slots=True)
class QueryFlowResult:
    """Structured result for the question-to-result flow."""

    question: str
    plan: dict[str, object]
    planner_response: PlannerResponse
    execution_result: ExecutionResult | None
    explanation: str | None
    requires_clarification: bool


class QueryFlowService:
    """Run the structured planner and deterministic execution end to end."""

    def __init__(self, planner: PlannerClient) -> None:
        self.planner = planner

    def run(
        self,
        *,
        question: str,
        schema,
        frame: pd.DataFrame,
        include_explanation: bool = False,
        few_shot_examples: list[dict[str, object]] | None = None,
    ) -> QueryFlowResult:
        request = PlannerRequest(
            question=question,
            schema=schema,
            few_shot_examples=few_shot_examples or [],
        )
        planner_response = self.planner.plan(request)
        if planner_response.plan is None:
            raise ValueError("Planner returned no plan.")

        plan = planner_response.plan
        requires_clarification = bool(plan.get("requires_clarification", False))
        if requires_clarification:
            return QueryFlowResult(
                question=question,
                plan=plan,
                planner_response=planner_response,
                execution_result=None,
                explanation=None,
                requires_clarification=True,
            )

        execution_result = execute_plan(frame, plan)
        explanation = None
        if include_explanation:
            explanation = summarize_result(execution_result.result_frame, question)

        return QueryFlowResult(
            question=question,
            plan=plan,
            planner_response=planner_response,
            execution_result=execution_result,
            explanation=explanation,
            requires_clarification=False,
        )
