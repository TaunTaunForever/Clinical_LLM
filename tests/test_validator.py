from icu_qa.data.schema import ColumnSchema, DatasetSchema
from icu_qa.planning.validator import validate_plan_dict


def demo_schema() -> DatasetSchema:
    return DatasetSchema(
        name="demo",
        columns=[
            ColumnSchema(name="age", dtype="int", description="Age"),
            ColumnSchema(
                name="mortality_flag",
                dtype="binary",
                description="Mortality",
                supported_aggregations=["mortality_rate", "count", "proportion", "mean"],
            ),
            ColumnSchema(name="sepsis_flag", dtype="binary", description="Sepsis cohort membership"),
            ColumnSchema(
                name="episode_number",
                dtype="int",
                description="Episode",
                supports_group_by=False,
                supported_aggregations=["count"],
            ),
        ],
    )


def valid_plan() -> dict[str, object]:
    return {
        "intent": "cohort_mortality",
        "analysis_type": "outcome_rate",
        "select": ["mortality_rate"],
        "filters": [{"column": "sepsis_flag", "operator": "eq", "value": 1}],
        "group_by": [],
        "aggregations": [
            {"name": "mortality_rate", "column": "mortality_flag", "alias": "mortality_rate"}
        ],
        "comparisons": [],
        "order_by": [{"column": "mortality_rate", "direction": "desc"}],
        "limit": 5,
        "requires_clarification": False,
        "confidence": 0.9,
        "notes": [],
    }


def test_validator_accepts_supported_plan() -> None:
    result = validate_plan_dict(valid_plan(), demo_schema())
    assert result.is_valid
    assert result.errors == []


def test_validator_rejects_unknown_column() -> None:
    plan = valid_plan()
    plan["filters"] = [{"column": "unknown_column", "operator": "eq", "value": 1}]
    result = validate_plan_dict(plan, demo_schema())
    assert not result.is_valid
    assert any("Unsupported filter column" in error for error in result.errors)


def test_validator_rejects_group_by_for_disallowed_column() -> None:
    plan = valid_plan()
    plan["group_by"] = ["episode_number"]
    result = validate_plan_dict(plan, demo_schema())
    assert not result.is_valid
    assert any("does not support group_by" in error for error in result.errors)


def test_validator_rejects_unsupported_aggregation_for_column() -> None:
    plan = valid_plan()
    plan["aggregations"] = [{"name": "std", "column": "mortality_flag", "alias": "std_mortality"}]
    result = validate_plan_dict(plan, demo_schema())
    assert not result.is_valid
    assert any("is not supported for column" in error for error in result.errors)
