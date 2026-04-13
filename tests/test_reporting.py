import json

import pandas as pd

from icu_qa.evaluation.benchmark import generate_benchmark_examples
from icu_qa.evaluation.reporting import evaluate_plan_predictions


def demo_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age_years": [20, 40, 70, 80],
            "sex_0male_1female": [0, 1, 0, 1],
            "episode_number": [1, 1, 2, 2],
            "hospital_outcome_1alive_0dead": [1, 0, 1, 0],
            "sex_label": ["male", "female", "male", "female"],
            "survival_flag": [1, 0, 1, 0],
            "mortality_flag": [0, 1, 0, 1],
        }
    )


def test_evaluate_plan_predictions_reports_family_and_complexity() -> None:
    examples = generate_benchmark_examples(demo_frame(), split_name="evaluation")
    predicted_plans = [example.gold_plan for example in examples]

    report = evaluate_plan_predictions(examples, predicted_plans)

    assert report["overall"]["exact_plan_match_rate"] == 1.0
    assert "outcome_rate" in report["by_analysis_family"]
    assert "hard" in report["by_complexity_tier"]

