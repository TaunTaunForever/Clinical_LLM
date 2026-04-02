from icu_qa.planning.json_schema import ALLOWED_AGGREGATIONS, ANALYSIS_PLAN_JSON_SCHEMA


def test_required_plan_fields_present() -> None:
    required = set(ANALYSIS_PLAN_JSON_SCHEMA["required"])
    assert "intent" in required
    assert "analysis_type" in required
    assert "aggregations" in required
    assert "requires_clarification" in required


def test_expected_aggregations_supported() -> None:
    assert {"count", "mean", "mortality_rate", "survival_rate"}.issubset(ALLOWED_AGGREGATIONS)
