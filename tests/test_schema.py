from icu_qa.data.schema import build_sepsis_survival_schema
from icu_qa.planning.json_schema import ALLOWED_AGGREGATIONS, ANALYSIS_PLAN_JSON_SCHEMA


def test_required_plan_fields_present() -> None:
    required = set(ANALYSIS_PLAN_JSON_SCHEMA["required"])
    assert "intent" in required
    assert "analysis_type" in required
    assert "aggregations" in required
    assert "requires_clarification" in required


def test_expected_aggregations_supported() -> None:
    assert {"count", "mean", "mortality_rate", "survival_rate"}.issubset(ALLOWED_AGGREGATIONS)


def test_bound_sepsis_schema_contains_rich_planner_metadata() -> None:
    schema = build_sepsis_survival_schema()
    payload = schema.to_prompt_payload()

    assert payload["cohort_role"] == "evaluation"
    assert payload["entity_grain"] == "episode"
    assert payload["planner_guidance"]

    mortality_column = schema.get_column("mortality_flag")
    assert mortality_column is not None
    assert mortality_column.is_derived
    assert "mortality" in mortality_column.synonyms
    assert "mortality_rate" in mortality_column.supported_aggregations

    sex_label_column = schema.get_column("sex_label")
    assert sex_label_column is not None
    assert sex_label_column.supports_group_by
    assert "gender" in sex_label_column.synonyms
