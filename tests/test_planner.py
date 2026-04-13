import json
from urllib.error import URLError

import pytest

from icu_qa.config import Settings
from icu_qa.data.schema import build_sepsis_survival_schema
from icu_qa.planning.planner import (
    HTTPPlannerTransport,
    PlannerParseError,
    PlannerRejectedError,
    PlannerRequest,
    PlannerTransportError,
    SequentialPlannerTransport,
    StaticJSONPlannerTransport,
    StructuredPlanner,
    build_default_planner,
    parse_planner_output,
)


def valid_plan() -> dict[str, object]:
    return {
        "intent": "cohort_mortality",
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


def test_parse_planner_output_accepts_plain_json() -> None:
    parsed = parse_planner_output(json.dumps(valid_plan()))
    assert parsed["intent"] == "cohort_mortality"


def test_parse_planner_output_accepts_fenced_json() -> None:
    raw_text = f"```json\n{json.dumps(valid_plan(), indent=2)}\n```"
    parsed = parse_planner_output(raw_text)
    assert parsed["analysis_type"] == "outcome_rate"


def test_parse_planner_output_rejects_invalid_json() -> None:
    with pytest.raises(PlannerParseError):
        parse_planner_output("not json")


def test_structured_planner_validates_transport_output() -> None:
    planner = StructuredPlanner(StaticJSONPlannerTransport(json.dumps(valid_plan())))
    request = PlannerRequest(
        question="What is the mortality rate?",
        schema=build_sepsis_survival_schema(),
    )
    response = planner.plan(request)

    assert response.plan is not None
    assert response.validation is not None
    assert response.validation.is_valid
    assert response.attempts == 1


def test_structured_planner_rejects_invalid_plan() -> None:
    invalid = valid_plan()
    invalid["aggregations"] = [
        {"name": "mortality_rate", "column": "unknown_column", "alias": "mortality_rate"}
    ]
    planner = StructuredPlanner(StaticJSONPlannerTransport(json.dumps(invalid)))
    request = PlannerRequest(
        question="What is the mortality rate?",
        schema=build_sepsis_survival_schema(),
    )

    with pytest.raises(PlannerRejectedError):
        planner.plan(request)


def test_structured_planner_repairs_invalid_json() -> None:
    planner = StructuredPlanner(
        SequentialPlannerTransport(["not json", json.dumps(valid_plan())]),
        max_repair_attempts=1,
    )
    request = PlannerRequest(
        question="What is the mortality rate?",
        schema=build_sepsis_survival_schema(),
    )

    response = planner.plan(request)

    assert response.plan is not None
    assert response.plan["intent"] == "cohort_mortality"
    assert response.attempts == 2


def test_structured_planner_repairs_schema_invalid_plan() -> None:
    invalid = valid_plan()
    invalid["aggregations"] = [
        {"name": "mortality_rate", "column": "unknown_column", "alias": "mortality_rate"}
    ]
    planner = StructuredPlanner(
        SequentialPlannerTransport([json.dumps(invalid), json.dumps(valid_plan())]),
        max_repair_attempts=1,
    )
    request = PlannerRequest(
        question="What is the mortality rate?",
        schema=build_sepsis_survival_schema(),
    )

    response = planner.plan(request)

    assert response.validation is not None
    assert response.validation.is_valid
    assert response.attempts == 2


def test_structured_planner_raises_after_exhausting_repairs() -> None:
    planner = StructuredPlanner(
        SequentialPlannerTransport(["not json", "still not json"]),
        max_repair_attempts=1,
    )
    request = PlannerRequest(
        question="What is the mortality rate?",
        schema=build_sepsis_survival_schema(),
    )

    with pytest.raises(PlannerParseError):
        planner.plan(request)


def test_http_planner_transport_extracts_string_content() -> None:
    decoded = {
        "choices": [
            {
                "message": {
                    "content": "{\"intent\": \"ok\"}",
                }
            }
        ]
    }
    assert HTTPPlannerTransport._extract_message_content(decoded) == "{\"intent\": \"ok\"}"


def test_http_planner_transport_extracts_text_parts() -> None:
    decoded = {
        "choices": [
            {
                "message": {
                    "content": [
                        {"type": "text", "text": "{\"intent\":"},
                        {"type": "text", "text": " \"ok\"}"},
                    ]
                }
            }
        ]
    }
    assert HTTPPlannerTransport._extract_message_content(decoded) == "{\"intent\": \"ok\"}"


def test_build_default_planner_requires_api_key() -> None:
    settings = Settings(planner_api_key="")
    with pytest.raises(PlannerTransportError):
        build_default_planner(settings)


def test_http_planner_transport_wraps_url_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = HTTPPlannerTransport(
        api_url="https://example.com/v1/chat/completions",
        api_key="test-key",
        model="test-model",
    )

    def fake_urlopen(*args: object, **kwargs: object) -> object:
        raise URLError("offline")

    monkeypatch.setattr("icu_qa.planning.planner.request.urlopen", fake_urlopen)

    with pytest.raises(PlannerTransportError):
        transport.complete([{"role": "user", "content": "hi"}])
