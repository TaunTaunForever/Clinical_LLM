import pandas as pd

from icu_qa.execution.engine import execute_plan


def test_execution_engine_computes_grouped_mortality_rate() -> None:
    frame = pd.DataFrame(
        {
            "sepsis_flag": [1, 1, 1, 0],
            "sex": ["F", "F", "M", "M"],
            "mortality_flag": [1, 0, 1, 0],
        }
    )
    plan = {
        "filters": [{"column": "sepsis_flag", "operator": "eq", "value": 1}],
        "group_by": ["sex"],
        "aggregations": [
            {"name": "mortality_rate", "column": "mortality_flag", "alias": "mortality_rate"}
        ],
        "select": ["sex", "mortality_rate"],
        "order_by": [{"column": "sex", "direction": "asc"}],
        "limit": None,
    }

    result = execute_plan(frame, plan).result_frame

    assert list(result["sex"]) == ["F", "M"]
    assert list(result["mortality_rate"]) == [0.5, 1.0]
