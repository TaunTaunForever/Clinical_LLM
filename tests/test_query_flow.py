import json

import pandas as pd

from icu_qa.data.schema import build_sepsis_survival_schema
from icu_qa.planning.planner import StaticJSONPlannerTransport, StructuredPlanner
from icu_qa.query_flow import QueryFlowService


def executable_plan() -> dict[str, object]:
    return {
        "intent": "overall_mortality",
        "analysis_type": "outcome_rate",
        "select": ["mortality_rate"],
        "filters": [],
        "group_by": [],
        "aggregations": [
            {"name": "mortality_rate", "column": "mortality_flag", "alias": "mortality_rate"}
        ],
        "comparisons": [],
        "order_by": [],
        "limit": None,
        "requires_clarification": False,
        "confidence": 0.9,
        "notes": [],
    }


def grouped_ranking_plan() -> dict[str, object]:
    return {
        "intent": "mortality_by_sex",
        "analysis_type": "top_risk_groups",
        "select": ["sex_label", "mortality_rate"],
        "filters": [],
        "group_by": ["sex_label"],
        "aggregations": [
            {"name": "mortality_rate", "column": "mortality_flag", "alias": "mortality_rate"}
        ],
        "comparisons": [],
        "order_by": [{"column": "mortality_rate", "direction": "desc"}],
        "limit": 1,
        "requires_clarification": False,
        "confidence": 0.9,
        "notes": [],
    }


def clarification_plan() -> dict[str, object]:
    return {
        "intent": "ambiguous_question",
        "analysis_type": "descriptive_summary",
        "select": [],
        "filters": [],
        "group_by": [],
        "aggregations": [],
        "comparisons": [],
        "order_by": [],
        "limit": None,
        "requires_clarification": True,
        "confidence": 0.2,
        "notes": ["Question is ambiguous."],
    }


def demo_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age_years": [20, 40, 70],
            "sex_0male_1female": [0, 1, 0],
            "episode_number": [1, 1, 2],
            "hospital_outcome_1alive_0dead": [1, 0, 1],
            "sex_label": ["male", "female", "male"],
            "survival_flag": [1, 0, 1],
            "mortality_flag": [0, 1, 0],
        }
    )


def test_query_flow_executes_non_ambiguous_plan() -> None:
    planner = StructuredPlanner(StaticJSONPlannerTransport(json.dumps(executable_plan())))
    flow = QueryFlowService(planner)

    result = flow.run(
        question="What is the mortality rate?",
        schema=build_sepsis_survival_schema(),
        frame=demo_frame(),
        include_explanation=True,
    )

    assert not result.requires_clarification
    assert result.execution_result is not None
    assert list(result.execution_result.result_frame["mortality_rate"]) == [1 / 3]
    assert result.explanation is not None


def test_query_flow_skips_execution_when_clarification_required() -> None:
    planner = StructuredPlanner(StaticJSONPlannerTransport(json.dumps(clarification_plan())))
    flow = QueryFlowService(planner)

    result = flow.run(
        question="How severe were outcomes?",
        schema=build_sepsis_survival_schema(),
        frame=demo_frame(),
    )

    assert result.requires_clarification
    assert result.execution_result is None


def test_query_flow_executes_grouped_ranking_plan() -> None:
    planner = StructuredPlanner(StaticJSONPlannerTransport(json.dumps(grouped_ranking_plan())))
    flow = QueryFlowService(planner)

    result = flow.run(
        question="Which sex group has the highest mortality rate?",
        schema=build_sepsis_survival_schema(),
        frame=demo_frame(),
    )

    assert result.execution_result is not None
    result_frame = result.execution_result.result_frame
    assert list(result_frame["sex_label"]) == ["female"]
    assert list(result_frame["mortality_rate"]) == [1.0]
